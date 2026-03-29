from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    default_ip_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    auto_reenable: Mapped[bool] = mapped_column(Boolean, default=True)
    reenable_delay_sec: Mapped[int] = mapped_column(Integer, default=300)
    notify_on_violation: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    users: Mapped[list["UserIPConfig"]] = relationship(back_populates="policy")


from src.models.user import UserIPConfig  # noqa: E402
