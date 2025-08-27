from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from ..database.core import Base
from ..urls.utils import encode_base62


class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    long_url = Column(String(2083), nullable=False)
    short_code = Column(String(10), unique=True, index=True)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def generate_short_code(self):
        if not self.id:
            raise ValueError("ID must exist before generating short_code")
        self.short_code = encode_base62(self.id)

    def __repr__(self):
        return f"<URL(short_code='{self.short_code}', long_url='{self.long_url}')>"
