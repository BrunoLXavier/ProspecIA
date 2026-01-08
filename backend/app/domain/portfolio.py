"""Domain models for Portfolio (RF-03)

Wave 2 - RF-03: Gestão do Portfólio Institucional
"""

from enum import Enum
"""
Domain models for Portfolio (RF-03)

Wave 2 - RF-03: Gestão do Portfólio Institucional
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, DateTime, Date, Enum as SAEnum, BigInteger, Integer, SmallInteger
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.adapters.postgres.connection import Base


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


class Institute(Base):
    """SQLAlchemy ORM model for institutes."""

    __tablename__ = "institutes"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    acronym = Column(String(20), nullable=True)
    description = Column(Text, nullable=False)
    website = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20), nullable=True)
    status = Column(SAEnum(InstituteStatus, name="institute_status", native_enum=False), nullable=False, default=InstituteStatus.ACTIVE)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    historico_atualizacoes = Column(JSONB, nullable=False, default=list)
    criado_por = Column(PGUUID(as_uuid=True), nullable=False)
    atualizado_por = Column(PGUUID(as_uuid=True), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def add_history(self, campos: Dict[str, Any], usuario_id: UUID, acao: str, motivo: Optional[str] = None) -> None:
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


class Project(Base):
    """SQLAlchemy ORM model for projects."""

    __tablename__ = "projects"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    institute_id = Column(PGUUID(as_uuid=True), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    objectives = Column(Text, nullable=False)
    trl = Column(SmallInteger, nullable=False)
    budget = Column(BigInteger, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    team_size = Column(Integer, nullable=False, default=1)
    status = Column(SAEnum(ProjectStatus, name="project_status", native_enum=False), nullable=False, default=ProjectStatus.PLANNING)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    historico_atualizacoes = Column(JSONB, nullable=False, default=list)
    criado_por = Column(PGUUID(as_uuid=True), nullable=False)
    atualizado_por = Column(PGUUID(as_uuid=True), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    @staticmethod
    def validate_trl(trl: int) -> None:
        if not (1 <= trl <= 9):
            raise ValueError("TRL deve ter entre 1 e 9")

    def add_history(self, campos: Dict[str, Any], usuario_id: UUID, acao: str, motivo: Optional[str] = None) -> None:
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


class Competence(Base):
    """SQLAlchemy ORM model for competences."""

    __tablename__ = "competences"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    tenant_id = Column(PGUUID(as_uuid=True), nullable=False)
    criado_por = Column(PGUUID(as_uuid=True), nullable=False)
    criado_em = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
