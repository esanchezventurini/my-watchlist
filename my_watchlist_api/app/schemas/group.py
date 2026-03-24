from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GroupBase(BaseModel):
    name: str
    description: str


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    pass


class Member(BaseModel):
    user_id: int
    username: str
    first_name: str
    last_name: str
    is_admin: bool
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Movie(BaseModel):
    id: int
    title: str
    release_date: datetime
    rating_imdb: float
    description: str
    director: str

    model_config = ConfigDict(from_attributes=True)


class Watchlist(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    movies: list[Movie]

    model_config = ConfigDict(from_attributes=True)


class GroupRead(GroupBase):
    id: int
    created_date: datetime
    members: list[Member] = Field(default_factory=list)
    watchlist: list[Watchlist] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)




