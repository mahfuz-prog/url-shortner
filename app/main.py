from fastapi import FastAPI

from .database.core import engine, Base
from .logging import configure_logging, LogLevels

configure_logging(LogLevels.info)

app = FastAPI()

""" Only uncomment below to create new tables, 
otherwise the tests will fail if not connected
"""
from .entities.user import User  # noqa: E402, F401

Base.metadata.create_all(bind=engine)

from .auth.controller import router as auth_router  # noqa: E402
from .users.controller import router as users_router  # noqa: E402

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
