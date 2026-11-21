
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_storage_upload_success():

    mock_result = {
        "status": "success",
        "bucket": "incubrix-assets",
        "object_name": "uploads/sample.txt",
        "etag": "test-etag"
    }

    with patch(
        "app.api.routes.storage.upload_file",
        return_value=mock_result
    ):

        response = client.post(
            "/api/v1/storage/upload",
            files={
                "file": (
                    "sample.txt",
                    b"This is a storage test file.",
                    "text/plain"
                )
            }
        )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["filename"] == "sample.txt"


def test_storage_list_success():

    mock_files = [
        {
            "name": "uploads/sample.txt",
            "size": 28,
            "etag": "test-etag"
        }
    ]

    with patch(
        "app.api.routes.storage.list_files",
        return_value=mock_files
    ):

        response = client.get(
            "/api/v1/storage/files"
        )

    assert response.status_code == 200
    assert response.json()["total_files"] == 1
    assert response.json()["files"][0]["name"] == "uploads/sample.txt"
