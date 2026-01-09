"""
ProspecIA - Logging Middleware

Structured logging middleware following Single Responsibility Principle.
Logs all HTTP requests/responses with context.
"""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured logging of HTTP requests and responses.

    Responsibilities:
    - Generate request IDs
    - Log request details
    - Log response details
    - Measure request duration
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process HTTP request/response with logging.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            Response: HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Add request ID to request state
        request.state.request_id = request_id

        # Extract client information
        client_host = request.client.host if request.client else "unknown"

        # Log request
        logger.info(
            "http_request_received",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_host=client_host,
            user_agent=request.headers.get("user-agent", "unknown"),
        )

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                "http_request_completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=round(duration, 3),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            logger.error(
                "http_request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                duration_seconds=round(duration, 3),
                error=str(exc),
                error_type=type(exc).__name__,
            )

            # Re-raise exception
            raise
