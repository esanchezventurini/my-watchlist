from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user_group import user_group_table

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.watchlist import Watchlist
    from app.models.viewing import Viewing


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(), nullable=True)
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    users: Mapped[List["User"]] = relationship(
        "User", secondary=user_group_table, back_populates="groups"
    )

    watchlists: Mapped[List["Watchlist"]] = relationship(
        "Watchlist", back_populates="group"
    )

    viewings: Mapped[List["Viewing"]] = relationship(
        "Viewing", back_populates="group"
    )
