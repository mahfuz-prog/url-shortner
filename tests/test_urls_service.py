import pytest
from unittest.mock import Mock
from app.urls.utils import encode_base62, decode_base62
import app.urls.service as urls_service
from app.entities.url import URL
from app.exceptions import UrlNotFoundError, InternalServerError
from app.urls.model import ShortUrlRequest
from app.auth.model import TokenData


class TestUrlsService:
    def test_get_long_url(self, db_session, test_url_public):
        # non existing url
        with pytest.raises(UrlNotFoundError) as exc_info:
            invalid_short_code = "10"
            urls_service.get_long_url(db_session, invalid_short_code)
            assert (
                exc_info.value
                == f"{invalid_short_code} corresponding long url not found"
            )

        # success response
        db_session.add(test_url_public)
        db_session.flush()
        test_url_public.generate_short_code()
        db_session.commit()

        response = urls_service.get_long_url(db_session, str(test_url_public.id))
        assert response.status_code == 307
        assert response.headers["location"] == test_url_public.long_url

    def test_register_url_private(self, db_session, test_user, test_url_private):
        # url registration fail
        user_request = ShortUrlRequest(long_url=test_url_private.long_url)
        mock_db = Mock()
        mock_db.add.side_effect = Exception

        with pytest.raises(InternalServerError) as exc_info:
            urls_service.register_url(mock_db, user_request)
            assert exc_info.value == "An unexpected error occurred"

        # successfully create private url
        response = urls_service.register_url(db_session, user_request)
        assert (
            str(response.short_code) == f"{urls_service.SERVER_ADDRESS}/urls/get-url/1"
        )

    def test_register_url_public(self, db_session, test_url_public):
        # url registration fail
        user_request = ShortUrlRequest(long_url=test_url_public.long_url)
        mock_db = Mock()
        mock_db.add.side_effect = Exception

        with pytest.raises(InternalServerError) as exc_info:
            urls_service.register_url(mock_db, user_request)
            assert exc_info.value == "An unexpected error occurred"

        # successfully create public url
        response = urls_service.register_url(db_session, user_request)
        assert (
            str(response.short_code) == f"{urls_service.SERVER_ADDRESS}/urls/get-url/1"
        )

    def test_list_urls(self, test_user, db_session):
        # create 20 urls
        for i in range(20):
            url = URL(user_id=test_user.id, long_url=f"https://example.com/{i}")
            db_session.add(url)
            db_session.flush()
            url.generate_short_code()

        db_session.commit()

        current_user = TokenData(user_id=str(test_user.id))
        urls = urls_service.list_urls(current_user, db_session)
        assert len(urls) == 20
        assert all(test_user.id == url.user_id for url in urls)


def test_encode_decode_base62():
    n = 99999999999999999
    assert decode_base62(encode_base62(n)) == n
