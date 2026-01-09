"""Compatibility wrapper: re-export infrastructure implementation.

This keeps existing imports working while we move concrete code
to the infrastructure layer.
"""

from app.infrastructure.repositories.consent_repository import ConsentimentoRepository


def get_kafka_producer():
    """Compatibility stub for tests that patch this symbol.

    The consent repository no longer uses a global Kafka producer directly,
    but some tests patch this function on the legacy module path.
    Returning None keeps attribute presence without side effects.
    """
    return None


__all__ = ["ConsentimentoRepository", "get_kafka_producer"]
