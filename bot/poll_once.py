"""One pass of the uploader, run on a schedule by GitHub Actions.

Unlike main.py (which holds a connection open and answers instantly), this
wakes up, deals with whatever has arrived since last time, and exits. It
runs inside a checkout of the site, so it edits files in place and leaves
committing and pushing to the workflow.

Caption contract — the name on the first line, a category hashtag anywhere,
and an optional description after:

    Ocean Blue Ruffle Scrunchie #scrunchies
    Deep teal ruffles on a soft white band.
"""

import html
import json
import logging
import os
import re
import sys
from pathlib import Path

import httpx

from catalogue import BY_KEY, CATEGORIES
from media import save_photo, slugify, unique_slug
from pricing import find_price
from site_edit import (
    SiteEditError,
    insert_into_film,
    insert_into_index,
    remove_product,
    update_product,
)
from telegram_api import Telegram

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("uploader")

REPO_ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.environ.get("GITHUB_REPO", "Sanu0910/Crochet_Mayuri").strip()
BRANCH = os.environ.get("GIT_BRANCH", "claude/website-mobile-redesign-xfmicu").strip()
SITE_URL = os.environ.get("SITE_URL", "").strip()
COMMIT_MSG_FILE = Path(os.environ.get("COMMIT_MSG_FILE", "/tmp/commit-msg.txt"))
ANNOUNCE_FILE = Path(os.environ.get("ANNOUNCE_FILE", "/tmp/announce.json"))

ALLOWED = {
    int(x) for x in os.environ.get("ALLOWED_USER_IDS", "").replace(" ", "").split(",") if x
}

TAGS = " ".join(f"#{c.key}" for c in CATEGORIES)

HELP = (
    "<b>Mayuri'z uploader</b>\n\n"
    "Send a photo. First line of the caption is the name, and put a category "
    "hashtag anywhere in it:\n\n"
    "<code>Ocean Blue Ruffle Scrunchie #scrunchies\n"
    "Deep teal ruffles on a soft white band.</code>\n\n"
    f"<b>Categories:</b> {TAGS}\n\n"
    "<b>Commands:</b> /help · /whoami · /film\n\n"
    "<i>I check for new photos every few minutes, so give me a moment.</i>"
)


# Each upload gets one message that updates through these stages, rather than
# a burst of separate notifications for a job that takes three seconds.
STAGES = [
    ("caption", "Reading the caption"),
    ("photo", "Saving the photo"),
    ("gallery", "Adding it to the gallery"),
    ("film", "Adding it to the film"),
    ("push", "Pushing to GitHub"),
    ("live", "Rebuilding the site"),
]


def progress(title: str, done: dict[str, str], current: str | None) -> str:
    """Render the checklist. `done` maps a stage key to its detail line."""
    lines = [f"🧶 <b>{html.escape(title)}</b>", ""]
    for key, label in STAGES:
        if key in done:
            detail = done[key]
            lines.append(f"✅ {label}{f' — {detail}' if detail else ''}")
        elif key == current:
            lines.append(f"⏳ {label}…")
        else:
            lines.append(f"▫️ {label}")
    return "\n".join(lines)


def parse_caption(caption: str) -> tuple[str | None, str, str | None, str | None]:
    """-> (category key or None, name, description or None, price or None)."""
    found = None
    for category in CATEGORIES:
        if re.search(rf"#{category.key}\b", caption, re.IGNORECASE):
            found = category.key
            break

    cleaned = re.sub(r"#\w+", "", caption)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if not lines:
        return found, "", None, None

    # The price is looked for on the first line only, so a description that
    # happens to mention a number is left alone.
    price, first = find_price(lines[0])
    return found, first[:80], (" ".join(lines[1:])[:300] or None), price


