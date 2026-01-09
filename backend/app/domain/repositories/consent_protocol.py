"""Domain protocol for Consentimento repository.

Defines abstraction for consent data access so application/use cases
depend on interfaces, not infrastructure.
"""

from __future__ import annotations

from typing import List, Optional, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.consent import Consent


class ConsentRepositoryProtocol(Protocol):
    def __init__(self, session: AsyncSession, *args, **kwargs):
        ...

    async def create(self, consentimento: Consent, usuario_id: str) -> Consent:
        ...

    async def get_by_id(
        self, consentimento_id: str, tenant_id: Optional[str] = None
    ) -> Optional[Consent]:
        ...

    async def get_latest_version(
        self, consent_id_base: str, tenant_id: Optional[str] = None
    ) -> Optional[Consent]:
        ...

    async def get_all_versions(
        self, consent_id_base: str, tenant_id: Optional[str] = None
    ) -> List[Consent]:
        ...

    async def create_new_version(
        self, base_consent: Consent, usuario_id: str, **updates
    ) -> Consent:
        ...

    async def revogar_consentimento(
        self, consentimento: Consent, usuario_id: str, motivo: str = ""
    ) -> Consent:
        ...

    async def get_valid_consent(
        self, titular_id: str, finalidade: str, tenant_id: Optional[str] = None
    ) -> Optional[Consent]:
        ...


# Backward compatibility alias
ConsentimentoRepositoryProtocol = ConsentRepositoryProtocol
