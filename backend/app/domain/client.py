"""
Domain model for Clients (CRM).

Wave 2 - RF-04: Gestão de CRM
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4
import re

from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.adapters.postgres.connection import Base


class ClientStatus(str, Enum):
    """Status lifecycle for clients (soft delete pattern)."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


class ClientMaturity(str, Enum):
    """Client maturity level for CRM classification."""

    PROSPECT = "prospect"  # Initial contact
    LEAD = "lead"  # Qualified interest
    OPPORTUNITY = "opportunity"  # Active negotiation
    CLIENT = "client"  # Closed deal
    ADVOCATE = "advocate"  # Promoter/reference


class Client(Base):
    """SQLAlchemy ORM model for clients with basic validation helpers."""

    __tablename__ = "clients"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(18), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=False, default="general")
    size = Column(String(20), nullable=False, default="micro")
    maturity = Column(SAEnum(ClientMaturity, name="client_maturity", native_enum=False), nullable=False, default=ClientMaturity.PROSPECT)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(SAEnum(ClientStatus, name="client_status", native_enum=False), nullable=False, default=ClientStatus.ACTIVE)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    historico_atualizacoes = Column(JSONB, nullable=False, default=list)
    criado_por = Column(PGUUID(as_uuid=True), nullable=False)
    atualizado_por = Column(PGUUID(as_uuid=True), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    @staticmethod
    def validate_cnpj(cnpj: str) -> None:
        """Basic Brazilian CNPJ validation (format-only). Raises on invalid length."""
        cnpj_clean = re.sub(r"[^\d]", "", cnpj)
        if len(cnpj_clean) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")

    def can_transition_to(self, new_status: ClientStatus) -> bool:
        """Check if status transition is allowed."""
        allowed_transitions: Dict[ClientStatus, List[ClientStatus]] = {
            ClientStatus.ACTIVE: [ClientStatus.INACTIVE, ClientStatus.ARCHIVED, ClientStatus.EXCLUDED],
            ClientStatus.INACTIVE: [ClientStatus.ACTIVE, ClientStatus.ARCHIVED, ClientStatus.EXCLUDED],
            ClientStatus.ARCHIVED: [ClientStatus.ACTIVE, ClientStatus.EXCLUDED],
            ClientStatus.EXCLUDED: [],
        }
        return new_status in allowed_transitions.get(self.status, [])

    def add_history(self, campos: Dict[str, Any], usuario_id: UUID, acao: str, motivo: Optional[str] = None) -> None:
        """Append an entry to the audit trail."""
        entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "usuario_id": str(usuario_id),
            "acao": acao,
            "campos": campos,
        }
        if motivo:
            entry["motivo"] = motivo
        historico = self.historico_atualizacoes or []
        historico.append(entry)
        self.historico_atualizacoes = historico

    def __repr__(self) -> str:  # pragma: no cover - repr only for debugging
        return f"<Client(id={self.id}, name='{self.name}', maturity={self.maturity.value})>"
