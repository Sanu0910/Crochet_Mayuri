"""Mayuri'z uploader bot.

Send a photo with the piece's name as the caption, tap a category, and it
goes into images/, into the gallery on the site, and into the film's scene
list — then gets committed and pushed. See README.md.
"""

import asyncio
import html
import logging
import os
import sys
from pathlib import Path

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from catalogue import BY_KEY, CATEGORIES
from media import save_photo, slugify, unique_slug
from repo import GitError, Repo
from site_edit import SiteEditError, insert_into_film, insert_into_index

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("mayuriz-bot")

# --- configuration -------------------------------------------------------

TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.environ.get("GITHUB_REPO", "Sanu0910/Crochet_Mayuri").strip()
# GitHub Pages serves this repo from the branch below, not from main, so
# that is where an upload has to land to actually become visible.
BRANCH = os.environ.get("GIT_BRANCH", "claude/website-mobile-redesign-xfmicu").strip()
WORKDIR = Path(os.environ.get("WORKDIR", "/tmp/mayuriz-site"))
SITE_URL = os.environ.get("SITE_URL", "").strip()

_raw_allowed = os.environ.get("ALLOWED_USER_IDS", "").replace(" ", "")
ALLOWED: set[int] = {int(x) for x in _raw_allowed.split(",") if x}

MAX_PHOTO_BYTES = 12 * 1024 * 1024

repo = Repo(
    url=f"https://github.com/{GITHUB_REPO}.git",
    token=GITHUB_TOKEN,
    branch=BRANCH,
    workdir=WORKDIR,
)

# Photos waiting for their category, keyed by the id we put on the buttons.
pending: dict[str, dict] = {}


# --- access --------------------------------------------------------------

def authorised(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id in ALLOWED)


async def refuse(update: Update) -> None:
    """Tell an unknown user their id, so setting the whitelist is self-service."""
    user = update.effective_user
    chat = update.effective_chat
    await update.effective_message.reply_text(
        "Sorry — you're not on this bot's list, so I can't publish for you.\n\n"
        f"Your Telegram user ID: <code>{user.id if user else '?'}</code>\n"
        f"This chat's ID: <code>{chat.id if chat else '?'}</code>\n\n"
        "Whoever set the bot up can add that user ID to ALLOWED_USER_IDS.",
        parse_mode=ParseMode.HTML,
    )
    log.warning("refused user %s in chat %s", user.id if user else "?", chat.id if chat else "?")


# --- commands ------------------------------------------------------------

HELP = """<b>Mayuri'z uploader</b>

<b>To add a piece:</b> send a photo with the name as the caption.
Put a description on the second line if you want one.

<i>Example caption:</i>
<code>Ocean Blue Ruffle Scrunchie
Deep teal ruffles on a soft white band.</code>

Then tap a category and I'll put it on the site.

<b>Commands</b>
/recent — the last few changes
/undo — undo the most recent change
/film — re-render the video with everything currently in the shop
/whoami — your Telegram ID and this chat's ID
/help — this message"""


async def cmd_start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return await refuse(update)
    await update.effective_message.reply_text(HELP, parse_mode=ParseMode.HTML)


