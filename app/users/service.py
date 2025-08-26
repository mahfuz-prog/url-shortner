import logging
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from . import model
from ..entities.user import User
from ..database.cache import redis_client
from ..auth.service import verify_password, get_pass_hash
from ..exceptions import UserNotFoundError, InvalidPasswordError, InternalServerError


def get_user_by_id(db: Session, user_id: UUID) -> model.UserProfileResponse:
    user = db.get(User, user_id)

    if not user:
        logging.warning(f"User not found with ID: {user_id}")
        raise UserNotFoundError(user_id)
    return user


def store_password_changed_in_cache(user_id: UUID, timestamp: int) -> None:
    """
    Store the last password change timestamp in Redis.
    Key: user:password_changed:<user_id>
    Value: timestamp in UTC
    """
    redis_client.set(f"user:password_changed:{user_id}", timestamp)


def change_user_password(
    db: Session, user_id: UUID, user_request: model.ChangeUserPassword
) -> None:
    try:
        user = get_user_by_id(db, user_id)

        # check the given password matched with current password
        if not verify_password(user_request.password, user.password):
            raise InvalidPasswordError()

        user.password = get_pass_hash(user_request.new_password)
        db.commit()

        timestamp = int(datetime.now(timezone.utc).timestamp())
        store_password_changed_in_cache(user_id, timestamp)

    except InvalidPasswordError:
        logging.warning(f"Invalid current password for user ID: {user_id}")
        raise
    except Exception as e:
        logging.warning(
            f"Unexpected error while changing password for user_id: {user_id}. Error: {str(e)}"
        )
        raise InternalServerError()


def change_user_username(
    db: Session, user_id: UUID, user_request: model.ChangeUserName
) -> None:
    try:
        user = get_user_by_id(db, user_id)
        user.username = user_request.username
        db.commit()
    except Exception as e:
        logging.warning(
            f"Unexpected error while changing username for user_id: {user_id}. Error: {str(e)}"
        )
        raise InternalServerError()
