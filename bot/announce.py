"""The message the uploader sends once a change is actually on GitHub.

poll_once.py runs before the commit exists, so it can only promise. This
runs after the push and reports what really happened, with a link to the
commit — the difference between "I think I did that" and "here it is".
"""

import json
import logging
import os
import sys
from pathlib import Path

from poll_once import STAGES
from telegram_api import Telegram

logging.basicConfig(format="%(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("announce")

TOKEN = os.environ.get("TELEGRAM_TOKEN", "").strip()
GITHUB_REPO = os.environ.get("GITHUB_REPO", "Sanu0910/Crochet_Mayuri").strip()
SITE_URL = os.environ.get("SITE_URL", "").strip()
ANNOUNCE_FILE = Path(os.environ.get("ANNOUNCE_FILE", "/tmp/announce.json"))
COMMIT_SHA = os.environ.get("COMMIT_SHA", "").strip()
PAGES_STATUS = os.environ.get("PAGES_STATUS", "").strip()


def main() -> int:
    if not ANNOUNCE_FILE.exists():
        log.info("nothing was published, so nothing to announce")
        return 0
    if not TOKEN:
        log.warning("no TELEGRAM_TOKEN, skipping the announcement")
        return 0

    plan = json.loads(ANNOUNCE_FILE.read_text())
    notices = plan.get("notices") or []
    chats = plan.get("chats") or []
    removed = plan.get("removed") or []

    telegram = Telegram(TOKEN)
    try:
        # Finish each upload's own checklist, so the message someone watched
        # fill in is the message that tells them it's done.
        for notice in notices:
            done = dict(notice.get("done") or {})
            done["push"] = f"commit {COMMIT_SHA[:7]}" if COMMIT_SHA else "done"
            done["live"] = (
                "live in a minute or two" if PAGES_STATUS == "201"
                else f"rebuild returned {PAGES_STATUS}" if PAGES_STATUS
                else "queued"
            )
            lines = [f"🧶 <b>{notice['title']}</b>", ""]
            for key, label in STAGES:
                detail = done.get(key)
                lines.append(f"✅ {label}" + (f" — {detail}" if detail else ""))
            if COMMIT_SHA:
                lines.append(
                    f'\n🔗 <a href="https://github.com/{GITHUB_REPO}/commit/'
                    f'{COMMIT_SHA}">commit {COMMIT_SHA[:7]}</a>'
                )
            if SITE_URL:
                lines.append(SITE_URL)
            if notice.get("message_id"):
                telegram.edit(int(notice["chat"]), int(notice["message_id"]),
                              "\n".join(lines))

        # Removals have no checklist of their own, so they get a short note.
        if removed:
            text = "🗑 <b>Removed from the site:</b>\n" + "\n".join(
                f"  • {name}" for name in removed)
            if COMMIT_SHA:
                text += (f'\n\n🔗 <a href="https://github.com/{GITHUB_REPO}/commit/'
                         f'{COMMIT_SHA}">commit {COMMIT_SHA[:7]}</a>')
            for chat_id in chats:
                telegram.send(int(chat_id), text)
    finally:
        telegram.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
