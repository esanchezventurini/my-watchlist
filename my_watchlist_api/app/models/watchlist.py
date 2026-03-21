from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.watchlist_movie import watchlist_movie_table

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.user import User
    from app.models.movie import Movie


class Watchlist(Base):
    __tablename__ = "watchlists"
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
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="watchlists")
    group: Mapped[Optional["Group"]] = relationship("Group", back_populates="watchlists")

    movies: Mapped[List["Movie"]] = relationship(
        "Movie", secondary=watchlist_movie_table, back_populates="watchlists"
    )
