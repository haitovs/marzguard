import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.dependencies import get_db
from src.models.audit import AuditLog

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/marzban")
async def marzban_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_webhook_secret: str = Header(default=""),
):
    """Receive webhook events from Marzban."""
    settings = get_settings()

    if settings.webhook_secret and x_webhook_secret != settings.webhook_secret:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    body = await request.json()
    action = body.get("action", "unknown")
    username = body.get("username", "")

    logger.info("Marzban webhook: %s for user %s", action, username)

    audit = AuditLog(
        event_type=f"webhook_{action}",
        username=username,
        details=str(body),
        source="marzban_webhook",
    )
    db.add(audit)
    await db.commit()

    return {"status": "received"}
