
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base


class PublishingJob(Base):
    __tablename__ = "publishing_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, nullable=False)
    idempotency_key = Column(String(100), unique=True, nullable=True)
    request_hash = Column(String(64), nullable=True)
    platform = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="queued")
    retry_count = Column(Integer, default=0, nullable=False)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
