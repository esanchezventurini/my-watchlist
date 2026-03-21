from datetime import datetime
from typing import List

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.watchlist import Watchlist
from app.models.watchlist_movie import watchlist_movie_table


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    release_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    rating_imdb: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(), nullable=False)
    director: Mapped[str] = mapped_column(String(100), nullable=False)

    watchlists: Mapped[List["Watchlist"]] = relationship(
        "Watchlist", secondary=watchlist_movie_table, back_populates="movies"
    )
