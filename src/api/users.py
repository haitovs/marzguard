import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import get_settings
from src.core.tracker import IPTracker
from src.dependencies import get_current_admin, get_db, get_tracker
from src.models.audit import AuditLog
from src.models.user import UserIPConfig
from src.schemas.user import UserIPConfigOut, UserIPConfigUpdate, UserListOut, UserSyncResult
from src.services.marzban import MarzbanClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

# Singleton set during app startup
_marzban: Optional[MarzbanClient] = None


def set_marzban(client: MarzbanClient):
    global _marzban
    _marzban = client


def _to_out(config: UserIPConfig, tracker: IPTracker) -> UserIPConfigOut:
    settings = get_settings()
    active_ips = tracker.get_active_ips(config.username)
    effective_limit = config.get_effective_limit(settings.default_ip_limit)
    return UserIPConfigOut(
        id=config.id,
        username=config.username,
        ip_limit=config.ip_limit,
        policy_id=config.policy_id,
        policy_name=config.policy.name if config.policy else None,
        is_monitored=config.is_monitored,
        is_exempt=config.is_exempt,
        auto_reenable=config.auto_reenable,
        reenable_delay_sec=config.reenable_delay_sec,
        disabled_at=config.disabled_at,
        disabled_reason=config.disabled_reason,
        active_ip_count=len(active_ips),
        active_ips=active_ips,
        effective_limit=effective_limit,
    )


@router.get("", response_model=UserListOut)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    tracker: IPTracker = Depends(get_tracker),
    _admin: str = Depends(get_current_admin),
):
    """List all users with their active IP counts."""
    stmt = select(UserIPConfig).options(selectinload(UserIPConfig.policy))
    count_stmt = select(func.count()).select_from(UserIPConfig)

    if search:
        stmt = stmt.where(UserIPConfig.username.ilike(f"%{search}%"))
        count_stmt = count_stmt.where(UserIPConfig.username.ilike(f"%{search}%"))

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    configs = result.scalars().all()

    return UserListOut(
        users=[_to_out(c, tracker) for c in configs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{username}", response_model=UserIPConfigOut)
async def get_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    tracker: IPTracker = Depends(get_tracker),
    _admin: str = Depends(get_current_admin),
):
    """Get a single user's config and active IPs."""
    stmt = (
        select(UserIPConfig)
        .where(UserIPConfig.username == username)
        .options(selectinload(UserIPConfig.policy))
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="User not found")
    return _to_out(config, tracker)


@router.put("/{username}", response_model=UserIPConfigOut)
async def update_user(
    username: str,
    data: UserIPConfigUpdate,
    db: AsyncSession = Depends(get_db),
    tracker: IPTracker = Depends(get_tracker),
    _admin: str = Depends(get_current_admin),
):
    """Update a user's IP limit configuration."""
    stmt = (
        select(UserIPConfig)
        .where(UserIPConfig.username == username)
        .options(selectinload(UserIPConfig.policy))
    )
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    audit = AuditLog(
        event_type="user_updated",
        username=username,
        details=json.dumps(update_data),
        source="admin",
    )
    db.add(audit)
    await db.commit()
    await db.refresh(config)
    return _to_out(config, tracker)


@router.post("/{username}/disable")
async def disable_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    """Manually disable a user via Marzban."""
    if not _marzban:
        raise HTTPException(status_code=503, detail="Marzban client not available")

    stmt = select(UserIPConfig).where(UserIPConfig.username == username)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="User not found")

    from datetime import datetime, timezone
    await _marzban.disable_user(username)
    config.disabled_at = datetime.now(timezone.utc)
    config.disabled_reason = "Manually disabled by admin"

    audit = AuditLog(
        event_type="user_disabled",
        username=username,
        details="Manual disable by admin",
        source="admin",
    )
    db.add(audit)
    await db.commit()
    return {"status": "disabled", "username": username}


@router.post("/{username}/enable")
async def enable_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    """Manually re-enable a user via Marzban."""
    if not _marzban:
        raise HTTPException(status_code=503, detail="Marzban client not available")

    stmt = select(UserIPConfig).where(UserIPConfig.username == username)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="User not found")

    await _marzban.enable_user(username)
    config.disabled_at = None
    config.disabled_reason = None

    audit = AuditLog(
        event_type="user_reenabled",
        username=username,
        details="Manual re-enable by admin",
        source="admin",
    )
    db.add(audit)
    await db.commit()
    return {"status": "enabled", "username": username}


@router.post("/sync", response_model=UserSyncResult)
async def sync_users(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    """Sync user list from Marzban panel."""
    if not _marzban:
        raise HTTPException(status_code=503, detail="Marzban client not available")

    added = 0
    offset = 0
    all_usernames = []

    while True:
        data = await _marzban.get_users(offset=offset, limit=100)
        users = data.get("users", [])
        if not users:
            break
        for user in users:
            uname = user.get("username")
            if uname:
                all_usernames.append(uname)
        offset += len(users)
        if len(users) < 100:
            break

    for uname in all_usernames:
        stmt = select(UserIPConfig).where(UserIPConfig.username == uname)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            db.add(UserIPConfig(username=uname))
            added += 1

    await db.commit()
    return UserSyncResult(added=added, total=len(all_usernames))
