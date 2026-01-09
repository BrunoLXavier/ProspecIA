"""
HTTP endpoints for LGPD consent management.

Implements:
- GET /consentimentos/{id}: Get consent details
"""

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.postgres.connection import get_session
from app.infrastructure.middleware.auth_middleware import get_current_user
from app.infrastructure.repositories.consent_repository import ConsentimentoRepository
from app.infrastructure.services.audit_logger import KafkaAuditLogger

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/consents", tags=["Consent"])


def get_audit_logger() -> KafkaAuditLogger:
    return KafkaAuditLogger()


@router.get("/{id}", summary="Get Consent")
async def get_consentimento(
    id: UUID, session: AsyncSession = Depends(get_session), user: dict = Depends(get_current_user)
):
    """Get consent details by ID."""
    try:
        consent_repo = ConsentimentoRepository(session, audit_logger=get_audit_logger())
        tenant_id = user.get("tenant_id", "nacional")

        consent = await consent_repo.get_by_id(id, tenant_id=tenant_id)

        if not consent:
            raise HTTPException(status_code=404, detail="Consent not found")

        logger.info("consent_retrieved", consent_id=str(id))

        return {
            "id": consent.id,
            "versao": consent.versao,
            "finalidade": consent.finalidade,
            "categorias_dados": consent.categorias_dados,
            "consentimento_dado": consent.consentimento_dado,
            "data_consentimento": consent.data_consentimento,
            "revogado": consent.revogado,
            "data_revogacao": consent.data_revogacao,
            "motivo_revogacao": consent.motivo_revogacao,
            "origem_coleta": consent.origem_coleta,
            "consentimento_marketing": consent.consentimento_marketing,
            "consentimento_compartilhamento": consent.consentimento_compartilhamento,
            "consentimento_analise": consent.consentimento_analise,
            "base_legal": consent.base_legal,
            "data_expiracao": consent.data_expiracao,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_consent_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get consent: {str(e)}")
