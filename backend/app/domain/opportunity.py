"""Domain model for Opportunities (Pipeline - RF-05)."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Column, DateTime, Enum as SAEnum, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import validates

from app.adapters.postgres.connection import Base


class OpportunityStage(str, Enum):
    """Pipeline stages for opportunities."""

    INTELLIGENCE = "intelligence"
    VALIDATION = "validation"
    APPROACH = "approach"
    REGISTRATION = "registration"
    CONVERSION = "conversion"
    POST_SALE = "post_sale"


class OpportunityStatus(str, Enum):
    """Status for opportunities."""

    ACTIVE = "active"
    WON = "won"
    LOST = "lost"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


class Opportunity(Base):
    """SQLAlchemy ORM model for pipeline opportunities."""

    __tablename__ = "opportunities"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(PGUUID(as_uuid=True), nullable=False)
    funding_source_id = Column(PGUUID(as_uuid=True), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    stage = Column(
        SAEnum(OpportunityStage, name="opportunity_stage", native_enum=False),
        nullable=False,
        default=OpportunityStage.INTELLIGENCE,
    )
    score = Column(SmallInteger, nullable=False, default=0)
    estimated_value = Column(BigInteger, nullable=False, default=0)
    probability = Column(SmallInteger, nullable=False, default=50)
    expected_close_date = Column(DateTime(timezone=True), nullable=False)
    responsible_user_id = Column(PGUUID(as_uuid=True), nullable=False)
    status = Column(
        SAEnum(OpportunityStatus, name="opportunity_status", native_enum=False),
        nullable=False,
        default=OpportunityStatus.ACTIVE,
    )
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    historico_atualizacoes = Column(JSONB, nullable=False, default=list)
    historico_transicoes = Column(JSONB, nullable=False, default=list)
    criado_por = Column(PGUUID(as_uuid=True), nullable=False)
    atualizado_por = Column(PGUUID(as_uuid=True), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    @validates("score", "probability")
    def _validate_percentual(self, key: str, value: int) -> int:
        """Ensure score and probability stay within 0-100."""

        if value is None:
            return value
        if value < 0 or value > 100:
            raise ValueError(f"{key} must be between 0 and 100")
        return value

    def can_transition_to(self, new_stage: OpportunityStage) -> bool:
        """Validate stage transitions (one step forward only)."""

        allowed: Dict[OpportunityStage, List[OpportunityStage]] = {
            OpportunityStage.INTELLIGENCE: [OpportunityStage.VALIDATION],
            OpportunityStage.VALIDATION: [OpportunityStage.APPROACH],
            OpportunityStage.APPROACH: [OpportunityStage.REGISTRATION],
            OpportunityStage.REGISTRATION: [OpportunityStage.CONVERSION],
            OpportunityStage.CONVERSION: [OpportunityStage.POST_SALE],
            OpportunityStage.POST_SALE: [],
        }
        return new_stage in allowed.get(self.stage, [])

    def add_transition(self, new_stage: OpportunityStage, usuario_id: UUID, motivo: str) -> None:
        """Append transition to history and update current stage."""

        entry = {
            "from_stage": self.stage.value,
            "to_stage": new_stage.value,
            "usuario_id": str(usuario_id),
            "motivo": motivo,
            "timestamp": datetime.utcnow().isoformat(),
        }
        transicoes = self.historico_transicoes or []
        transicoes.append(entry)
        self.historico_transicoes = transicoes

        historico = self.historico_atualizacoes or []
        historico.append(
            {
                "timestamp": entry["timestamp"],
                "usuario_id": entry["usuario_id"],
                "acao": "transicao_stage",
                "campos": {"stage": {"from": entry["from_stage"], "to": entry["to_stage"]}},
                "motivo": motivo,
            }
        )
        self.historico_atualizacoes = historico

        self.stage = new_stage
        self.atualizado_em = datetime.utcnow()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Opportunity(id={self.id}, stage={self.stage.value}, score={self.score})>"
