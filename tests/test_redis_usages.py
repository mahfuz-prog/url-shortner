import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
import app.users.service as users_service
import app.auth.service as auth_service
from app.database.cache import redis_client
from app.exceptions import AuthenticationError
from app.users.model import ChangeUserPassword


class TestRedisUsages:
    def test_users_service_caching(self):
        user_id = uuid4()
        timestamp = int(datetime.now(timezone.utc).timestamp())
        users_service.store_password_changed_in_cache(user_id, timestamp)

        get_timestamp = redis_client.get(f"user:password_changed:{user_id}")
        assert timestamp == int(get_timestamp)

    def test_password_change_reset_token(self, test_user, db_session):
        db_session.add(test_user)
        db_session.commit()

        token = auth_service.create_access_token(
            test_user.email, test_user.id, timedelta(seconds=10)
        )

        token_data = auth_service.verify_token(token)
        assert token_data.get_uuid() == test_user.id

        form_data = ChangeUserPassword(password="string", new_password="string")
        users_service.change_user_password(db_session, test_user.id, form_data)

        # get last password change time
        last_changed = redis_client.get(f"user:password_changed:{test_user.id}")
        assert last_changed

        # after password change token verification fail
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.verify_token(token)
            assert exc_info.value == "Token invalid due to password change"
