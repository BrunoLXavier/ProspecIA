"""
ProspecIA - Consentimento Domain Model

SQLAlchemy model for LGPD consent records with versioning.
Implements legal compliance for data processing consent.
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.adapters.postgres.connection import Base


class Consentimento(Base):
    """
    Consentimento model for LGPD consent tracking.
    
    Implements:
    - LGPD Art. 8º: Consent must be free, informed, and unambiguous
    - LGPD Art. 9º: Specific purpose declaration required
    - LGPD Art. 18º: Right to revoke consent
    - PT-01: Full versioning and audit trail
    
    Features:
    - Versioned consent records (allows tracking changes)
    - Specific purpose declaration
    - Revocation tracking
    - Granular consent for different data types
    - Audit trail of all consent changes
    
    Follows Clean Architecture principles:
    - Domain entity with business rules
    - Independent of infrastructure
    - Immutable history
    """
    
    __tablename__ = "consentimentos"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Consent version (for tracking changes to same subject)
    versao = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Consent version number (increments on updates)"
    )
    consent_id_base = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Base consent ID (groups versions together)"
    )
    
    # Subject identification
    titular_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Data subject UUID (optional, for anonymized consent)"
    )
    titular_email = Column(
        String(255),
        nullable=True,
        comment="Data subject email (if applicable)"
    )
    titular_documento = Column(
        String(100),
        nullable=True,
        comment="Data subject document (CPF, CNPJ) - encrypted"
    )
    
    # Consent details
    finalidade = Column(
        Text,
        nullable=False,
        comment="Specific purpose for data processing (LGPD Art. 9º)"
    )
    categorias_dados = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Array of data categories covered by consent"
    )
    
    # Consent status
    consentimento_dado = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether consent was given (True) or denied (False)"
    )
    data_consentimento = Column(
        DateTime,
        nullable=True,
        comment="Timestamp when consent was given"
    )
    
    # Revocation tracking
    revogado = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Whether consent was revoked"
    )
    data_revogacao = Column(
        DateTime,
        nullable=True,
        comment="Timestamp when consent was revoked"
    )
    motivo_revogacao = Column(
        Text,
        nullable=True,
        comment="Reason for revocation (optional)"
    )
    
    # Collection context
    origem_coleta = Column(
        String(100),
        nullable=False,
        default="sistema",
        comment="Where consent was collected (sistema, formulario, api, etc)"
    )
    ip_origem = Column(
        String(45),
        nullable=True,
        comment="IP address where consent was collected"
    )
    user_agent = Column(
        Text,
        nullable=True,
        comment="User agent string"
    )
    
    # Granular consent (checkboxes for different purposes)
    consentimento_marketing = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Consent for marketing communications"
    )
    consentimento_compartilhamento = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Consent for data sharing with third parties"
    )
    consentimento_analise = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Consent for data analysis and profiling"
    )
    
    # Legal basis (LGPD Art. 7º)
    base_legal = Column(
        String(100),
        nullable=False,
        default="consentimento",
        comment="Legal basis for processing (consentimento, legítimo_interesse, etc)"
    )
    
    # Audit trail
    historico_alteracoes = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Immutable array of all consent changes"
    )
    
    # User and tenant context
    coletado_por = Column(
        UUID(as_uuid=True),
        nullable=False,
        comment="User UUID who collected the consent"
    )
    tenant_id = Column(
        String(50),
        nullable=False,
        default="nacional",
        index=True,
        comment="Tenant identifier"
    )
    
    # Timestamps
    data_criacao = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Record creation timestamp"
    )
    data_atualizacao = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Last update timestamp"
    )
    data_expiracao = Column(
        DateTime,
        nullable=True,
        comment="Consent expiration date (if applicable)"
    )
    
    # Additional metadata
    metadata_adicional = Column(
        JSON,
        nullable=True,
        default=dict,
        comment="Additional metadata"
    )
    
    def __repr__(self):
        return f"<Consentimento(id={self.id}, versao={self.versao}, consentimento_dado={self.consentimento_dado})>"
    
    def to_dict(self):
        """
        Convert model to dictionary for API responses.
        
        Returns:
            dict: Model data as dictionary
        """
        return {
            "id": str(self.id),
            "versao": self.versao,
            "consent_id_base": str(self.consent_id_base) if self.consent_id_base else None,
            "titular_id": str(self.titular_id) if self.titular_id else None,
            "titular_email": self.titular_email,
            "finalidade": self.finalidade,
            "categorias_dados": self.categorias_dados,
            "consentimento_dado": self.consentimento_dado,
            "data_consentimento": self.data_consentimento.isoformat() if self.data_consentimento else None,
            "revogado": self.revogado,
            "data_revogacao": self.data_revogacao.isoformat() if self.data_revogacao else None,
            "motivo_revogacao": self.motivo_revogacao,
            "origem_coleta": self.origem_coleta,
            "consentimento_marketing": self.consentimento_marketing,
            "consentimento_compartilhamento": self.consentimento_compartilhamento,
            "consentimento_analise": self.consentimento_analise,
            "base_legal": self.base_legal,
            "historico_alteracoes": self.historico_alteracoes,
            "coletado_por": str(self.coletado_por),
            "tenant_id": self.tenant_id,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None,
            "data_atualizacao": self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            "data_expiracao": self.data_expiracao.isoformat() if self.data_expiracao else None,
            "metadata_adicional": self.metadata_adicional,
        }
    
    def adicionar_historico(
        self,
        usuario_id: str,
        acao: str,
        detalhes: str,
    ):
        """
        Add entry to historico_alteracoes (immutable audit trail).
        
        Args:
            usuario_id: User who made the change
            acao: Action type (concessao, revogacao, atualizacao)
            detalhes: Additional details about the change
        """
        if self.historico_alteracoes is None:
            self.historico_alteracoes = []
        
        self.historico_alteracoes.append({
            "timestamp": datetime.utcnow().isoformat(),
            "usuario_id": usuario_id,
            "acao": acao,
            "detalhes": detalhes,
            "versao": self.versao,
        })
    
    def revogar(self, usuario_id: str, motivo: str = ""):
        """
        Revoke consent (LGPD Art. 18º - Right to revoke).
        
        Args:
            usuario_id: User who is revoking
            motivo: Reason for revocation (optional)
        """
        self.revogado = True
        self.data_revogacao = datetime.utcnow()
        self.motivo_revogacao = motivo
        
        self.adicionar_historico(
            usuario_id=usuario_id,
            acao="revogacao",
            detalhes=f"Consentimento revogado. Motivo: {motivo or 'Não informado'}",
        )
    
    def is_valido(self) -> bool:
        """
        Check if consent is valid (not revoked, not expired).
        
        Returns:
            bool: True if consent is valid, False otherwise
        """
        if self.revogado:
            return False
        
        if not self.consentimento_dado:
            return False
        
        if self.data_expiracao and datetime.utcnow() > self.data_expiracao:
            return False
        
        return True
