from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MovieBase(BaseModel):
    title: str
    release_date: datetime
    rating_imdb: float
    description: str
    director: str
    genre: str
    imdb_id: str


class MovieRead(MovieBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class MovieSearch(MovieBase):
    pass

    model_config = ConfigDict(from_attributes=True)
