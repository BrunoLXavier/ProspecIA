"""Domain repositories package."""

from app.domain.repositories.consent_repository import ConsentRepository, ConsentimentoRepository
from app.domain.repositories.ingestion_repository import IngestionRepository, IngestaoRepository

__all__ = [
    "IngestaoRepository",
    "IngestionRepository",
    "ConsentimentoRepository",
    "ConsentRepository",
]
