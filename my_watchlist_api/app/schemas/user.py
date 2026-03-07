from pydantic import BaseModel, ConfigDict, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    firstName: str
    lastName: str
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    firstName: str | None = None
    lastName: str | None = None


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    firstName: str
    lastName: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)

class PublicUserRead(BaseModel):
    username: str
    firstName: str
    lastName: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)