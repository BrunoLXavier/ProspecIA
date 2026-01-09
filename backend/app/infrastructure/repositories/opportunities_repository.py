"""Repository for opportunities management (RF-05 Pipeline)."""

import inspect
from datetime import UTC, datetime
from typing import Any, Dict, Optional, Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models.opportunity import Opportunity, OpportunityStage, OpportunityStatus


class OpportunitiesRepository:
    """Repository for managing opportunities with RLS support."""

    def __init__(self, session: AsyncSession, kafka_producer: Any):
        self.session = session
        self.kafka_producer = kafka_producer

    async def create(self, opportunity: Opportunity) -> Opportunity:
        """Create a new opportunity and emit audit event."""
        add_result = self.session.add(opportunity)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result
        refresh_result = self.session.refresh(opportunity)
        if inspect.isawaitable(refresh_result):
            await refresh_result

        await self.kafka_producer.send_event(
            topic="opportunities",
            event_type="opportunity.created",
            entity_id=str(opportunity.id),
            tenant_id=str(opportunity.tenant_id),
            user_id=str(opportunity.criado_por),
            data={
                "title": opportunity.title,
                "client_id": str(opportunity.client_id),
                "funding_source_id": str(opportunity.funding_source_id),
                "stage": opportunity.stage.value,
            },
        )

        return opportunity

    async def get(
        self,
        opportunity_id: UUID,
        tenant_id: UUID,
        include_excluded: bool = False,
    ) -> Optional[Opportunity]:
        """Get opportunity by ID (soft-delete aware)."""

        stmt = select(Opportunity).where(
            Opportunity.id == opportunity_id,
            Opportunity.tenant_id == tenant_id,
        )
        if not include_excluded:
            stmt = stmt.where(Opportunity.status != OpportunityStatus.EXCLUDED)

        result = await self.session.execute(stmt)
        value = result.scalar_one_or_none()
        if inspect.isawaitable(value):
            value = await value
        return value

    async def list(
        self,
        tenant_id: UUID,
        status: Optional[OpportunityStatus] = None,
        stage: Optional[OpportunityStage] = None,
        client_id: Optional[UUID] = None,
        funding_source_id: Optional[UUID] = None,
        responsible_user_id: Optional[UUID] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Opportunity], int]:
        """List opportunities with filters and pagination."""

        base_query = select(Opportunity).where(
            Opportunity.tenant_id == tenant_id,
            Opportunity.status != OpportunityStatus.EXCLUDED,
        )

        if status:
            base_query = base_query.where(Opportunity.status == status)

        if stage:
            base_query = base_query.where(Opportunity.stage == stage)

        if client_id:
            base_query = base_query.where(Opportunity.client_id == client_id)

        if funding_source_id:
            base_query = base_query.where(Opportunity.funding_source_id == funding_source_id)

        if responsible_user_id:
            base_query = base_query.where(Opportunity.responsible_user_id == responsible_user_id)

        if min_score is not None:
            base_query = base_query.where(Opportunity.score >= min_score)

        if max_score is not None:
            base_query = base_query.where(Opportunity.score <= max_score)

        query = base_query.order_by(Opportunity.criado_em.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        scalars = result.scalars()
        if inspect.isawaitable(scalars):
            scalars = await scalars
        opportunities = scalars.all()
        if inspect.isawaitable(opportunities):
            opportunities = await opportunities

        count_stmt = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()
        if inspect.isawaitable(total):
            total = await total
        total = total or 0

        return opportunities, total

    async def update(
        self,
        opportunity_id: UUID,
        tenant_id: UUID,
        updates: Dict[str, Any],
        updated_by: UUID,
        motivo: Optional[str] = None,
    ) -> Optional[Opportunity]:
        """Update opportunity with versioning."""

        existing = await self.get(opportunity_id, tenant_id, include_excluded=True)
        if not existing:
            return None

        history_entry: Dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "usuario_id": str(updated_by),
            "acao": "atualizacao",
            "campos": updates,
        }
        if motivo:
            history_entry["motivo"] = motivo

        historico = existing.historico_atualizacoes or []
        historico.append(history_entry)
        existing.historico_atualizacoes = historico

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
            topic="opportunities",
            event_type="opportunity.updated",
            entity_id=str(opportunity_id),
            tenant_id=str(tenant_id),
            user_id=str(updated_by),
            data={"updates": list(updates.keys()), "motivo": motivo},
        )

        return existing

    async def transition_stage(
        self,
        opportunity_id: UUID,
        tenant_id: UUID,
        new_stage: OpportunityStage,
        updated_by: UUID,
        motivo: str,
    ) -> Optional[Opportunity]:
        """Transition opportunity to a new stage with history tracking."""

        existing = await self.get(opportunity_id, tenant_id)
        if not existing:
            return None

        if not existing.can_transition_to(new_stage):
            return None

        existing.add_transition(new_stage, updated_by, motivo)
        existing.atualizado_por = updated_by

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
            topic="opportunities",
            event_type="opportunity.stage_transition",
            entity_id=str(opportunity_id),
            tenant_id=str(tenant_id),
            user_id=str(updated_by),
            data={
                "from_stage": existing.historico_transicoes[-1]["from_stage"],
                "to_stage": new_stage.value,
                "motivo": motivo,
            },
        )

        return existing

    async def delete(
        self,
        opportunity_id: UUID,
        tenant_id: UUID,
        deleted_by: UUID,
        motivo: str,
    ) -> bool:
        """Soft delete an opportunity (status -> excluded)."""

        existing = await self.get(opportunity_id, tenant_id)
        if not existing:
            return False

        history_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "usuario_id": str(deleted_by),
            "acao": "exclusao",
            "campos": {"status": OpportunityStatus.EXCLUDED.value},
            "motivo": motivo,
        }

        historico = existing.historico_atualizacoes or []
        historico.append(history_entry)
        existing.historico_atualizacoes = historico

        existing.status = OpportunityStatus.EXCLUDED
        existing.atualizado_por = deleted_by
        existing.atualizado_em = datetime.now(UTC)

        add_result = self.session.add(existing)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result

        await self.kafka_producer.send_event(
            topic="opportunities",
            event_type="opportunity.deleted",
            entity_id=str(opportunity_id),
            tenant_id=str(tenant_id),
            user_id=str(deleted_by),
            data={"motivo": motivo},
        )

        return True

    async def get_transitions(self, opportunity_id: UUID, tenant_id: UUID) -> Optional[list]:
        """Return stage transition history."""

        existing = await self.get(opportunity_id, tenant_id, include_excluded=True)
        return existing.historico_transicoes if existing else None

    async def get_history(self, opportunity_id: UUID, tenant_id: UUID) -> Optional[list]:
        """Return general audit history."""

        existing = await self.get(opportunity_id, tenant_id, include_excluded=True)
        return existing.historico_atualizacoes if existing else None
