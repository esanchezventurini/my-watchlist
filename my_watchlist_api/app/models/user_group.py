from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base

user_group_table = Table(
    "user_group",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
    Column("admin", Integer, nullable=False, default=0)
)
