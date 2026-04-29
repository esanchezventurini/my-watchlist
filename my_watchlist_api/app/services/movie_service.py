from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.providers.movie_provider_client import MovieProviderClient
from app.repositories.movie_repository import MovieRepository
from app.schemas.movie import MovieSearch


class MovieService:
    def __init__(self, db: Session):
        self.repo = MovieRepository(db)

    async def search_movie_on_movies_provider(self, name: str) -> MovieSearch:
        movie_search = await MovieProviderClient.get_movie(name)

        if movie_search is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

        movie = self.repo.get_by_imdb_id(movie_search.imdb_id)
        if movie:
            return self.repo.update_movie(movie, movie_search)
        else:
            return self.repo.create_from_dict(movie_search.model_dump())
