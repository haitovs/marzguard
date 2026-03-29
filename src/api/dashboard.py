from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.core.tracker import IPTracker
from src.dependencies import get_current_admin, get_db, get_tracker
from src.models.audit import AuditLog
from src.models.user import UserIPConfig
from src.schemas.dashboard import DashboardSummary, LiveIPEntry, LiveSnapshot

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    tracker: IPTracker = Depends(get_tracker),
    _admin: str = Depends(get_current_admin),
):
    """Get dashboard summary stats."""
    settings = get_settings()

    total = (await db.execute(select(func.count()).select_from(UserIPConfig))).scalar() or 0
    monitored = (
        await db.execute(
            select(func.count())
            .select_from(UserIPConfig)
            .where(UserIPConfig.is_monitored.is_(True))
        )
    ).scalar() or 0
    disabled = (
        await db.execute(
            select(func.count())
            .select_from(UserIPConfig)
            .where(UserIPConfig.disabled_at.isnot(None))
        )
    ).scalar() or 0

    all_active = tracker.get_all_active()
    active_users = len(all_active)
    total_ips = sum(len(ips) for ips in all_active.values())

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    violations_today = (
        await db.execute(
            select(func.count())
            .select_from(AuditLog)
            .where(
                AuditLog.event_type == "user_disabled",
                AuditLog.timestamp >= today_start,
            )
        )
    ).scalar() or 0

    return DashboardSummary(
        total_users=total,
        monitored_users=monitored,
        active_users=active_users,
        disabled_users=disabled,
        total_active_ips=total_ips,
        violations_today=violations_today,
    )


@router.get("/live", response_model=LiveSnapshot)
async def get_live_snapshot(
    db: AsyncSession = Depends(get_db),
    tracker: IPTracker = Depends(get_tracker),
    _admin: str = Depends(get_current_admin),
):
    """Get full live IP tracking snapshot."""
    settings = get_settings()
    all_active = tracker.get_all_active()

    entries = []
    total_ips = 0

    for username, ips in all_active.items():
        stmt = select(UserIPConfig).where(UserIPConfig.username == username)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()

        effective_limit = settings.default_ip_limit
        is_disabled = False
        if config:
            effective_limit = config.get_effective_limit(settings.default_ip_limit)
            is_disabled = config.disabled_at is not None

        entries.append(
            LiveIPEntry(
                username=username,
                active_ips=ips,
                ip_count=len(ips),
                effective_limit=effective_limit,
                is_over_limit=len(ips) > effective_limit,
                is_disabled=is_disabled,
            )
        )
        total_ips += len(ips)

    entries.sort(key=lambda e: e.ip_count, reverse=True)

    return LiveSnapshot(
        entries=entries,
        total_active_users=len(entries),
        total_active_ips=total_ips,
    )
