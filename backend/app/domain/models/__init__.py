"""Domain models package."""

from app.domain.models.ingestao import Ingestao, IngestionStatus, IngestionMethod, IngestionSource
from app.domain.models.consentimento import Consentimento

__all__ = [
    "Ingestao",
    "IngestionStatus",
    "IngestionMethod",
    "IngestionSource",
    "Consentimento",
]
