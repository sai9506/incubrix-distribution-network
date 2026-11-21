
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.database.connection import Base


class PublishingLog(Base):
    __tablename__ = "publishing_logs"

    id = Column(Integer, primary_key=True, index=True)

    idempotency_key = Column(
        String(100),
        unique=True,
        nullable=False
    )

    request_hash = Column(
        String(64),
        nullable=True
    )

    platform = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    response = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )
