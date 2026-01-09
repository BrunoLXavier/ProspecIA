"""Pydantic schemas module.

This module contains all Pydantic schemas for request/response validation.
Schemas follow Pydantic v2 conventions with proper validation and documentation.
"""

from app.interfaces.schemas.clients import (
    ClientCreate,
    ClientHistoryResponse,
    ClientListItem,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
)
from app.interfaces.schemas.funding_sources import (
    FundingSourceCreate,
    FundingSourceHistoryResponse,
    FundingSourceListItem,
    FundingSourceListResponse,
    FundingSourceResponse,
    FundingSourceUpdate,
)
from app.interfaces.schemas.interactions import (
    InteractionCreate,
    InteractionListItem,
    InteractionListResponse,
    InteractionResponse,
    InteractionUpdate,
)
from app.interfaces.schemas.opportunities import (
    OpportunityCreate,
    OpportunityListItem,
    OpportunityListResponse,
    OpportunityResponse,
    OpportunityStageTransition,
    OpportunityTransitionsResponse,
    OpportunityUpdate,
)
from app.interfaces.schemas.portfolio import (
    CompetenceCreate,
    CompetenceListResponse,
    CompetenceResponse,
    InstituteCreate,
    InstituteListItem,
    InstituteListResponse,
    InstituteResponse,
    InstituteUpdate,
    ProjectCreate,
    ProjectListItem,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

__all__ = [
    # Funding Sources
    "FundingSourceCreate",
    "FundingSourceUpdate",
    "FundingSourceResponse",
    "FundingSourceListItem",
    "FundingSourceListResponse",
    "FundingSourceHistoryResponse",
    # Clients
    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    "ClientListItem",
    "ClientListResponse",
    "ClientHistoryResponse",
    # Interactions
    "InteractionCreate",
    "InteractionUpdate",
    "InteractionResponse",
    "InteractionListItem",
    "InteractionListResponse",
    # Opportunities
    "OpportunityCreate",
    "OpportunityUpdate",
    "OpportunityStageTransition",
    "OpportunityResponse",
    "OpportunityListItem",
    "OpportunityListResponse",
    "OpportunityTransitionsResponse",
    # Portfolio
    "InstituteCreate",
    "InstituteUpdate",
    "InstituteResponse",
    "InstituteListItem",
    "InstituteListResponse",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListItem",
    "ProjectListResponse",
    "CompetenceCreate",
    "CompetenceResponse",
    "CompetenceListResponse",
]
