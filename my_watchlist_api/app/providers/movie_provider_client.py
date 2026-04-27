from datetime import datetime

import httpx

from app.core.config import settings
from app.schemas.movie import MovieSearch


class MovieProviderClient:
    @staticmethod
    async def get_movie(movie_title: str) -> MovieSearch | None:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.omdb_base_url,
                params={"apikey": settings.omdb_api_key, "t": movie_title},
            )

        data = response.json()

        if data.get("Response") == "False":
            return None

        release_date = datetime.strptime(data.get("Released", "N/A"), "%d %b %Y") if data.get("Released") != "N/A" else None
        rating_imdb = float(data.get("imdbRating", 0)) if data.get("imdbRating") != "N/A" else 0.0

        return MovieSearch(
            title=data.get("Title", ""),
            release_date=release_date,
            rating_imdb=rating_imdb,
            description=data.get("Plot", ""),
            director=data.get("Director", ""),
            genre=data.get("Genre", ""),
            imdb_id = data.get("imdbID", "")
        )