def shop_list() -> str:
    """Every piece, by category — the names /remove and /caption expect."""
    index = (REPO_ROOT / "index.html").read_text()
    entries = re.findall(r"name: '([^']+)',\n      cat: '([a-z]+)'", index)
    if not entries:
        return "Nothing on the site yet."

    by_cat: dict[str, list[str]] = {}
    for name, cat in entries:
        by_cat.setdefault(cat, []).append(name.replace("\\'", "'"))

    out = [f"🧶 <b>{len(entries)} pieces</b>", ""]
    for key in (c.key for c in CATEGORIES):
        if key in by_cat:
            out.append(f"<b>{html.escape(BY_KEY[key].button)}</b>")
            out += [f"  \u2022 {html.escape(n)}" for n in by_cat[key]]
            out.append("")
    out.append("<i>/remove or /caption take any of these names.</i>")
    return "\n".join(out)


def shop_status() -> str:
    """A plain account of what is on the site and whether the film matches."""
    import subprocess
    from collections import Counter

    index = (REPO_ROOT / "index.html").read_text()
    cats = Counter(re.findall(r"cat: '([a-z]+)'", index))
    photos = len(list((REPO_ROOT / "images").glob("*.jpg")))
    film_scenes = len(re.findall(r'image: "', (REPO_ROOT / "video/src/theme.ts").read_text()))

    try:
        last = subprocess.run(
            ["git", "log", "-1", "--pretty=%h \u00b7 %s \u00b7 %cr"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        last = "unknown"

    breakdown = "\n".join(
        f"  {html.escape(BY_KEY[key].button)} {count}" for key, count in
        sorted(cats.items(), key=lambda kv: -kv[1]) if key in BY_KEY)

    film_note = ("matches the shop" if film_scenes == photos
                 else f"{film_scenes} scenes vs {photos} photos \u2014 run /film")

    return (
        f"🧶 <b>{photos} pieces on the site</b>\n{breakdown}\n\n"
        f"🎬 Film: {film_note}\n"
        f"📝 Last change: <code>{html.escape(last)}</code>\n"
        f"🌿 Publishing from <code>{BRANCH}</code>"
    )


def dispatch_film_render() -> str:
    url = (
        f"https://api.github.com/repos/{GITHUB_REPO}"
        "/actions/workflows/render-film.yml/dispatches"
    )
    response = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        json={"ref": BRANCH},
        timeout=30,
    )
    if response.status_code == 204:
        return (
            "🎬 Re-rendering the film — about five minutes, then it updates "
            f"itself.\nhttps://github.com/{GITHUB_REPO}/actions"
        )
    return f"⚠️ GitHub wouldn't start the render (HTTP {response.status_code})."


def handle_photo(tg: Telegram, message: dict, added: list[str],
                 notices: list[dict]) -> None:
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    caption = (message.get("caption") or "").strip()

    if not caption:
        tg.send(chat_id,
                "I need a name and a category in the caption.\n\n" + HELP,
                reply_to=message_id)
        return

    category_key, name, desc, price = parse_caption(caption)
    if not name:
        tg.send(chat_id, "I couldn't find a name in that caption.\n\n" + HELP,
                reply_to=message_id)
        return
    if category_key is None:
        tg.send(
            chat_id,
            f"<b>{html.escape(name)}</b> — which shelf?\n\n"
            f"Send it again with one of: {TAGS}",
            reply_to=message_id,
        )
        return

    desc = desc or f"{name} — handmade to order, in any colour you like."
    photo = message["photo"][-1]  # the largest size Telegram kept

    # A reaction on the photo itself, so the original message shows its own
    # state without anyone scrolling to find the reply.
    tg.react(chat_id, message_id, "👀")

    done: dict[str, str] = {}
    status_id = tg.send(chat_id, progress(name, done, "caption"), reply_to=message_id)

    def step(finished: str, detail: str, nxt: str | None) -> None:
        done[finished] = detail
        if status_id:
            tg.edit(chat_id, status_id, progress(name, done, nxt))

    step("caption", f"{BY_KEY[category_key].tag}"
         + (f", ignoring {price}" if price else ""), "photo")

    images_dir = REPO_ROOT / "images"
    slug = unique_slug(slugify(name), images_dir)

    try:
        raw = tg.download(photo["file_id"])
        filename = save_photo(raw, images_dir, slug)
        size_kb = (images_dir / filename).stat().st_size // 1024
        step("photo", f"{filename} ({size_kb} KB)", "gallery")

        insert_into_index(REPO_ROOT / "index.html", product_id=slug, name=name,
                          cat=category_key, desc=desc, image=filename)
        total = len(list(images_dir.glob("*.jpg")))
        step("gallery", f"{total} pieces now", "film")

        insert_into_film(REPO_ROOT / "video/src/theme.ts", name=name,
                         cat=category_key, image=filename)
        step("film", "scene added", "push")
    except SiteEditError as exc:
        tg.react(chat_id, message_id, "🤔")
        if status_id:
            tg.edit(chat_id, status_id,
                    progress(name, done, None) + f"\n\n⚠️ {html.escape(str(exc))}")
        else:
            tg.send(chat_id, f"⚠️ {html.escape(str(exc))}", reply_to=message_id)
        return
    except Exception as exc:
        log.exception("failed to add %s", name)
        tg.react(chat_id, message_id, "🤔")
        if status_id:
            tg.edit(chat_id, status_id, progress(name, done, None)
                    + f"\n\n⚠️ Couldn't add that one: {html.escape(str(exc))}")
        else:
            tg.send(chat_id, f"⚠️ Couldn't add that one: {html.escape(str(exc))}",
                    reply_to=message_id)
        return

    tg.react(chat_id, message_id, "🎉")
    who = message.get("from", {}).get("first_name", "someone")
    added.append(f"{name} ({BY_KEY[category_key].tag}, from {who})")
    # announce.py finishes this same message once the push has really happened.
    notices.append({"chat": chat_id, "message_id": status_id,
                    "title": name, "done": done})


def main() -> int:
    if not TOKEN:
        sys.exit("TELEGRAM_TOKEN is not set")
    if not ALLOWED:
        log.warning("ALLOWED_USER_IDS is empty — nobody can publish")

    tg = Telegram(TOKEN)
    added: list[str] = []
    removed: list[str] = []
    notices: list[dict] = []
    chats_touched: set[int] = set()
    edited: list[str] = []

    try:
        updates = tg.get_updates()
        log.info("%d update(s) waiting", len(updates))

        for update in updates:
            message = update.get("message") or update.get("channel_post")
            try:
                if not message:
                    continue

                user_id = message.get("from", {}).get("id")
                chat_id = message["chat"]["id"]
                text = (message.get("text") or "").strip()

                if user_id not in ALLOWED:
                    # Tell them their id so the allow-list is easy to fill in,
                    # but only when they actually addressed the bot.
                    if text.startswith("/") or message.get("photo"):
                        tg.send(
                            chat_id,
                            "You're not on this bot's list, so I can't publish "
                            f"for you.\nYour user ID: <code>{user_id}</code>\n"
                            f"This chat: <code>{chat_id}</code>",
                            reply_to=message["message_id"],
                        )
                    continue

                if text.startswith(("/start", "/help")):
                    tg.send(chat_id, HELP, reply_to=message["message_id"])
                elif text.startswith("/whoami"):
                    tg.send(chat_id,
                            f"Your user ID: <code>{user_id}</code>\n"
                            f"This chat: <code>{chat_id}</code>\nAllowed: yes",
                            reply_to=message["message_id"])
                elif text.startswith("/list"):
                    tg.send(chat_id, shop_list(), reply_to=message["message_id"])
                elif text.startswith(("/caption", "/rename")):
                    verb = "/caption" if text.startswith("/caption") else "/rename"
                    rest = text[len(verb):].strip()
                    if "|" not in rest:
                        tg.send(chat_id,
                                f"Use <code>{verb} piece name | new "
                                f"{'wording' if verb == '/caption' else 'name'}</code>",
                                reply_to=message["message_id"])
                    else:
                        target, value = (part.strip() for part in rest.split("|", 1))
                        try:
                            field = {"desc": value} if verb == "/caption" else {"name": value}
                            was, now = update_product(
                                REPO_ROOT / "index.html",
                                REPO_ROOT / "video/src/theme.ts",
                                target, **field,
                            )
                            chats_touched.add(chat_id)
                            edited.append(f"{was}" + (f" \u2192 {now}" if was != now else ""))
                            tg.react(chat_id, message["message_id"], "🎉")
                            tg.send(chat_id,
                                    f"✏️ Updated <b>{html.escape(now)}</b>. "
                                    "Live in a minute or two.",
                                    reply_to=message["message_id"])
                        except SiteEditError as exc:
                            tg.react(chat_id, message["message_id"], "🤔")
                            tg.send(chat_id, f"⚠️ {html.escape(str(exc))}",
                                    reply_to=message["message_id"])
                elif text.startswith("/status"):
                    tg.send(chat_id, shop_status(), reply_to=message["message_id"])
                elif text.startswith("/remove"):
                    query = text[len("/remove"):].strip()
                    if not query:
                        tg.send(chat_id,
                                "Which one? <code>/remove Ocean Blue Ruffle Scrunchie</code>",
                                reply_to=message["message_id"])
                    else:
                        try:
                            gone, image = remove_product(
                                REPO_ROOT / "index.html",
                                REPO_ROOT / "video/src/theme.ts",
                                REPO_ROOT / "images",
                                query,
                            )
                            removed.append(gone)
                            chats_touched.add(chat_id)
                            tg.send(chat_id,
                                    f"🗑 Removed <b>{html.escape(gone)}</b> and its photo. "
                                    "Gone from the site in a minute or two.",
                                    reply_to=message["message_id"])
                        except SiteEditError as exc:
                            tg.send(chat_id, f"⚠️ {html.escape(str(exc))}",
                                    reply_to=message["message_id"])
                elif text.startswith("/film"):
                    tg.send(chat_id, dispatch_film_render(), reply_to=message["message_id"])
                elif message.get("photo"):
                    handle_photo(tg, message, added, notices)
            finally:
                # Acknowledge every update even if handling it went wrong, so
                # one bad message can't jam the queue on every future run.
                tg.acknowledge(update["update_id"])

    finally:
        tg.close()

    if added or removed or edited:
        if added and not removed:
            title = (f"Add {added[0].split(' (')[0]} to the shop"
                     if len(added) == 1 else f"Add {len(added)} pieces to the shop")
        elif removed and not added and not edited:
            title = (f"Remove {removed[0]} from the shop"
                     if len(removed) == 1 else f"Remove {len(removed)} pieces from the shop")
        elif edited and not added and not removed:
            title = (f"Reword {edited[0]}" if len(edited) == 1
                     else f"Reword {len(edited)} pieces")
        else:
            parts = []
            if added:
                parts.append(f"add {len(added)}")
            if removed:
                parts.append(f"remove {len(removed)}")
            if edited:
                parts.append(f"reword {len(edited)}")
            title = "Shop update: " + ", ".join(parts)

        body = ""
        if added:
            body += "\nAdded via Telegram:\n" + "\n".join(f"- {x}" for x in added)
        if removed:
            body += "\nRemoved via Telegram:\n" + "\n".join(f"- {x}" for x in removed)
        if edited:
            body += "\nReworded via Telegram:\n" + "\n".join(f"- {x}" for x in edited)

        COMMIT_MSG_FILE.write_text(
            title + "\n" + body
            + "\n\nThe film's scene list was updated to match; /film re-renders it.\n"
        )
        ANNOUNCE_FILE.write_text(json.dumps({
            "notices": notices,
            "chats": sorted({n["chat"] for n in notices} | chats_touched),
            "added": [a.split(" (")[0] for a in added],
            "removed": removed,
            "edited": edited,
        }))
        log.info("added: %s | removed: %s | edited: %s", added, removed, edited)
    else:
        log.info("nothing to publish")

    return 0


if __name__ == "__main__":
    sys.exit(main())
