import pytest
from uuid import uuid4
from unittest.mock import Mock
import app.users.service as users_service
from app.exceptions import UserNotFoundError
from app.users.model import ChangeUserPassword, ChangeUserName
from app.exceptions import InvalidPasswordError, InternalServerError


class TestUsersService:
    def test_get_user_by_id(self, db_session, test_user):
        db_session.add(test_user)
        db_session.commit()

        user = users_service.get_user_by_id(db_session, test_user.id)
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.username == test_user.username

        with pytest.raises(UserNotFoundError):
            users_service.get_user_by_id(db_session, uuid4())

    def test_change_user_password(self, db_session, test_user):
        db_session.add(test_user)
        db_session.commit()

        # successful change password
        form_data = ChangeUserPassword(password="string", new_password="string")
        users_service.change_user_password(db_session, test_user.id, form_data)

        # invalid password
        form_data = ChangeUserPassword(password="invalid", new_password="string")
        with pytest.raises(InvalidPasswordError) as exc_info:
            users_service.change_user_password(db_session, test_user.id, form_data)
            assert exc_info == "Current password is incorrect"

        # other error
        form_data = ChangeUserPassword(password="string", new_password="string")
        mock_db = Mock()
        mock_db.commit.side_effect = Exception
        with pytest.raises(InternalServerError) as exc_info:
            users_service.change_user_password(mock_db, test_user.id, form_data)
            assert exc_info == "An unexpected error occurred"

    def test_change_user_username(self, db_session, test_user):
        db_session.add(test_user)
        db_session.commit()

        # successful name change
        form_data = ChangeUserName(username="new")
        users_service.change_user_username(db_session, test_user.id, form_data)

        # error
        mock_db = Mock()
        mock_db.commit.side_effect = Exception
        with pytest.raises(InternalServerError) as exc_info:
            users_service.change_user_username(mock_db, test_user.id, form_data)
            assert exc_info == "An unexpected error occurred"
