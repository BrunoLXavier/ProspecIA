from typing import Any, Dict, List, Optional

import pytest
from fastapi import FastAPI, Depends, Request
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

from app.interfaces.http.routers import model_config as mc_router


class FakeSession:
    async def execute(self, *args, **kwargs):
        class _Result:
            def first(self):
                return (1,)
        return _Result()


class FakeRepo:
    def __init__(self, session=None):
        self.session = session
        if not hasattr(self.__class__, 'store'):
            self.__class__.store = {
                'Ingestao': [
                    {
                        'id': '1',
                        'model_name': 'Ingestao',
                        'field_name': 'nome',
                        'field_type': 'string',
                        'label_key': 'ingestion.field.nome',
                        'validators': { 'min_length': 1 },
                        'visibility_rule': 'all',
                        'required': True,
                        'default_value': None,
                        'description': 'Nome da ingestão',
                        'created_at': None,
                        'updated_at': None,
                        'created_by': None,
                    }
                ]
            }

    async def list_by_model(self, session, model_name: str) -> List[Dict[str, Any]]:
        return list(self.__class__.store.get(model_name, []))

    async def update_field(self, session, model_name: str, field_name: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rows = self.__class__.store.get(model_name, [])
        for r in rows:
            if r['field_name'] == field_name:
                r.update(updates)
                return dict(r)
        return None


def fake_get_session():
    return FakeSession()


def fake_current_user():
    return {
        "id": "test-user",
        "username": "test-user",
        "roles": ["admin"],
        "tenant_id": "test-tenant",
    }


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(mc_router, 'ModelFieldConfigRepository', FakeRepo)

    # Middleware to inject mock user into request state
    class MockAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            request.state.user = fake_current_user()
            return await call_next(request)

    fastapi_app = FastAPI()
    fastapi_app.add_middleware(MockAuthMiddleware)
    fastapi_app.dependency_overrides[mc_router.get_session] = lambda: fake_get_session()
    fastapi_app.include_router(mc_router.router, prefix='/system')
    return fastapi_app


def test_list_model_configs(app):
    client = TestClient(app)
    resp = client.get('/system/model-configs/Ingestao')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list) and len(data) == 1
    assert data[0]['field_name'] == 'nome'


def test_patch_model_config(app):
    client = TestClient(app)
    resp = client.patch('/system/model-configs/Ingestao/nome', json={'label_key': 'ingestion.field.name.en'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['label_key'] == 'ingestion.field.name.en'
