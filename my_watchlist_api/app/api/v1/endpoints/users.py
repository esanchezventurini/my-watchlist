from fastapi import APIRouter, Depends, Query, status

from app.core.security import get_current_user
from app.dependencies.dependencies import get_user_service
from app.schemas.user import UserCreate, UserRead, UserUpdate, PublicUserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, user_service = Depends(get_user_service)):
    return user_service.create_user(user_in)


@router.get("/", response_model=list[PublicUserRead])
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    user_service = Depends(get_user_service)
):
    return user_service.list_users(skip=skip, limit=limit)


@router.get("/me", response_model=UserRead)
def get_user(user_service = Depends(get_user_service), current_user = Depends(get_current_user)):
    return user_service.get_user(current_user.id)


@router.patch("/me", response_model=UserRead)
def update_user(user_in: UserUpdate,
                user_service = Depends(get_user_service),
                current_user = Depends(get_current_user)
):
    return user_service.update_user(current_user.id, user_in)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_service = Depends(get_user_service), current_user = Depends(get_current_user)):
    return user_service.delete_user(current_user.id)

