from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_in: UserCreate) -> User:
        user = User(**user_in.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalar_one_or_none()

    def username_exists(self, username: str) -> bool:
        stmt = select(User).where(User.username == username)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def email_exists(self, email: EmailStr) -> bool:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def update(self, user: User, user_in: UserUpdate) -> User:
        update_data = user_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        #self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()