"""Domain-level interface for logging LGPD decisions.

Use the interface in use cases to avoid coupling to infrastructure.
Concrete implementations live under app.infrastructure.services.
"""

from __future__ import annotations

from typing import Any, Dict, List, Protocol


class LgpdEventLogger(Protocol):
    def log_decision(
        self,
        ingestao_id: str,
        pii_detectado: Dict[str, List[Dict[str, Any]]],
        acoes_tomadas: List[str],
        consentimento_validado: bool,
        score_confiabilidade: int,
    ) -> None:
        ...


class NoOpLgpdEventLogger:
    def log_decision(
        self,
        ingestao_id: str,
        pii_detectado: Dict[str, List[Dict[str, Any]]],
        acoes_tomadas: List[str],
        consentimento_validado: bool,
        score_confiabilidade: int,
    ) -> None:
        return None
