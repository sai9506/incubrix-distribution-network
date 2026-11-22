
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
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
# HOME - REDIRECT TO SWAGGER UI
# --------------------------------------------------

@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse(url="/docs")


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
