import uuid
from typing import Any, Dict, List, Optional

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.interfaces.http.routers import ingestao as ingestao_router
from app.domain.models.ingestao import Ingestao, IngestionSource, IngestionMethod, IngestionStatus


class FakeSession:
    async def flush(self):
        return None
    
    async def commit(self):
        return None


class FakeIngestaoRepository:
    def __init__(self, session):
        self.session = session
        # shared store per test module
        if not hasattr(self.__class__, "store"):
            self.__class__.store = {}
    async def create(self, ingestao: Ingestao, usuario_id: str, ip_cliente: Optional[str] = None):
        self.__class__.store[str(ingestao.id)] = ingestao
        return ingestao
    async def get_by_id(self, ingestao_id: str, tenant_id: Optional[str] = None):
        return self.__class__.store.get(str(ingestao_id))
    async def list_with_filters(self, tenant_id: Optional[str] = None, offset: int = 0, limit: int = 50, **filters):
        items = list(self.__class__.store.values())
        return items, len(items)
    async def update_status(self, ingestao: Ingestao, new_status: str, usuario_id: str, motivo: str = None, ip_cliente: Optional[str] = None):
        if ingestao:
            ingestao.status = new_status
        return ingestao


class FakeConsentimentoRepository:
    def __init__(self, session):
        self.session = session
    async def get_by_id(self, consentimento_id, tenant_id: Optional[str] = None):
        return None


class FakeLGPD:
    async def process_ingestao(self, text_content: str, consentimento_id, titular_id, finalidade, ingestao_id, repository):
        return {
            "pii_detected": {"cpf": [], "email": []},
            "masked_data": {"actions_taken": []},
            "consent_validation": {"valid": False},
            "compliance_score": 90,
        }


def fake_get_lgpd_agent():
    return FakeLGPD()


def fake_get_minio_client():
    class Stub:
        def upload_bytes(self, object_name, data, content_type=None):
            self.last = (object_name, data, content_type)
            return object_name
        def read_sample_text(self, object_name, max_bytes=2048):
            return "sample"
        def presigned_get_url(self, object_name, expiry_minutes=60):
            return f"http://minio/{object_name}?exp={expiry_minutes}"
    return Stub()


def fake_neo4j_conn():
    class Stub:
        async def create_lineage_node(self, *args, **kwargs):
            return None
        async def get_lineage_path(self, *args, **kwargs):
            return []
    return Stub()


def fake_current_user():
    return {"id": str(uuid.uuid4()), "sub": str(uuid.uuid4()), "tenant_id": "nacional", "roles": ["admin"]}


def fake_require_roles(*roles: str):
    async def checker():
        return True
    return checker


def fake_get_session():
    return FakeSession()


@pytest.fixture
def app(monkeypatch):
    from starlette.middleware.base import BaseHTTPMiddleware
    from fastapi import Request
    
    monkeypatch.setattr(ingestao_router, "IngestaoRepository", FakeIngestaoRepository)
    monkeypatch.setattr(ingestao_router, "ConsentimentoRepository", FakeConsentimentoRepository)
    monkeypatch.setattr(ingestao_router, "get_lgpd_agent", fake_get_lgpd_agent)
    monkeypatch.setattr(ingestao_router, "get_minio_client", fake_get_minio_client)
    monkeypatch.setattr(ingestao_router, "get_neo4j_connection", fake_neo4j_conn)
    monkeypatch.setattr(ingestao_router, "require_roles", fake_require_roles)

    # Middleware to inject mock user into request state
    class MockAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            request.state.user = fake_current_user()
            return await call_next(request)

    fastapi_app = FastAPI()
    fastapi_app.add_middleware(MockAuthMiddleware)
    fastapi_app.dependency_overrides[ingestao_router.get_session] = lambda: fake_get_session()
    fastapi_app.include_router(ingestao_router.router)
    return fastapi_app


def test_post_ingestao_and_list(app):
    client = TestClient(app)
    files = {"file": ("sample.txt", b"hello", "text/plain")}
    params = {"fonte": IngestionSource.RAIS.value, "metodo": IngestionMethod.BATCH_UPLOAD.value}

    resp = client.post("/ingestions", files=files, params=params)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == IngestionStatus.CONCLUIDA.value
    ingestao_id = data["id"]

    list_resp = client.get("/ingestions")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    dl_resp = client.get(f"/ingestions/{ingestao_id}/download")
    assert dl_resp.status_code == 200
    assert "url" in dl_resp.json()
