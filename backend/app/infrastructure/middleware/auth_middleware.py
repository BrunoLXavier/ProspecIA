"""
ProspecIA - Authentication Middleware

JWT authentication middleware with Keycloak integration.
Validates tokens, extracts user claims, and manages authentication context.
"""

from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
import jwt
from jwt import PyJWKClient
from datetime import datetime, timedelta

logger = structlog.get_logger()


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT authentication validation with Keycloak.
    
    Responsibilities (SRP):
    - Validate JWT tokens against Keycloak JWKS
    - Extract user information (sub, email, roles, tenant)
    - Handle authentication errors with proper logging
    - Cache JWKS for performance
    
    Exempt paths (public routes that don't require authentication):
    - /health, /docs, /openapi.json, /metrics
    """
    
    # Public paths that don't require authentication
    EXEMPT_PATHS = {
        "/",
        "/health",
        "/health/ready",
        "/health/live",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/metrics",
    }
    
    def __init__(self, app, settings):
        """
        Initialize authentication middleware.
        
        Args:
            app: FastAPI application instance
            settings: Application settings with Keycloak configuration
        """
        super().__init__(app)
        self.settings = settings
        self._jwks_client: Optional[PyJWKClient] = None
        
    @property
    def jwks_client(self) -> PyJWKClient:
        """Lazy-loaded JWKS client with connection pooling and caching."""
        if self._jwks_client is None:
            jwks_url = (
                f"{self.settings.keycloak_url}/realms/{self.settings.KEYCLOAK_REALM}"
                f"/protocol/openid-connect/certs"
            )
            self._jwks_client = PyJWKClient(
                jwks_url,
                cache_keys=True,
                max_cached_keys=10,
                cache_jwk_set=True,
                lifespan=3600,  # Cache for 1 hour
            )
        return self._jwks_client
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process HTTP request with authentication.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            Response: HTTP response
            
        Raises:
            HTTPException: If authentication fails
        """
        # Check if JWT is required (feature flag)
        if not self.settings.FEATURE_JWT_REQUIRED:
            # Development mode: use mock user
            request.state.user = self._get_mock_user()
            return await call_next(request)
        
        # Check if path is exempt from authentication
        if request.url.path in self.EXEMPT_PATHS or request.url.path.startswith("/docs"):
            return await call_next(request)
        
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            logger.warning(
                "authentication_missing",
                path=request.url.path,
                method=request.method,
                ip=request.client.host if request.client else "unknown",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate Bearer token format
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            logger.warning(
                "authentication_invalid_format",
                path=request.url.path,
                method=request.method,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication format. Expected: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate JWT token with Keycloak
        try:
            user_info = await self._validate_token(token)
            request.state.user = user_info
            
            logger.debug(
                "authentication_success",
                path=request.url.path,
                user_id=user_info["id"],
                username=user_info["username"],
                roles=user_info["roles"],
            )
            
        except jwt.ExpiredSignatureError:
            logger.warning(
                "authentication_token_expired",
                path=request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            logger.warning(
                "authentication_token_invalid",
                path=request.url.path,
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(
                "authentication_unexpected_error",
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error",
            )
        
        return await call_next(request)
    
    async def _validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token with Keycloak and extract user information.
        
        Args:
            token: JWT token string
            
        Returns:
            Dict containing user information:
                - id: User UUID (sub claim)
                - username: Username (preferred_username)
                - email: User email
                - roles: List of roles (from realm_access or resource_access)
                - tenant_id: Tenant identifier (from custom claim or default)
                - given_name, family_name: User names
                
        Raises:
            jwt.InvalidTokenError: If token validation fails
        """
        # Get signing key from JWKS
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and validate token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],  # Keycloak uses RS256
            audience=self.settings.KEYCLOAK_CLIENT_ID,
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_exp": True,
            },
        )
        
        # Extract user information from claims
        user_info = {
            "id": payload.get("sub"),  # User UUID
            "username": payload.get("preferred_username", payload.get("sub")),
            "email": payload.get("email"),
            "given_name": payload.get("given_name", ""),
            "family_name": payload.get("family_name", ""),
            "roles": self._extract_roles(payload),
            "tenant_id": payload.get("tenant_id", "nacional"),  # Custom claim or default
            "email_verified": payload.get("email_verified", False),
            "token_issued_at": datetime.fromtimestamp(payload.get("iat", 0)),
            "token_expires_at": datetime.fromtimestamp(payload.get("exp", 0)),
        }
        
        return user_info
    
    def _extract_roles(self, payload: Dict[str, Any]) -> list:
        """
        Extract roles from JWT payload.
        
        Keycloak can store roles in multiple places:
        - realm_access.roles (realm-level roles)
        - resource_access.{client_id}.roles (client-level roles)
        
        Args:
            payload: Decoded JWT payload
            
        Returns:
            List of role strings
        """
        roles = []
        
        # Realm-level roles
        if "realm_access" in payload:
            roles.extend(payload["realm_access"].get("roles", []))
        
        # Client-level roles
        if "resource_access" in payload:
            client_access = payload["resource_access"].get(
                self.settings.KEYCLOAK_CLIENT_ID, {}
            )
            roles.extend(client_access.get("roles", []))
        
        # Filter out default Keycloak roles
        filtered_roles = [
            role for role in roles
            if role not in ["offline_access", "uma_authorization", "default-roles-prospecai"]
        ]
        
        return filtered_roles or ["viewer"]  # Default to viewer if no roles
    
    def _get_mock_user(self) -> Dict[str, Any]:
        """
        Return mock user for development when JWT is not required.
        
        Returns:
            Dict with mock user information
        """
        return {
            "id": "00000000-0000-0000-0000-000000000000",
            "username": "dev-user",
            "email": "dev@prospecai.local",
            "given_name": "Development",
            "family_name": "User",
            "roles": ["admin", "gestor", "analista"],
            "tenant_id": "nacional",
            "email_verified": True,
            "token_issued_at": datetime.now(),
            "token_expires_at": datetime.now() + timedelta(hours=8),
        }


def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from request state.
    
    Usage in route:
        @router.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            return {"user_id": user["id"]}
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Dict with user information
        
    Raises:
        HTTPException: If user not found in request state
    """
    if hasattr(request.state, "user"):
        return request.state.user

    # Fallback for tests/dev when middleware isn't installed and JWT isn't required
    try:
        from app.infrastructure.config.settings import get_settings
        settings = get_settings()
        if not settings.FEATURE_JWT_REQUIRED:
            return {
                "id": "00000000-0000-0000-0000-000000000000",
                "sub": "00000000-0000-0000-0000-000000000000",
                "username": "dev-user",
                "roles": ["admin", "gestor", "analista"],
                "tenant_id": "nacional",
                "email_verified": True,
            }
    except Exception:
        # If settings cannot be loaded, continue to raise 401
        pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not authenticated",
    )


def require_roles(*required_roles: str):
    """
    Dependency factory to require specific roles.
    
    Usage:
        @router.post("/admin-only", dependencies=[Depends(require_roles("admin"))])
        async def admin_route():
            return {"message": "Admin access granted"}
    
    Args:
        *required_roles: Role names that are required
        
    Returns:
        Callable dependency function
    """
    def role_checker(request: Request) -> Dict[str, Any]:
        user = get_current_user(request)
        user_roles = set(user.get("roles", []))
        
        if not any(role in user_roles for role in required_roles):
            logger.warning(
                "authorization_insufficient_roles",
                user_id=user.get("id"),
                user_roles=list(user_roles),
                required_roles=list(required_roles),
                path=request.url.path,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(required_roles)}",
            )
        
        return user
    
    return role_checker
