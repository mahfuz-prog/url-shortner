from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from . import service
from . import model
from ..database.core import DbSession


router = APIRouter()


# create account
@router.post("/sign-up/", status_code=status.HTTP_201_CREATED)
async def sign_up(db: DbSession, user_request: model.RegisterUserRequest):
    service.register_user(db, user_request)


# login route
@router.post("/log-in/", response_model=model.Token)
async def log_in(
    db: DbSession, user_request: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    model.Token

    - It Guarantees a Consistent Response Format
    - response will always be a JSON object containing an
      access_token (a string) and a token_type (a string), and nothing else


    OAuth2PasswordRequestForm

    - Parse the form data from the incoming request body.
    - Validate that the username and password fields are present.
    - OAuth2PasswordRequestForm → expects form-data (not JSON).

    - POST /auth/log-in/
    - Content-Type: application/x-www-form-urlencoded
    - username=test@example.com&password=string&grant_type=password
    """
    return service.get_access_token(db, user_request)
