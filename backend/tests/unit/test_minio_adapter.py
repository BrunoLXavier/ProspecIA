import pytest

from app.adapters.minio import client as minio_cli


class FakeResponse:
    def __init__(self, data: bytes):
        self._data = data
    def read(self, max_bytes: int):
        return self._data[:max_bytes]
    def close(self):
        return None
    def release_conn(self):
        return None


class FakeMinio:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.bucket_created = False
        self.objects: dict[str, bytes] = {}
    def bucket_exists(self, bucket: str) -> bool:
        return self.bucket_created
    def make_bucket(self, bucket: str):
        self.bucket_created = True
    def put_object(self, bucket: str, object_name: str, data: bytes, length: int, content_type: str):
        self.objects[object_name] = data if isinstance(data, (bytes, bytearray)) else bytes(data)
    def get_presigned_url(self, method: str, bucket: str, object_name: str, expires):
        return f"http://{self.endpoint}/{bucket}/{object_name}?exp={int(expires.total_seconds())}"
    def get_object(self, bucket: str, object_name: str):
        return FakeResponse(self.objects.get(object_name, b""))


class DummySettings:
    MINIO_HOST = "localhost"
    MINIO_PORT = 9000
    MINIO_ROOT_USER = "user"
    MINIO_ROOT_PASSWORD = "pass"
    MINIO_BUCKET_NAME = "test-bucket"

    @property
    def minio_endpoint(self) -> str:
        return f"{self.MINIO_HOST}:{self.MINIO_PORT}"


def test_minio_adapter_upload_and_presign(monkeypatch):
    monkeypatch.setattr(minio_cli, "Minio", FakeMinio)
    adapter = minio_cli.MinioClientAdapter(DummySettings())

    adapter.connect()
    stored_path = adapter.upload_bytes("ingestoes/1.txt", b"hello world", content_type="text/plain")
    assert stored_path == "ingestoes/1.txt"

    url = adapter.presigned_get_url(stored_path, expiry_minutes=60)
    assert "ingestoes/1.txt" in url
    assert "exp=" in url

    sample = adapter.read_sample_text(stored_path, max_bytes=1024)
    assert sample == "hello world"
