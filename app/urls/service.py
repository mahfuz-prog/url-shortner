import os
import logging
from uuid import UUID
from typing import List
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from . import model
from ..entities.url import URL
from ..auth.model import TokenData
from ..database.cache import redis_client
from ..exceptions import InternalServerError, UrlNotFoundError


load_dotenv()

SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
CLICKS_EXPIRE_SECONDS = os.getenv("CLICKS_EXPIRE_SECONDS")
SHORTCODE_EXPIRE_SECONDS = os.getenv("SHORTCODE_EXPIRE_SECONDS")


def get_long_url(db: Session, short_code: str) -> RedirectResponse:
    """take short_code for long_url lookup"""

    # check Redis first
    cached_url = redis_client.get(short_code)
    if cached_url:
        # Redis: clicks += 1
        redis_client.incr(f"clicks:{short_code}")

        # also mark this shortcode as "dirty" (needs syncing)
        redis_client.sadd("dirty_clicks", short_code)
        return RedirectResponse(cached_url, status_code=307)

    # cache miss
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if url is None:
        logging.warning(f"{short_code} corresponding long url not found")
        raise UrlNotFoundError(short_code)

    # if cache miss than store
    # short_code -> long_url
    redis_client.set(short_code, str(url.long_url), ex=SHORTCODE_EXPIRE_SECONDS)
    # clicks -> url.clicks
    redis_client.set(f"clicks:{short_code}", url.clicks + 1, ex=CLICKS_EXPIRE_SECONDS)

    return RedirectResponse(url.long_url, status_code=307)


def list_urls(current_user: TokenData, db: Session) -> List[model.ListUrlsResponse]:
    """list all urls of current user"""
    return db.query(URL).filter(URL.user_id == current_user.get_uuid()).all()


def register_url(
    db: Session, user_request: model.ShortUrlRequest, user_id: UUID | None = None
) -> model.ShortUrlResponse:
    """create a url in database"""
    try:
        long_url = str(user_request.long_url)
        create_url = URL(user_id=user_id, long_url=long_url)
        db.add(create_url)
        db.flush()
        create_url.generate_short_code()
        db.commit()

        # Redis: short_code -> long_url
        redis_client.set(create_url.short_code, long_url, ex=SHORTCODE_EXPIRE_SECONDS)
        # Redis: clicks:short_code -> click count
        redis_client.set(f"clicks:{create_url.short_code}", 0, ex=CLICKS_EXPIRE_SECONDS)

        logging.info("Successfully new url created")
        return model.ShortUrlResponse(
            short_code=f"{SERVER_ADDRESS}/urls/get-url/{create_url.short_code}"
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to create url. Error: {str(e)}")
        raise InternalServerError()
