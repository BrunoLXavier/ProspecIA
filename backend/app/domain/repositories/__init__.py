"""Domain repositories package."""

from app.domain.repositories.ingestao_repository import IngestaoRepository
from app.domain.repositories.consentimento_repository import ConsentimentoRepository

__all__ = [
    "IngestaoRepository",
    "ConsentimentoRepository",
]
