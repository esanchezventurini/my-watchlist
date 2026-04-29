from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.movie import Movie
from app.schemas.movie import MovieSearch


class MovieRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_from_dict(self, data: dict) -> Movie:
        movie = Movie(**data)
        self.db.add(movie)

        try:
            self.db.commit()
            self.db.refresh(movie)
            return movie

        # Avoid race condition issues
        except IntegrityError:
            return self.get_by_imdb_id(movie.imdb_id)


    def update_movie(self, existing_movie: Movie, updated_movie: MovieSearch) -> Movie:
        existing_movie.title = updated_movie.title
        existing_movie.release_date = updated_movie.release_date
        existing_movie.rating_imdb = updated_movie.rating_imdb
        existing_movie.genre = updated_movie.genre
        existing_movie.director = updated_movie.director
        existing_movie.description = updated_movie.description
        self.db.commit()
        self.db.refresh(existing_movie)
        return existing_movie


    def get_by_imdb_id(self, imdb_id: str) -> Movie | None:
        return self.db.query(Movie).filter(Movie.imdb_id == imdb_id).first()