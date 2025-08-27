from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict


class ShortUrlRequest(BaseModel):
    """2083 len charecter http/https"""

    long_url: HttpUrl


class ShortUrlResponse(BaseModel):
    short_code: HttpUrl


class ListUrlsResponse(BaseModel):
    id: int
    user_id: UUID | None
    long_url: str
    short_code: str
    clicks: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
