from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base


class UserIPConfig(Base):
    __tablename__ = "user_ip_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    admin_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    ip_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    policy_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("policies.id", ondelete="SET NULL"), nullable=True
    )
    is_monitored: Mapped[bool] = mapped_column(Boolean, default=True)
    is_exempt: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_reenable: Mapped[bool] = mapped_column(Boolean, default=True)
    reenable_delay_sec: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    disabled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    disabled_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    policy: Mapped[Optional["Policy"]] = relationship(back_populates="users")

    def get_effective_limit(self, global_default: int) -> int:
        """Resolve effective IP limit: user > policy > global."""
        if self.ip_limit is not None:
            return self.ip_limit
        if self.policy and self.policy.default_ip_limit is not None:
            return self.policy.default_ip_limit
        return global_default


# Import here to avoid circular imports at module level
from src.models.policy import Policy  # noqa: E402
