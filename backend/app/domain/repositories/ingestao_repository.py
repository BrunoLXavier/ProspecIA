"""
ProspecIA - Ingestao Repository

Repository pattern implementation for Ingestao entity.
Provides data access abstraction following SOLID principles.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import structlog

from app.domain.models.ingestao import Ingestao, StatusIngestao, FonteIngestao
from app.adapters.kafka.producer import get_kafka_producer

logger = structlog.get_logger()


class IngestaoRepository:
    """
    Repository for Ingestao entity following Repository Pattern.
    
    Responsibilities (SRP):
    - CRUD operations for Ingestao
    - Query building with filters
    - Audit log integration
    - Business logic for status transitions
    
    Follows DIP: Depends on abstractions (AsyncSession), not concretions
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
        ingestao: Ingestao,
        usuario_id: str,
        ip_cliente: Optional[str] = None,
    ) -> Ingestao:
        """
        Create new ingestion record with audit log.
        
        Args:
            ingestao: Ingestao entity to create
            usuario_id: User creating the record
            ip_cliente: Client IP address (optional)
            
        Returns:
            Created Ingestao entity
        """
        # Add initial history entry
        ingestao.add_historico(
            usuario_id=usuario_id,
            campo="status",
            valor_antigo=None,
            valor_novo=ingestao.status.value,
            motivo="Ingestão criada",
        )
        
        self.session.add(ingestao)
        await self.session.flush()
        
        # Publish audit log to Kafka
        kafka = get_kafka_producer()
        kafka.publish_audit_log(
            usuario_id=usuario_id,
            acao="CREATE",
            tabela="ingestoes",
            record_id=str(ingestao.id),
            valor_novo=ingestao.to_dict(),
            ip_cliente=ip_cliente,
            tenant_id=ingestao.tenant_id,
        )
        
        logger.info(
            "ingestao_created",
            ingestao_id=str(ingestao.id),
            fonte=ingestao.fonte.value,
            usuario_id=usuario_id,
        )
        
        return ingestao
    
    async def get_by_id(
        self,
        ingestao_id: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[Ingestao]:
        """
        Get ingestion by ID with optional tenant filtering (RLS).
        
        Args:
            ingestao_id: Ingestion UUID
            tenant_id: Tenant ID for RLS (optional)
            
        Returns:
            Ingestao entity or None if not found
        """
        query = select(Ingestao).where(Ingestao.id == ingestao_id)
        
        if tenant_id:
            query = query.where(Ingestao.tenant_id == tenant_id)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_with_filters(
        self,
        tenant_id: Optional[str] = None,
        fonte: Optional[FonteIngestao] = None,
        status: Optional[StatusIngestao] = None,
        criado_por: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[List[Ingestao], int]:
        """
        List ingestions with filters and pagination.
        
        Args:
            tenant_id: Filter by tenant (RLS)
            fonte: Filter by data source
            status: Filter by status
            criado_por: Filter by creator
            data_inicio: Filter by start date
            data_fim: Filter by end date
            offset: Pagination offset
            limit: Page size
            
        Returns:
            Tuple of (list of Ingestao, total count)
        """
        # Build query with filters
        query = select(Ingestao)
        filters = []
        
        if tenant_id:
            filters.append(Ingestao.tenant_id == tenant_id)
        
        if fonte:
            filters.append(Ingestao.fonte == fonte)
        
        if status:
            filters.append(Ingestao.status == status)
        
        if criado_por:
            filters.append(Ingestao.criado_por == criado_por)
        
        if data_inicio:
            filters.append(Ingestao.data_ingestao >= data_inicio)
        
        if data_fim:
            filters.append(Ingestao.data_ingestao <= data_fim)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(Ingestao.id).where(and_(*filters)) if filters else select(Ingestao.id)
        count_result = await self.session.execute(count_query)
        total = len(count_result.all())
        
        # Apply pagination and ordering
        query = query.order_by(desc(Ingestao.data_ingestao)).offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        ingestoes = result.scalars().all()
        
        return list(ingestoes), total
    
    async def update_status(
        self,
        ingestao: Ingestao,
        new_status: StatusIngestao,
        usuario_id: str,
        motivo: str,
        ip_cliente: Optional[str] = None,
    ) -> Ingestao:
        """
        Update ingestion status with audit trail.
        
        Args:
            ingestao: Ingestao entity to update
            new_status: New status
            usuario_id: User making the change
            motivo: Reason for status change
            ip_cliente: Client IP address (optional)
            
        Returns:
            Updated Ingestao entity
        """
        old_status = ingestao.status
        
        ingestao.status = new_status
        ingestao.data_atualizacao = datetime.utcnow()
        
        if new_status == StatusIngestao.CONCLUIDA:
            ingestao.data_processamento = datetime.utcnow()
        
        # Add history entry
        ingestao.add_historico(
            usuario_id=usuario_id,
            campo="status",
            valor_antigo=old_status.value,
            valor_novo=new_status.value,
            motivo=motivo,
        )
        
        await self.session.flush()
        
        # Publish audit log
        kafka = get_kafka_producer()
        kafka.publish_audit_log(
            usuario_id=usuario_id,
            acao="UPDATE",
            tabela="ingestoes",
            record_id=str(ingestao.id),
            valor_antigo={"status": old_status.value},
            valor_novo={"status": new_status.value},
            ip_cliente=ip_cliente,
            tenant_id=ingestao.tenant_id,
        )
        
        logger.info(
            "ingestao_status_updated",
            ingestao_id=str(ingestao.id),
            old_status=old_status.value,
            new_status=new_status.value,
            usuario_id=usuario_id,
        )
        
        return ingestao
    
    async def update_lgpd_info(
        self,
        ingestao: Ingestao,
        pii_detectado: Dict[str, Any],
        acoes_lgpd: Dict[str, Any],
        consentimento_id: Optional[str],
        usuario_id: str,
    ) -> Ingestao:
        """
        Update LGPD-related information.
        
        Args:
            ingestao: Ingestao entity to update
            pii_detectado: PII detection results
            acoes_lgpd: LGPD actions taken
            consentimento_id: Associated consent ID
            usuario_id: User making the update
            
        Returns:
            Updated Ingestao entity
        """
        ingestao.pii_detectado = pii_detectado
        ingestao.acoes_lgpd = acoes_lgpd
        if consentimento_id:
            ingestao.consentimento_id = consentimento_id
        
        ingestao.data_atualizacao = datetime.utcnow()
        
        # Add history entry
        ingestao.add_historico(
            usuario_id=usuario_id,
            campo="lgpd_info",
            valor_antigo=None,
            valor_novo="LGPD processing completed",
            motivo="LGPD agent processed data",
        )
        
        await self.session.flush()
        
        logger.info(
            "ingestao_lgpd_updated",
            ingestao_id=str(ingestao.id),
            pii_types=list(pii_detectado.keys()) if pii_detectado else [],
            usuario_id=usuario_id,
        )
        
        return ingestao
    
    async def delete(
        self,
        ingestao: Ingestao,
        usuario_id: str,
        motivo: str,
        ip_cliente: Optional[str] = None,
    ) -> None:
        """
        Soft delete ingestion (mark as cancelled).
        
        Args:
            ingestao: Ingestao entity to delete
            usuario_id: User deleting the record
            motivo: Reason for deletion
            ip_cliente: Client IP address (optional)
        """
        await self.update_status(
            ingestao=ingestao,
            new_status=StatusIngestao.CANCELADA,
            usuario_id=usuario_id,
            motivo=motivo,
            ip_cliente=ip_cliente,
        )
        
        logger.info(
            "ingestao_deleted",
            ingestao_id=str(ingestao.id),
            usuario_id=usuario_id,
        )
