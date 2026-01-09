"""
Domain entities - Pure business models independent of persistence.

These entities define the core business rules and domain logic.
They have no SQLAlchemy, ORM, or infrastructure dependencies.
"""

from .client_entity import ClientEntity, ClientMaturity, ClientStatus
from .funding_source_entity import FundingSourceEntity, FundingSourceStatus, FundingSourceType
from .interaction_entity import (
    InteractionEntity,
    InteractionOutcome,
    InteractionStatus,
    InteractionType,
)
from .opportunity_entity import OpportunityEntity, OpportunityStage, OpportunityStatus
from .portfolio_entity import InstituteEntity, InstituteStatus, ProjectEntity, ProjectStatus

__all__ = [
    "ClientEntity",
    "ClientStatus",
    "ClientMaturity",
    "OpportunityEntity",
    "OpportunityStage",
    "OpportunityStatus",
    "InteractionEntity",
    "InteractionType",
    "InteractionOutcome",
    "InteractionStatus",
    "FundingSourceEntity",
    "FundingSourceType",
    "FundingSourceStatus",
    "InstituteEntity",
    "ProjectEntity",
    "InstituteStatus",
    "ProjectStatus",
]
