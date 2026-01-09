"""
ProspecIA - Ingestao Domain Model

SQLAlchemy model for data ingestion records with full audit trail.
Implements Wave 1 requirements (RF-01) with LGPD compliance.
"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.adapters.postgres.connection import Base


class IngestionStatus(enum.Enum):
    """Status enum for ingestion records."""

    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    CONCLUIDA = "concluida"
    FALHA = "falha"
    CANCELADA = "cancelada"


class IngestionMethod(enum.Enum):
    """Method enum for data ingestion."""

    BATCH_UPLOAD = "batch_upload"
    API_PULL = "api_pull"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


class IngestionSource(enum.Enum):
    """Data source enum for ingestion."""

    RAIS = "rais"
    IBGE = "ibge"
    INPI = "inpi"
    FINEP = "finep"
    BNDES = "bndes"
    CUSTOMIZADA = "customizada"


class Ingestion(Base):
    """
    Ingestao model representing data ingestion records.

    Implements:
    - RF-01: Data ingestion with metadata capture
    - PT-01: Full versioning and audit trail
    - PT-02: Human-in-the-loop tracking
    - PT-03/04: Transparency and lineage

    Relationships:
    - Links to Consentimento for LGPD compliance
    - Links to user (via criado_por)
    - Links to tenant (via tenant_id)

    Follows Clean Architecture principles:
    - Entity layer in domain
    - Independent of infrastructure details
    - Immutable history in historico_atualizacoes
    """

    __tablename__ = "ingestions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Source metadata
    fonte = Column(
        SQLEnum(IngestionSource, native_enum=False, validate_strings=True),
        nullable=False,
        comment="Data source (RAIS, IBGE, INPI, FINEP, BNDES, Customizada)",
    )
    metodo = Column(
        SQLEnum(IngestionMethod, native_enum=False, validate_strings=True),
        nullable=False,
        comment="Ingestion method (batch upload, API pull, etc)",
    )

    # File information
    arquivo_original = Column(String(500), nullable=True, comment="Original filename")
    arquivo_storage_path = Column(String(1000), nullable=True, comment="MinIO storage path")
    arquivo_size_bytes = Column(Integer, nullable=True, comment="File size in bytes")
    arquivo_mime_type = Column(String(100), nullable=True, comment="MIME type")

    # Quality and reliability
    confiabilidade_score = Column(
        Integer, nullable=False, default=50, comment="Reliability score (0-100)"
    )
    total_registros = Column(Integer, nullable=True, comment="Total records in ingestion")
    registros_validos = Column(Integer, nullable=True, comment="Valid records")
    registros_invalidos = Column(Integer, nullable=True, comment="Invalid records")

    # Status tracking
    status = Column(
        SQLEnum(IngestionStatus, native_enum=False, validate_strings=True),
        nullable=False,
        default=IngestionStatus.PENDENTE,
        index=True,
        comment="Current ingestion status",
    )
    erros_encontrados = Column(
        JSON, nullable=True, default=list, comment="Array of errors encountered during processing"
    )

    # LGPD compliance
    pii_detectado = Column(
        JSON, nullable=True, comment="PII detected by LGPD agent (types and counts)"
    )
    acoes_lgpd = Column(JSON, nullable=True, comment="LGPD actions taken (masking, tokenization)")
    consentimento_id = Column(
        UUID(as_uuid=True), nullable=True, comment="Reference to consent record"
    )

    # Audit trail (PT-01)
    historico_atualizacoes = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Immutable array of all updates with user, timestamp, reason",
    )

    # User and tenant context
    criado_por = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User UUID who created this ingestion",
    )
    tenant_id = Column(
        String(50),
        nullable=False,
        default="nacional",
        index=True,
        comment="Tenant identifier for multi-tenant isolation",
    )

    # Timestamps
    data_ingestao = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="Ingestion start timestamp",
    )
    data_processamento = Column(DateTime, nullable=True, comment="Processing completion timestamp")
    data_criacao = Column(
        DateTime, nullable=False, default=datetime.utcnow, comment="Record creation timestamp"
    )
    data_atualizacao = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last update timestamp",
    )

    # Additional metadata
    descricao = Column(Text, nullable=True, comment="Optional description")
    tags = Column(JSON, nullable=True, default=list, comment="Array of tags for categorization")
    metadata_adicional = Column(JSON, nullable=True, default=dict, comment="Additional metadata")

    def __repr__(self):
        return f"<Ingestao(id={self.id}, fonte={self.fonte.value}, status={self.status.value})>"

    def to_dict(self):
        """
        Convert model to dictionary for API responses.

        Returns:
            dict: Model data as dictionary
        """
        return {
            "id": str(self.id),
            "fonte": self.fonte.value,
            "metodo": self.metodo.value,
            "arquivo_original": self.arquivo_original,
            "arquivo_storage_path": self.arquivo_storage_path,
            "arquivo_size_bytes": self.arquivo_size_bytes,
            "arquivo_mime_type": self.arquivo_mime_type,
            "confiabilidade_score": self.confiabilidade_score,
            "total_registros": self.total_registros,
            "registros_validos": self.registros_validos,
            "registros_invalidos": self.registros_invalidos,
            "status": self.status.value,
            "erros_encontrados": self.erros_encontrados,
            "pii_detectado": self.pii_detectado,
            "acoes_lgpd": self.acoes_lgpd,
            "consentimento_id": str(self.consentimento_id) if self.consentimento_id else None,
            "historico_atualizacoes": self.historico_atualizacoes,
            "criado_por": str(self.criado_por),
            "tenant_id": self.tenant_id,
            "data_ingestao": self.data_ingestao.isoformat() if self.data_ingestao else None,
            "data_processamento": (
                self.data_processamento.isoformat() if self.data_processamento else None
            ),
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None,
            "data_atualizacao": (
                self.data_atualizacao.isoformat() if self.data_atualizacao else None
            ),
            "descricao": self.descricao,
            "tags": self.tags,
            "metadata_adicional": self.metadata_adicional,
        }

    def add_historico(
        self,
        usuario_id: str,
        campo: str,
        valor_antigo: any,
        valor_novo: any,
        motivo: str,
    ):
        """
        Add entry to historico_atualizacoes (immutable audit trail).

        Args:
            usuario_id: User who made the change
            campo: Field that was changed
            valor_antigo: Previous value
            valor_novo: New value
            motivo: Reason for change
        """
        if self.historico_atualizacoes is None:
            self.historico_atualizacoes = []

        self.historico_atualizacoes.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "usuario_id": usuario_id,
                "campo": campo,
                "valor_antigo": str(valor_antigo),
                "valor_novo": str(valor_novo),
                "motivo": motivo,
            }
        )


# Backward compatibility alias
Ingestao = Ingestion
