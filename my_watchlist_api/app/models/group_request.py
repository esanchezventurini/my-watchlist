from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.group_request_status import GroupRequestStatus

# Needed to avoid circular dependency
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group


class GroupRequest(Base):
    __tablename__ = "group_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[GroupRequestStatus] = mapped_column(nullable=False, default=GroupRequestStatus.PENDING.value)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="group_requests")
    group: Mapped["Group"] = relationship("Group", back_populates="requests")

