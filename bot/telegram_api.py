"""The few Telegram endpoints this bot needs, over plain HTTPS.

Deliberately not python-telegram-bot: the scheduled runner is a short-lived
script, not a long-running application, and this keeps the workflow's
install step to one small dependency.
"""

import logging
from typing import Any

import httpx

log = logging.getLogger(__name__)
TIMEOUT = 60


class Telegram:
    def __init__(self, token: str):
        self._token = token
        self._client = httpx.Client(timeout=TIMEOUT)

    def _call(self, method: str, **params: Any) -> Any:
        response = self._client.post(
            f"https://api.telegram.org/bot{self._token}/{method}", json=params
        )
        payload = response.json()
        if not payload.get("ok"):
            raise RuntimeError(
                f"Telegram {method} failed: {payload.get('description', payload)}"
            )
        return payload["result"]

    # -- reading ----------------------------------------------------------

    def get_updates(self, offset: int | None = None, limit: int = 25) -> list[dict]:
        params: dict[str, Any] = {"limit": limit, "timeout": 0}
        if offset is not None:
            params["offset"] = offset
        return self._call("getUpdates", **params)

    def acknowledge(self, update_id: int) -> None:
        """Tell Telegram this update is handled so it isn't served again.

        Telegram treats a getUpdates with an offset as confirmation of
        everything before it — this is the only state the bot keeps, which
        is why a scheduled run needs no database.
        """
        self._call("getUpdates", offset=update_id + 1, limit=1, timeout=0)

    def download(self, file_id: str) -> bytes:
        meta = self._call("getFile", file_id=file_id)
        url = f"https://api.telegram.org/file/bot{self._token}/{meta['file_path']}"
        response = self._client.get(url)
        response.raise_for_status()
        return response.content

    # -- writing ----------------------------------------------------------

    def send(self, chat_id: int, text: str, reply_to: int | None = None) -> None:
        params: dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        if reply_to is not None:
            params["reply_to_message_id"] = reply_to
            params["allow_sending_without_reply"] = True
        try:
            self._call("sendMessage", **params)
        except Exception:
            # A reply failing must never cost us the upload that succeeded.
            log.exception("could not send a reply to chat %s", chat_id)

    def close(self) -> None:
        self._client.close()
