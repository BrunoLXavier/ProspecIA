"""
Domain entity for Interaction.

Pure Python model with no infrastructure dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID


class InteractionType(str, Enum):
    """Types of interactions with clients."""

    MEETING = "meeting"
    EMAIL = "email"
    CALL = "call"
    VISIT = "visit"
    EVENT = "event"
    OTHER = "other"


class InteractionOutcome(str, Enum):
    """Outcome/result of interaction."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    PENDING = "pending"


class InteractionStatus(str, Enum):
    """Status of interaction record."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    EXCLUDED = "excluded"


@dataclass
class InteractionEntity:
    """
    Pure domain entity for Interaction.

    No SQLAlchemy or ORM dependencies. Contains only business logic.
    """

    id: UUID
    client_id: UUID
    title: str
    description: str
    interaction_type: InteractionType
    date: datetime
    status: InteractionStatus = InteractionStatus.ACTIVE
    outcome: Optional[InteractionOutcome] = None
    participants: List[str] = field(default_factory=list)
    next_steps: Optional[str] = None
    tenant_id: Optional[UUID] = None
    criado_por: Optional[UUID] = None
    criado_em: Optional[datetime] = None

    def complete(self, outcome: InteractionOutcome) -> None:
        """Mark interaction as complete with an outcome."""
        self.status = InteractionStatus.COMPLETED
        self.outcome = outcome
