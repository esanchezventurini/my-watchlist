from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group


class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True, index=True)
    admin: Mapped[int] = mapped_column(nullable=False, default=0)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_groups")
    group: Mapped["Group"] = relationship("Group", back_populates="user_groups")