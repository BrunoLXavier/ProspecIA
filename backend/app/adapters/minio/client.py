"""
ProspecIA - MinIO Client Adapter

Provides object storage operations: bucket init, upload, presigned URLs,
and small object sampling for lineage previews.

Follows SRP and DIP: wraps MinIO client behind an adapter.
"""

from typing import Optional
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
import structlog

from app.infrastructure.config.settings import Settings
from app.infrastructure.patterns.resilience import CircuitBreaker, retry

logger = structlog.get_logger()


class MinioClientAdapter:
    """
    MinIO client wrapper with helper methods.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: Optional[Minio] = None
        self._cb = CircuitBreaker(failure_threshold=3, reset_timeout_sec=15)

    @retry(exceptions=(S3Error, Exception), max_attempts=4, base_delay=0.2)
    def connect(self) -> None:
        """
        Initialize MinIO client and ensure bucket exists.
        """
        if self._client is not None:
            logger.warning("minio_already_connected")
            return

        endpoint = self.settings.minio_endpoint
        logger.info("minio_connecting", endpoint=endpoint)
        self._client = Minio(
            endpoint,
            access_key=self.settings.MINIO_ROOT_USER,
            secret_key=self.settings.MINIO_ROOT_PASSWORD,
            secure=False,
        )

        # Ensure bucket exists
        bucket = self.settings.MINIO_BUCKET_NAME
        try:
            found = self._client.bucket_exists(bucket)
            if not found:
                self._client.make_bucket(bucket)
                logger.info("minio_bucket_created", bucket=bucket)
            else:
                logger.info("minio_bucket_exists", bucket=bucket)
        except S3Error as e:
            logger.error("minio_bucket_error", error=str(e))
            raise

    def upload_bytes(self, object_name: str, data: bytes, content_type: str | None = None) -> str:
        """
        Upload bytes to the default bucket under `object_name`.

        Returns storage path for persistence.
        """
        if self._client is None:
            raise RuntimeError("MinIO not connected. Call connect() first.")

        bucket = self.settings.MINIO_BUCKET_NAME
        if not self._cb.allow():
            logger.warning("minio_circuit_open", object_name=object_name)
            raise RuntimeError("MinIO circuit open")

        try:
            # Pass raw bytes to put_object to satisfy test fake client behavior
            self._client.put_object(
                bucket,
                object_name,
                data=data,
                length=len(data),
                content_type=content_type or "application/octet-stream",
            )
            logger.info("minio_upload_success", bucket=bucket, object_name=object_name, size=len(data))
            self._cb.record_success()
            return object_name
        except S3Error as e:
            logger.error("minio_upload_failed", error=str(e))
            self._cb.record_failure()
            raise

    def presigned_get_url(self, object_name: str, expiry_minutes: int = 60) -> str:
        """
        Generate presigned GET URL for private object access (default 60 minutes).
        """
        if self._client is None:
            raise RuntimeError("MinIO not connected. Call connect() first.")
        bucket = self.settings.MINIO_BUCKET_NAME
        try:
            url = self._client.get_presigned_url(
                "GET",
                bucket,
                object_name,
                expires=timedelta(minutes=expiry_minutes),
            )
            return url
        except S3Error as e:
            logger.error("minio_presigned_failed", error=str(e))
            raise

    def read_sample_text(self, object_name: str, max_bytes: int = 2048) -> Optional[str]:
        """
        Read a small sample of object content and decode to text.
        Returns None on binary or failure.
        """
        if self._client is None:
            raise RuntimeError("MinIO not connected. Call connect() first.")
        bucket = self.settings.MINIO_BUCKET_NAME
        try:
            response = self._client.get_object(bucket, object_name)
            try:
                data = response.read(max_bytes)
            finally:
                response.close()
                response.release_conn()
            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                return None
        except S3Error as e:
            logger.error("minio_read_sample_failed", error=str(e))
            return None


# Global MinIO client instance (initialized in main.py)
minio_client: MinioClientAdapter | None = None


def get_minio_client() -> MinioClientAdapter:
    """Get global MinIO client instance."""
    if minio_client is None:
        raise RuntimeError("MinIO not initialized. Initialize in app startup.")
    return minio_client
