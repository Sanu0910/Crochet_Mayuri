"""Collect photos waiting in Telegram without publishing them.

The uploader puts a photo on the site exactly as it arrives. When a batch
needs editing first, this takes the waiting photos instead: it saves each one
at full size with its caption and sender into OUT_DIR, plus a manifest, and
leaves the site alone. The workflow then commits them to a side branch.

    TELEGRAM_TOKEN=... ALLOWED_USER_IDS=1,2 OUT_DIR=incoming python fetch_incoming.py
    TELEGRAM_TOKEN=... python fetch_incoming.py --ack 123456   # mark handled up to 123456

Nothing is acknowledged until --ack is run, and the workflow only runs that
after the photos are safely pushed, so a failure part-way loses nothing: the
photos stay waiting in Telegram for the next attempt.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from telegram_api import Telegram

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("fetch")

ALLOWED = {
    int(x) for x in os.environ.get("ALLOWED_USER_IDS", "").replace(" ", "").split(",") if x
}


def main() -> int:
    tg = Telegram(os.environ["TELEGRAM_TOKEN"].strip())

    if "--ack" in sys.argv:
        last = int(sys.argv[sys.argv.index("--ack") + 1])
        tg.acknowledge(last)
        log.info("acknowledged everything up to update %s", last)
        return 0

    out = Path(os.environ.get("OUT_DIR", "incoming"))
    out.mkdir(parents=True, exist_ok=True)
    updates = tg.get_updates(limit=100)
    log.info("%d update(s) waiting", len(updates))

    manifest = []
    for update in updates:
        message = update.get("message") or update.get("channel_post") or {}
        sender = (message.get("from") or {}).get("id")
        caption = message.get("caption", "")
        if message.get("photo"):
            file_id = message["photo"][-1]["file_id"]  # the largest size kept
        elif (message.get("document") or {}).get("mime_type", "").startswith("image/"):
            file_id = message["document"]["file_id"]  # sent as a file: full quality
        else:
            if message.get("text"):
                log.info("update %s: text, not a photo — skipped", update["update_id"])
            continue
        if ALLOWED and sender not in ALLOWED:
            log.info("update %s: from someone not on the list — skipped", update["update_id"])
            continue
        raw = tg.download(file_id)
        name = f"{update['update_id']}.jpg"
        (out / name).write_bytes(raw)
        sent = datetime.fromtimestamp(message.get("date", 0), timezone.utc).isoformat()
        manifest.append({
            "file": name,
            "update_id": update["update_id"],
            "message_id": message.get("message_id"),
            "chat_id": (message.get("chat") or {}).get("id"),
            "album": message.get("media_group_id"),
            "from": (message.get("from") or {}).get("first_name"),
            "sent": sent,
            "caption": caption,
        })
        log.info("saved %s (%d KB) from %s: %r", name, len(raw) // 1024,
                 manifest[-1]["from"], caption[:80])

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    last = max((u["update_id"] for u in updates), default=None)
    summary = os.environ.get("GITHUB_OUTPUT")
    if summary:
        with open(summary, "a") as fh:
            fh.write(f"count={len(manifest)}\n")
            fh.write(f"last_update={last if last is not None else ''}\n")
    log.info("%d photo(s) collected", len(manifest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
