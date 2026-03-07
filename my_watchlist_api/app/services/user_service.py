from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def create_user(self, user_in: UserCreate) -> User:
        errors = []

        if self.repo.username_exists(user_in.username):
            errors.append("Username already exists")

        if self.repo.email_exists(user_in.email):
            errors.append("Email already exists")

        if errors:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)

        user_data = user_in.model_dump(exclude={"password"})
        user_data["password_hash"] = hash_password(user_in.password)

        try:
            return self.repo.create_from_dict(user_data)
        # Avoid race condition issues
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Username or email already exists",
            )

    def get_user(self, user_id: int) -> User:
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.repo.list(skip=skip, limit=limit)

    def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return self.repo.update(user, user_in)

    def delete_user(self, user_id: int) -> None:
        user = self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.repo.delete(user)

