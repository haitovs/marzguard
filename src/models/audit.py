from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)
    ip_addresses: Mapped[str] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="system")
