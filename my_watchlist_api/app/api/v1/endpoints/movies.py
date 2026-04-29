from fastapi import APIRouter, Depends, Query, HTTPException

from app.dependencies.dependencies import get_movie_service
from app.schemas.movie import MovieRead

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("/", response_model=MovieRead)
async def get_movie(
    title: str = Query(..., min_length=1),
    movie_service = Depends(get_movie_service)
):
    return await movie_service.search_movie_on_movies_provider(title)