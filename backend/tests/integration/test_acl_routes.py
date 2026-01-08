from typing import Any, Dict, List

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.interfaces.http.routers import acl as acl_router


class AuthenticatedTestClient(TestClient):
    """Test client that injects a mock authenticated user into requests."""
    
    def request(self, *args, **kwargs):
        """Override to inject user into request state."""
        response = super().request(*args, **kwargs)
        return response
    
    def __call__(self, *args, **kwargs):
        """Make requests with mock user credentials."""
        # Add mock auth header
        kwargs.setdefault("headers", {})
        # While we don't process this header, having it signals an authenticated request
        kwargs["headers"]["Authorization"] = "Bearer mock-token"
        return super().__call__(*args, **kwargs)


class FakeSession:
    async def execute(self, *args, **kwargs):
        class _Result:
            def first(self):
                return (1,)
        return _Result()


class FakeACLRepo:
    def __init__(self, session=None):
        self.session = session
        if not hasattr(self.__class__, 'rules'):
            self.__class__.rules = []

    async def list_rules(self, session) -> List[Dict[str, Any]]:
        return list(self.__class__.rules)

    async def create_rule(self, session, data: Dict[str, Any]) -> Dict[str, Any]:
        item = {
            'id': str(len(self.__class__.rules) + 1),
            'role': data['role'],
            'resource': data['resource'],
            'action': data['action'],
            'condition': data.get('condition'),
            'description': data.get('description'),
        }
        self.__class__.rules.append(item)
        return dict(item)

    async def update_rule(self, session, rule_id: str, data: Dict[str, Any]):
        for r in self.__class__.rules:
            if r['id'] == rule_id:
                r.update(data)
                return dict(r)
        return None

    async def delete_rule(self, session, rule_id: str) -> bool:
        before = len(self.__class__.rules)
        self.__class__.rules = [r for r in self.__class__.rules if r['id'] != rule_id]
        return len(self.__class__.rules) < before

    async def is_allowed(self, session, roles: List[str], resource: str, action: str) -> bool:
        # Allow if there is a rule matching any role
        for r in self.__class__.rules:
            if r['resource'] == resource and r['action'] == action and r['role'] in roles:
                return True
        return False


def fake_require_roles(*roles: str):
    async def checker():
        return True
    return checker


def fake_get_session():
    return FakeSession()


@pytest.fixture
def app(monkeypatch):
    from app.infrastructure.middleware.auth_middleware import get_current_user
    from app.interfaces.http.routers import acl as acl_router
    from starlette.middleware.base import BaseHTTPMiddleware
    from fastapi import Request
    
    # Middleware to inject mock user into request state
    class MockAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            request.state.user = {
                "id": "test-user",
                "username": "test-user",
                "roles": ["admin"],
                "tenant_id": "test-tenant",
            }
            return await call_next(request)
    
    # Create the app
    fastapi_app = FastAPI()
    
    # Add middleware to inject mock user
    fastapi_app.add_middleware(MockAuthMiddleware)
    
    # Set up dependency overrides
    fastapi_app.dependency_overrides[acl_router.get_session] = lambda: fake_get_session()
    
    # Patch the repository
    monkeypatch.setattr(acl_router, 'ACLRepository', FakeACLRepo)
    
    # Include the router
    fastapi_app.include_router(acl_router.router, prefix='/system')
    return fastapi_app


def test_acl_crud_and_check(app):
    client = TestClient(app)
    # Initially empty
    r = client.get('/system/acl/rules')
    assert r.status_code == 200 and r.json() == []

    # Create a rule
    r = client.post('/system/acl/rules', json={'role': 'admin', 'resource': 'model_config', 'action': 'read'})
    assert r.status_code == 201

    # List has 1
    r = client.get('/system/acl/rules')
    assert r.status_code == 200 and len(r.json()) == 1

    # Update rule
    rule_id = r.json()[0]['id']
    r = client.patch(f'/system/acl/rules/{rule_id}', json={'description': 'allow admin'})
    assert r.status_code == 200 and r.json()['description'] == 'allow admin'

    # Check endpoint (without actual user/roles, expect default False)
    r = client.get('/system/acl/check?resource=model_config&action=read')
    assert r.status_code == 200 and 'allowed' in r.json()

    # Delete
    r = client.delete(f'/system/acl/rules/{rule_id}')
    assert r.status_code == 204
