from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserProfileResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr


class ChangeUserPassword(BaseModel):
    password: str
    new_password: str


class ChangeUserName(BaseModel):
    username: str
