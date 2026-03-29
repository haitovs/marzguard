from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserIPConfigOut(BaseModel):
    id: int
    username: str
    admin_username: Optional[str] = None
    ip_limit: Optional[int] = None
    policy_id: Optional[int] = None
    policy_name: Optional[str] = None
    is_monitored: bool = True
    is_exempt: bool = False
    auto_reenable: bool = True
    reenable_delay_sec: Optional[int] = None
    disabled_at: Optional[datetime] = None
    disabled_reason: Optional[str] = None
    active_ip_count: int = 0
    active_ips: list[str] = []
    effective_limit: int = 0

    model_config = {"from_attributes": True}


class UserIPConfigUpdate(BaseModel):
    ip_limit: Optional[int] = None
    policy_id: Optional[int] = None
    is_monitored: Optional[bool] = None
    is_exempt: Optional[bool] = None
    auto_reenable: Optional[bool] = None
    reenable_delay_sec: Optional[int] = None


class UserListOut(BaseModel):
    users: list[UserIPConfigOut]
    total: int
    page: int
    page_size: int


class UserSyncResult(BaseModel):
    added: int
    total: int
