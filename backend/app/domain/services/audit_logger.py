"""Domain-level audit logging abstraction.

Defines a minimal contract for emitting audit events without coupling to
any transport (Kafka, HTTP, etc.). Implementations live in the
infrastructure layer. A no-op implementation is provided for tests or
scenarios where audit emission is optional.
"""

from __future__ import annotations

from typing import Any, Optional, Protocol


class AuditLogger(Protocol):
    """Abstraction for audit/event emission."""

    def publish_audit_log(
        self,
        usuario_id: str,
        acao: str,
        tabela: str,
        record_id: str,
        valor_novo: Optional[Any] = None,
        valor_antigo: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        ip_cliente: Optional[str] = None,
    ) -> None:
        """Emit an audit event describing a state change."""
        ...


class NoOpAuditLogger:
    """Safe default implementation that ignores audit events."""

    def publish_audit_log(
        self,
        usuario_id: str,
        acao: str,
        tabela: str,
        record_id: str,
        valor_novo: Optional[Any] = None,
        valor_antigo: Optional[Any] = None,
        tenant_id: Optional[str] = None,
        ip_cliente: Optional[str] = None,
    ) -> None:
        return None
