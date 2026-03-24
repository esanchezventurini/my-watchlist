from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models.group import Group  # noqa: F401
from app.models.user import User  # noqa: F401 # noqa: F401
from app.models.watchlist import Watchlist  # noqa: F401
from app.models.movie import Movie  # noqa: F401
from app.models.viewing import Viewing  # noqa: F401
from app.models.watchlist_movie import watchlist_movie_table  # noqa: F401
from app.models.user_group import UserGroup # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
