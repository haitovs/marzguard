from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    username: Optional[str] = None
    details: Optional[str] = None
    ip_addresses: Optional[str] = None
    source: str

    model_config = {"from_attributes": True}


class AuditLogList(BaseModel):
    logs: list[AuditLogOut]
    total: int
    page: int
    page_size: int
