"""
Domain model for Funding Sources (Fontes de Fomento).

This module defines the FundingSource entity with versioning support,
soft delete capabilities, and multi-tenancy support.

Wave 2 - RF-02: Gestão de Fontes de Fomento
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, Date, DateTime, Enum as SAEnum, BigInteger, SmallInteger
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.adapters.postgres.connection import Base


class FundingSourceStatus(str, Enum):
    """Status lifecycle for funding sources."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


class FundingSourceType(str, Enum):
    """Types of funding sources following Brazilian innovation ecosystem."""

    GRANT = "grant"
    FINANCING = "financing"
    EQUITY = "equity"
    NON_REFUNDABLE = "non_refundable"
    TAX_INCENTIVE = "tax_incentive"
    MIXED = "mixed"


class FundingSource(Base):
    """SQLAlchemy ORM model for funding sources."""

    __tablename__ = "funding_sources"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(SAEnum(FundingSourceType, name="funding_source_type", native_enum=False), nullable=False)
    sectors = Column(JSONB, nullable=False, default=list)
    amount = Column(BigInteger, nullable=False)
    trl_min = Column(SmallInteger, nullable=False)
    trl_max = Column(SmallInteger, nullable=False)
    deadline = Column(Date, nullable=False)
    url = Column(String(500), nullable=True)
    requirements = Column(Text, nullable=True)
    status = Column(SAEnum(FundingSourceStatus, name="funding_source_status", native_enum=False), nullable=False, default=FundingSourceStatus.ACTIVE)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    historico_atualizacoes = Column(JSONB, nullable=False, default=list)
    criado_por = Column(PGUUID(as_uuid=True), nullable=False)
    atualizado_por = Column(PGUUID(as_uuid=True), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def validate_trl(self) -> None:
        if not (1 <= self.trl_min <= 9):
            raise ValueError(f"trl_min must be between 1 and 9, got {self.trl_min}")
        if not (1 <= self.trl_max <= 9):
            raise ValueError(f"trl_max must be between 1 and 9, got {self.trl_max}")
        if self.trl_min > self.trl_max:
            raise ValueError("trl_min cannot be greater than trl_max")

    def can_transition_to(self, new_status: FundingSourceStatus) -> bool:
        """Check if status transition is valid."""

        allowed_transitions: Dict[FundingSourceStatus, List[FundingSourceStatus]] = {
            FundingSourceStatus.ACTIVE: [FundingSourceStatus.INACTIVE, FundingSourceStatus.ARCHIVED, FundingSourceStatus.EXCLUDED],
            FundingSourceStatus.INACTIVE: [FundingSourceStatus.ACTIVE, FundingSourceStatus.ARCHIVED, FundingSourceStatus.EXCLUDED],
            FundingSourceStatus.ARCHIVED: [FundingSourceStatus.ACTIVE, FundingSourceStatus.EXCLUDED],
            FundingSourceStatus.EXCLUDED: [],
        }
        return new_status in allowed_transitions.get(self.status, [])

    def add_audit_entry(self, campo: str, valor_antigo: Any, valor_novo: Any, motivo: str, usuario_id: UUID) -> None:
        """Add an entry to the audit trail (historico_atualizacoes)."""

        entry = {
            "campo": campo,
            "valor_antigo": valor_antigo,
            "valor_novo": valor_novo,
            "motivo": motivo,
            "usuario_id": str(usuario_id),
            "timestamp": datetime.utcnow().isoformat(),
        }
        historico = self.historico_atualizacoes or []
        historico.append(entry)
        self.historico_atualizacoes = historico

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<FundingSource(id={self.id}, name='{self.name}', "
            f"type={self.type.value}, status={self.status.value})>"
        )
