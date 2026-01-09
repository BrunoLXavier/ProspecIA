"""
Domain entity for Opportunity.

Pure Python model with no infrastructure dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID


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


@dataclass
class OpportunityEntity:
    """
    Pure domain entity for Opportunity.

    No SQLAlchemy or ORM dependencies. Contains only business logic.
    """

    id: UUID
    title: str
    description: str
    client_id: UUID
    funding_source_id: UUID
    stage: OpportunityStage = OpportunityStage.INTELLIGENCE
    status: OpportunityStatus = OpportunityStatus.ACTIVE
    score: int = 0
    estimated_value: int = 0
    probability: int = 50
    expected_close_date: Optional[datetime] = None
    responsible_user_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    historico_atualizacoes: List[Dict[str, Any]] = field(default_factory=list)
    historico_transicoes: List[Dict[str, Any]] = field(default_factory=list)
    criado_por: Optional[UUID] = None
    atualizado_por: Optional[UUID] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    def can_transition_to(self, new_stage: OpportunityStage) -> bool:
        """Check if stage transition is allowed (simple: always allowed)."""
        return new_stage != self.stage

    def add_stage_transition(
        self, new_stage: OpportunityStage, usuario_id: UUID, motivo: str
    ) -> None:
        """Record a stage transition in history."""
        entry = {
            "timestamp": datetime.now(datetime.UTC).isoformat(),
            "de_stage": self.stage.value,
            "para_stage": new_stage.value,
            "usuario_id": str(usuario_id),
            "motivo": motivo,
        }
        self.historico_transicoes.append(entry)
        self.stage = new_stage

    def add_history_entry(
        self, campos: Dict[str, Any], usuario_id: UUID, acao: str, motivo: Optional[str] = None
    ) -> None:
        """Append an entry to the audit trail."""
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(datetime.UTC).isoformat(),
            "usuario_id": str(usuario_id),
            "acao": acao,
            "campos": campos,
        }
        if motivo:
            entry["motivo"] = motivo
        self.historico_atualizacoes.append(entry)
