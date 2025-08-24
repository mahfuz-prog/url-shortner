import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.core import Base
from app.auth import service as auth_service
from app.entities.user import User


@pytest.fixture(scope="function")
def db_session():
    """
    Creates a temporary SQLite database for testing.
    Builds all tables before the test.
    Provides a DB session to your tests.
    Cleans up after each test (closes session + drops tables).
    """
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

    """
	connect_args={"check_same_thread": False} is required for 
	SQLite because SQLite doesn’t allow multiple threads to 
	use the same connection by default, and tests often run 
	in a multi-threaded context.
	"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user():
    hashed_password = auth_service.get_pass_hash("string")
    return User(
        id=uuid4(),
        email="test@example.com",
        username="string",
        password=hashed_password,
    )


# send request without running the server
@pytest.fixture(scope="function")
def client(db_session):
    from app.main import app
    from app.database.core import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    # replaces the real DB session factory with a
    # test version (db_session from another fixture)
    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client

    # Ensures no test state leaks into other tests.
    app.dependency_overrides.clear()
