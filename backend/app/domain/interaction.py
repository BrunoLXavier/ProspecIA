"""
Domain model for Client Interactions (CRM).

Wave 2 - RF-04: Gestão de CRM
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.adapters.postgres.connection import Base


class InteractionType(str, Enum):
    """Types of interactions with clients."""

    MEETING = "meeting"  # Reunião
    EMAIL = "email"  # E-mail
    CALL = "call"  # Ligação
    VISIT = "visit"  # Visita técnica
    EVENT = "event"  # Evento/Workshop
    OTHER = "other"  # Outro


class InteractionOutcome(str, Enum):
    """Outcome/result of interaction."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    PENDING = "pending"


class InteractionStatus(str, Enum):
    """Status of interaction record."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


class Interaction(Base):
    """SQLAlchemy ORM model for interactions (timeline entries)."""

    __tablename__ = "interactions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(PGUUID(as_uuid=True), nullable=False)
    title = Column("subject", String(255), nullable=False)
    description = Column("summary", Text, nullable=False)
    type = Column(SAEnum(InteractionType, name="interaction_type", native_enum=False), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    outcome = Column(SAEnum(InteractionOutcome, name="interaction_outcome", native_enum=False), nullable=False, default=InteractionOutcome.PENDING)
    next_steps = Column(Text, nullable=True)
    participants = Column(JSONB, nullable=False, default=list)
    status = Column(SAEnum(InteractionStatus, name="interaction_status", native_enum=False), nullable=False, default=InteractionStatus.ACTIVE)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    historico_atualizacoes = Column(JSONB, nullable=False, default=list)
    criado_por = Column(PGUUID(as_uuid=True), nullable=False)
    atualizado_por = Column(PGUUID(as_uuid=True), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def add_history(self, campos: Dict[str, Any], usuario_id: UUID, acao: str) -> None:
        """Append an entry to the audit trail."""

        entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "usuario_id": str(usuario_id),
            "acao": acao,
            "campos": campos,
        }
        historico = self.historico_atualizacoes or []
        historico.append(entry)
        self.historico_atualizacoes = historico

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Interaction(id={self.id}, client_id={self.client_id}, type={self.type.value})>"
