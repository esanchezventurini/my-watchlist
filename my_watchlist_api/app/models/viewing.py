from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.group import Group
    from app.models.movie import Movie


class Viewing(Base):
    __tablename__ = "viewings"
    __table_args__ = (
        CheckConstraint(
            "user_id IS NOT NULL OR group_id IS NOT NULL",
            name="ck_watchlist_user_or_group_not_null",
        ),
        CheckConstraint(
            "NOT (user_id IS NOT NULL AND group_id IS NOT NULL)",
            name="ck_watchlist_user_and_group_mutually_exclusive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    watched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    score: Mapped[Optional[int]] = mapped_column(nullable=True)
    review: Mapped[Optional[str]] = mapped_column(String(), nullable=True)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"), nullable=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), nullable=False)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="viewings")
    group: Mapped[Optional["Group"]] = relationship("Group", back_populates="viewings")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="viewings")