"""REST API router for Opportunities (RF-05 Pipeline)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from prometheus_client import Counter, Histogram
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.kafka.producer import KafkaProducerAdapter, get_kafka_producer
from app.domain.opportunity import OpportunityStage, OpportunityStatus
from app.infrastructure.database import get_async_session
from app.infrastructure.repositories.opportunities_repository import OpportunitiesRepository
from app.interfaces.schemas.opportunities import (
    OpportunityCreate,
    OpportunityListResponse,
    OpportunityResponse,
    OpportunityStageTransition,
    OpportunityTransitionsResponse,
    OpportunityUpdate,
)

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])

# Prometheus metrics
opportunities_created_total = Counter("opportunities_created_total", "Total opportunities created")
opportunities_updated_total = Counter("opportunities_updated_total", "Total opportunities updated")
opportunities_deleted_total = Counter(
    "opportunities_deleted_total", "Total opportunities soft-deleted"
)
opportunities_stage_transitions_total = Counter(
    "opportunities_stage_transitions_total", "Total opportunity stage transitions"
)
opportunities_request_duration_seconds = Histogram(
    "opportunities_request_duration_seconds", "Request duration for opportunities endpoints"
)


async def get_opportunities_repository(
    session: AsyncSession = Depends(get_async_session),
    kafka_producer: KafkaProducerAdapter = Depends(get_kafka_producer),
) -> OpportunitiesRepository:
    """Dependency injection for opportunities repository."""
    return OpportunitiesRepository(session, kafka_producer)


async def get_current_user() -> dict:
    """Placeholder for ACL user extraction (Wave 3)."""
    return {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "tenant_id": UUID("00000000-0000-0000-0000-000000000001"),
    }


async def require_opportunities_write():
    """ACL placeholder: check write permission for opportunities."""
    pass


async def require_opportunities_read():
    """ACL placeholder: check read permission for opportunities."""
    pass


@router.post(
    "",
    response_model=OpportunityResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_opportunities_write)],
)
@opportunities_request_duration_seconds.time()
async def create_opportunity(
    data: OpportunityCreate,
    repository: OpportunitiesRepository = Depends(get_opportunities_repository),
    current_user: dict = Depends(get_current_user),
):
    """Create a new opportunity."""
    from datetime import datetime
    from uuid import uuid4

    from app.domain.opportunity import Opportunity

    opportunity = Opportunity(
        id=uuid4(),
        client_id=data.client_id,
        funding_source_id=data.funding_source_id,
        title=data.title,
        description=data.description,
        stage=OpportunityStage.INTELLIGENCE,
        score=data.score,
        estimated_value=data.estimated_value,
        probability=data.probability,
        expected_close_date=data.expected_close_date,
        responsible_user_id=data.responsible_user_id,
        status=OpportunityStatus.ACTIVE,
        tenant_id=current_user["tenant_id"],
        historico_atualizacoes=[],
        historico_transicoes=[],
        criado_por=current_user["id"],
        atualizado_por=current_user["id"],
        criado_em=datetime.now(datetime.UTC),
        atualizado_em=datetime.now(datetime.UTC),
    )

    created = await repository.create(opportunity)
    opportunities_created_total.inc()

    return created


@router.get(
    "", response_model=OpportunityListResponse, dependencies=[Depends(require_opportunities_read)]
)
@opportunities_request_duration_seconds.time()
async def list_opportunities(
    status: Optional[OpportunityStatus] = Query(None, description="Filter by status"),
    stage: Optional[OpportunityStage] = Query(None, description="Filter by pipeline stage"),
    client_id: Optional[UUID] = Query(None, description="Filter by client"),
    funding_source_id: Optional[UUID] = Query(None, description="Filter by funding source"),
    responsible_user_id: Optional[UUID] = Query(None, description="Filter by responsible user"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Max results per page"),
    repository: OpportunitiesRepository = Depends(get_opportunities_repository),
    current_user: dict = Depends(get_current_user),
):
    """List opportunities with filters and pagination."""
    opportunities, total = await repository.list(
        tenant_id=current_user["tenant_id"],
        status=status,
        stage=stage,
        client_id=client_id,
        funding_source_id=funding_source_id,
        responsible_user_id=responsible_user_id,
        skip=skip,
        limit=limit,
    )

    return OpportunityListResponse(items=opportunities, total=total, skip=skip, limit=limit)


@router.get(
    "/{opportunity_id}",
    response_model=OpportunityResponse,
    dependencies=[Depends(require_opportunities_read)],
)
@opportunities_request_duration_seconds.time()
async def get_opportunity(
    opportunity_id: UUID,
    repository: OpportunitiesRepository = Depends(get_opportunities_repository),
    current_user: dict = Depends(get_current_user),
):
    """Get opportunity by ID."""
    opportunity = await repository.find_by_id(opportunity_id, current_user["tenant_id"])

    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    return opportunity


@router.patch(
    "/{opportunity_id}",
    response_model=OpportunityResponse,
    dependencies=[Depends(require_opportunities_write)],
)
@opportunities_request_duration_seconds.time()
async def update_opportunity(
    opportunity_id: UUID,
    data: OpportunityUpdate,
    repository: OpportunitiesRepository = Depends(get_opportunities_repository),
    current_user: dict = Depends(get_current_user),
):
    """Update opportunity."""
    updates = data.model_dump(exclude_unset=True, exclude={"motivo"})

    updated = await repository.update(
        opportunity_id=opportunity_id,
        tenant_id=current_user["tenant_id"],
        updates=updates,
        updated_by=current_user["id"],
        motivo=data.motivo,
    )

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    opportunities_updated_total.inc()
    return updated


@router.post(
    "/{opportunity_id}/transition",
    response_model=OpportunityResponse,
    dependencies=[Depends(require_opportunities_write)],
)
@opportunities_request_duration_seconds.time()
async def transition_opportunity_stage(
    opportunity_id: UUID,
    data: OpportunityStageTransition,
    repository: OpportunitiesRepository = Depends(get_opportunities_repository),
    current_user: dict = Depends(get_current_user),
):
    """Transition opportunity to a new pipeline stage (human-in-loop)."""
    updated = await repository.transition_stage(
        opportunity_id=opportunity_id,
        tenant_id=current_user["tenant_id"],
        new_stage=data.new_stage,
        updated_by=current_user["id"],
        motivo=data.motivo,
    )

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    opportunities_stage_transitions_total.inc()
    return updated


@router.delete(
    "/{opportunity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_opportunities_write)],
)
@opportunities_request_duration_seconds.time()
async def delete_opportunity(
    opportunity_id: UUID,
    motivo: str = Query(..., min_length=1, description="Reason for deletion"),
    repository: OpportunitiesRepository = Depends(get_opportunities_repository),
    current_user: dict = Depends(get_current_user),
):
    """Soft delete an opportunity."""
    success = await repository.soft_delete(
        opportunity_id=opportunity_id,
        tenant_id=current_user["tenant_id"],
        deleted_by=current_user["id"],
        motivo=motivo,
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    opportunities_deleted_total.inc()


@router.get(
    "/{opportunity_id}/transitions",
    response_model=OpportunityTransitionsResponse,
    dependencies=[Depends(require_opportunities_read)],
)
@opportunities_request_duration_seconds.time()
async def get_opportunity_transitions(
    opportunity_id: UUID,
    repository: OpportunitiesRepository = Depends(get_opportunities_repository),
    current_user: dict = Depends(get_current_user),
):
    """Get opportunity stage transitions history."""
    opportunity = await repository.find_by_id(opportunity_id, current_user["tenant_id"])

    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    return OpportunityTransitionsResponse(
        id=opportunity.id,
        title=opportunity.title,
        stage=opportunity.stage,
        historico_transicoes=opportunity.historico_transicoes,
    )
