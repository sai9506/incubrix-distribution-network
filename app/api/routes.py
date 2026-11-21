
import hashlib
import json
import uuid
import logging
import os
import shutil
import tempfile

from pathlib import Path
from datetime import datetime, time as datetime_time

from fastapi import (
    APIRouter,
    Depends,
    Header,
    BackgroundTasks,
    HTTPException,
    UploadFile,
    File,
    Response,
    status
)

from pydantic import BaseModel, Field

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.config import settings
from app.database.connection import get_db

from app.models.publishing_log import PublishingLog
from app.models.publishing_job import PublishingJob

from app.connectors.registry import ConnectorRegistry
from app.connectors.manual import ManualConnector
from app.connectors.webhook import WebhookConnector
from app.connectors.discourse import DiscourseConnector
from app.connectors.lemmy import LemmyConnector
from app.connectors.devto import DevToConnector
from app.connectors.ghost import GhostConnector

from app.rules.engine import PostingRulesEngine
from app.services.publishing import PublishingService
from app.services.background import process_publishing_job

from app.storage.object_storage import storage


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["Distribution"]
)


# --------------------------------------------------
# STRUCTURED ERROR RESPONSE
# --------------------------------------------------

def raise_api_error(
    status_code: int,
    code: str,
    message: str
):
    raise HTTPException(
        status_code=status_code,
        detail={
            "code": code,
            "message": message
        }
    )


# --------------------------------------------------
# CONNECTOR REGISTRATION
# --------------------------------------------------

registry = ConnectorRegistry()

registry.register("manual", ManualConnector())

if settings.WEBHOOK_URL and settings.WEBHOOK_SECRET:
    registry.register(
        "webhook",
        WebhookConnector(
            settings.WEBHOOK_URL,
            settings.WEBHOOK_SECRET
        )
    )

if (
    settings.DISCOURSE_URL
    and settings.DISCOURSE_API_KEY
    and settings.DISCOURSE_USERNAME
):
    registry.register(
        "discourse",
        DiscourseConnector(
            settings.DISCOURSE_URL,
            settings.DISCOURSE_API_KEY,
            settings.DISCOURSE_USERNAME
        )
    )

if (
    settings.LEMMY_URL
    and settings.LEMMY_AUTH_TOKEN
    and settings.LEMMY_COMMUNITY_ID
):
    registry.register(
        "lemmy",
        LemmyConnector(
            settings.LEMMY_URL,
            settings.LEMMY_AUTH_TOKEN,
            int(settings.LEMMY_COMMUNITY_ID)
        )
    )

if settings.DEVTO_API_KEY:
    registry.register(
        "devto",
        DevToConnector(
            api_key=settings.DEVTO_API_KEY,
            base_url=settings.DEVTO_URL
        )
    )

if settings.GHOST_URL and settings.GHOST_ADMIN_API_KEY:
    registry.register(
        "ghost",
        GhostConnector(
            settings.GHOST_URL,
            settings.GHOST_ADMIN_API_KEY
        )
    )


# --------------------------------------------------
# PUBLISHING SERVICE
# --------------------------------------------------

