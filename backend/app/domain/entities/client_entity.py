"""
Domain entity for Client.

Pure Python model with no infrastructure dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID


class ClientStatus(str, Enum):
    """Status lifecycle for clients (soft delete pattern)."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


class ClientMaturity(str, Enum):
    """Client maturity level for CRM classification."""

    PROSPECT = "prospect"
    LEAD = "lead"
    OPPORTUNITY = "opportunity"
    CLIENT = "client"
    ADVOCATE = "advocate"


@dataclass
class ClientEntity:
    """
    Pure domain entity for Client.

    No SQLAlchemy or ORM dependencies. Contains only business logic.
    """

    id: UUID
    name: str
    cnpj: str
    email: str
    maturity: ClientMaturity
    status: ClientStatus = ClientStatus.ACTIVE
    phone: Optional[str] = None
    website: Optional[str] = None
    sector: str = "general"
    size: str = "micro"
    address: Optional[str] = None
    notes: Optional[str] = None
    tenant_id: Optional[UUID] = None
    historico_atualizacoes: List[Dict[str, Any]] = field(default_factory=list)
    criado_por: Optional[UUID] = None
    atualizado_por: Optional[UUID] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    def can_transition_to(self, new_status: ClientStatus) -> bool:
        """Check if status transition is allowed."""
        allowed_transitions: Dict[ClientStatus, List[ClientStatus]] = {
            ClientStatus.ACTIVE: [
                ClientStatus.INACTIVE,
                ClientStatus.ARCHIVED,
                ClientStatus.EXCLUDED,
            ],
            ClientStatus.INACTIVE: [
                ClientStatus.ACTIVE,
                ClientStatus.ARCHIVED,
                ClientStatus.EXCLUDED,
            ],
            ClientStatus.ARCHIVED: [ClientStatus.ACTIVE, ClientStatus.EXCLUDED],
            ClientStatus.EXCLUDED: [],
        }
        return new_status in allowed_transitions.get(self.status, [])

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
