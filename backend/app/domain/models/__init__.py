"""Domain models package.

Exports both legacy Portuguese names and English aliases to ensure
readability while maintaining backward compatibility.
"""

# Primary exports (English names) with Portuguese aliases for backward compatibility
from app.domain.models.consent import Consent, Consentimento
from app.domain.models.ingestion import (
    Ingestao,
    Ingestion,
    IngestionMethod,
    IngestionSource,
    IngestionStatus,
)

__all__ = [
    "Ingestion",
    "Ingestao",
    "IngestionStatus",
    "IngestionMethod",
    "IngestionSource",
    "Consent",
    "Consentimento",
]
