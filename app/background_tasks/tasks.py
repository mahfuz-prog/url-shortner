from sqlalchemy.orm import Session

from ..entities.url import URL
from ..database.cache import redis_client


def sync_clicks_to_db(db: Session) -> None:
    """Redis: clicks:short_code -> database"""

    needs_sync = redis_client.smembers("dirty_clicks")

    for short_code in needs_sync:
        clicks = int(redis_client.get(f"clicks:{short_code}"))
        url = db.query(URL).filter(URL.short_code == short_code).first()
        url.clicks = clicks

        # after syncing, remove from dirty set
        redis_client.srem("dirty_clicks", short_code)
    db.commit()
