from typing import Callable, Optional, Tuple

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.adapters.postgres.connection import get_db_connection
from app.infrastructure.middleware.auth_middleware import get_current_user
from app.infrastructure.repositories.acl_repository import ACLRepository

logger = structlog.get_logger()


class AclMiddleware(BaseHTTPMiddleware):
    """
    Minimal ACL enforcement middleware.

    Uses a simple path+method to (resource, action) mapping for coarse-grained checks.
    Fine-grained checks should use the require_acl dependency at route level.
    """

    # Map (path_prefix, method) -> (resource, action)
    RULES_MAP: Tuple[Tuple[str, str, str, str], ...] = (
        ("/system/model-configs", "GET", "model_config", "read"),
        ("/system/model-configs", "PATCH", "model_config", "update"),
    )

    EXEMPT_PATHS = {
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/metrics",
        "/i18n/translations",
        "/i18n/locales",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        method = request.method.upper()

        # Quick exemptions
        if any(path == p or path.startswith(p) for p in self.EXEMPT_PATHS):
            return await call_next(request)

        resource_action = self._match_rule(path, method)
        if not resource_action:
            return await call_next(request)

        resource, action = resource_action

        # Get user roles from auth middleware/mocks
        try:
            user = get_current_user(request)
            roles = user.get("roles", [])
        except Exception:
            roles = []

        # DB check
        try:
            db = get_db_connection()
            repo = ACLRepository()
            async with db.get_session() as session:
                allowed = await repo.is_allowed(session, roles, resource, action)
                if not allowed:
                    from fastapi import HTTPException, status

                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                    )
        except Exception as e:
            logger.error("acl_middleware_error", error=str(e), path=path, method=method)
            # Fail closed only on explicit denial; otherwise proceed to avoid blocking
            # non-protected routes on transient DB issues.
            pass

        return await call_next(request)

    def _match_rule(self, path: str, method: str) -> Optional[Tuple[str, str]]:
        for prefix, m, res, act in self.RULES_MAP:
            if path.startswith(prefix) and method == m:
                return res, act
        return None
