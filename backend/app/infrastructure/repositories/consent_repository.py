"""
Infrastructure repository implementation for Consent.
Moves concrete SQLAlchemy + audit logic to infrastructure layer.
"""

from __future__ import annotations

from typing import List, Optional

import structlog
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.constants import (
    ACTION_ATUALIZACAO,
    ACTION_CONCESSAO,
    ACTION_NEGACAO,
    AUDIT_ACTION_CREATE,
    AUDIT_ACTION_UPDATE,
    TABLE_CONSENTS,
)
from app.domain.models.consent import Consent
from app.domain.services.audit_logger import AuditLogger, NoOpAuditLogger

logger = structlog.get_logger()


class ConsentRepository:
    def __init__(self, session: AsyncSession, audit_logger: AuditLogger | None = None):
        self.session = session
        self.audit_logger = audit_logger or NoOpAuditLogger()

    async def create(self, consentimento: Consent, usuario_id: str) -> Consent:
        if not consentimento.consent_id_base:
            consentimento.consent_id_base = consentimento.id
        consentimento.adicionar_historico(
            usuario_id=usuario_id,
            acao=ACTION_CONCESSAO if consentimento.consentimento_dado else ACTION_NEGACAO,
            detalhes=(
                f"Consent {'granted' if consentimento.consentimento_dado else 'denied'} "
                f"for: {consentimento.finalidade}"
            ),
        )
        self.session.add(consentimento)
        await self.session.flush()
        self.audit_logger.publish_audit_log(
            usuario_id=usuario_id,
            acao=AUDIT_ACTION_CREATE,
            tabela=TABLE_CONSENTS,
            record_id=str(consentimento.id),
            valor_novo=consentimento.to_dict(),
            tenant_id=consentimento.tenant_id,
        )
        logger.info(
            "consent_created",
            consent_id=str(consentimento.id),
            version=consentimento.versao,
            granted=consentimento.consentimento_dado,
            user_id=usuario_id,
        )
        return consentimento

    async def get_by_id(
        self, consentimento_id: str, tenant_id: Optional[str] = None
    ) -> Optional[Consent]:
        query = select(Consent).where(Consent.id == consentimento_id)
        if tenant_id:
            query = query.where(Consent.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_latest_version(
        self, consent_id_base: str, tenant_id: Optional[str] = None
    ) -> Optional[Consent]:
        query = (
            select(Consent)
            .where(Consent.consent_id_base == consent_id_base)
            .order_by(desc(Consent.versao))
            .limit(1)
        )
        if tenant_id:
            query = query.where(Consent.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_versions(
        self, consent_id_base: str, tenant_id: Optional[str] = None
    ) -> List[Consent]:
        query = (
            select(Consent)
            .where(Consent.consent_id_base == consent_id_base)
            .order_by(Consent.versao)
        )
        if tenant_id:
            query = query.where(Consent.tenant_id == tenant_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_new_version(
        self, base_consent: Consent, usuario_id: str, **updates
    ) -> Consent:
        new_consent = Consent(
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
        for key, value in updates.items():
            if hasattr(new_consent, key):
                setattr(new_consent, key, value)
        new_consent.adicionar_historico(
            usuario_id=usuario_id,
            acao=ACTION_ATUALIZACAO,
            detalhes=(
                f"Created version {new_consent.versao} with changes: "
                f"{', '.join(updates.keys())}"
            ),
        )
        return await self.create(new_consent, usuario_id)

    async def revogar_consentimento(
        self, consentimento: Consent, usuario_id: str, motivo: str = ""
    ) -> Consent:
        consentimento.revogar(usuario_id=usuario_id, motivo=motivo)
        await self.session.flush()
        self.audit_logger.publish_audit_log(
            usuario_id=usuario_id,
            acao=AUDIT_ACTION_UPDATE,
            tabela=TABLE_CONSENTS,
            record_id=str(consentimento.id),
            valor_antigo={"revogado": False},
            valor_novo={"revogado": True, "motivo": motivo},
            tenant_id=consentimento.tenant_id,
        )
        logger.warning(
            "consent_revoked",
            consent_id=str(consentimento.id),
            base_id=str(consentimento.consent_id_base),
            user_id=usuario_id,
            reason=motivo,
        )
        return consentimento

    async def get_valid_consent(
        self, titular_id: str, finalidade: str, tenant_id: Optional[str] = None
    ) -> Optional[Consent]:
        query = (
            select(Consent)
            .where(
                and_(
                    Consent.titular_id == titular_id,
                    Consent.finalidade == finalidade,
                    Consent.consentimento_dado.is_(True),
                    Consent.revogado.is_(False),
                )
            )
            .order_by(desc(Consent.versao))
            .limit(1)
        )
        if tenant_id:
            query = query.where(Consent.tenant_id == tenant_id)
        result = await self.session.execute(query)
        consent = result.scalar_one_or_none()
        if consent and consent.is_valido():
            return consent
        return None


# Backward compatibility alias
ConsentimentoRepository = ConsentRepository
