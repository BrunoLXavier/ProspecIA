"""
ProspecIA - Consentimento Repository

Repository pattern implementation for Consentimento entity.
Provides LGPD-compliant consent management.
"""

from typing import List, Optional
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import structlog

from app.domain.models.consentimento import Consentimento
from app.adapters.kafka.producer import get_kafka_producer

logger = structlog.get_logger()


class ConsentimentoRepository:
    """
    Repository for Consentimento entity following Repository Pattern.
    
    Responsibilities (SRP):
    - CRUD operations for consent records
    - Version management
    - Revocation handling
    - Audit log integration
    
    Implements LGPD compliance for consent management.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: Async SQLAlchemy session
        """
        self.session = session
    
    async def create(
        self,
        consentimento: Consentimento,
        usuario_id: str,
    ) -> Consentimento:
        """
        Create new consent record with audit log.
        
        Args:
            consentimento: Consentimento entity to create
            usuario_id: User creating the record
            
        Returns:
            Created Consentimento entity
        """
        # If no base consent ID, this is the first version
        if not consentimento.consent_id_base:
            consentimento.consent_id_base = consentimento.id
        
        # Add initial history entry
        consentimento.adicionar_historico(
            usuario_id=usuario_id,
            acao="concessao" if consentimento.consentimento_dado else "negacao",
            detalhes=f"Consentimento {'concedido' if consentimento.consentimento_dado else 'negado'} para: {consentimento.finalidade}",
        )
        
        self.session.add(consentimento)
        await self.session.flush()
        
        # Publish audit log to Kafka
        kafka = get_kafka_producer()
        kafka.publish_audit_log(
            usuario_id=usuario_id,
            acao="CREATE",
            tabela="consentimentos",
            record_id=str(consentimento.id),
            valor_novo=consentimento.to_dict(),
            tenant_id=consentimento.tenant_id,
        )
        
        logger.info(
            "consentimento_created",
            consentimento_id=str(consentimento.id),
            versao=consentimento.versao,
            consentimento_dado=consentimento.consentimento_dado,
            usuario_id=usuario_id,
        )
        
        return consentimento
    
    async def get_by_id(
        self,
        consentimento_id: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[Consentimento]:
        """
        Get consent by ID with optional tenant filtering.
        
        Args:
            consentimento_id: Consent UUID
            tenant_id: Tenant ID for RLS (optional)
            
        Returns:
            Consentimento entity or None if not found
        """
        query = select(Consentimento).where(Consentimento.id == consentimento_id)
        
        if tenant_id:
            query = query.where(Consentimento.tenant_id == tenant_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_latest_version(
        self,
        consent_id_base: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[Consentimento]:
        """
        Get the latest version of a consent record.
        
        Args:
            consent_id_base: Base consent ID
            tenant_id: Tenant ID for RLS (optional)
            
        Returns:
            Latest Consentimento version or None if not found
        """
        query = select(Consentimento).where(
            Consentimento.consent_id_base == consent_id_base
        ).order_by(desc(Consentimento.versao)).limit(1)
        
        if tenant_id:
            query = query.where(Consentimento.tenant_id == tenant_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_versions(
        self,
        consent_id_base: str,
        tenant_id: Optional[str] = None,
    ) -> List[Consentimento]:
        """
        Get all versions of a consent record (audit trail).
        
        Args:
            consent_id_base: Base consent ID
            tenant_id: Tenant ID for RLS (optional)
            
        Returns:
            List of Consentimento versions ordered by version
        """
        query = select(Consentimento).where(
            Consentimento.consent_id_base == consent_id_base
        ).order_by(Consentimento.versao)
        
        if tenant_id:
            query = query.where(Consentimento.tenant_id == tenant_id)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create_new_version(
        self,
        base_consent: Consentimento,
        usuario_id: str,
        **updates,
    ) -> Consentimento:
        """
        Create a new version of an existing consent (for updates).
        
        Args:
            base_consent: Original consent record
            usuario_id: User creating the new version
            **updates: Fields to update in new version
            
        Returns:
            New Consentimento version
        """
        # Create new consent with incremented version
        new_consent = Consentimento(
            versao=base_consent.versao + 1,
            consent_id_base=base_consent.consent_id_base,
            titular_id=base_consent.titular_id,
            titular_email=base_consent.titular_email,
            titular_documento=base_consent.titular_documento,
            finalidade=base_consent.finalidade,
            categorias_dados=base_consent.categorias_dados,
            consentimento_dado=base_consent.consentimento_dado,
            data_consentimento=base_consent.data_consentimento,
            origem_coleta=base_consent.origem_coleta,
            consentimento_marketing=base_consent.consentimento_marketing,
            consentimento_compartilhamento=base_consent.consentimento_compartilhamento,
            consentimento_analise=base_consent.consentimento_analise,
            base_legal=base_consent.base_legal,
            historico_alteracoes=base_consent.historico_alteracoes.copy(),
            coletado_por=base_consent.coletado_por,
            tenant_id=base_consent.tenant_id,
        )
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(new_consent, key):
                setattr(new_consent, key, value)
        
        # Add history entry
        new_consent.adicionar_historico(
            usuario_id=usuario_id,
            acao="atualizacao",
            detalhes=f"Criada versão {new_consent.versao} com alterações: {', '.join(updates.keys())}",
        )
        
        return await self.create(new_consent, usuario_id)
    
    async def revogar_consentimento(
        self,
        consentimento: Consentimento,
        usuario_id: str,
        motivo: str = "",
    ) -> Consentimento:
        """
        Revoke consent (LGPD Art. 18º).
        
        Args:
            consentimento: Consent to revoke
            usuario_id: User revoking (usually the data subject)
            motivo: Reason for revocation
            
        Returns:
            Updated Consentimento with revocation
        """
        consentimento.revogar(usuario_id=usuario_id, motivo=motivo)
        await self.session.flush()
        
        # Publish audit log
        kafka = get_kafka_producer()
        kafka.publish_audit_log(
            usuario_id=usuario_id,
            acao="UPDATE",
            tabela="consentimentos",
            record_id=str(consentimento.id),
            valor_antigo={"revogado": False},
            valor_novo={"revogado": True, "motivo": motivo},
            tenant_id=consentimento.tenant_id,
        )
        
        logger.warning(
            "consentimento_revogado",
            consentimento_id=str(consentimento.id),
            consent_id_base=str(consentimento.consent_id_base),
            usuario_id=usuario_id,
            motivo=motivo,
        )
        
        return consentimento
    
    async def get_valid_consent(
        self,
        titular_id: str,
        finalidade: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[Consentimento]:
        """
        Get valid (not revoked, not expired) consent for a specific purpose.
        
        Args:
            titular_id: Data subject UUID
            finalidade: Purpose for data processing
            tenant_id: Tenant ID for RLS (optional)
            
        Returns:
            Valid Consentimento or None if not found/invalid
        """
        query = select(Consentimento).where(
            and_(
                Consentimento.titular_id == titular_id,
                Consentimento.finalidade == finalidade,
                Consentimento.consentimento_dado == True,
                Consentimento.revogado == False,
            )
        ).order_by(desc(Consentimento.versao)).limit(1)
        
        if tenant_id:
            query = query.where(Consentimento.tenant_id == tenant_id)
        
        result = await self.session.execute(query)
        consent = result.scalar_one_or_none()
        
        if consent and consent.is_valido():
            return consent
        
        return None
