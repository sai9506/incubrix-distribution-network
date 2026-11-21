
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.utils.logging_config import setup_logging

# Configure JSON logging before loading API routes
setup_logging()

from app.api.routes import router
from app.database.connection import engine


app = FastAPI(
    title="IncuBrix Distribution Service",
    description="Long-Tail Destination Distribution Network",
    version="1.0.0"
)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to IncuBrix Distribution Service",
        "status": "running"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# --------------------------------------------------
# READINESS CHECK
# --------------------------------------------------

@app.get("/ready")
def ready():

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "database": "connected"
        }

    except SQLAlchemyError:

        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "database": "disconnected"
            }
        )


# --------------------------------------------------
# API ROUTES
# --------------------------------------------------

app.include_router(router)
