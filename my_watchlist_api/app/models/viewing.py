from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.movie import Movie


class Viewing(Base):
    __tablename__ = "viewings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    watched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    score: Mapped[Optional[int]] = mapped_column(nullable=True)
    review: Mapped[Optional[str]] = mapped_column(String(), nullable=True)

    user_id: Mapped[int] = mapped_column(nullable=False)
    movie_id: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="viewings")
    movie: Mapped["Movie"] = relationship("Movie", back_populates="viewings")