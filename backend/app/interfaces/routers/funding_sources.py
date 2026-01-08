"""
REST API endpoints for Funding Sources.

Implements RF-02: Gestão de Fontes de Fomento with:
- CRUD operations with RLS
- ACL enforcement (Regra 10)
- Soft delete (Regra 11)
- i18n support (Regra 9)
- Prometheus metrics

Wave 2 - RF-02
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from prometheus_client import Counter, Histogram

from app.interfaces.schemas.funding_sources import (
    FundingSourceCreate,
    FundingSourceUpdate,
    FundingSourceResponse,
    FundingSourceListResponse,
    FundingSourceListItem,
    FundingSourceHistoryResponse,
    FundingSourceHistoryEntry,
)
from app.domain.funding_source import FundingSourceStatus, FundingSourceType
from app.infrastructure.repositories.funding_sources_repository import FundingSourcesRepository
from app.infrastructure.database import get_db_session
from app.adapters.kafka.producer import get_kafka_producer, KafkaProducer


# Prometheus metrics
funding_sources_created = Counter(
    "funding_sources_created_total",
    "Total number of funding sources created"
)
funding_sources_updated = Counter(
    "funding_sources_updated_total",
    "Total number of funding sources updated"
)
funding_sources_deleted = Counter(
    "funding_sources_deleted_total",
    "Total number of funding sources soft deleted"
)
funding_sources_request_duration = Histogram(
    "funding_sources_request_duration_seconds",
    "Duration of funding sources API requests",
    ["method", "endpoint"]
)

router = APIRouter(prefix="/funding-sources", tags=["Funding Sources"])
logger = structlog.get_logger()


# Dependency: Get current user (placeholder for Keycloak integration)
async def get_current_user() -> dict:
    """
    Get current user from JWT token.
    TODO: Implement full Keycloak JWT validation from Wave 0
    """
    # Placeholder: return mock admin user
    return {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "tenant_id": UUID("00000000-0000-0000-0000-000000000100"),
        "roles": ["admin"],
    }


# Dependency: ACL check (simplified, full implementation in middleware)
async def require_funding_sources_read(user: dict = Depends(get_current_user)) -> dict:
    """Require read permission for funding_sources resource."""
    # TODO: Full ACL check via acl_rules table
    if "admin" not in user["roles"] and "gestor" not in user["roles"] and "analista" not in user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to read funding sources"
        )
    return user


async def require_funding_sources_write(user: dict = Depends(get_current_user)) -> dict:
    """Require write permission for funding_sources resource."""
    # TODO: Full ACL check via acl_rules table
    if "admin" not in user["roles"] and "gestor" not in user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to write funding sources"
        )
    return user


@router.post(
    "",
    response_model=FundingSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create funding source",
    description="Create a new funding source with versioning and audit trail"
)
async def create_funding_source(
    data: FundingSourceCreate,
    user: dict = Depends(require_funding_sources_write),
    session: AsyncSession = Depends(get_db_session),
    kafka_producer: Optional[KafkaProducer] = Depends(get_kafka_producer),
) -> FundingSourceResponse:
    """
    Create a new funding source.
    
    Requires: admin or gestor role
    """
    with funding_sources_request_duration.labels(method="POST", endpoint="/funding-sources").time():
        repo = FundingSourcesRepository(session, kafka_producer)
        
        try:
            entity = await repo.create(
                name=data.name,
                description=data.description,
                type=data.type,
                sectors=data.sectors,
                amount=data.amount,
                trl_min=data.trl_min,
                trl_max=data.trl_max,
                deadline=data.deadline,
                url=data.url,
                requirements=data.requirements,
                tenant_id=user["tenant_id"],
                criado_por=user["id"],
            )
            
            funding_sources_created.inc()
            
            return FundingSourceResponse.model_validate(entity)
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@router.get(
    "",
    response_model=FundingSourceListResponse,
    summary="List funding sources",
    description="List funding sources with pagination and filtering"
)
async def list_funding_sources(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records"),
    status_filter: Optional[List[FundingSourceStatus]] = Query(None, description="Filter by status"),
    type_filter: Optional[List[FundingSourceType]] = Query(None, description="Filter by type"),
    sector_filter: Optional[List[str]] = Query(None, description="Filter by sectors (any match)"),
    user: dict = Depends(require_funding_sources_read),
    session: AsyncSession = Depends(get_db_session),
    kafka_producer: Optional[KafkaProducer] = Depends(get_kafka_producer),
) -> FundingSourceListResponse:
    """
    List funding sources with RLS filtering by tenant_id.
    
    Requires: admin, gestor, or analista role
    """
    with funding_sources_request_duration.labels(method="GET", endpoint="/funding-sources").time():
        repo = FundingSourcesRepository(session, kafka_producer)
        
        items = await repo.list(
            tenant_id=user["tenant_id"],
            skip=skip,
            limit=limit,
            status_filter=status_filter,
            type_filter=type_filter,
            sector_filter=sector_filter,
        )
        
        # Convert to list items (no history for performance)
        list_items = [
            FundingSourceListItem(
                id=item.id,
                name=item.name,
                type=item.type,
                sectors=item.sectors,
                amount=item.amount,
                trl_min=item.trl_min,
                trl_max=item.trl_max,
                deadline=item.deadline,
                status=item.status,
                criado_em=item.criado_em,
            )
            for item in items
        ]
        
        # TODO: Add total count query for pagination
        total = len(list_items)
        
        return FundingSourceListResponse(
            items=list_items,
            total=total,
            skip=skip,
            limit=limit,
        )


@router.get(
    "/{funding_source_id}",
    response_model=FundingSourceResponse,
    summary="Get funding source by ID",
    description="Get a single funding source with full details and audit trail"
)
async def get_funding_source(
    funding_source_id: UUID,
    user: dict = Depends(require_funding_sources_read),
    session: AsyncSession = Depends(get_db_session),
    kafka_producer: Optional[KafkaProducer] = Depends(get_kafka_producer),
) -> FundingSourceResponse:
    """
    Get funding source by ID with RLS filtering.
    
    Requires: admin, gestor, or analista role
    """
    with funding_sources_request_duration.labels(method="GET", endpoint="/funding-sources/{id}").time():
        repo = FundingSourcesRepository(session, kafka_producer)
        
        entity = await repo.find_by_id(
            funding_source_id=funding_source_id,
            tenant_id=user["tenant_id"],
            include_excluded=False,
        )
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Funding source {funding_source_id} not found"
            )
        
        return FundingSourceResponse.model_validate(entity)


@router.patch(
    "/{funding_source_id}",
    response_model=FundingSourceResponse,
    summary="Update funding source",
    description="Update funding source with versioning (requires reason)"
)
async def update_funding_source(
    funding_source_id: UUID,
    data: FundingSourceUpdate,
    user: dict = Depends(require_funding_sources_write),
    session: AsyncSession = Depends(get_db_session),
    kafka_producer: Optional[KafkaProducer] = Depends(get_kafka_producer),
) -> FundingSourceResponse:
    """
    Update funding source with versioning.
    
    All changes are tracked in historico_atualizacoes.
    Requires: admin or gestor role
    """
    with funding_sources_request_duration.labels(method="PATCH", endpoint="/funding-sources/{id}").time():
        repo = FundingSourcesRepository(session, kafka_producer)
        
        # Extract motivo and prepare updates dict
        motivo = data.motivo
        updates = data.model_dump(exclude={"motivo"}, exclude_none=True)
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        try:
            entity = await repo.update(
                funding_source_id=funding_source_id,
                tenant_id=user["tenant_id"],
                updates=updates,
                motivo=motivo,
                atualizado_por=user["id"],
            )
            
            if not entity:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Funding source {funding_source_id} not found"
                )
            
            funding_sources_updated.inc()
            
            return FundingSourceResponse.model_validate(entity)
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )


@router.delete(
    "/{funding_source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete funding source",
    description="Soft delete funding source (set status=excluded, never hard DELETE)"
)
async def delete_funding_source(
    funding_source_id: UUID,
    motivo: str = Query(..., min_length=5, description="Reason for deletion (required)"),
    user: dict = Depends(require_funding_sources_write),
    session: AsyncSession = Depends(get_db_session),
    kafka_producer: Optional[KafkaProducer] = Depends(get_kafka_producer),
) -> None:
    """
    Soft delete funding source (Regra 11: never hard DELETE).
    
    Requires: admin or gestor role
    """
    with funding_sources_request_duration.labels(method="DELETE", endpoint="/funding-sources/{id}").time():
        repo = FundingSourcesRepository(session, kafka_producer)
        
        success = await repo.soft_delete(
            funding_source_id=funding_source_id,
            tenant_id=user["tenant_id"],
            motivo=motivo,
            atualizado_por=user["id"],
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Funding source {funding_source_id} not found"
            )
        
        funding_sources_deleted.inc()


@router.get(
    "/{funding_source_id}/history",
    response_model=FundingSourceHistoryResponse,
    summary="Get funding source history",
    description="Get audit trail (historico_atualizacoes) for a funding source"
)
async def get_funding_source_history(
    funding_source_id: UUID,
    user: dict = Depends(require_funding_sources_read),
    session: AsyncSession = Depends(get_db_session),
    kafka_producer: Optional[KafkaProducer] = Depends(get_kafka_producer),
) -> FundingSourceHistoryResponse:
    """
    Get funding source audit trail.
    
    Requires: admin, gestor, or analista role
    """
    with funding_sources_request_duration.labels(method="GET", endpoint="/funding-sources/{id}/history").time():
        repo = FundingSourcesRepository(session, kafka_producer)
        
        entity = await repo.find_by_id(
            funding_source_id=funding_source_id,
            tenant_id=user["tenant_id"],
            include_excluded=False,
        )
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Funding source {funding_source_id} not found"
            )
        
        history_entries = [
            FundingSourceHistoryEntry(**entry)
            for entry in entity.historico_atualizacoes
        ]
        
        return FundingSourceHistoryResponse(
            funding_source_id=entity.id,
            name=entity.name,
            historico=history_entries,
        )
