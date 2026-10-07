"""Send a pack of ready-to-copy messages to a Telegram chat.

Used to deliver marketing copy (captions, DM templates) to the team's group
without that copy ever touching the website: the text arrives as a workflow
input, not as a file in the repository.

The pack is JSON — a list of items, each either:
    {"text": "<b>already formatted</b> HTML"}
    {"label": "1 · Launch post", "when": "Wed / Thu, feed", "copy": "plain text"}

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

LIMIT = 4096  # Telegram's maximum message length


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
    messages = [render(item) for item in pack]

    too_long = [i for i, m in enumerate(messages, 1) if len(m) > LIMIT]
    if too_long:
        sys.exit(f"message(s) {too_long} exceed Telegram's {LIMIT}-character limit")

    if "--dry-run" in sys.argv:
        for i, m in enumerate(messages, 1):
            print(f"--- {i} ({len(m)} chars) ---\n{m}\n")
        return 0

    import httpx

    token = os.environ["TELEGRAM_TOKEN"].strip()
    chat_id = os.environ["CHAT_ID"].strip()
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    with httpx.Client(timeout=30) as client:
        for i, text in enumerate(messages, 1):
            for _ in range(2):
                reply = client.post(url, json={
                    "chat_id": chat_id, "text": text, "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                }).json()
                if reply.get("ok"):
                    print(f"sent {i}/{len(messages)}")
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
    print(f"done — {len(messages)} messages to chat {chat_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
