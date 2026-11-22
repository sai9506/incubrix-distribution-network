
from minio import Minio
from minio.error import S3Error

from app.config import settings


class ObjectStorage:

    def __init__(self):
        self.enabled = bool(
            settings.MINIO_ENDPOINT
            and settings.MINIO_ROOT_USER
            and settings.MINIO_ROOT_PASSWORD
        )

        self.bucket = settings.MINIO_BUCKET
        self.client = None

        if self.enabled:
            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ROOT_USER,
                secret_key=settings.MINIO_ROOT_PASSWORD,
                secure=settings.MINIO_SECURE
            )

    def _check_enabled(self):
        if not self.enabled:
            raise RuntimeError("Object storage is not configured")

    def create_bucket(self):
        self._check_enabled()

        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)

            return {
                "status": "success",
                "bucket": self.bucket,
                "message": "Bucket is ready"
            }
        except S3Error:
            raise

    def upload_file(self, object_name: str, file_path: str):
        self._check_enabled()

        try:
            result = self.client.fput_object(
                self.bucket,
                object_name,
                file_path
            )

            return {
                "status": "success",
                "bucket": self.bucket,
                "object_name": object_name,
                "etag": result.etag
            }
        except S3Error:
            raise

    def download_file(self, object_name: str, file_path: str):
        self._check_enabled()

        try:
            self.client.fget_object(
                self.bucket,
                object_name,
                file_path
            )

            return {
                "status": "success",
                "object_name": object_name,
                "download_path": file_path
            }
        except S3Error:
            raise

    def list_files(self):
        self._check_enabled()

        try:
            objects = self.client.list_objects(
                self.bucket,
                recursive=True
            )

            return [
                {
                    "name": obj.object_name,
                    "size": obj.size,
                    "etag": obj.etag
                }
                for obj in objects
            ]
        except S3Error:
            raise


storage = ObjectStorage()
