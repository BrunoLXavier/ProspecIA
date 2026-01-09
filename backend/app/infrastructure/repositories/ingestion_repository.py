"""
Infrastructure repository implementation for Ingestion.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import structlog
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.ingestion import Ingestion, IngestionSource, IngestionStatus
from app.domain.services.audit_logger import AuditLogger, NoOpAuditLogger
from app.infrastructure.monitoring.metrics import ingestoes_status

logger = structlog.get_logger()


class IngestionRepository:
    def __init__(self, session: AsyncSession, audit_logger: AuditLogger | None = None):
        self.session = session
        self.audit_logger = audit_logger or NoOpAuditLogger()

    async def create(
        self, ingestao: Ingestion, usuario_id: str, ip_cliente: Optional[str] = None
    ) -> Ingestion:
        ingestao.add_historico(
            usuario_id=usuario_id,
            campo="status",
            valor_antigo=None,
            valor_novo=ingestao.status.value,
            motivo="Ingestão criada",
        )
        self.session.add(ingestao)
        await self.session.flush()
        self.audit_logger.publish_audit_log(
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
        self, ingestao_id: str, tenant_id: Optional[str] = None
    ) -> Optional[Ingestion]:
        query = select(Ingestion).where(Ingestion.id == ingestao_id)
        if tenant_id:
            query = query.where(Ingestion.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_with_filters(
        self,
        tenant_id: Optional[str] = None,
        fonte: Optional[IngestionSource] = None,
        status: Optional[IngestionStatus] = None,
        criado_por: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[List[Ingestion], int]:
        query = select(Ingestion)
        filters = []
        if tenant_id:
            filters.append(Ingestion.tenant_id == tenant_id)
        if fonte:
            filters.append(Ingestion.fonte == fonte)
        if status:
            filters.append(Ingestion.status == status)
        if criado_por:
            filters.append(Ingestion.criado_por == criado_por)
        if data_inicio:
            filters.append(Ingestion.data_ingestao >= data_inicio)
        if data_fim:
            filters.append(Ingestion.data_ingestao <= data_fim)
        if filters:
            query = query.where(and_(*filters))
        count_query = select(Ingestion.id).where(and_(*filters)) if filters else select(Ingestion.id)
        count_result = await self.session.execute(count_query)
        total = len(count_result.all())
        query = query.order_by(desc(Ingestion.data_ingestao)).offset(offset).limit(limit)
        result = await self.session.execute(query)
        ingestoes = result.scalars().all()
        return list(ingestoes), total

    async def update_status(
        self,
        ingestao: Ingestion,
        new_status: IngestionStatus,
        usuario_id: str,
        motivo: str,
        ip_cliente: Optional[str] = None,
    ) -> Ingestion:
        old_status = ingestao.status
        ingestao.status = new_status
        ingestao.data_atualizacao = datetime.now(UTC)
        if new_status == IngestionStatus.CONCLUIDA:
            ingestao.data_processamento = datetime.now(UTC)
        ingestao.add_historico(
            usuario_id=usuario_id,
            campo="status",
            valor_antigo=old_status.value,
            valor_novo=new_status.value,
            motivo=motivo,
        )
        await self.session.flush()
        try:
            ingestoes_status.labels(status=old_status.value).dec()
            ingestoes_status.labels(status=new_status.value).inc()
        except Exception:
            pass
        self.audit_logger.publish_audit_log(
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
        ingestao: Ingestion,
        pii_detectado: Dict[str, Any],
        acoes_lgpd: Dict[str, Any],
        consentimento_id: Optional[str],
        usuario_id: str,
    ) -> Ingestion:
        ingestao.pii_detectado = pii_detectado
        ingestao.acoes_lgpd = acoes_lgpd
        if consentimento_id:
            ingestao.consentimento_id = consentimento_id
        ingestao.data_atualizacao = datetime.now(UTC)
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
        self, ingestao: Ingestion, usuario_id: str, motivo: str, ip_cliente: Optional[str] = None
    ) -> None:
        await self.update_status(
            ingestao=ingestao,
            new_status=IngestionStatus.CANCELADA,
            usuario_id=usuario_id,
            motivo=motivo,
            ip_cliente=ip_cliente,
        )
        logger.info("ingestao_deleted", ingestao_id=str(ingestao.id), usuario_id=usuario_id)


# Backward compatibility alias
IngestaoRepository = IngestionRepository
