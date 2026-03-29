import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.core.tracker import IPTracker
from src.models.audit import AuditLog
from src.models.user import UserIPConfig
from src.services.marzban import MarzbanClient
from src.services.notify import NotificationDispatcher

logger = logging.getLogger(__name__)


class Enforcer:
    """Detects IP limit violations and enforces via Marzban API."""

    def __init__(
        self,
        tracker: IPTracker,
        marzban: MarzbanClient,
        notifier: NotificationDispatcher,
        session_factory,
    ):
        self._tracker = tracker
        self._marzban = marzban
        self._notifier = notifier
        self._session_factory = session_factory

    async def enforce(self):
        """Main enforcement loop — check all users for violations."""
        settings = get_settings()
        all_active = self._tracker.get_all_active()

        if not all_active:
            return

        async with self._session_factory() as session:
            for username, ips in all_active.items():
                try:
                    await self._check_user(session, username, ips, settings)
                except Exception as e:
                    logger.error("Error enforcing for user %s: %s", username, e)

            await session.commit()

    async def _check_user(
        self,
        session: AsyncSession,
        username: str,
        active_ips: list[str],
        settings,
    ):
        """Check a single user for violations."""
        config = await self._get_or_create_config(session, username)

        if config.is_exempt or not config.is_monitored:
            return

        if config.disabled_at is not None:
            return

        effective_limit = config.get_effective_limit(settings.default_ip_limit)
        ip_count = len(active_ips)

        if ip_count > effective_limit:
            logger.warning(
                "User %s has %d IPs (limit: %d) — disabling",
                username,
                ip_count,
                effective_limit,
            )
            try:
                await self._marzban.disable_user(username)
            except Exception as e:
                logger.error("Failed to disable user %s via Marzban: %s", username, e)
                return

            config.disabled_at = datetime.now(timezone.utc)
            config.disabled_reason = (
                f"IP limit exceeded: {ip_count}/{effective_limit}"
            )

            audit = AuditLog(
                event_type="user_disabled",
                username=username,
                details=config.disabled_reason,
                ip_addresses=json.dumps(active_ips),
                source="enforcer",
            )
            session.add(audit)

            await self._notifier.notify_disabled(username, config.disabled_reason)
            await self._notifier.notify_violation(
                username, ip_count, effective_limit, active_ips
            )

    async def check_reenable(self):
        """Check disabled users for re-enablement eligibility."""
        settings = get_settings()

        async with self._session_factory() as session:
            stmt = select(UserIPConfig).where(UserIPConfig.disabled_at.isnot(None))
            result = await session.execute(stmt)
            disabled_users = result.scalars().all()

            for config in disabled_users:
                try:
                    await self._try_reenable(session, config, settings)
                except Exception as e:
                    logger.error(
                        "Error checking re-enable for %s: %s", config.username, e
                    )

            await session.commit()

    async def _try_reenable(
        self, session: AsyncSession, config: UserIPConfig, settings
    ):
        """Try to re-enable a single disabled user."""
        if not config.auto_reenable:
            if config.policy and not config.policy.auto_reenable:
                return
            elif not config.policy:
                return

        delay = (
            config.reenable_delay_sec
            or (config.policy.reenable_delay_sec if config.policy else None)
            or settings.default_reenable_delay
        )

        now = datetime.now(timezone.utc)
        disabled_at = config.disabled_at
        if disabled_at.tzinfo is None:
            disabled_at = disabled_at.replace(tzinfo=timezone.utc)

        elapsed = (now - disabled_at).total_seconds()
        if elapsed < delay:
            return

        effective_limit = config.get_effective_limit(settings.default_ip_limit)
        current_count = self._tracker.get_active_count(config.username)

        if current_count <= effective_limit:
            logger.info("Re-enabling user %s (IPs: %d/%d)", config.username, current_count, effective_limit)
            try:
                await self._marzban.enable_user(config.username)
            except Exception as e:
                logger.error("Failed to re-enable user %s: %s", config.username, e)
                return

            config.disabled_at = None
            config.disabled_reason = None

            audit = AuditLog(
                event_type="user_reenabled",
                username=config.username,
                details=f"Auto re-enabled (IPs: {current_count}/{effective_limit})",
                source="enforcer",
            )
            session.add(audit)

            await self._notifier.notify_reenabled(config.username)

    async def _get_or_create_config(
        self, session: AsyncSession, username: str
    ) -> UserIPConfig:
        """Get existing config or create a new one."""
        stmt = select(UserIPConfig).where(UserIPConfig.username == username)
        result = await session.execute(stmt)
        config = result.scalar_one_or_none()

        if config is None:
            config = UserIPConfig(username=username)
            session.add(config)
            await session.flush()

        return config
