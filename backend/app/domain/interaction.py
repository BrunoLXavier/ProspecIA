"""Compatibility re-exports for legacy imports.

Interaction ORM definitions moved to infrastructure/models.
This module forwards imports to maintain backward compatibility.
"""

from app.infrastructure.models.interaction import (
    Interaction,
    InteractionOutcome,
    InteractionStatus,
    InteractionType,
)

__all__ = [
    "Interaction",
    "InteractionOutcome",
    "InteractionStatus",
    "InteractionType",
]
