from datetime import datetime
from sqlalchemy.orm import Session

from .tasks import sync_clicks_to_db
from ..database.core import SessionLocal


def main():
    db: Session = SessionLocal()

    try:
        sync_clicks_to_db(db)
        print(f"Clicks synced successfully at {datetime.now()}")
    except Exception as e:
        print(f"Failed to sync clicks at {datetime.now()}. Error: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
