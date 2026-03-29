from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_current_admin, get_db
from src.models.audit import AuditLog
from src.schemas.audit import AuditLogList, AuditLogOut

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=AuditLogList)
async def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    event_type: Optional[str] = None,
    username: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    """Query audit logs with filtering and pagination."""
    stmt = select(AuditLog)
    count_stmt = select(func.count()).select_from(AuditLog)

    if event_type:
        stmt = stmt.where(AuditLog.event_type == event_type)
        count_stmt = count_stmt.where(AuditLog.event_type == event_type)
    if username:
        stmt = stmt.where(AuditLog.username.ilike(f"%{username}%"))
        count_stmt = count_stmt.where(AuditLog.username.ilike(f"%{username}%"))

    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = (
        stmt.order_by(desc(AuditLog.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    return AuditLogList(
        logs=[AuditLogOut.model_validate(log) for log in logs],
        total=total,
        page=page,
        page_size=page_size,
    )
