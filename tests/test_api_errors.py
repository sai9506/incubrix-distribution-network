
import json

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import get_db
from app.api.routes import generate_request_hash


client = TestClient(app)


def create_fake_db():
    return MagicMock()


def test_invalid_job_returns_404():

    fake_db = create_fake_db()

    fake_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        response = client.get("/api/v1/jobs/invalid-job-id")

        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "JOB_NOT_FOUND"

    finally:
        app.dependency_overrides.clear()


def test_idempotency_conflict_returns_409():

    fake_db = create_fake_db()

    existing_log = MagicMock()
    existing_log.request_hash = "old-request-hash"

    fake_db.query.return_value.filter.return_value.first.return_value = existing_log

    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        response = client.post(
            "/api/v1/publish",
            headers={"Idempotency-Key": "test-conflict-001"},
            json={
                "platform": "manual",
                "title": "Changed title",
                "body": "Testing idempotency conflict",
                "dry_run": True
            }
        )

        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "IDEMPOTENCY_KEY_REUSED"

    finally:
        app.dependency_overrides.clear()


def test_async_publish_returns_202():

    fake_db = create_fake_db()

    fake_db.query.return_value.filter.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        with patch("app.api.routes.process_publishing_job"):
            response = client.post(
                "/api/v1/publish/async",
                headers={"Idempotency-Key": "test-async-001"},
                json={
                    "platform": "manual",
                    "title": "Async Test",
                    "body": "Testing asynchronous publishing",
                    "dry_run": True
                }
            )

        assert response.status_code == 202
        assert response.json()["status"] == "queued"
        assert "job_id" in response.json()

    finally:
        app.dependency_overrides.clear()


def test_duplicate_sync_request_returns_existing_response():

    fake_db = create_fake_db()

    request_data = {
        "platform": "manual",
        "title": "Duplicate Test",
        "body": "Testing duplicate synchronous request",
        "dry_run": True
    }

    existing_log = MagicMock()
    existing_log.request_hash = generate_request_hash(request_data)
    existing_log.response = json.dumps({
        "status": "preview",
        "message": "Original response"
    })

    fake_db.query.return_value.filter.return_value.first.return_value = existing_log

    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        response = client.post(
            "/api/v1/publish",
            headers={"Idempotency-Key": "test-sync-duplicate-001"},
            json=request_data
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Original response"

    finally:
        app.dependency_overrides.clear()


def test_duplicate_async_request_returns_existing_job():

    fake_db = create_fake_db()

    request_data = {
        "platform": "manual",
        "title": "Duplicate Async Test",
        "body": "Testing duplicate asynchronous request",
        "dry_run": True
    }

    existing_job = MagicMock()
    existing_job.job_id = "existing-job-001"
    existing_job.status = "queued"
    existing_job.request_hash = generate_request_hash(request_data)

    fake_db.query.return_value.filter.return_value.first.return_value = existing_job

    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        with patch("app.api.routes.process_publishing_job") as mock_task:

            response = client.post(
                "/api/v1/publish/async",
                headers={"Idempotency-Key": "test-async-duplicate-001"},
                json=request_data
            )

        assert response.status_code == 200
        assert response.json()["job_id"] == "existing-job-001"
        assert response.json()["status"] == "queued"
        mock_task.assert_not_called()

    finally:
        app.dependency_overrides.clear()