async def cmd_whoami(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user, chat = update.effective_user, update.effective_chat
    await update.effective_message.reply_text(
        f"Your user ID: <code>{user.id}</code>\n"
        f"This chat's ID: <code>{chat.id}</code>\n"
        f"On the allow-list: {'yes' if authorised(update) else 'no'}",
        parse_mode=ParseMode.HTML,
    )


async def cmd_recent(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return await refuse(update)
    async with repo.lock:
        try:
            await asyncio.to_thread(repo.refresh)
            lines = await asyncio.to_thread(repo.last_commits, 6)
        except GitError as exc:
            return await update.effective_message.reply_text(f"⚠️ {exc}")
    body = "\n".join(html.escape(line) for line in lines)
    await update.effective_message.reply_text(
        f"<b>Recent changes</b>\n<pre>{body}</pre>", parse_mode=ParseMode.HTML
    )


async def cmd_undo(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return await refuse(update)
    message = await update.effective_message.reply_text("Undoing the last change…")
    async with repo.lock:
        try:
            await asyncio.to_thread(repo.refresh)
            subject, sha = await asyncio.to_thread(repo.revert_last_bot_commit)
        except GitError as exc:
            return await message.edit_text(f"⚠️ Couldn't undo it: {exc}")
    await message.edit_text(
        f"↩️ Undone: <i>{html.escape(subject)}</i>\nNew commit <code>{sha}</code>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_film(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return await refuse(update)
    message = await update.effective_message.reply_text("Asking GitHub to re-render the film…")
    url = (
        f"https://api.github.com/repos/{GITHUB_REPO}"
        "/actions/workflows/render-film.yml/dispatches"
    )
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github+json",
                },
                json={"ref": BRANCH},
            )
    except Exception as exc:
        return await message.edit_text(f"⚠️ Couldn't reach GitHub: {exc}")

    if response.status_code == 204:
        await message.edit_text(
            "🎬 Re-rendering. It takes about 5 minutes, then the new film is "
            "pushed automatically.\n"
            f"Progress: https://github.com/{GITHUB_REPO}/actions"
        )
    else:
        await message.edit_text(
            f"⚠️ GitHub said {response.status_code}. The token may be missing "
            "the Actions permission — see bot/README.md."
        )


# --- the upload flow -----------------------------------------------------

async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not authorised(update):
        return await refuse(update)

    message = update.effective_message
    caption = (message.caption or "").strip()
    if not caption:
        await message.reply_text(
            "I need a name for it — send the photo again with the name as the "
            "caption.\n\nLike: <code>Ocean Blue Ruffle Scrunchie</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    lines = [line.strip() for line in caption.splitlines() if line.strip()]
    name = lines[0][:80]
    desc = " ".join(lines[1:])[:300] or f"{name} — handmade to order, in any colour you like."

    photo = message.photo[-1]  # the largest size Telegram kept
    if photo.file_size and photo.file_size > MAX_PHOTO_BYTES:
        return await message.reply_text("That photo is very large — send a smaller one.")

    key = f"{message.chat_id}:{message.message_id}"
    pending[key] = {
        "file_id": photo.file_id,
        "name": name,
        "desc": desc,
        "user": update.effective_user.full_name,
    }
    # Don't let abandoned uploads pile up in memory forever.
    if len(pending) > 50:
        pending.pop(next(iter(pending)))

    rows, row = [], []
    for category in CATEGORIES:
        row.append(InlineKeyboardButton(category.button, callback_data=f"c|{key}|{category.key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("✖️ Cancel", callback_data=f"x|{key}|-")])

    await message.reply_text(
        f"<b>{html.escape(name)}</b>\n{html.escape(desc)}\n\nWhich shelf does it go on?",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode=ParseMode.HTML,
    )


async def on_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if not authorised(update):
        return await query.edit_message_text("You're not on this bot's list.")

    action, key, cat = query.data.split("|", 2)
    item = pending.get(key)
    if item is None:
        return await query.edit_message_text(
            "I've lost track of that photo (the bot restarted). Send it again."
        )

    if action == "x":
        pending.pop(key, None)
        return await query.edit_message_text("Cancelled — nothing was published.")

    pending.pop(key, None)
    name, desc, who = item["name"], item["desc"], item["user"]
    await query.edit_message_text(f"Adding <b>{html.escape(name)}</b>…", parse_mode=ParseMode.HTML)

    try:
        file = await context.bot.get_file(item["file_id"])
        raw = bytes(await file.download_as_bytearray())
    except Exception as exc:
        log.exception("download failed")
        return await query.edit_message_text(f"⚠️ Couldn't download the photo: {exc}")

    async with repo.lock:
        try:
            result = await asyncio.to_thread(_publish, raw, name, desc, cat, who)
        except (GitError, SiteEditError) as exc:
            await asyncio.to_thread(repo.discard)
            return await query.edit_message_text(f"⚠️ {html.escape(str(exc))}",
                                                 parse_mode=ParseMode.HTML)
        except Exception as exc:
            log.exception("publish failed")
            await asyncio.to_thread(repo.discard)
            return await query.edit_message_text(f"⚠️ Something went wrong: {html.escape(str(exc))}",
                                                 parse_mode=ParseMode.HTML)

    sha, filename, total = result
    where = f"\n{SITE_URL}" if SITE_URL else ""
    await query.edit_message_text(
        f"✅ <b>{html.escape(name)}</b> is in the shop.\n"
        f"{BY_KEY[cat].tag} · <code>{filename}</code> · {total} pieces total\n"
        f"Commit <code>{sha}</code> — live in a minute or two.{where}\n\n"
        "<i>/undo if that wasn't right. /film to refresh the video.</i>",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


def _publish(raw: bytes, name: str, desc: str, cat: str, who: str) -> tuple[str, str, int]:
    """The whole blocking half of an upload. Runs under the repo lock."""
    repo.refresh()

    images_dir = repo.path / "images"
    slug = unique_slug(slugify(name), images_dir)
    filename = save_photo(raw, images_dir, slug)

    insert_into_index(
        repo.path / "index.html",
        product_id=slug, name=name, cat=cat, desc=desc, image=filename,
    )
    insert_into_film(
        repo.path / "video/src/theme.ts", name=name, cat=cat, image=filename,
    )

    total = len(list(images_dir.glob("*.jpg")))
    sha = repo.commit_and_push(
        f"Add {name} to the shop\n\n"
        f"Uploaded via Telegram by {who}. Filed under {BY_KEY[cat].tag}.\n"
        f"The film's scene list was updated to match; run /film to re-render it."
    )
    return sha, filename, total


async def on_text(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """A photo-less message in a DM — nudge, but stay quiet in groups."""
    if update.effective_chat.type != "private":
        return
    if not authorised(update):
        return await refuse(update)
    await update.effective_message.reply_text(
        "Send me a photo with the name as its caption. /help for the details."
    )


# --- startup -------------------------------------------------------------

def check_config() -> None:
    missing = [
        name for name, value in
        (("TELEGRAM_TOKEN", TOKEN), ("GITHUB_TOKEN", GITHUB_TOKEN))
        if not value
    ]
    if missing:
        sys.exit(f"Missing environment variable(s): {', '.join(missing)}")
    if not ALLOWED:
        log.warning(
            "ALLOWED_USER_IDS is empty — the bot will publish for nobody and "
            "will reply with each person's ID so you can fill it in."
        )


def main() -> None:
    check_config()
    repo.clone()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler(["start", "help"], cmd_start))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("recent", cmd_recent))
    app.add_handler(CommandHandler("undo", cmd_undo))
    app.add_handler(CommandHandler("film", cmd_film))
    app.add_handler(MessageHandler(filters.PHOTO, on_photo))
    app.add_handler(CallbackQueryHandler(on_category))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    log.info("listening — %d user(s) allowed, pushing to %s@%s",
             len(ALLOWED), GITHUB_REPO, BRANCH)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
