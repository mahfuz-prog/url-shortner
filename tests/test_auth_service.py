import time
import pytest
from datetime import timedelta
from unittest.mock import Mock
from app.entities.user import User
from app.auth import service as auth_service
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.model import RegisterUserRequest
from app.exceptions import (
    AuthenticationError,
    UserEmailConflictError,
    UserUserNameConflictError,
    InternalServerError,
)


class TestAuthService:
    def test_verify_password(self):
        plain_password = "string"
        hashed_password = auth_service.get_pass_hash(plain_password)
        assert auth_service.verify_password(plain_password, hashed_password)
        assert not auth_service.verify_password("wrongpassword", hashed_password)

    def test_authenticate_user(self, db_session, test_user):
        """
        pytest sees db_session and looks for a fixture named db_session/test_user
        It runs the fixture, gets the db object, and injects it.
        """

        db_session.add(test_user)
        db_session.commit()

        # authenticate the created user
        user = auth_service.authenticate_user(test_user.email, "string", db_session)
        assert user is not False
        assert user.email == test_user.email
        assert user.password == test_user.password
        assert user.username == test_user.username

    def test_get_access_token(self, db_session, test_user):
        db_session.add(test_user)
        db_session.commit()

        form_data = OAuth2PasswordRequestForm(
            username=test_user.email, password="string"
        )
        token = auth_service.get_access_token(db_session, form_data)
        assert token.token_type == "bearer"
        assert token.access_token is not None

    def test_create_and_verify_access_token(self, test_user, db_session):
        token = auth_service.create_access_token(
            test_user.email, test_user.id, timedelta(seconds=1)
        )
        assert token

        token_data = auth_service.verify_token(token)
        assert token_data.get_uuid() == test_user.id

        # sleep 1 seconds for expire the token
        time.sleep(1)
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.verify_token(token)
            assert exc_info.value == "Token expired"

        # invalid token
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.verify_token("invalid token")
            assert exc_info.value == "Invalid token"

        # try to get a access token for a non existing user
        with pytest.raises(AuthenticationError) as exc_info:
            form_data = OAuth2PasswordRequestForm(
                username=test_user.email, password="string"
            )

            auth_service.get_access_token(db_session, form_data)
            assert exc_info.value == "Invalid credentials"

    def test_register_user(self, db_session, test_user):
        form_data = RegisterUserRequest(
            email=test_user.email, username=test_user.username, password="string"
        )

        # create user
        auth_service.register_user(db_session, form_data)
        user = db_session.query(User).filter_by(email=test_user.email).first()
        assert user is not None
        assert user.username == test_user.username
        assert user.email == test_user.email

        # username exist in database
        form_data = RegisterUserRequest(
            email="test@email.com", username=test_user.username, password="string"
        )
        with pytest.raises(UserUserNameConflictError) as exc_info:
            auth_service.register_user(db_session, form_data)
            assert exc_info.value == "Username already registered"

        # email exist in database
        form_data = RegisterUserRequest(
            email=test_user.email, username="test", password="string"
        )
        with pytest.raises(UserEmailConflictError) as exc_info:
            auth_service.register_user(db_session, form_data)
            assert exc_info.value == "Email already registered"

        # other error
        db_mock = Mock()

        # make commit() raise an exception
        db_mock.commit.side_effect = Exception

        with pytest.raises(InternalServerError) as exc_info:
            auth_service.register_user(db_mock, form_data)
            assert exc_info.value == "An unexpected error occurred"
