"""Domain protocol for Ingestao repository.

Defines abstraction for ingestion data access.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.ingestion import Ingestion, IngestionSource, IngestionStatus


class IngestionRepositoryProtocol(Protocol):
    def __init__(self, session: AsyncSession, *args, **kwargs):
        ...

    async def create(
        self, ingestao: Ingestion, usuario_id: str, ip_cliente: Optional[str] = None
    ) -> Ingestion:
        ...

    async def get_by_id(
        self, ingestao_id: str, tenant_id: Optional[str] = None
    ) -> Optional[Ingestion]:
        ...

    async def list_with_filters(
        self,
        tenant_id: Optional[str] = None,
        fonte: Optional[IngestionSource] = None,
        status: Optional[IngestionStatus] = None,
        criado_por: Optional[str] = None,
        data_inicio: Optional[Any] = None,
        data_fim: Optional[Any] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Ingestion], int]:
        ...

    async def update_status(
        self,
        ingestao: Ingestion,
        new_status: IngestionStatus,
        usuario_id: str,
        motivo: str,
        ip_cliente: Optional[str] = None,
    ) -> Ingestion:
        ...

    async def update_lgpd_info(
        self,
        ingestao: Ingestion,
        pii_detectado: Dict[str, Any],
        acoes_lgpd: Dict[str, Any],
        consentimento_id: Optional[str],
        usuario_id: str,
    ) -> Ingestion:
        ...

    async def delete(
        self, ingestao: Ingestion, usuario_id: str, motivo: str, ip_cliente: Optional[str] = None
    ) -> None:
        ...


# Backward compatibility alias
IngestaoRepositoryProtocol = IngestionRepositoryProtocol
