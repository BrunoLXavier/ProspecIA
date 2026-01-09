"""English-compatible repository wrapper for consent domain."""

from app.infrastructure.repositories.consent_repository import (  # noqa: F401
    ConsentRepository,
    ConsentimentoRepository,
)

__all__ = [
    "ConsentRepository",
    "ConsentimentoRepository",
]
