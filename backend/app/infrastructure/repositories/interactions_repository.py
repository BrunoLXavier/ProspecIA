"""Repository for client interactions management (RF-04 CRM)."""

import inspect
from datetime import UTC, datetime
from typing import Any, Dict, Optional, Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.kafka.producer import KafkaProducer
from app.infrastructure.models.interaction import (
    Interaction,
    InteractionOutcome,
    InteractionStatus,
    InteractionType,
)


class InteractionsRepository:
    """Repository for managing client interactions."""

    def __init__(self, session: AsyncSession, kafka_producer: KafkaProducer):
        self.session = session
        self.kafka_producer = kafka_producer

    async def create(self, interaction: Interaction) -> Interaction:
        """Create a new interaction (ORM)."""
        add_result = self.session.add(interaction)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result
        refresh_result = self.session.refresh(interaction)
        if inspect.isawaitable(refresh_result):
            await refresh_result

        await self.kafka_producer.send_event(
            topic="interactions",
            event_type="interaction.created",
            entity_id=str(interaction.id),
            tenant_id=str(interaction.tenant_id),
            user_id=str(interaction.criado_por),
            data={
                "client_id": str(interaction.client_id),
                "type": interaction.type.value,
                "title": interaction.title,
            },
        )
        return interaction

    async def get(self, interaction_id: UUID, tenant_id: UUID) -> Optional[Interaction]:
        """Get interaction by ID respecting soft-delete."""
        stmt = select(Interaction).where(
            Interaction.id == interaction_id,
            Interaction.tenant_id == tenant_id,
            Interaction.status != InteractionStatus.EXCLUDED,
        )
        result = await self.session.execute(stmt)
        value = result.scalar_one_or_none()
        if inspect.isawaitable(value):
            value = await value
        return value

    async def list_by_client(
        self,
        client_id: UUID,
        tenant_id: UUID,
        interaction_type: Optional[InteractionType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Interaction], int]:
        """List timeline interactions for a client."""
        base_query = select(Interaction).where(
            Interaction.client_id == client_id,
            Interaction.tenant_id == tenant_id,
            Interaction.status != InteractionStatus.EXCLUDED,
        )
        if interaction_type:
            base_query = base_query.where(Interaction.type == interaction_type)

        query = base_query.order_by(Interaction.date.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        scalars = result.scalars()
        if inspect.isawaitable(scalars):
            scalars = await scalars
        interactions = scalars.all()
        if inspect.isawaitable(interactions):
            interactions = await interactions

        count_stmt = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()
        if inspect.isawaitable(total):
            total = await total
        total = total or 0

        return interactions, total

    async def list(
        self,
        tenant_id: UUID,
        outcome: Optional[InteractionOutcome] = None,
        status: Optional[InteractionStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Interaction], int]:
        """List all interactions with filters and pagination."""
        base_query = select(Interaction).where(
            Interaction.tenant_id == tenant_id, Interaction.status != InteractionStatus.EXCLUDED
        )
        if outcome:
            base_query = base_query.where(Interaction.outcome == outcome)
        if status:
            base_query = base_query.where(Interaction.status == status)

        query = base_query.order_by(Interaction.date.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        scalars = result.scalars()
        if inspect.isawaitable(scalars):
            scalars = await scalars
        interactions = scalars.all()
        if inspect.isawaitable(interactions):
            interactions = await interactions

        count_stmt = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()
        if inspect.isawaitable(total):
            total = await total
        total = total or 0

        return interactions, total

    async def update(
        self,
        interaction_id: UUID,
        tenant_id: UUID,
        updates: Dict[str, Any],
    ) -> Optional[Interaction]:
        """Update interaction fields and emit audit."""
        existing = await self.get(interaction_id, tenant_id)
        if not existing:
            return None

        for key, value in updates.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        existing.add_history(updates, existing.criado_por, "atualizacao")
        existing.atualizado_por = existing.criado_por
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
            topic="interactions",
            event_type="interaction.updated",
            entity_id=str(interaction_id),
            tenant_id=str(tenant_id),
            user_id=str(existing.criado_por),
            data={"updates": list(updates.keys())},
        )
        return existing

    async def delete(self, interaction_id: UUID, tenant_id: UUID) -> bool:
        """Soft delete an interaction (status -> cancelled)."""
        existing = await self.get(interaction_id, tenant_id)
        if not existing:
            return False
        existing.status = InteractionStatus.CANCELLED
        existing.add_history(
            {"status": InteractionStatus.CANCELLED.value},
            usuario_id=existing.criado_por,
            acao="exclusao",
        )
        existing.atualizado_em = datetime.now(UTC)

        add_result = self.session.add(existing)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result

        await self.kafka_producer.send_event(
            topic="interactions",
            event_type="interaction.deleted",
            entity_id=str(interaction_id),
            tenant_id=str(tenant_id),
            user_id=str(existing.criado_por),
        )
        return True
