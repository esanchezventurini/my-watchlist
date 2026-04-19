from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base

watchlist_movie_table = Table(
    "watchlist_movie",
    Base.metadata,
    Column("watchlist_id", Integer, ForeignKey("watchlists.id"), primary_key=True),
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True)
)
