from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.group_service import GroupService
from app.services.user_service import UserService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


def get_group_service(db: Session = Depends(get_db)) -> GroupService:
    return GroupService(db)