"""Integration tests for the /movies endpoint."""
from unittest.mock import AsyncMock, patch

import pytest
from app.schemas.movie import MovieSearch

SAMPLE_MOVIE = MovieSearch(
    title="The Godfather",
    release_date="1972-03-24T00:00:00",
    rating_imdb=9.9,
    description="The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
    director="Francis Ford Coppola",
    genre="Crime, Drama",
    imdb_id="tt0068646",
)


class TestGetMovie:
    @patch("app.providers.movie_provider_client.MovieProviderClient.get_movie", new_callable=AsyncMock)
    def test_returns_movie_from_provider(self, mock_get_movie, client):
        mock_get_movie.return_value = SAMPLE_MOVIE
        resp = client.get("/api/v1/movies/?title=The Godfather")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "The Godfather"
        assert data["imdb_id"] == "tt0068646"
        assert "id" in data

    @patch("app.providers.movie_provider_client.MovieProviderClient.get_movie", new_callable=AsyncMock)
    def test_second_call_updates_existing(self, mock_get_movie, client):
        mock_get_movie.return_value = SAMPLE_MOVIE
        client.get("/api/v1/movies/?title=The Godfather")
        resp = client.get("/api/v1/movies/?title=The Godfather")
        assert resp.status_code == 200
        assert resp.json()["title"] == "The Godfather"

    @patch("app.providers.movie_provider_client.MovieProviderClient.get_movie", new_callable=AsyncMock)
    def test_not_found_returns_404(self, mock_get_movie, client):
        mock_get_movie.return_value = None
        resp = client.get("/api/v1/movies/?title=nonexistent")
        assert resp.status_code == 404

    def test_missing_title_returns_422(self, client):
        resp = client.get("/api/v1/movies/")
        assert resp.status_code == 422
