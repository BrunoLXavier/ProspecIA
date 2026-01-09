"""
Repository for FundingSource persistence.

Implements async CRUD operations with:
- Row-Level Security (RLS) filtering by tenant_id
- Soft delete (status=excluded, never hard DELETE)
- Kafka audit logging for all operations
- Status transition validation
- Full audit trail in historico_atualizacoes

Wave 2 - RF-02: Gestão de Fontes de Fomento
Following patterns from Wave 1 IngestaoRepository
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.kafka.producer import KafkaProducer
from app.domain.funding_source import FundingSource, FundingSourceStatus, FundingSourceType

logger = structlog.get_logger()


class FundingSourcesRepository:
    """
    Repository for FundingSource persistence with RLS and audit logging.

    Implements Repository pattern (SRP) and Dependency Inversion Principle (DIP).
    All database operations are isolated here, domain logic stays in entity.
    """

    def __init__(
        self, session: AsyncSession, kafka_producer: Optional[KafkaProducer] = None
    ) -> None:
        """
        Initialize repository with database session and optional Kafka producer.

        Args:
            session: Async SQLAlchemy session
            kafka_producer: Optional Kafka producer for audit logging
        """
        self.session = session
        self.kafka_producer = kafka_producer
        self._logger = logger.bind(repository="FundingSourcesRepository")

    async def create(
        self,
        name: str,
        description: str,
        type: FundingSourceType,
        sectors: List[str],
        amount: int,
        trl_min: int,
        trl_max: int,
        deadline: datetime,
        url: Optional[str],
        requirements: Optional[str],
        tenant_id: UUID,
        criado_por: UUID,
    ) -> FundingSource:
        """
        Create a new funding source.

        Args:
            name: Funding source name
            description: Detailed description
            type: Funding type enum
            sectors: List of applicable sectors
            amount: Amount in BRL cents
            trl_min: Minimum TRL (1-9)
            trl_max: Maximum TRL (1-9)
            deadline: Application deadline
            url: Optional official URL
            requirements: Optional eligibility requirements
            tenant_id: Tenant identifier for multi-tenancy
            criado_por: Creator user ID

        Returns:
            Created FundingSource entity

        Raises:
            ValueError: If validation fails
        """
        from sqlalchemy import text

        # Validate TRL ranges (domain validation)
        if not (1 <= trl_min <= 9):
            raise ValueError(f"trl_min must be between 1 and 9, got {trl_min}")
        if not (1 <= trl_max <= 9):
            raise ValueError(f"trl_max must be between 1 and 9, got {trl_max}")
        if trl_min > trl_max:
            raise ValueError(f"trl_min ({trl_min}) cannot be greater than trl_max ({trl_max})")

        # Insert into database
        query = text(
            """
            INSERT INTO funding_sources (
                name, description, type, sectors, amount, trl_min, trl_max,
                deadline, url, requirements, status, tenant_id,
                historico_atualizacoes, criado_por, atualizado_por
            ) VALUES (
                :name, :description, :type, :sectors, :amount, :trl_min, :trl_max,
                :deadline, :url, :requirements, 'active', :tenant_id,
                '[]'::jsonb, :criado_por, :criado_por
            )
            RETURNING id, criado_em, atualizado_em
        """
        )

        result = await self.session.execute(
            query,
            {
                "name": name,
                "description": description,
                "type": type.value,
                "sectors": sectors,
                "amount": amount,
                "trl_min": trl_min,
                "trl_max": trl_max,
                "deadline": deadline,
                "url": url,
                "requirements": requirements,
                "tenant_id": str(tenant_id),
                "criado_por": str(criado_por),
            },
        )

        row = result.fetchone()
        await self.session.commit()

        # Create domain entity
        entity = FundingSource(
            id=row[0],
            name=name,
            description=description,
            type=type,
            sectors=sectors,
            amount=amount,
            trl_min=trl_min,
            trl_max=trl_max,
            deadline=deadline.date() if hasattr(deadline, "date") else deadline,
            url=url,
            requirements=requirements,
            status=FundingSourceStatus.ACTIVE,
            tenant_id=tenant_id,
            historico_atualizacoes=[],
            criado_por=criado_por,
            atualizado_por=criado_por,
            criado_em=row[1],
            atualizado_em=row[2],
        )

        # Kafka audit logging
        if self.kafka_producer:
            await self.kafka_producer.send_message(
                topic="funding-sources-events",
                key=str(entity.id),
                value={
                    "event_type": "funding_source_created",
                    "funding_source_id": str(entity.id),
                    "name": name,
                    "type": type.value,
                    "tenant_id": str(tenant_id),
                    "criado_por": str(criado_por),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

        self._logger.info(
            "funding_source_created",
            funding_source_id=str(entity.id),
            name=name,
            tenant_id=str(tenant_id),
        )

        return entity

    async def find_by_id(
        self,
        funding_source_id: UUID,
        tenant_id: UUID,
        include_excluded: bool = False,
    ) -> Optional[FundingSource]:
        """
        Find funding source by ID with RLS filtering.

        Args:
            funding_source_id: Funding source UUID
            tenant_id: Tenant identifier for RLS
            include_excluded: Whether to include soft-deleted records

        Returns:
            FundingSource entity or None if not found
        """
        from sqlalchemy import text

        status_filter = "" if include_excluded else "AND status != 'excluded'"

        query = text(
            f"""
            SELECT
                id, name, description, type, sectors, amount, trl_min, trl_max,
                deadline, url, requirements, status, tenant_id, historico_atualizacoes,
                criado_por, atualizado_por, criado_em, atualizado_em
            FROM funding_sources
            WHERE id = :id AND tenant_id = :tenant_id {status_filter}
        """
        )

        result = await self.session.execute(
            query, {"id": str(funding_source_id), "tenant_id": str(tenant_id)}
        )

        row = result.fetchone()
        if not row:
            return None

        return self._row_to_entity(row)

    async def list(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[List[FundingSourceStatus]] = None,
        type_filter: Optional[List[FundingSourceType]] = None,
        sector_filter: Optional[List[str]] = None,
    ) -> List[FundingSource]:
        """
        List funding sources with RLS filtering and pagination.

        Args:
            tenant_id: Tenant identifier for RLS
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            status_filter: Optional list of statuses to filter by
            type_filter: Optional list of types to filter by
            sector_filter: Optional list of sectors to filter by (any match)

        Returns:
            List of FundingSource entities
        """
        from sqlalchemy import text

        # Build dynamic WHERE clause
        where_clauses = ["tenant_id = :tenant_id"]
        params: Dict[str, Any] = {
            "tenant_id": str(tenant_id),
            "skip": skip,
            "limit": limit,
        }

        if status_filter:
            statuses = [s.value for s in status_filter]
            where_clauses.append(f"status = ANY(ARRAY{statuses}::funding_source_status[])")
        else:
            where_clauses.append("status != 'excluded'")  # Default: exclude soft-deleted

        if type_filter:
            types = [t.value for t in type_filter]
            where_clauses.append(f"type = ANY(ARRAY{types}::funding_source_type[])")

        if sector_filter:
            # Use JSONB containment operator ?| (overlaps)
            where_clauses.append("sectors ?| ARRAY[:sectors]")
            params["sectors"] = sector_filter

        where_sql = " AND ".join(where_clauses)

        query = text(
            f"""
            SELECT
                id, name, description, type, sectors, amount, trl_min, trl_max,
                deadline, url, requirements, status, tenant_id, historico_atualizacoes,
                criado_por, atualizado_por, criado_em, atualizado_em
            FROM funding_sources
            WHERE {where_sql}
            ORDER BY deadline ASC, criado_em DESC
            LIMIT :limit OFFSET :skip
        """
        )

        result = await self.session.execute(query, params)

        return [self._row_to_entity(row) for row in result.fetchall()]

    async def update(
        self,
        funding_source_id: UUID,
        tenant_id: UUID,
        updates: Dict[str, Any],
        motivo: str,
        atualizado_por: UUID,
    ) -> Optional[FundingSource]:
        """
        Update funding source with versioning.

        Implements PT-01 (Versionamento): tracks all changes in historico_atualizacoes.

        Args:
            funding_source_id: Funding source UUID
            tenant_id: Tenant identifier for RLS
            updates: Dictionary of fields to update
            motivo: Reason for update (required for transparency)
            atualizado_por: User making the update

        Returns:
            Updated FundingSource entity or None if not found

        Raises:
            ValueError: If trying to update invalid fields or transition to invalid status
        """
        # Fetch current entity
        current = await self.find_by_id(funding_source_id, tenant_id)
        if not current:
            return None

        # Validate allowed fields
        allowed_fields = {
            "name",
            "description",
            "type",
            "sectors",
            "amount",
            "trl_min",
            "trl_max",
            "deadline",
            "url",
            "requirements",
            "status",
        }
        invalid_fields = set(updates.keys()) - allowed_fields
        if invalid_fields:
            raise ValueError(f"Cannot update fields: {invalid_fields}")

        # Validate status transition if status is being updated
        if "status" in updates:
            new_status = FundingSourceStatus(updates["status"])
            if not current.can_transition_to(new_status):
                raise ValueError(
                    f"Cannot transition from {current.status.value} to {new_status.value}"
                )

        # Build audit entries for historico_atualizacoes
        audit_entries = []
        for campo, valor_novo in updates.items():
            valor_antigo = getattr(current, campo)

            # Convert enums to values for comparison
            if isinstance(valor_antigo, Enum):
                valor_antigo = valor_antigo.value
            if isinstance(valor_novo, Enum):
                valor_novo = valor_novo.value

            if valor_antigo != valor_novo:
                audit_entry = {
                    "campo": campo,
                    "valor_antigo": valor_antigo,
                    "valor_novo": valor_novo,
                    "motivo": motivo,
                    "usuario_id": str(atualizado_por),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                audit_entries.append(audit_entry)

        if not audit_entries:
            # No actual changes, return current entity
            return current

        # Prepare update query
        from sqlalchemy import text

        set_clauses = []
        params: Dict[str, Any] = {
            "id": str(funding_source_id),
            "tenant_id": str(tenant_id),
            "atualizado_por": str(atualizado_por),
        }

        for campo, valor in updates.items():
            if isinstance(valor, Enum):
                valor = valor.value
            set_clauses.append(f"{campo} = :{campo}")
            params[campo] = valor

        # Append audit entries to historico_atualizacoes
        set_clauses.append(
            "historico_atualizacoes = historico_atualizacoes || :audit_entries::jsonb"
        )
        params["audit_entries"] = audit_entries

        set_clauses.append("atualizado_por = :atualizado_por")
        set_clauses.append("atualizado_em = now()")

        set_sql = ", ".join(set_clauses)

        query = text(
            f"""
            UPDATE funding_sources
            SET {set_sql}
            WHERE id = :id AND tenant_id = :tenant_id AND status != 'excluded'
            RETURNING atualizado_em
        """
        )

        result = await self.session.execute(query, params)
        row = result.fetchone()

        if not row:
            return None

        await self.session.commit()

        # Kafka audit logging
        if self.kafka_producer:
            await self.kafka_producer.send_message(
                topic="funding-sources-events",
                key=str(funding_source_id),
                value={
                    "event_type": "funding_source_updated",
                    "funding_source_id": str(funding_source_id),
                    "updates": updates,
                    "motivo": motivo,
                    "atualizado_por": str(atualizado_por),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        self._logger.info(
            "funding_source_updated",
            funding_source_id=str(funding_source_id),
            updates=list(updates.keys()),
            motivo=motivo,
        )

        # Fetch and return updated entity
        return await self.find_by_id(funding_source_id, tenant_id, include_excluded=False)

    async def soft_delete(
        self,
        funding_source_id: UUID,
        tenant_id: UUID,
        motivo: str,
        atualizado_por: UUID,
    ) -> bool:
        """
        Soft delete funding source (set status=excluded).

        Implements Regra 11 (Integridade): never hard DELETE.

        Args:
            funding_source_id: Funding source UUID
            tenant_id: Tenant identifier for RLS
            motivo: Reason for deletion (required)
            atualizado_por: User performing deletion

        Returns:
            True if deleted, False if not found
        """
        result = await self.update(
            funding_source_id=funding_source_id,
            tenant_id=tenant_id,
            updates={"status": FundingSourceStatus.EXCLUDED},
            motivo=motivo,
            atualizado_por=atualizado_por,
        )

        return result is not None

    def _row_to_entity(self, row: Any) -> FundingSource:
        """Convert database row to FundingSource entity."""
        return FundingSource(
            id=row[0],
            name=row[1],
            description=row[2],
            type=FundingSourceType(row[3]),
            sectors=row[4],
            amount=row[5],
            trl_min=row[6],
            trl_max=row[7],
            deadline=row[8],
            url=row[9],
            requirements=row[10],
            status=FundingSourceStatus(row[11]),
            tenant_id=row[12],
            historico_atualizacoes=row[13],
            criado_por=row[14],
            atualizado_por=row[15],
            criado_em=row[16],
            atualizado_em=row[17],
        )
