import logging

import httpx

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications via Telegram Bot API."""

    def __init__(self, bot_token: str, chat_id: str):
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._client = httpx.AsyncClient(timeout=10.0)
        self._base_url = f"https://api.telegram.org/bot{bot_token}"

    async def close(self):
        await self._client.aclose()

    async def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Send a message to the configured chat."""
        try:
            resp = await self._client.post(
                f"{self._base_url}/sendMessage",
                json={
                    "chat_id": self._chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                },
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.error("Telegram send failed: %s", e)
            return False
