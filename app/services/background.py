
import json
import time
import logging

from datetime import datetime, time as datetime_time

import httpx

from app.database.connection import SessionLocal
from app.models.publishing_job import PublishingJob
from app.models.publishing_log import PublishingLog

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


def is_retryable_error(result: dict) -> bool:
    """
    Check whether a publishing failure is temporary
    and can be retried.
    """

    message = result.get("message", "").lower()

    retryable_status_codes = [408, 429, 500, 502, 503, 504]

    if result.get("status_code") in retryable_status_codes:
        return True

    retryable_messages = [
        "timeout",
        "connection",
        "network",
        "temporary",
        "temporarily unavailable",
        "request failed"
    ]

    return any(word in message for word in retryable_messages)


def process_publishing_job(job_id: str, request_data: dict):
    """
    Process a queued publishing job with retry support.
    """

    db = SessionLocal()

    try:
        job = db.query(PublishingJob).filter(
            PublishingJob.job_id == job_id
        ).first()

        if not job:
            logger.error("Publishing job not found: %s", job_id)
            return

        from app.api.routes import service

        content = {
            "title": request_data["title"],
            "body": request_data["body"],
            "tags": request_data.get("tags", []),
            "ai_generated": request_data.get("ai_generated", False),
            "ai_disclosure": request_data.get("ai_disclosure", False),
            "is_self_promotion": request_data.get("is_self_promotion", False),
            "self_promo_disclosure": request_data.get(
                "self_promo_disclosure", False
            )
        }

        final_result = None

        for attempt in range(MAX_RETRIES + 1):

            job.status = "processing"
            job.retry_count = attempt
            db.commit()

            try:
                today_start = datetime.combine(
                    datetime.now().date(),
                    datetime_time.min
                )

                recent_posts = db.query(PublishingLog).filter(
                    PublishingLog.platform == request_data["platform"],
                    PublishingLog.status == "success",
                    PublishingLog.created_at >= today_start
                ).count()

                result = service.publish(
                    platform=request_data["platform"],
                    content=content,
                    recent_posts=recent_posts,
                    dry_run=request_data.get("dry_run", True)
                )

                if result.get("status") == "failed":

                    if (
                        is_retryable_error(result)
                        and attempt < MAX_RETRIES
                    ):
                        delay = 2 ** attempt

                        logger.warning(
                            "Retrying job %s after %s seconds",
                            job_id,
                            delay
                        )

                        time.sleep(delay)
                        continue

                final_result = result
                break

            except (
                httpx.TimeoutException,
                httpx.NetworkError
            ) as error:

                logger.warning(
                    "Temporary network error for job %s: %s",
                    job_id,
                    str(error)
                )

                if attempt < MAX_RETRIES:
                    delay = 2 ** attempt
                    time.sleep(delay)
                    continue

                final_result = {
                    "status": "failed",
                    "message": "Network error after maximum retries"
                }

            except Exception:

                logger.exception(
                    "Unexpected error while processing job %s",
                    job_id
                )

                final_result = {
                    "status": "failed",
                    "message": "Unexpected publishing error"
                }

                break

        if final_result is None:
            final_result = {
                "status": "failed",
                "message": "Publishing failed after maximum retries"
            }

        job.status = final_result.get("status", "failed")
        job.result = json.dumps(final_result)

        log = PublishingLog(
            idempotency_key=f"async-log-{job_id}",
            request_hash=None,
            platform=request_data["platform"],
            title=request_data["title"],
            status=final_result.get("status", "unknown"),
            response=json.dumps(final_result)
        )

        db.add(log)
        db.commit()

        logger.info(
            "Publishing job completed. Job ID=%s Status=%s Retries=%s",
            job_id,
            job.status,
            job.retry_count
        )

    except Exception:

        db.rollback()

        logger.exception(
            "Failed to process publishing job: %s",
            job_id
        )

        job = db.query(PublishingJob).filter(
            PublishingJob.job_id == job_id
        ).first()

        if job:
            job.status = "failed"
            job.result = json.dumps({
                "status": "failed",
                "message": "Job processing failed due to an internal error"
            })

            db.commit()

    finally:
        db.close()
