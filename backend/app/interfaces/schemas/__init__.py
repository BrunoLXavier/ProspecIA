"""Pydantic schemas module.

This module contains all Pydantic schemas for request/response validation.
Schemas follow Pydantic v2 conventions with proper validation and documentation.
"""

from app.interfaces.schemas.funding_sources import (
    FundingSourceCreate,
    FundingSourceUpdate,
    FundingSourceResponse,
    FundingSourceListItem,
    FundingSourceListResponse,
    FundingSourceHistoryResponse,
)
from app.interfaces.schemas.clients import (
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    ClientListItem,
    ClientListResponse,
    ClientHistoryResponse,
)
from app.interfaces.schemas.interactions import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    InteractionListItem,
    InteractionListResponse,
)
from app.interfaces.schemas.opportunities import (
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityStageTransition,
    OpportunityResponse,
    OpportunityListItem,
    OpportunityListResponse,
    OpportunityTransitionsResponse,
)
from app.interfaces.schemas.portfolio import (
    InstituteCreate,
    InstituteUpdate,
    InstituteResponse,
    InstituteListItem,
    InstituteListResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListItem,
    ProjectListResponse,
    CompetenceCreate,
    CompetenceResponse,
    CompetenceListResponse,
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
