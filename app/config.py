
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    APP_NAME = os.getenv(
        "APP_NAME",
        "IncuBrix Distribution Service"
    )

    ENVIRONMENT = os.getenv(
        "ENVIRONMENT",
        "development"
    )

    DATABASE_URL = os.getenv("DATABASE_URL")

    # Webhook
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

    # Discourse
    DISCOURSE_URL = os.getenv("DISCOURSE_URL")
    DISCOURSE_API_KEY = os.getenv("DISCOURSE_API_KEY")
    DISCOURSE_USERNAME = os.getenv("DISCOURSE_USERNAME")

    # Lemmy
    LEMMY_URL = os.getenv("LEMMY_URL")
    LEMMY_AUTH_TOKEN = os.getenv("LEMMY_AUTH_TOKEN")
    LEMMY_COMMUNITY_ID = os.getenv("LEMMY_COMMUNITY_ID")

    # Dev.to
    DEVTO_API_KEY = os.getenv("DEVTO_API_KEY")
    DEVTO_URL = os.getenv(
        "DEVTO_URL",
        "https://dev.to"
    )

    # Ghost
    GHOST_URL = os.getenv("GHOST_URL")
    GHOST_ADMIN_API_KEY = os.getenv(
        "GHOST_ADMIN_API_KEY"
    )

    # S3-compatible object storage
    MINIO_ENDPOINT = os.getenv(
        "MINIO_ENDPOINT",
        "localhost:9002"
    )

    MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
    MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")

    MINIO_BUCKET = os.getenv(
        "MINIO_BUCKET",
        "incubrix-assets"
    )

    MINIO_SECURE = os.getenv(
        "MINIO_SECURE",
        "false"
    ).lower() == "true"


settings = Settings()
