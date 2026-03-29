from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_users: int
    monitored_users: int
    active_users: int
    disabled_users: int
    total_active_ips: int
    violations_today: int


class LiveIPEntry(BaseModel):
    username: str
    active_ips: list[str]
    ip_count: int
    effective_limit: int
    is_over_limit: bool
    is_disabled: bool


class LiveSnapshot(BaseModel):
    entries: list[LiveIPEntry]
    total_active_users: int
    total_active_ips: int
