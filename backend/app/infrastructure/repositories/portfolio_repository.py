"""Repository for portfolio management (RF-03)."""

import inspect
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, Optional, Sequence
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.kafka.producer import KafkaProducer
from app.domain.portfolio import Competence, Institute, InstituteStatus, Project, ProjectStatus


class InstitutesRepository:
    """Repository for managing institutes with RLS support."""

    def __init__(self, session: AsyncSession, kafka_producer: KafkaProducer):
        self.session = session
        self.kafka_producer = kafka_producer

    async def create(self, institute: Institute) -> Institute:
        """Create a new institute (ORM)."""
        add_result = self.session.add(institute)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result
        refresh_result = self.session.refresh(institute)
        if inspect.isawaitable(refresh_result):
            await refresh_result

        await self.kafka_producer.send_event(
            topic="institutes",
            event_type="institute_created",
            entity_id=str(institute.id),
            tenant_id=str(institute.tenant_id),
            user_id=str(institute.criado_por),
            data={"name": institute.name, "acronym": institute.acronym},
        )
        return institute

    async def get(
        self,
        institute_id: UUID,
        tenant_id: UUID,
        include_excluded: bool = False,
    ) -> Optional[Institute]:
        """Get institute by ID with soft-delete awareness."""
        stmt = select(Institute).where(
            Institute.id == institute_id, Institute.tenant_id == tenant_id
        )
        if not include_excluded:
            stmt = stmt.where(Institute.status != InstituteStatus.EXCLUDED)
        result = await self.session.execute(stmt)
        value = result.scalar_one_or_none()
        if inspect.isawaitable(value):
            value = await value
        return value

    async def list(
        self,
        tenant_id: UUID,
        status: Optional[InstituteStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Institute], int]:
        """List institutes with filters and pagination."""
        base_query = select(Institute).where(
            Institute.tenant_id == tenant_id, Institute.status != InstituteStatus.EXCLUDED
        )
        if status:
            base_query = base_query.where(Institute.status == status)
        if search:
            search_pattern = f"%{search}%"
            base_query = base_query.where(
                or_(
                    Institute.name.ilike(search_pattern),
                    Institute.description.ilike(search_pattern),
                )
            )

        query = base_query.order_by(Institute.name).offset(skip).limit(limit)
        result = await self.session.execute(query)
        scalars = result.scalars()
        if inspect.isawaitable(scalars):
            scalars = await scalars
        institutes = scalars.all()
        if inspect.isawaitable(institutes):
            institutes = await institutes

        count_stmt = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()
        if inspect.isawaitable(total):
            total = await total
        total = total or 0

        return institutes, total

    async def update(
        self,
        institute_id: UUID,
        tenant_id: UUID,
        updates: Dict[str, Any],
        updated_by: UUID,
        motivo: str | None = None,
    ) -> Optional[Institute]:
        """Update institute with versioning (ORM)."""
        existing = await self.get(institute_id, tenant_id, include_excluded=True)
        if not existing:
            return None

        historico_atual = list(existing.historico_atualizacoes or [])
        for field, new_value in updates.items():
            if field in ("id", "tenant_id", "criado_por", "criado_em", "historico_atualizacoes"):
                continue
            old_value = getattr(existing, field, None)
            if isinstance(old_value, Enum):
                old_value = old_value.value
            if isinstance(new_value, Enum):
                new_value = new_value.value
            if old_value != new_value:
                entry = {
                    "campo": field,
                    "valor_anterior": old_value,
                    "valor_novo": new_value,
                    "atualizado_por": str(updated_by),
                    "atualizado_em": datetime.now(UTC).isoformat(),
                }
                if motivo:
                    entry["motivo"] = motivo
                historico_atual.append(entry)
        existing.historico_atualizacoes = historico_atual

        for k, v in updates.items():
            if hasattr(existing, k):
                setattr(existing, k, v)
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
            topic="institutes",
            event_type="institute_updated",
            entity_id=str(institute_id),
            tenant_id=str(tenant_id),
            user_id=str(updated_by),
            data={"updates": list(updates.keys()), "motivo": motivo},
        )
        return existing

    async def delete(
        self,
        institute_id: UUID,
        tenant_id: UUID,
        deleted_by: UUID,
        motivo: str,
    ) -> bool:
        """Soft delete institute (status -> excluded)."""
        existing = await self.get(institute_id, tenant_id)
        if not existing:
            return False
        historico = list(existing.historico_atualizacoes or [])
        historico.append(
            {
                "campo": "status",
                "valor_anterior": existing.status.value,
                "valor_novo": InstituteStatus.EXCLUDED.value,
                "atualizado_por": str(deleted_by),
                "atualizado_em": datetime.now(UTC).isoformat(),
                "motivo": motivo,
            }
        )
        existing.historico_atualizacoes = historico
        existing.status = InstituteStatus.EXCLUDED
        existing.atualizado_por = deleted_by
        existing.atualizado_em = datetime.now(UTC)
        add_result = self.session.add(existing)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result
        await self.kafka_producer.send_event(
            topic="institutes",
            event_type="institute_deleted",
            entity_id=str(institute_id),
            tenant_id=str(tenant_id),
            user_id=str(deleted_by),
            data={"motivo": motivo},
        )
        return True


