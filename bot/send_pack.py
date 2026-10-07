"""Send a pack of ready-to-copy messages to a Telegram chat.

Used to deliver marketing copy (captions, DM templates) to the team's group
without that copy ever touching the website: the text arrives as a workflow
input, not as a file in the repository.

The pack is JSON — a list of items, each one of:
    {"text": "<b>already formatted</b> HTML"}
    {"label": "1 · Launch post", "when": "Wed / Thu, feed", "copy": "plain text"}
    {"photo": "path/relative/to/the/repo.jpg", "caption": "<b>HTML</b>"}
    {"video": "path/relative/to/the/repo.mp4", "caption": "<b>HTML</b>",
     "width": 1080, "height": 1920}

Photos and videos are read from the checkout the job runs on, so they can live on a
branch the website is never built from.

A "copy" item is sent inside a <pre> block. In Telegram a monospace block
copies to the clipboard with a single tap, so whoever posts it gets exactly
the caption — none of the label around it.

    PACK='[...]' CHAT_ID=-123 TELEGRAM_TOKEN=... python send_pack.py
    PACK='[...]' python send_pack.py --dry-run     # render only, send nothing
"""

import html
import json
import os
import sys
import time
from pathlib import Path

LIMIT = 4096          # Telegram's maximum message length
CAPTION_LIMIT = 1024  # ...and its maximum photo caption
UPLOAD_LIMIT = 50 * 1024 * 1024  # the most a bot may upload in one file
REPO = Path(__file__).resolve().parent.parent


def render(item: dict) -> str:
    if "text" in item:
        return item["text"]
    parts = [f"<b>{html.escape(item['label'])}</b>"]
    if item.get("when"):
        parts.append(f"<i>{html.escape(item['when'])}</i>")
    parts.append(f"<pre>{html.escape(item['copy'])}</pre>")
    return "\n".join(parts)


def main() -> int:
    pack = json.loads(os.environ["PACK"])

    # Check everything before sending anything, so a bad item can't leave the
    # group with half a pack.
    for i, item in enumerate(pack, 1):
        media = item.get("photo") or item.get("video")
        if media:
            path = REPO / media
            if not path.is_file():
                sys.exit(f"item {i}: no such file {media}")
            if path.stat().st_size > UPLOAD_LIMIT:
                sys.exit(f"item {i}: {media} is over Telegram's 50 MB bot limit")
            if len(item.get("caption", "")) > CAPTION_LIMIT:
                sys.exit(f"item {i}: caption exceeds {CAPTION_LIMIT} characters")
        elif len(render(item)) > LIMIT:
            sys.exit(f"item {i} exceeds Telegram's {LIMIT}-character limit")

    if "--dry-run" in sys.argv:
        for i, item in enumerate(pack, 1):
            media = item.get("photo") or item.get("video")
            body = f"[{media}] {item.get('caption', '')}" if media else render(item)
            print(f"--- {i} ---\n{body}\n")
        return 0

    import httpx

    token = os.environ["TELEGRAM_TOKEN"].strip()
    chat_id = os.environ["CHAT_ID"].strip()
    api = f"https://api.telegram.org/bot{token}"

    with httpx.Client(timeout=60) as client:
        for i, item in enumerate(pack, 1):
            for _ in range(2):
                if "photo" in item:
                    path = REPO / item["photo"]
                    reply = client.post(f"{api}/sendPhoto", data={
                        "chat_id": chat_id, "caption": item.get("caption", ""),
                        "parse_mode": "HTML",
                    }, files={"photo": (path.name, path.read_bytes(), "image/jpeg")}).json()
                elif "video" in item:
                    # Without the size Telegram shows a portrait Reel as a
                    # square thumbnail until someone taps it.
                    path = REPO / item["video"]
                    data = {"chat_id": chat_id, "caption": item.get("caption", ""),
                            "parse_mode": "HTML", "supports_streaming": "true"}
                    data.update({k: str(item[k]) for k in ("width", "height") if k in item})
                    reply = client.post(f"{api}/sendVideo", data=data, files={
                        "video": (path.name, path.read_bytes(), "video/mp4"),
                    }, timeout=300).json()
                else:
                    reply = client.post(f"{api}/sendMessage", json={
                        "chat_id": chat_id, "text": render(item), "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    }).json()
                if reply.get("ok"):
                    print(f"sent {i}/{len(pack)}")
                    break
                # A group that has been upgraded to a supergroup gets a new id;
                # Telegram says what it is, so follow it once and carry on.
                new_id = (reply.get("parameters") or {}).get("migrate_to_chat_id")
                if new_id:
                    print(f"chat moved to {new_id} — retrying there")
                    chat_id = str(new_id)
                    continue
                sys.exit(f"message {i} failed: {reply.get('description', reply)}")
            time.sleep(0.4)  # stay well under Telegram's per-chat rate limit
    print(f"done — {len(pack)} items to chat {chat_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
