"""REST API router for Interactions (RF-04 CRM)."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from prometheus_client import Counter, Histogram
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.kafka.producer import KafkaProducer
from app.domain.interaction import InteractionType
from app.infrastructure.database import get_async_session
from app.infrastructure.repositories.interactions_repository import InteractionsRepository
from app.interfaces.schemas.interactions import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    InteractionListResponse,
)

router = APIRouter(prefix="/interactions", tags=["Interactions"])

# Prometheus metrics
interactions_created_total = Counter("interactions_created_total", "Total interactions created")
interactions_updated_total = Counter("interactions_updated_total", "Total interactions updated")
interactions_deleted_total = Counter("interactions_deleted_total", "Total interactions soft-deleted")
interactions_request_duration_seconds = Histogram("interactions_request_duration_seconds", "Request duration for interactions endpoints")


async def get_interactions_repository(
    session: AsyncSession = Depends(get_async_session),
    kafka_producer: KafkaProducer = Depends(),
) -> InteractionsRepository:
    """Dependency injection for interactions repository."""
    return InteractionsRepository(session, kafka_producer)


async def get_current_user() -> dict:
    """Placeholder for ACL user extraction (Wave 3)."""
    return {"id": UUID("00000000-0000-0000-0000-000000000001"), "tenant_id": UUID("00000000-0000-0000-0000-000000000001")}


async def require_interactions_write():
    """ACL placeholder: check write permission for interactions."""
    pass


async def require_interactions_read():
    """ACL placeholder: check read permission for interactions."""
    pass


@router.post("", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_interactions_write)])
@interactions_request_duration_seconds.time()
async def create_interaction(
    data: InteractionCreate,
    repository: InteractionsRepository = Depends(get_interactions_repository),
    current_user: dict = Depends(get_current_user),
):
    """Create a new interaction."""
    from datetime import datetime
    from uuid import uuid4
    from app.domain.interaction import Interaction, InteractionStatus
    
    interaction = Interaction(
        id=uuid4(),
        client_id=data.client_id,
        title=data.title,
        description=data.description,
        type=data.type,
        date=data.date,
        participants=data.participants,
        outcome=data.outcome,
        next_steps=data.next_steps,
        status=InteractionStatus.COMPLETED,
        tenant_id=current_user["tenant_id"],
        criado_por=current_user["id"],
        criado_em=datetime.utcnow(),
    )
    
    created = await repository.create(interaction)
    interactions_created_total.inc()
    
    return created


@router.get("/clients/{client_id}", response_model=InteractionListResponse, dependencies=[Depends(require_interactions_read)])
@interactions_request_duration_seconds.time()
async def list_client_interactions(
    client_id: UUID,
    type: Optional[InteractionType] = Query(None, description="Filter by interaction type"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Max results per page"),
    repository: InteractionsRepository = Depends(get_interactions_repository),
    current_user: dict = Depends(get_current_user),
):
    """List interactions for a specific client."""
    interactions, total = await repository.list_by_client(
        client_id=client_id,
        tenant_id=current_user["tenant_id"],
        type=type,
        skip=skip,
        limit=limit,
    )
    
    return InteractionListResponse(items=interactions, total=total, skip=skip, limit=limit)


@router.get("/{interaction_id}", response_model=InteractionResponse, dependencies=[Depends(require_interactions_read)])
@interactions_request_duration_seconds.time()
async def get_interaction(
    interaction_id: UUID,
    repository: InteractionsRepository = Depends(get_interactions_repository),
    current_user: dict = Depends(get_current_user),
):
    """Get interaction by ID."""
    interaction = await repository.find_by_id(interaction_id, current_user["tenant_id"])
    
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
    
    return interaction


@router.patch("/{interaction_id}", response_model=InteractionResponse, dependencies=[Depends(require_interactions_write)])
@interactions_request_duration_seconds.time()
async def update_interaction(
    interaction_id: UUID,
    data: InteractionUpdate,
    repository: InteractionsRepository = Depends(get_interactions_repository),
    current_user: dict = Depends(get_current_user),
):
    """Update interaction."""
    updates = data.model_dump(exclude_unset=True)
    
    updated = await repository.update(
        interaction_id=interaction_id,
        tenant_id=current_user["tenant_id"],
        updates=updates,
        updated_by=current_user["id"],
    )
    
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
    
    interactions_updated_total.inc()
    return updated


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_interactions_write)])
@interactions_request_duration_seconds.time()
async def delete_interaction(
    interaction_id: UUID,
    repository: InteractionsRepository = Depends(get_interactions_repository),
    current_user: dict = Depends(get_current_user),
):
    """Soft delete an interaction."""
    success = await repository.soft_delete(
        interaction_id=interaction_id,
        tenant_id=current_user["tenant_id"],
        deleted_by=current_user["id"],
    )
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
    
    interactions_deleted_total.inc()
