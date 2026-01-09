"""English-compatible repository wrapper for ingestion domain."""

from app.infrastructure.repositories.ingestion_repository import (  # noqa: F401
    IngestionRepository,
    IngestaoRepository,
)

__all__ = [
    "IngestionRepository",
    "IngestaoRepository",
]
