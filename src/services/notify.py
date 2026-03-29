import logging
from typing import Optional

from src.config import get_settings

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """Dispatches notifications to configured channels."""

    def __init__(self):
        self._telegram: Optional["TelegramNotifier"] = None

    async def init(self):
        settings = get_settings()
        if settings.telegram_bot_token and settings.telegram_chat_id:
            from src.services.telegram import TelegramNotifier

            self._telegram = TelegramNotifier(
                settings.telegram_bot_token, settings.telegram_chat_id
            )
            logger.info("Telegram notifications enabled")

    async def close(self):
        if self._telegram:
            await self._telegram.close()

    async def notify_violation(
        self, username: str, ip_count: int, limit: int, ips: list[str]
    ):
        """Notify about an IP limit violation."""
        message = (
            f"⚠️ *IP Limit Violation*\n\n"
            f"User: `{username}`\n"
            f"Active IPs: {ip_count} / {limit}\n"
            f"IPs: {', '.join(ips[:5])}"
        )
        if len(ips) > 5:
            message += f"\n...and {len(ips) - 5} more"
        await self._send(message)

    async def notify_disabled(self, username: str, reason: str):
        """Notify that a user was disabled."""
        message = (
            f"🚫 *User Disabled*\n\n"
            f"User: `{username}`\n"
            f"Reason: {reason}"
        )
        await self._send(message)

    async def notify_reenabled(self, username: str):
        """Notify that a user was re-enabled."""
        message = f"✅ *User Re-enabled*\n\nUser: `{username}`"
        await self._send(message)

    async def _send(self, message: str):
        if self._telegram:
            try:
                await self._telegram.send_message(message)
            except Exception as e:
                logger.error("Failed to send Telegram notification: %s", e)
