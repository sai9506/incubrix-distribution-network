
from unittest.mock import MagicMock, patch

from app.services import background


def create_fake_job(job_id):
    fake_job = MagicMock()
    fake_job.job_id = job_id

    fake_db = MagicMock()
    fake_db.query.return_value.filter.return_value.first.return_value = fake_job
    fake_db.query.return_value.filter.return_value.count.return_value = 0

    return fake_job, fake_db


def test_background_job_retries_failed_publish():

    fake_job, fake_db = create_fake_job("test-job-001")

    failed_result = {
        "status": "failed",
        "message": "Temporary publishing failure"
    }

    success_result = {
        "status": "success",
        "message": "Published successfully"
    }

    with patch.object(
        background,
        "SessionLocal",
        return_value=fake_db
    ), patch(
        "app.api.routes.service.publish",
        side_effect=[failed_result, success_result]
    ) as mock_publish, patch.object(
        background.time,
        "sleep"
    ):

        background.process_publishing_job(
            "test-job-001",
            {
                "platform": "manual",
                "title": "Retry Test",
                "body": "Testing retry mechanism",
                "dry_run": False
            }
        )

    assert mock_publish.call_count == 2
    assert fake_job.status == "success"
    assert fake_job.retry_count == 1
    fake_db.close.assert_called_once()


def test_background_job_maximum_retries():

    fake_job, fake_db = create_fake_job("test-job-002")

    failed_result = {
        "status": "failed",
        "message": "Temporary network failure"
    }

    with patch.object(
        background,
        "SessionLocal",
        return_value=fake_db
    ), patch(
        "app.api.routes.service.publish",
        return_value=failed_result
    ) as mock_publish, patch.object(
        background.time,
        "sleep"
    ):

        background.process_publishing_job(
            "test-job-002",
            {
                "platform": "manual",
                "title": "Maximum Retry Test",
                "body": "Testing maximum retries",
                "dry_run": False
            }
        )

    assert mock_publish.call_count == 4
    assert fake_job.status == "failed"
    assert fake_job.retry_count == 3
    fake_db.close.assert_called_once()


def test_permanent_failure_is_not_retried():

    fake_job, fake_db = create_fake_job("test-job-003")

    failed_result = {
        "status": "failed",
        "message": "Invalid connector configuration"
    }

    with patch.object(
        background,
        "SessionLocal",
        return_value=fake_db
    ), patch(
        "app.api.routes.service.publish",
        return_value=failed_result
    ) as mock_publish, patch.object(
        background.time,
        "sleep"
    ):

        background.process_publishing_job(
            "test-job-003",
            {
                "platform": "manual",
                "title": "Permanent Failure Test",
                "body": "Testing permanent failure",
                "dry_run": False
            }
        )

    assert mock_publish.call_count == 1
    assert fake_job.status == "failed"
    assert fake_job.retry_count == 0
    fake_db.close.assert_called_once()