class ProjectsRepository:
    """Repository for managing projects with RLS support."""

    def __init__(self, session: AsyncSession, kafka_producer: KafkaProducer):
        self.session = session
        self.kafka_producer = kafka_producer

    async def create(self, project: Project) -> Project:
        """Create a new project (ORM)."""
        add_result = self.session.add(project)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result
        refresh_result = self.session.refresh(project)
        if inspect.isawaitable(refresh_result):
            await refresh_result

        await self.kafka_producer.send_event(
            topic="projects",
            event_type="project_created",
            entity_id=str(project.id),
            tenant_id=str(project.tenant_id),
            user_id=str(project.criado_por),
            data={
                "title": project.title,
                "institute_id": str(project.institute_id),
                "trl": project.trl,
            },
        )
        return project

    async def get(
        self,
        project_id: UUID,
        tenant_id: UUID,
        include_excluded: bool = False,
    ) -> Optional[Project]:
        """Get project by ID with soft-delete awareness."""
        stmt = select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
        if not include_excluded:
            stmt = stmt.where(Project.status != ProjectStatus.EXCLUDED)
        result = await self.session.execute(stmt)
        value = result.scalar_one_or_none()
        if inspect.isawaitable(value):
            value = await value
        return value

    async def list(
        self,
        tenant_id: UUID,
        status: Optional[ProjectStatus] = None,
        institute_id: Optional[UUID] = None,
        min_trl: Optional[int] = None,
        max_trl: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Project], int]:
        """List projects with filters and pagination."""
        base_query = select(Project).where(
            Project.tenant_id == tenant_id, Project.status != ProjectStatus.EXCLUDED
        )
        if status:
            base_query = base_query.where(Project.status == status)
        if institute_id:
            base_query = base_query.where(Project.institute_id == institute_id)
        if min_trl is not None:
            base_query = base_query.where(Project.trl >= min_trl)
        if max_trl is not None:
            base_query = base_query.where(Project.trl <= max_trl)

        query = base_query.order_by(Project.criado_em.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        scalars = result.scalars()
        if inspect.isawaitable(scalars):
            scalars = await scalars
        projects = scalars.all()
        if inspect.isawaitable(projects):
            projects = await projects

        count_stmt = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()
        if inspect.isawaitable(total):
            total = await total
        total = total or 0

        return projects, total

    async def update(
        self,
        project_id: UUID,
        tenant_id: UUID,
        updates: Dict[str, Any],
        updated_by: UUID,
        motivo: str | None = None,
    ) -> Optional[Project]:
        """Update project with versioning (ORM)."""
        existing = await self.get(project_id, tenant_id, include_excluded=True)
        if not existing:
            return None

        historico_atual = list(existing.historico_atualizacoes or [])
        for field, new_value in updates.items():
            if field in ("id", "tenant_id", "criado_por", "criado_em", "historico_atualizacoes"):
                continue
            old_value = getattr(existing, field, None)
            if isinstance(old_value, Enum):
                old_value = old_value.value
            if isinstance(new_value, Enum):
                new_value = new_value.value
            if old_value != new_value:
                entry = {
                    "campo": field,
                    "valor_anterior": old_value,
                    "valor_novo": new_value,
                    "atualizado_por": str(updated_by),
                    "atualizado_em": datetime.now(UTC).isoformat(),
                }
                if motivo:
                    entry["motivo"] = motivo
                historico_atual.append(entry)
        existing.historico_atualizacoes = historico_atual

        for k, v in updates.items():
            if hasattr(existing, k):
                setattr(existing, k, v)
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
            topic="projects",
            event_type="project_updated",
            entity_id=str(project_id),
            tenant_id=str(tenant_id),
            user_id=str(updated_by),
            data={"updates": list(updates.keys()), "motivo": motivo},
        )
        return existing

    async def delete(
        self,
        project_id: UUID,
        tenant_id: UUID,
        deleted_by: UUID,
        motivo: str,
    ) -> bool:
        """Soft delete project (status -> excluded)."""
        existing = await self.get(project_id, tenant_id)
        if not existing:
            return False
        historico = list(existing.historico_atualizacoes or [])
        historico.append(
            {
                "campo": "status",
                "valor_anterior": existing.status.value,
                "valor_novo": ProjectStatus.EXCLUDED.value,
                "atualizado_por": str(deleted_by),
                "atualizado_em": datetime.now(UTC).isoformat(),
                "motivo": motivo,
            }
        )
        existing.historico_atualizacoes = historico
        existing.status = ProjectStatus.EXCLUDED
        existing.atualizado_por = deleted_by
        existing.atualizado_em = datetime.now(UTC)
        add_result = self.session.add(existing)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result
        await self.kafka_producer.send_event(
            topic="projects",
            event_type="project_deleted",
            entity_id=str(project_id),
            tenant_id=str(tenant_id),
            user_id=str(deleted_by),
            data={"motivo": motivo},
        )
        return True


