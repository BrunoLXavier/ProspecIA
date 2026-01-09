"""Application service for Clients (CRM).

Encapsulates orchestration and guards so FastAPI routers stay thin and the
use cases depend on abstractions rather than infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4

from app.domain.client import Client, ClientMaturity, ClientStatus
from app.domain.repositories.clients_protocol import ClientsRepositoryProtocol


@dataclass(frozen=True)
class TenantContext:
    """Represents the current tenant and user performing the action."""

    tenant_id: UUID
    user_id: UUID


class ClientsService:
    """Use-case layer for client lifecycle operations."""

    def __init__(self, repository: ClientsRepositoryProtocol):
        self.repository = repository

    async def create_client(
        self,
        data: dict,
        context: TenantContext,
    ) -> Client:
        Client.validate_cnpj(data["cnpj"])
        client = Client(
            id=uuid4(),
            name=data["name"],
            cnpj=data["cnpj"],
            email=data["email"],
            phone=data.get("phone"),
            website=data.get("website"),
            address=data.get("address"),
            maturity=data.get("maturity", ClientMaturity.PROSPECT),
            notes=data.get("notes"),
            status=ClientStatus.ACTIVE,
            tenant_id=context.tenant_id,
            historico_atualizacoes=[],
            criado_por=context.user_id,
            atualizado_por=context.user_id,
            criado_em=datetime.now(UTC),
            atualizado_em=datetime.now(UTC),
        )

        created = await self.repository.create(client)
        return created

    async def list_clients(
        self,
        context: TenantContext,
        status: Optional[ClientStatus] = None,
        maturity: Optional[ClientMaturity] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Client], int]:
        items, total = await self.repository.list(
            tenant_id=context.tenant_id,
            status=status,
            maturity=maturity,
            search=search,
            skip=skip,
            limit=limit,
        )
        return list(items), total

    async def get_client(self, client_id: UUID, context: TenantContext) -> Optional[Client]:
        return await self.repository.get(client_id, context.tenant_id)

    async def update_client(
        self,
        client_id: UUID,
        context: TenantContext,
        updates: dict,
        motivo: str,
    ) -> Optional[Client]:
        if "cnpj" in updates:
            Client.validate_cnpj(updates["cnpj"])

        if "status" in updates:
            existing = await self.repository.get(
                client_id, context.tenant_id, include_excluded=True
            )
            if not existing:
                return None
            if not existing.can_transition_to(updates["status"]):
                raise ValueError("Invalid status transition")

        return await self.repository.update(
            client_id=client_id,
            tenant_id=context.tenant_id,
            updates=updates,
            updated_by=context.user_id,
            motivo=motivo,
        )

    async def delete_client(
        self,
        client_id: UUID,
        context: TenantContext,
        motivo: str,
    ) -> bool:
        client = await self.repository.get(client_id, context.tenant_id)
        if not client:
            return False
        if not client.can_transition_to(ClientStatus.EXCLUDED):
            raise ValueError("Client cannot transition to excluded")

        return await self.repository.delete(
            client_id=client_id,
            tenant_id=context.tenant_id,
            deleted_by=context.user_id,
            motivo=motivo,
        )

    async def get_history(self, client_id: UUID, context: TenantContext):
        return await self.repository.get_history(client_id, context.tenant_id)
