from typing import List
from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

from . import model
from . import service
from ..auth.service import current_user
from ..database.core import DbSession

router = APIRouter()


# logged in user short url
@router.post("/short-url/", status_code=status.HTTP_201_CREATED)
async def short_url_private(
    current_user: current_user, db: DbSession, user_request: model.ShortUrlRequest
):
    return service.register_url(db, user_request, current_user.get_uuid())


# public short url route
@router.post("/short-url-public/", status_code=status.HTTP_201_CREATED)
async def short_url_public(db: DbSession, user_request: model.ShortUrlRequest):
    return service.register_url(db, user_request)


# list all current user shorted urls
@router.get("/list-urls/", response_model=List[model.ListUrlsResponse])
async def list_urls(current_user: current_user, db: DbSession):
    return service.list_urls(current_user, db)


# get a long url from short code
@router.get("/get-url/{short_code}", response_class=RedirectResponse)
async def get_long_url(db: DbSession, short_code: str):
    return service.get_long_url(db, short_code)
