"""
Domain entity for FundingSource.

Pure Python model with no infrastructure dependencies.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID


class FundingSourceType(str, Enum):
    """Types of funding sources following Brazilian innovation ecosystem."""

    GRANT = "grant"
    FINANCING = "financing"
    EQUITY = "equity"
    NON_REFUNDABLE = "non_refundable"
    TAX_INCENTIVE = "tax_incentive"
    MIXED = "mixed"


class FundingSourceStatus(str, Enum):
    """Status lifecycle for funding sources."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


@dataclass
class FundingSourceEntity:
    """
    Pure domain entity for FundingSource.

    No SQLAlchemy or ORM dependencies. Contains only business logic.
    """

    id: UUID
    name: str
    description: str
    funding_type: FundingSourceType
    sectors: List[str]
    amount: int  # In cents
    trl_min: int
    trl_max: int
    deadline: date
    status: FundingSourceStatus = FundingSourceStatus.ACTIVE
    url: Optional[str] = None
    requirements: Optional[str] = None
    tenant_id: Optional[UUID] = None
    historico_atualizacoes: List[Dict[str, Any]] = field(default_factory=list)
    criado_por: Optional[UUID] = None
    atualizado_por: Optional[UUID] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    def is_open(self) -> bool:
        """Check if deadline has not passed."""
        return date.today() <= self.deadline

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
