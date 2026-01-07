"""
ProspecIA - Health Check Router

Health check endpoints following Interface Segregation Principle.
Provides multiple health check endpoints for different purposes.
"""

from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime
from typing import Any
import structlog

logger = structlog.get_logger()

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    environment: str


class DetailedHealthResponse(HealthResponse):
    """Detailed health check response with service statuses."""
    services: dict[str, dict[str, Any]]


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic application health status",
)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.
    
    Used by load balancers and monitoring systems for simple up/down checks.
    
    Returns:
        HealthResponse: Basic health information
    """
    from app.infrastructure.config.settings import get_settings
    settings = get_settings()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION,
        environment=settings.ENV,
    )


@router.get(
    "/ready",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Checks if application is ready to serve requests (all dependencies available)",
)
async def readiness_check() -> DetailedHealthResponse:
    """
    Readiness check endpoint.
    
    Verifies that all required services (database, cache, etc.) are available.
    Used by Kubernetes and container orchestrators.
    
    Returns:
        DetailedHealthResponse: Detailed health information with service statuses
    """
    from app.infrastructure.config.settings import get_settings
    from app.adapters.postgres.connection import get_db_connection
    from app.adapters.neo4j.connection import get_neo4j_connection
    from app.adapters.kafka.producer import get_kafka_producer
    import httpx
    from time import perf_counter
    
    settings = get_settings()
    
    services = {}
    
    # Check PostgreSQL
    try:
        start = perf_counter()
        db = get_db_connection()
        postgres_healthy = await db.health_check()
        elapsed = (perf_counter() - start) * 1000
        
        services["postgres"] = {
            "status": "healthy" if postgres_healthy else "unhealthy",
            "response_time_ms": round(elapsed, 2),
            "message": "Connected" if postgres_healthy else "Connection failed",
        }
    except Exception as e:
        services["postgres"] = {
            "status": "unhealthy",
            "response_time_ms": 0,
            "message": f"Error: {str(e)}",
        }
    
    # Check Neo4j
    try:
        start = perf_counter()
        neo4j = get_neo4j_connection()
        neo4j_healthy = await neo4j.health_check()
        elapsed = (perf_counter() - start) * 1000
        
        services["neo4j"] = {
            "status": "healthy" if neo4j_healthy else "unhealthy",
            "response_time_ms": round(elapsed, 2),
            "message": "Connected" if neo4j_healthy else "Connection failed",
        }
    except Exception as e:
        services["neo4j"] = {
            "status": "unhealthy",
            "response_time_ms": 0,
            "message": f"Error: {str(e)}",
        }
    
    # Check Kafka
    try:
        start = perf_counter()
        kafka = get_kafka_producer()
        kafka_healthy = kafka.health_check()
        elapsed = (perf_counter() - start) * 1000
        
        services["kafka"] = {
            "status": "healthy" if kafka_healthy else "unhealthy",
            "response_time_ms": round(elapsed, 2),
            "message": "Connected" if kafka_healthy else "Connection failed",
        }
    except Exception as e:
        services["kafka"] = {
            "status": "unhealthy",
            "response_time_ms": 0,
            "message": f"Error: {str(e)}",
        }
    
    # Check Keycloak
    try:
        start = perf_counter()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.keycloak_url}/health")
            keycloak_healthy = response.status_code == 200
        elapsed = (perf_counter() - start) * 1000
        
        services["keycloak"] = {
            "status": "healthy" if keycloak_healthy else "unhealthy",
            "response_time_ms": round(elapsed, 2),
            "message": "Reachable" if keycloak_healthy else "Not reachable",
        }
    except Exception as e:
        services["keycloak"] = {
            "status": "unhealthy",
            "response_time_ms": 0,
            "message": f"Error: {str(e)}",
        }
    
    # Determine overall status
    all_healthy = all(s["status"] == "healthy" for s in services.values())
    overall_status = "ready" if all_healthy else "degraded"
    
    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION,
        environment=settings.ENV,
        services=services,
    )


@router.get(
    "/live",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Checks if application is alive (process running)",
)
async def liveness_check() -> HealthResponse:
    """
    Liveness check endpoint.
    
    Simple check to verify the application process is running.
    Used by Kubernetes to restart unhealthy pods.
    
    Returns:
        HealthResponse: Basic liveness information
    """
    from app.infrastructure.config.settings import get_settings
    settings = get_settings()
    
    return HealthResponse(
        status="alive",
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION,
        environment=settings.ENV,
    )
