"""REST API router for Clients (RF-04 CRM)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from prometheus_client import Counter, Histogram
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.kafka.producer import KafkaProducerAdapter, get_kafka_producer
from app.application.services.clients_service import ClientsService, TenantContext
from app.domain.client import ClientMaturity, ClientStatus
from app.domain.repositories.clients_protocol import ClientsRepositoryProtocol
from app.infrastructure.database import get_async_session
from app.infrastructure.repositories.clients_repository import ClientsRepository
from app.interfaces.schemas.clients import (
    ClientCreate,
    ClientHistoryResponse,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
)

router = APIRouter(prefix="/clients", tags=["Clients"])

# Prometheus metrics
clients_created_total = Counter("clients_created_total", "Total clients created")
clients_updated_total = Counter("clients_updated_total", "Total clients updated")
clients_deleted_total = Counter("clients_deleted_total", "Total clients soft-deleted")
clients_request_duration_seconds = Histogram(
    "clients_request_duration_seconds", "Request duration for clients endpoints"
)


async def get_clients_repository(
    session: AsyncSession = Depends(get_async_session),
    kafka_producer: KafkaProducerAdapter = Depends(get_kafka_producer),
) -> ClientsRepositoryProtocol:
    """Dependency injection for clients repository."""
    return ClientsRepository(session, kafka_producer)


async def get_tenant_context() -> TenantContext:
    """Build tenant context from the authenticated user (placeholder)."""
    user = await get_current_user()
    return TenantContext(tenant_id=user["tenant_id"], user_id=user["id"])


async def get_clients_service(
    repository: ClientsRepositoryProtocol = Depends(get_clients_repository),
) -> ClientsService:
    """Provide the clients application service with injected repository."""
    return ClientsService(repository)


async def get_current_user() -> dict:
    """Placeholder for ACL user extraction (Wave 3)."""
    return {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "tenant_id": UUID("00000000-0000-0000-0000-000000000001"),
    }


async def require_clients_write():
    """ACL placeholder: check write permission for clients."""
    pass


async def require_clients_read():
    """ACL placeholder: check read permission for clients."""
    pass


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_clients_write)],
)
@clients_request_duration_seconds.time()
async def create_client(
    data: ClientCreate,
    service: ClientsService = Depends(get_clients_service),
    context: TenantContext = Depends(get_tenant_context),
):
    """Create a new client."""
    try:
        created = await service.create_client(data.model_dump(), context)
    except ValueError as exc:  # Validation errors from domain
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    clients_created_total.inc()

    return created


@router.get("", response_model=ClientListResponse, dependencies=[Depends(require_clients_read)])
@clients_request_duration_seconds.time()
async def list_clients(
    status: Optional[ClientStatus] = Query(None, description="Filter by status"),
    maturity: Optional[ClientMaturity] = Query(None, description="Filter by maturity level"),
    search: Optional[str] = Query(None, description="Search in name/email/notes"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Max results per page"),
    service: ClientsService = Depends(get_clients_service),
    context: TenantContext = Depends(get_tenant_context),
):
    """List clients with filters and pagination."""
    clients, total = await service.list_clients(
        context=context,
        status=status,
        maturity=maturity,
        search=search,
        skip=skip,
        limit=limit,
    )

    return ClientListResponse(items=clients, total=total, skip=skip, limit=limit)


@router.get(
    "/{client_id}", response_model=ClientResponse, dependencies=[Depends(require_clients_read)]
)
@clients_request_duration_seconds.time()
async def get_client(
    client_id: UUID,
    service: ClientsService = Depends(get_clients_service),
    context: TenantContext = Depends(get_tenant_context),
):
    """Get client by ID."""
    client = await service.get_client(client_id, context)

    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    return client


@router.patch(
    "/{client_id}", response_model=ClientResponse, dependencies=[Depends(require_clients_write)]
)
@clients_request_duration_seconds.time()
async def update_client(
    client_id: UUID,
    data: ClientUpdate,
    service: ClientsService = Depends(get_clients_service),
    context: TenantContext = Depends(get_tenant_context),
):
    """Update client."""
    updates = data.model_dump(exclude_unset=True, exclude={"motivo"})
    try:
        updated = await service.update_client(
            client_id=client_id,
            context=context,
            updates=updates,
            motivo=data.motivo,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    clients_updated_total.inc()
    return updated


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_clients_write)],
)
@clients_request_duration_seconds.time()
async def delete_client(
    client_id: UUID,
    motivo: str = Query(..., min_length=1, description="Reason for deletion"),
    service: ClientsService = Depends(get_clients_service),
    context: TenantContext = Depends(get_tenant_context),
):
    """Soft delete a client."""
    try:
        success = await service.delete_client(client_id=client_id, context=context, motivo=motivo)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    clients_deleted_total.inc()


@router.get(
    "/{client_id}/history",
    response_model=ClientHistoryResponse,
    dependencies=[Depends(require_clients_read)],
)
@clients_request_duration_seconds.time()
async def get_client_history(
    client_id: UUID,
    service: ClientsService = Depends(get_clients_service),
    context: TenantContext = Depends(get_tenant_context),
):
    """Get client update history."""
    client = await service.get_client(client_id, context)

    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    return ClientHistoryResponse(
        id=client.id,
        name=client.name,
        historico_atualizacoes=client.historico_atualizacoes,
    )
