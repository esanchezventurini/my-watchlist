"""Unit tests for MovieService."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.schemas.movie import MovieSearch
from app.services.movie_service import MovieService

SAMPLE_MOVIE = MovieSearch(
    title="The Godfather",
    release_date="1972-03-24T00:00:00",
    rating_imdb=9.9,
    description="The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
    director="Francis Ford Coppola",
    genre="Crime, Drama",
    imdb_id="tt0068646",
)


def _service_with_repo(repo):
    svc = MovieService.__new__(MovieService)
    svc.repo = repo
    return svc


class TestSearchMovie:
    @pytest.mark.asyncio
    @patch("app.services.movie_service.MovieProviderClient.get_movie", new_callable=AsyncMock)
    async def test_creates_new_movie_when_not_in_db(self, mock_get_movie):
        mock_get_movie.return_value = SAMPLE_MOVIE
        repo = MagicMock()
        repo.get_by_imdb_id.return_value = None
        fake_movie = MagicMock()
        repo.create_from_dict.return_value = fake_movie

        svc = _service_with_repo(repo)
        result = await svc.search_movie_on_movies_provider("The Godfather")

        mock_get_movie.assert_called_once_with("The Godfather")
        repo.get_by_imdb_id.assert_called_once_with("tt0068646")
        repo.create_from_dict.assert_called_once()
        assert result is fake_movie

    @pytest.mark.asyncio
    @patch("app.services.movie_service.MovieProviderClient.get_movie", new_callable=AsyncMock)
    async def test_updates_existing_movie(self, mock_get_movie):
        mock_get_movie.return_value = SAMPLE_MOVIE
        existing = MagicMock()
        repo = MagicMock()
        repo.get_by_imdb_id.return_value = existing
        repo.update_movie.return_value = existing

        svc = _service_with_repo(repo)
        result = await svc.search_movie_on_movies_provider("The Godfather")

        repo.update_movie.assert_called_once_with(existing, SAMPLE_MOVIE)
        repo.create_from_dict.assert_not_called()
        assert result is existing

    @pytest.mark.asyncio
    @patch("app.services.movie_service.MovieProviderClient.get_movie", new_callable=AsyncMock)
    async def test_raises_404_when_provider_returns_none(self, mock_get_movie):
        mock_get_movie.return_value = None
        repo = MagicMock()

        svc = _service_with_repo(repo)
        with pytest.raises(HTTPException) as exc_info:
            await svc.search_movie_on_movies_provider("nonexistent")

        assert exc_info.value.status_code == 404

