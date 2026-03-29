from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PolicyCreate(BaseModel):
    name: str
    default_ip_limit: Optional[int] = None
    auto_reenable: bool = True
    reenable_delay_sec: int = 300
    notify_on_violation: bool = True


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    default_ip_limit: Optional[int] = None
    auto_reenable: Optional[bool] = None
    reenable_delay_sec: Optional[int] = None
    notify_on_violation: Optional[bool] = None


class PolicyOut(BaseModel):
    id: int
    name: str
    default_ip_limit: Optional[int] = None
    auto_reenable: bool
    reenable_delay_sec: int
    notify_on_violation: bool
    created_at: datetime
    user_count: int = 0

    model_config = {"from_attributes": True}


class PolicyBatchAssign(BaseModel):
    usernames: list[str]
    policy_id: int
