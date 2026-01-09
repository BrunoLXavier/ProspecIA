"""Domain-level repository protocol for Clients (CRM).

Defines the contract used by application services so they do not depend on
infrastructure details. Concrete implementations live under
`app.infrastructure.repositories`.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol, Sequence, runtime_checkable
from uuid import UUID

from app.domain.client import Client, ClientMaturity, ClientStatus


@runtime_checkable
class ClientsRepositoryProtocol(Protocol):
    """Abstraction for client persistence with RLS-aware operations."""

    async def create(self, client: Client) -> Client:
        ...

    async def get(
        self, client_id: UUID, tenant_id: UUID, include_excluded: bool = False
    ) -> Optional[Client]:
        ...

    async def list(
        self,
        tenant_id: UUID,
        status: Optional[ClientStatus] = None,
        maturity: Optional[ClientMaturity] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Client], int]:
        ...

    async def update(
        self,
        client_id: UUID,
        tenant_id: UUID,
        updates: Dict[str, Any],
        updated_by: UUID,
        motivo: Optional[str] = None,
    ) -> Optional[Client]:
        ...

    async def delete(
        self,
        client_id: UUID,
        tenant_id: UUID,
        deleted_by: UUID,
        motivo: str,
    ) -> bool:
        ...

    async def get_history(
        self, client_id: UUID, tenant_id: UUID
    ) -> Optional[list[Dict[str, Any]]]:
        ...
