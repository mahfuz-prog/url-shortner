import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
import app.urls.service as urls_service
import app.users.service as users_service
import app.auth.service as auth_service
from app.entities.url import URL
from app.database.cache import redis_client
from app.background_tasks.tasks import sync_clicks_to_db
from app.exceptions import AuthenticationError
from app.users.model import ChangeUserPassword


class TestRedisUsages:
    def test_urls_service_caching(self, db_session, test_url_public):
        class UserRequest:
            def __init__(self):
                self.long_url = test_url_public.long_url

        user_request = UserRequest()
        response = urls_service.register_url(db_session, user_request)
        short_code = str(response.short_code).split("/")[-1]

        # Redis: short_code -> long_url
        get_url_cache = redis_client.get(short_code)
        assert get_url_cache == test_url_public.long_url

        # Redis: clicks:short_code -> count
        get_count_cache = redis_client.get(f"clicks:{short_code}")
        assert get_count_cache == "0"

        # mimic clicks
        for _ in range(20):
            urls_service.get_long_url(db_session, short_code)

        get_count_cache = redis_client.get(f"clicks:{short_code}")
        assert get_count_cache == "20"

        # clicks only stored in redis
        # corn job will ensure update clicks redis -> db
        url = db_session.query(URL).filter(URL.short_code == short_code).first()
        assert url.clicks == 0

    def test_sync_clicks_to_db(self, db_session, test_url_public):
        class UserRequest:
            def __init__(self):
                self.long_url = test_url_public.long_url

        user_request = UserRequest()

        short_codes = []
        # set 20 random shortcode clicks and test
        for i in range(20):
            # save url
            response = urls_service.register_url(db_session, user_request)
            short_code = str(response.short_code).split("/")[-1]
            short_codes.append(short_code)

            # add test clicks to this url
            redis_client.set(f"clicks:{short_code}", i * 2)

            # also mark this shortcode as "dirty" (needs syncing)
            redis_client.sadd("dirty_clicks", short_code)
            assert redis_client.sismember("dirty_clicks", short_code)

        # Redis: clicks -> db
        sync_clicks_to_db(db_session)
        for i, short_code in enumerate(short_codes):
            # load the url from database to get clicks
            url = db_session.query(URL).filter(URL.short_code == short_code).first()
            assert url.clicks == i * 2

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
