import os
import jwt
import logging
from fastapi import Depends
from typing import Annotated
from uuid import uuid4, UUID
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from . import model
from ..entities.user import User
from ..database.cache import redis_client
from ..exceptions import (
    UserEmailConflictError,
    UserUserNameConflictError,
    InternalServerError,
    AuthenticationError,
)

load_dotenv()

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

""" 
OAuth 2.0 protocol for authentication

- It looks for the Authorization header.
- checks if the header has the format Bearer <token>.
- If the header is missing or in the wrong format, 
  FastAPI immediately returns a 401 Unauthorized HTTP error
  telling them they must log in.
- If the header is present and correctly formatted, FastAPI extracts the <token> string.
"""
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/log-in")

# password hashing
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# hash a pasword
def get_pass_hash(password: str) -> str:
    return bcrypt_context.hash(password)


# save a user in databse
def register_user(db: Session, user_request: model.RegisterUserRequest) -> None:
    create_user = User(
        id=uuid4(),
        username=user_request.username,
        email=user_request.email,
        password=get_pass_hash(user_request.password),
    )

    try:
        db.add(create_user)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        error_message = str(e)
        logging.warning(
            f"IntegrityError during registration for email: {user_request.email}, username: {user_request.username}"
        )

        """
        error messages may differ between databases 
        (Postgres, MySQL, SQLite) or versions.

        "users.email", "users.username"
        """

        if "users.email" in error_message:
            raise UserEmailConflictError()
        elif "users.username" in error_message:
            raise UserUserNameConflictError()

    except Exception as e:
        db.rollback()
        logging.error(f"Failed to create user: {user_request.email}. Error: {str(e)}")
        raise InternalServerError()


# verify a password
def verify_password(plain_pass: str, hashed_pass: str) -> bool:
    return bcrypt_context.verify(plain_pass, hashed_pass)


# authenticate a user
def authenticate_user(email: str, password: str, db: Session) -> User | bool:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        logging.warning(f"Failed authentication attempt for email: {email}")
        return False
    return user


# create a jwt token
def create_access_token(email: str, user_id: UUID, expires_delta: timedelta) -> str:
    encode = {
        "sub": email,
        "id": str(user_id),
        "exp": datetime.now(timezone.utc) + expires_delta,
        "iat": int(datetime.now(timezone.utc).timestamp()),  # issued at
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# login to get a access token
def get_access_token(
    db: Session, user_request: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> model.Token:
    # authenticate_user takes email and password
    # user_request.username is a email address
    user = authenticate_user(user_request.username, user_request.password, db)

    if not user:
        logging.warning(
            f"User not found for email: {user_request.username}! Request for JWT token."
        )
        raise AuthenticationError()

    # generate a token
    token = create_access_token(
        user.email, user.id, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return model.Token(access_token=token, token_type="bearer")


# verify a token
def verify_token(token: str) -> model.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")

        # Redis: track last user:password_changed:user_id
        last_changed = redis_client.get(f"user:password_changed:{user_id}")
        if last_changed:
            token_iat_ts = int(payload.get("iat", 0))
            last_changed_ts = int(last_changed)
            if last_changed_ts >= token_iat_ts:
                logging.warning(
                    f"Token invalidated for user {user_id} due to password change"
                )
                raise AuthenticationError("Token invalid due to password change")

        return model.TokenData(user_id=user_id)
    except AuthenticationError:
        raise
    except jwt.ExpiredSignatureError:
        logging.warning("Token expired")
        raise AuthenticationError("Token expired")
    except jwt.InvalidTokenError:
        logging.warning("Invalid token")
        raise AuthenticationError("Invalid token")
    except Exception as e:
        logging.error(f"Unexpected error while verifying token. Error: {str(e)}")
        raise AuthenticationError("Token validation failed")


# get current user from token
def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> model.TokenData:
    return verify_token(token)


# load the current user
current_user = Annotated[model.TokenData, Depends(get_current_user)]
