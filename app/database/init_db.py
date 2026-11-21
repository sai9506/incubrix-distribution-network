from app.database.connection import Base, engine
from app.models.destination import Destination
from app.models.publishing_log import PublishingLog
from app.models.publishing_job import PublishingJob

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")