import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from ..database.core import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}')>"
