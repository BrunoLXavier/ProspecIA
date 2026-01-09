"""
Domain services - Application business logic.

Services orchestrate repository operations and coordinate cross-cutting concerns.
Stateless, pure business logic with no HTTP or infrastructure dependencies.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.domain.entities.client_entity import ClientEntity, ClientMaturity, ClientStatus
from app.domain.entities.funding_source_entity import FundingSourceEntity
from app.domain.entities.interaction_entity import (
    InteractionEntity,
    InteractionOutcome,
    InteractionStatus,
    InteractionType,
)
from app.domain.entities.opportunity_entity import (
    OpportunityEntity,
    OpportunityStage,
    OpportunityStatus,
)
from app.domain.entities.portfolio_entity import InstituteEntity, ProjectEntity

# Type aliases for repository protocols (will be injected at runtime)
ClientsRepositoryType = Any
OpportunitiesRepositoryType = Any
InteractionsRepositoryType = Any
FundingSourcesRepositoryType = Any


class ClientService:
    """Service for client business logic and use-case orchestration."""

    def __init__(self, clients_repository: ClientsRepositoryType):
        self.clients_repository = clients_repository

    async def register_new_client(
        self,
        name: str,
        cnpj: str,
        email: str,
        tenant_id: UUID,
        created_by: UUID,
        maturity: Optional[ClientMaturity] = None,
        **kwargs,
    ) -> ClientEntity:
        """Register a new prospect client (CRM use case)."""
        # Validate CNPJ format
        if not self._validate_cnpj(cnpj):
            raise ValueError(f"Invalid CNPJ format: {cnpj}")

        # Create domain entity
        entity = ClientEntity(
            id=None,  # Will be set by repository
            name=name,
            cnpj=cnpj,
            email=email,
            maturity=maturity or ClientMaturity.PROSPECT,
            status=ClientStatus.ACTIVE,
            tenant_id=tenant_id,
            criado_por=created_by,
            criado_em=datetime.now(datetime.UTC),
            **kwargs,
        )

        # Persist via repository
        # Repository will handle ORM conversion
        persisted = await self.clients_repository.create(entity)
        return persisted

    async def upgrade_maturity(
        self,
        client_id: UUID,
        tenant_id: UUID,
        new_maturity: ClientMaturity,
        updated_by: UUID,
        reason: Optional[str] = None,
    ) -> bool:
        """Promote client to next maturity level (CRM workflow)."""
        client = await self.clients_repository.get(client_id, tenant_id)
        if not client:
            return False

        # Validate maturity progression
        allowed_transitions: Dict[ClientMaturity, List[ClientMaturity]] = {
            ClientMaturity.PROSPECT: [ClientMaturity.LEAD, ClientMaturity.OPPORTUNITY],
            ClientMaturity.LEAD: [ClientMaturity.OPPORTUNITY, ClientMaturity.CLIENT],
            ClientMaturity.OPPORTUNITY: [ClientMaturity.CLIENT, ClientMaturity.ADVOCATE],
            ClientMaturity.CLIENT: [ClientMaturity.ADVOCATE],
            ClientMaturity.ADVOCATE: [],
        }

        if new_maturity not in allowed_transitions.get(client.maturity, []):
            raise ValueError(f"Cannot transition from {client.maturity} to {new_maturity}")

        # Update via repository
        await self.clients_repository.update(
            client_id,
            tenant_id,
            {"maturity": new_maturity},
            updated_by,
            reason or f"Maturity upgrade to {new_maturity.value}",
        )
        return True

    @staticmethod
    def _validate_cnpj(cnpj: str) -> bool:
        """Validate CNPJ format (basic check)."""
        # Remove non-numeric characters
        clean = "".join(filter(str.isdigit, cnpj))
        return len(clean) == 14


class OpportunityService:
    """Service for opportunity business logic and pipeline management."""

    def __init__(self, opportunities_repository: OpportunitiesRepositoryType):
        self.opportunities_repository = opportunities_repository

    async def create_opportunity(
        self,
        client_id: UUID,
        title: str,
        description: str,
        tenant_id: UUID,
        created_by: UUID,
        funding_source_id: Optional[UUID] = None,
        **kwargs,
    ) -> OpportunityEntity:
        """Create new sales opportunity with stage validation."""
        entity = OpportunityEntity(
            id=None,
            client_id=client_id,
            title=title,
            description=description,
            stage=OpportunityStage.PROSPECTING,  # Initial stage
            status=OpportunityStatus.ACTIVE,
            tenant_id=tenant_id,
            criado_por=created_by,
            criado_em=datetime.utcnow(),
            funding_source_id=funding_source_id,
            **kwargs,
        )
        persisted = await self.opportunities_repository.create(entity)
        return persisted

    async def advance_opportunity(
        self,
        opportunity_id: UUID,
        tenant_id: UUID,
        new_stage: OpportunityStage,
        updated_by: UUID,
        reason: str,
    ) -> bool:
        """Advance opportunity through sales pipeline with validation."""
        existing = await self.opportunities_repository.get(opportunity_id, tenant_id)
        if not existing:
            return False

        if not existing.can_transition_to(new_stage):
            raise ValueError(f"Cannot advance from {existing.stage} to {new_stage}")

        # Transition via repository method that tracks history
        result = await self.opportunities_repository.transition_stage(
            opportunity_id, tenant_id, new_stage, updated_by, reason
        )
        return result is not None


class InteractionService:
    """Service for interaction timeline and engagement tracking."""

    def __init__(self, interactions_repository: InteractionsRepositoryType):
        self.interactions_repository = interactions_repository

    async def log_interaction(
        self,
        client_id: UUID,
        title: str,
        description: str,
        interaction_type: InteractionType,
        tenant_id: UUID,
        created_by: UUID,
        participants: Optional[List[str]] = None,
        **kwargs,
    ) -> InteractionEntity:
        """Log a client interaction for CRM timeline."""
        entity = InteractionEntity(
            id=None,
            client_id=client_id,
            title=title,
            description=description,
            type=interaction_type,
            status=InteractionStatus.ACTIVE,
            date=datetime.now(datetime.UTC),
            tenant_id=tenant_id,
            criado_por=created_by,
            criado_em=datetime.now(datetime.UTC),
            participants=participants or [],
            **kwargs,
        )
        persisted = await self.interactions_repository.create(entity)
        return persisted

    async def complete_interaction(
        self,
        interaction_id: UUID,
        tenant_id: UUID,
        outcome: InteractionOutcome,
        updated_by: UUID,
        notes: Optional[str] = None,
    ) -> bool:
        """Mark interaction as complete with outcome tracking."""
        existing = await self.interactions_repository.get(interaction_id, tenant_id)
        if not existing:
            return False

        updates = {
            "status": InteractionStatus.COMPLETED,
            "outcome": outcome,
        }
        if notes:
            updates["notes"] = notes

        result = await self.interactions_repository.update(
            interaction_id,
            tenant_id,
            updates,
            updated_by,
            f"Completed with outcome: {outcome.value}",
        )
        return result is not None


class FundingSourceService:
    """Service for funding source lifecycle and opportunity matching."""

    def __init__(self, funding_sources_repository: FundingSourcesRepositoryType):
        self.funding_sources_repository = funding_sources_repository

    async def check_opportunity_eligibility(
        self,
        funding_source_id: UUID,
        opportunity_score: int,
        tenant_id: UUID,
    ) -> bool:
        """Verify if opportunity meets funding source criteria."""
        source = await self.funding_sources_repository.get_by_id(funding_source_id, tenant_id)
        if not source:
            return False

        # Check score threshold
        if source.min_score and opportunity_score < source.min_score:
            return False

        # Check deadline
        if source.deadline and source.deadline < datetime.now(datetime.UTC):
            return False

        return True
