"""
ProspecIA - System Router

System administration and monitoring endpoints.
Follows Interface Segregation Principle for admin operations.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any
import structlog

logger = structlog.get_logger()

router = APIRouter()


class SystemInfoResponse(BaseModel):
    """System information response model."""
    application: Dict[str, Any]
    environment: Dict[str, Any]
    features: Dict[str, bool]
    timestamp: datetime


class FeatureFlagsResponse(BaseModel):
    """Feature flags response model."""
    features: Dict[str, bool]
    timestamp: datetime


@router.get(
    "/info",
    response_model=SystemInfoResponse,
    status_code=status.HTTP_200_OK,
    summary="System information",
    description="Returns system configuration and environment information",
)
async def get_system_info() -> SystemInfoResponse:
    """
    Get system information.
    
    Provides configuration and environment details for monitoring and debugging.
    
    Returns:
        SystemInfoResponse: System information
    """
    from app.infrastructure.config.settings import get_settings
    settings = get_settings()
    
    return SystemInfoResponse(
        application={
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENV,
            "debug": settings.DEBUG,
        },
        environment={
            "api_host": settings.API_HOST,
            "api_port": settings.API_PORT,
            "database": settings.POSTGRES_DB,
            "neo4j_database": settings.NEO4J_DATABASE,
        },
        features={
            "ai_suggestions": settings.FEATURE_AI_SUGGESTIONS,
            "jwt_required": settings.FEATURE_JWT_REQUIRED,
            "rls_enabled": settings.FEATURE_RLS_ENABLED,
            "audit_logging": settings.FEATURE_AUDIT_LOGGING,
            "lgpd_agent": settings.FEATURE_LGPD_AGENT,
        },
        timestamp=datetime.utcnow(),
    )


@router.get(
    "/features",
    response_model=FeatureFlagsResponse,
    status_code=status.HTTP_200_OK,
    summary="Feature flags",
    description="Returns current feature flag configuration",
)
async def get_feature_flags() -> FeatureFlagsResponse:
    """
    Get feature flags.
    
    Returns current state of all feature flags for the application.
    
    Returns:
        FeatureFlagsResponse: Feature flags status
    """
    from app.infrastructure.config.settings import get_settings
    settings = get_settings()
    
    return FeatureFlagsResponse(
        features={
            "ai_suggestions": settings.FEATURE_AI_SUGGESTIONS,
            "jwt_required": settings.FEATURE_JWT_REQUIRED,
            "rls_enabled": settings.FEATURE_RLS_ENABLED,
            "audit_logging": settings.FEATURE_AUDIT_LOGGING,
            "lgpd_agent": settings.FEATURE_LGPD_AGENT,
            "use_model_v2_matching": settings.FEATURE_USE_MODEL_V2_MATCHING,
            "ab_test_percentage": settings.FEATURE_AB_TEST_PERCENTAGE > 0,
        },
        timestamp=datetime.utcnow(),
    )


@router.get(
    "/metrics",
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Prometheus metrics",
    description="Returns Prometheus-compatible metrics for scraping",
)
async def get_metrics() -> PlainTextResponse:
    """
    Get Prometheus metrics.
    
    Returns metrics in Prometheus exposition format for scraping.
    Exposes application metrics, database connections, and system statistics.
    
    Returns:
        PlainTextResponse: Prometheus metrics in text format
    """
    from prometheus_client import generate_latest, REGISTRY, Gauge, Counter, Histogram
    from app.infrastructure.config.settings import get_settings
    
    settings = get_settings()
    
    # Note: In production, these metrics should be collected continuously
    # and exposed here. This is a simplified implementation.
    
    try:
        # Generate metrics from default registry
        metrics = generate_latest(REGISTRY)
        return PlainTextResponse(
            content=metrics.decode('utf-8'),
            media_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        logger.error("metrics_generation_failed", error=str(e))
        # Return minimal metrics on error
        return PlainTextResponse(
            content=f"# Error generating metrics: {str(e)}\n",
            media_type="text/plain; charset=utf-8"
        )
