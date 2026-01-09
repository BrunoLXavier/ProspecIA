"""
Domain entities for Portfolio (Institute and Project).

Pure Python models with no infrastructure dependencies.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID


class InstituteStatus(str, Enum):
    """Status for institutes."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


class ProjectStatus(str, Enum):
    """Status for projects."""

    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


@dataclass
class InstituteEntity:
    """
    Pure domain entity for Institute.

    No SQLAlchemy or ORM dependencies. Contains only business logic.
    """

    id: UUID
    name: str
    description: str
    status: InstituteStatus = InstituteStatus.ACTIVE
    acronym: Optional[str] = None
    website: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    established_year: Optional[int] = None
    headquarters_city: Optional[str] = None
    tenant_id: Optional[UUID] = None
    historico_atualizacoes: List[Dict[str, Any]] = field(default_factory=list)
    criado_por: Optional[UUID] = None
    atualizado_por: Optional[UUID] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

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


@dataclass
class ProjectEntity:
    """
    Pure domain entity for Project.

    No SQLAlchemy or ORM dependencies. Contains only business logic.
    """

    id: UUID
    institute_id: UUID
    title: str
    description: str
    objectives: str
    trl: int  # 1-9
    status: ProjectStatus = ProjectStatus.PLANNING
    budget: Optional[int] = None  # In cents
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    team_size: int = 1
    tenant_id: Optional[UUID] = None
    historico_atualizacoes: List[Dict[str, Any]] = field(default_factory=list)
    criado_por: Optional[UUID] = None
    atualizado_por: Optional[UUID] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    def validate_trl(self) -> bool:
        """Validate TRL is in range 1-9."""
        return 1 <= self.trl <= 9

    def is_active(self) -> bool:
        """Check if project is in active state."""
        return self.status == ProjectStatus.ACTIVE

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
