from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.watchlist import Watchlist
    from app.models.viewing import Viewing
    from app.models.user_group import UserGroup


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    firstName: Mapped[str] = mapped_column(String(80), nullable=False)
    lastName: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    groups: Mapped[List["Group"]] = relationship(
        "Group", secondary="user_groups", back_populates="users", viewonly=True
    )

    watchlists: Mapped[List["Watchlist"]] = relationship(
        "Watchlist", back_populates="user", cascade="all, delete-orphan"
    )

    viewings: Mapped[List["Viewing"]] = relationship(
        "Viewing", back_populates="user", cascade="all, delete-orphan"
    )

    user_groups: Mapped[List["UserGroup"]] = relationship(
        "UserGroup", back_populates="user", cascade="all, delete-orphan"
    )