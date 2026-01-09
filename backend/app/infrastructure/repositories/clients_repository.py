"""Repository for clients management (RF-04 CRM)."""

import inspect
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Sequence
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.kafka.producer import KafkaProducer
from app.domain.repositories.clients_protocol import ClientsRepositoryProtocol
from app.infrastructure.models.client import Client, ClientMaturity, ClientStatus


class ClientsRepository(ClientsRepositoryProtocol):
    """Repository for managing clients with RLS support."""

    def __init__(self, session: AsyncSession, kafka_producer: KafkaProducer):
        self.session = session
        self.kafka_producer = kafka_producer

    async def create(self, client: Client) -> Client:
        """Persist a new client and emit audit event."""
        # Keep working with ORM for now to preserve compatibility
        # Will transition to domain entity input in Phase 3
        add_result = self.session.add(client)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result
        refresh_result = self.session.refresh(client)
        if inspect.isawaitable(refresh_result):
            await refresh_result

        await self.kafka_producer.send_event(
            topic="clients",
            event_type="client.created",
            entity_id=str(client.id),
            tenant_id=str(client.tenant_id),
            user_id=str(client.criado_por),
            data={"name": client.name, "cnpj": client.cnpj, "maturity": client.maturity.value},
        )
        return client

    async def get(
        self,
        client_id: UUID,
        tenant_id: UUID,
        include_excluded: bool = False,
    ) -> Optional[Client]:
        """Get client by ID (soft-delete aware)."""
        stmt = select(Client).where(Client.id == client_id, Client.tenant_id == tenant_id)
        if not include_excluded:
            stmt = stmt.where(Client.status != ClientStatus.EXCLUDED)
        result = await self.session.execute(stmt)
        value = result.scalar_one_or_none()
        if inspect.isawaitable(value):
            value = await value
        return value

    async def list(
        self,
        tenant_id: UUID,
        status: Optional[ClientStatus] = None,
        maturity: Optional[ClientMaturity] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Client], int]:
        """List clients with filters and pagination."""
        base_query = select(Client).where(
            Client.tenant_id == tenant_id, Client.status != ClientStatus.EXCLUDED
        )
        if status:
            base_query = base_query.where(Client.status == status)
        if maturity:
            base_query = base_query.where(Client.maturity == maturity)
        if search:
            search_pattern = f"%{search}%"
            base_query = base_query.where(
                or_(
                    Client.name.ilike(search_pattern),
                    Client.email.ilike(search_pattern),
                    Client.notes.ilike(search_pattern),
                )
            )

        query = base_query.order_by(Client.criado_em.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        scalars = result.scalars()
        if inspect.isawaitable(scalars):
            scalars = await scalars
        clients = scalars.all()
        if inspect.isawaitable(clients):
            clients = await clients

        count_stmt = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()
        if inspect.isawaitable(total):
            total = await total
        total = total or 0

        return clients, total

    async def update(
        self,
        client_id: UUID,
        tenant_id: UUID,
        updates: Dict[str, Any],
        updated_by: UUID,
        motivo: Optional[str] = None,
    ) -> Optional[Client]:
        """Update client with history tracking."""
        existing = await self.get(client_id, tenant_id, include_excluded=True)
        if not existing:
            return None

        existing.add_history(
            campos=updates, usuario_id=updated_by, acao="atualizacao", motivo=motivo
        )
        for field, value in updates.items():
            if hasattr(existing, field):
                setattr(existing, field, value)
        existing.atualizado_por = updated_by
        existing.atualizado_em = datetime.now(UTC)

        add_result = self.session.add(existing)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result
        refresh_result = self.session.refresh(existing)
        if inspect.isawaitable(refresh_result):
            await refresh_result

        await self.kafka_producer.send_event(
            topic="clients",
            event_type="client.updated",
            entity_id=str(client_id),
            tenant_id=str(tenant_id),
            user_id=str(updated_by),
            data={"updates": list(updates.keys()), "motivo": motivo},
        )
        return existing

    async def delete(
        self,
        client_id: UUID,
        tenant_id: UUID,
        deleted_by: UUID,
        motivo: str,
    ) -> bool:
        """Soft delete a client (status -> excluded)."""
        existing = await self.get(client_id, tenant_id)
        if not existing:
            return False
        existing.status = ClientStatus.EXCLUDED
        existing.add_history(
            {"status": ClientStatus.EXCLUDED.value},
            usuario_id=deleted_by,
            acao="exclusao",
            motivo=motivo,
        )
        existing.atualizado_por = deleted_by
        existing.atualizado_em = datetime.now(UTC)

        add_result = self.session.add(existing)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result

        await self.kafka_producer.send_event(
            topic="clients",
            event_type="client.deleted",
            entity_id=str(client_id),
            tenant_id=str(tenant_id),
            user_id=str(deleted_by),
            data={"motivo": motivo},
        )
        return True

    async def get_history(self, client_id: UUID, tenant_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """Return audit history for a client."""
        existing = await self.get(client_id, tenant_id, include_excluded=True)
        return existing.historico_atualizacoes if existing else None
