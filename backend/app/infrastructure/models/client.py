import re
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.adapters.postgres.connection import Base


class ClientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


class ClientMaturity(str, Enum):
    PROSPECT = "prospect"
    LEAD = "lead"
    OPPORTUNITY = "opportunity"
    CLIENT = "client"
    ADVOCATE = "advocate"


class Client(Base):
    __tablename__ = "clients"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    cnpj = Column(String(18), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    sector = Column(String(100), nullable=False, default="general")
    size = Column(String(20), nullable=False, default="micro")
    maturity = Column(
        SAEnum(ClientMaturity, name="client_maturity", native_enum=False),
        nullable=False,
        default=ClientMaturity.PROSPECT,
    )
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(
        SAEnum(ClientStatus, name="client_status", native_enum=False),
        nullable=False,
        default=ClientStatus.ACTIVE,
    )
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    historico_atualizacoes = Column(JSONB, nullable=False, default=list)
    criado_por = Column(PGUUID(as_uuid=True), nullable=False)
    atualizado_por = Column(PGUUID(as_uuid=True), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    @staticmethod
    def validate_cnpj(cnpj: str) -> None:
        cnpj_clean = re.sub(r"[^\d]", "", cnpj)
        if len(cnpj_clean) != 14:
            raise ValueError("CNPJ deve ter 14 dígitos")

    def can_transition_to(self, new_status: ClientStatus) -> bool:
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

    def add_history(
        self, campos: Dict[str, Any], usuario_id: UUID, acao: str, motivo: Optional[str] = None
    ) -> None:
        entry: Dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "usuario_id": str(usuario_id),
            "acao": acao,
            "campos": campos,
        }
        if motivo:
            entry["motivo"] = motivo
        historico = self.historico_atualizacoes or []
        historico.append(entry)
        self.historico_atualizacoes = historico

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}', maturity={self.maturity.value})>"


class Translation(Base):
    __tablename__ = "translations"

    id = Column(String, primary_key=True)
    key = Column(String, nullable=False)
    namespace = Column(String, nullable=False)
    pt_br = Column(String, nullable=False)
    en_us = Column(String, nullable=False)
    es_es = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, default="system")
    updated_by = Column(String, default="system")

    def __repr__(self):
        return f"<Translation {self.namespace}:{self.key}>"
