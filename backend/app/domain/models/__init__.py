"""Domain models package."""

from app.domain.models.ingestao import Ingestao, StatusIngestao, MetodoIngestao, FonteIngestao
from app.domain.models.consentimento import Consentimento

__all__ = [
    "Ingestao",
    "StatusIngestao",
    "MetodoIngestao",
    "FonteIngestao",
    "Consentimento",
]
