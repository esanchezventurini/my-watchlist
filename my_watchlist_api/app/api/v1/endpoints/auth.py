from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token
from app.dependencies import get_user_service
from app.schemas.user import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service = Depends(get_user_service)
):
    user = user_service.authenticate_user(form_data.username, form_data.password)
    access_token = create_access_token(user.id)
    return Token(access_token=access_token)