service = PublishingService(
    registry,
    PostingRulesEngine(
        max_posts_per_day=3,
        max_links=5
    )
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class ContentRequest(BaseModel):
    platform: str
    title: str
    body: str

    tags: list[str] = Field(default_factory=list)

    ai_generated: bool = False
    ai_disclosure: bool = False

    is_self_promotion: bool = False
    self_promo_disclosure: bool = False

    dry_run: bool = True


# --------------------------------------------------
# REQUEST HASH
# --------------------------------------------------

def generate_request_hash(request_data: dict) -> str:

    # Normalize dictionary input using the request model.
    # This ensures default fields are included consistently.
    normalized_data = ContentRequest(
        **request_data
    ).model_dump()

    request_string = json.dumps(
        normalized_data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        request_string.encode("utf-8")
    ).hexdigest()


# --------------------------------------------------
# IDEMPOTENCY RESPONSE HELPERS
# --------------------------------------------------

def check_existing_sync_request(existing, request_hash):

    if existing.request_hash != request_hash:
        raise_api_error(
            409,
            "IDEMPOTENCY_KEY_REUSED",
            "Idempotency key already used with different content"
        )

    try:
        return json.loads(existing.response)

    except (TypeError, json.JSONDecodeError):
        raise_api_error(
            500,
            "INVALID_STORED_RESPONSE",
            "Could not read the stored publishing response"
        )


def check_existing_async_request(existing, request_hash):

    if existing.request_hash != request_hash:
        raise_api_error(
            409,
            "IDEMPOTENCY_KEY_REUSED",
            "Idempotency key already used with different content"
        )

    return {
        "job_id": existing.job_id,
        "status": existing.status,
        "message": "Duplicate request. Existing job returned."
    }


# --------------------------------------------------
# CONNECTOR LIST
# --------------------------------------------------

@router.get("/connectors")
def get_connectors():

    return {
        "connectors": registry.supported_platforms()
    }


# --------------------------------------------------
# SYNCHRONOUS PUBLISHING
# --------------------------------------------------

@router.post("/publish")
def publish_content(
    request: ContentRequest,
    db: Session = Depends(get_db),
    idempotency_key: str = Header(
        default=None,
        alias="Idempotency-Key"
    )
):

    key = idempotency_key or str(uuid.uuid4())

    request_data = request.model_dump()
    request_hash = generate_request_hash(request_data)

    try:

        existing = db.query(PublishingLog).filter(
            PublishingLog.idempotency_key == key
        ).first()

        if existing:
            return check_existing_sync_request(
                existing,
                request_hash
            )

        today_start = datetime.combine(
            datetime.now().date(),
            datetime_time.min
        )

        recent_posts = db.query(PublishingLog).filter(
            PublishingLog.platform == request.platform,
            PublishingLog.status == "success",
            PublishingLog.created_at >= today_start
        ).count()

        content = request.model_dump(
            exclude={"platform", "dry_run"}
        )

        result = service.publish(
            platform=request.platform,
            content=content,
            recent_posts=recent_posts,
            dry_run=request.dry_run
        )

        log = PublishingLog(
            idempotency_key=key,
            request_hash=request_hash,
            platform=request.platform,
            title=request.title,
            status=result.get("status", "unknown"),
            response=json.dumps(result)
        )

        db.add(log)
        db.commit()

        return result

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError:
        db.rollback()

        existing = db.query(PublishingLog).filter(
            PublishingLog.idempotency_key == key
        ).first()

        if existing:
            return check_existing_sync_request(
                existing,
                request_hash
            )

        raise_api_error(
            409,
            "DATABASE_CONFLICT",
            "Publishing request could not be saved because of a conflict"
        )

    except SQLAlchemyError:

        db.rollback()

        logger.exception(
            "Database error during synchronous publishing"
        )

        raise_api_error(
            500,
            "DATABASE_ERROR",
            "A database error occurred while processing the request"
        )


# --------------------------------------------------
# ASYNCHRONOUS PUBLISHING
# --------------------------------------------------

@router.post(
    "/publish/async",
    status_code=status.HTTP_202_ACCEPTED
)
def submit_background_job(
    request: ContentRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    db: Session = Depends(get_db),
    idempotency_key: str = Header(
        default=None,
        alias="Idempotency-Key"
    )
):

    key = idempotency_key or str(uuid.uuid4())

    request_data = request.model_dump()
    request_hash = generate_request_hash(request_data)

    try:

        existing = db.query(PublishingJob).filter(
            PublishingJob.idempotency_key == key
        ).first()

        if existing:

            result = check_existing_async_request(
                existing,
                request_hash
            )

            response.status_code = status.HTTP_200_OK

            return result

        job_id = str(uuid.uuid4())

        job = PublishingJob(
            job_id=job_id,
            idempotency_key=key,
            request_hash=request_hash,
            platform=request.platform,
            title=request.title,
            status="queued"
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        logger.info(
            "New publishing job created. Job ID=%s",
            job_id
        )

        background_tasks.add_task(
            process_publishing_job,
            job_id,
            request_data
        )

        return {
            "message": "Publishing job submitted",
            "job_id": job_id,
            "status": "queued"
        }

    except HTTPException:
        db.rollback()
        raise

    except IntegrityError:

        db.rollback()

        existing = db.query(PublishingJob).filter(
            PublishingJob.idempotency_key == key
        ).first()

        if existing:

            result = check_existing_async_request(
                existing,
                request_hash
            )

            response.status_code = status.HTTP_200_OK

            return result

        raise_api_error(
            409,
            "DATABASE_CONFLICT",
            "Publishing job could not be created because of a conflict"
        )

    except SQLAlchemyError:

        db.rollback()

        logger.exception(
            "Database error while creating publishing job"
        )

        raise_api_error(
            500,
            "DATABASE_ERROR",
            "A database error occurred while creating the publishing job"
        )


# --------------------------------------------------
# JOB STATUS
# --------------------------------------------------

@router.get("/jobs/{job_id}")
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):

    try:

        job = db.query(PublishingJob).filter(
            PublishingJob.job_id == job_id
        ).first()

        if not job:
            raise_api_error(
                404,
                "JOB_NOT_FOUND",
                "Publishing job not found"
            )

        try:
            result = json.loads(job.result) if job.result else None

        except (TypeError, json.JSONDecodeError):
            result = None

        return {
            "job_id": job.job_id,
            "platform": job.platform,
            "title": job.title,
            "status": job.status,
            "retry_count": job.retry_count,
            "result": result,
            "created_at": job.created_at
        }

    except HTTPException:
        raise

    except SQLAlchemyError:

        logger.exception(
            "Database error while retrieving job status"
        )

        raise_api_error(
            500,
            "DATABASE_ERROR",
            "A database error occurred while retrieving job status"
        )


# --------------------------------------------------
# STORAGE - UPLOAD FILE
# --------------------------------------------------

@router.post("/storage/upload")
def upload_storage_file(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise_api_error(
            400,
            "INVALID_FILENAME",
            "A valid filename is required"
        )

    original_filename = Path(file.filename).name

    object_name = (
        f"uploads/{uuid.uuid4()}_{original_filename}"
    )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False
        ) as temp_file:

            temp_path = temp_file.name

            shutil.copyfileobj(
                file.file,
                temp_file
            )

        result = storage.upload_file(
            object_name,
            temp_path
        )

        logger.info(
            "File uploaded successfully: %s",
            object_name
        )

        return {
            "status": "success",
            "message": "File uploaded successfully",
            "filename": original_filename,
            "object_name": object_name,
            "storage": result
        }

    except Exception:

        logger.exception("Storage upload failed")

        raise_api_error(
            500,
            "STORAGE_UPLOAD_FAILED",
            "Could not upload the file"
        )

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        file.file.close()


# --------------------------------------------------
# STORAGE - LIST FILES
# --------------------------------------------------

@router.get("/storage/files")
def list_storage_files():

    try:

        files = storage.list_files()

        return {
            "status": "success",
            "total_files": len(files),
            "files": files
        }

    except Exception:

        logger.exception("Storage listing failed")

        raise_api_error(
            500,
            "STORAGE_LIST_FAILED",
            "Could not retrieve stored files"
        )
