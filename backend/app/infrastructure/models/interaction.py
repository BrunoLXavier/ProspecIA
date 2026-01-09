from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.adapters.postgres.connection import Base


class InteractionType(str, Enum):
    MEETING = "meeting"
    EMAIL = "email"
    CALL = "call"
    VISIT = "visit"
    EVENT = "event"
    OTHER = "other"


class InteractionOutcome(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    PENDING = "pending"


class InteractionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(PGUUID(as_uuid=True), nullable=False)
    title = Column("subject", String(255), nullable=False)
    description = Column("summary", Text, nullable=False)
    type = Column(
        SAEnum(InteractionType, name="interaction_type", native_enum=False), nullable=False
    )
    date = Column(DateTime(timezone=True), nullable=False)
    outcome = Column(
        SAEnum(InteractionOutcome, name="interaction_outcome", native_enum=False),
        nullable=False,
        default=InteractionOutcome.PENDING,
    )
    next_steps = Column(Text, nullable=True)
    participants = Column(JSONB, nullable=False, default=list)
    status = Column(
        SAEnum(InteractionStatus, name="interaction_status", native_enum=False),
        nullable=False,
        default=InteractionStatus.ACTIVE,
    )
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    historico_atualizacoes = Column(JSONB, nullable=False, default=list)
    criado_por = Column(PGUUID(as_uuid=True), nullable=False)
    atualizado_por = Column(PGUUID(as_uuid=True), nullable=False)
    criado_em = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(datetime.UTC)
    )
    atualizado_em = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(datetime.UTC)
    )

    def add_history(self, campos: Dict[str, Any], usuario_id: UUID, acao: str) -> None:
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "usuario_id": str(usuario_id),
            "acao": acao,
            "campos": campos,
        }
        historico = self.historico_atualizacoes or []
        historico.append(entry)
        self.historico_atualizacoes = historico

    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, client_id={self.client_id}, type={self.type.value})>"