class CompetencesRepository:
    """Repository for managing competences (catalog)."""

    def __init__(self, session: AsyncSession, kafka_producer: KafkaProducer):
        self.session = session
        self.kafka_producer = kafka_producer

    async def create(self, competence: Competence) -> Competence:
        """Create a new competence (ORM)."""
        add_result = self.session.add(competence)
        if inspect.isawaitable(add_result):
            await add_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result
        refresh_result = self.session.refresh(competence)
        if inspect.isawaitable(refresh_result):
            await refresh_result

        await self.kafka_producer.send_event(
            topic="competences",
            event_type="competence_created",
            entity_id=str(competence.id),
            tenant_id=str(competence.tenant_id),
            user_id=str(competence.criado_por),
            data={"name": competence.name, "category": competence.category},
        )
        return competence

    async def get(
        self,
        competence_id: UUID,
        tenant_id: UUID,
    ) -> Optional[Competence]:
        """Get competence by ID with RLS."""
        stmt = select(Competence).where(
            Competence.id == competence_id, Competence.tenant_id == tenant_id
        )
        result = await self.session.execute(stmt)
        value = result.scalar_one_or_none()
        if inspect.isawaitable(value):
            value = await value
        return value

    async def list(
        self,
        tenant_id: UUID,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Competence], int]:
        """List competences with filters and pagination."""
        base_query = select(Competence).where(Competence.tenant_id == tenant_id)
        if category:
            base_query = base_query.where(Competence.category == category)

        query = base_query.order_by(Competence.name).offset(skip).limit(limit)
        result = await self.session.execute(query)
        scalars = result.scalars()
        if inspect.isawaitable(scalars):
            scalars = await scalars
        competences = scalars.all()
        if inspect.isawaitable(competences):
            competences = await competences

        count_stmt = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar()
        if inspect.isawaitable(total):
            total = await total
        total = total or 0

        return competences, total

    async def delete(
        self,
        competence_id: UUID,
        tenant_id: UUID,
    ) -> bool:
        """Hard delete a competence (catalog item)."""
        existing = await self.get(competence_id, tenant_id)
        if not existing:
            return False
        delete_result = self.session.delete(existing)
        if inspect.isawaitable(delete_result):
            await delete_result
        commit_result = self.session.commit()
        if inspect.isawaitable(commit_result):
            await commit_result

        await self.kafka_producer.send_event(
            topic="competences",
            event_type="competence_deleted",
            entity_id=str(competence_id),
            tenant_id=str(tenant_id),
            user_id=str(existing.criado_por),
            data={"name": existing.name},
        )
        return True
