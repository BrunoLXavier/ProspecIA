"""
Mappers - Convert between ORM models and domain entities.

These implement the Bridge pattern, decoupling domain from infrastructure.
"""

from app.domain.entities.client_entity import ClientEntity, ClientMaturity, ClientStatus
from app.domain.entities.funding_source_entity import FundingSourceEntity
from app.domain.entities.interaction_entity import InteractionEntity
from app.domain.entities.opportunity_entity import OpportunityEntity
from app.domain.entities.portfolio_entity import InstituteEntity, ProjectEntity
from app.infrastructure.models.client import Client as ClientORM
from app.infrastructure.models.funding_source import FundingSource as FundingSourceORM
from app.infrastructure.models.interaction import Interaction as InteractionORM
from app.infrastructure.models.opportunity import Opportunity as OpportunityORM
from app.infrastructure.models.portfolio import Institute as InstituteORM
from app.infrastructure.models.portfolio import Project as ProjectORM


class ClientMapper:
    """Mapper between Client ORM and ClientEntity domain model."""

    @staticmethod
    def to_entity(orm: ClientORM) -> ClientEntity:
        """Convert ORM model to domain entity."""
        return ClientEntity(
            id=orm.id,
            name=orm.name,
            cnpj=orm.cnpj,
            email=orm.email,
            maturity=(
                ClientMaturity(orm.maturity.value)
                if hasattr(orm.maturity, "value")
                else orm.maturity
            ),
            status=ClientStatus(orm.status.value) if hasattr(orm.status, "value") else orm.status,
            phone=orm.phone,
            website=orm.website,
            sector=orm.sector,
            size=orm.size,
            address=orm.address,
            notes=orm.notes,
            tenant_id=orm.tenant_id,
            historico_atualizacoes=orm.historico_atualizacoes or [],
            criado_por=orm.criado_por,
            atualizado_por=orm.atualizado_por,
            criado_em=orm.criado_em,
            atualizado_em=orm.atualizado_em,
        )

    @staticmethod
    def to_orm(entity: ClientEntity) -> ClientORM:
        """Convert domain entity to ORM model."""
        orm = ClientORM()
        orm.id = entity.id
        orm.name = entity.name
        orm.cnpj = entity.cnpj
        orm.email = entity.email
        orm.maturity = entity.maturity
        orm.status = entity.status
        orm.phone = entity.phone
        orm.website = entity.website
        orm.sector = entity.sector
        orm.size = entity.size
        orm.address = entity.address
        orm.notes = entity.notes
        orm.tenant_id = entity.tenant_id
        orm.historico_atualizacoes = entity.historico_atualizacoes
        orm.criado_por = entity.criado_por
        orm.atualizado_por = entity.atualizado_por
        orm.criado_em = entity.criado_em
        orm.atualizado_em = entity.atualizado_em
        return orm


class OpportunityMapper:
    """Mapper between Opportunity ORM and OpportunityEntity domain model."""

    @staticmethod
    def to_entity(orm: OpportunityORM) -> OpportunityEntity:
        """Convert ORM model to domain entity."""
        return OpportunityEntity(
            id=orm.id,
            title=orm.title,
            description=orm.description,
            client_id=orm.client_id,
            funding_source_id=orm.funding_source_id,
            stage=orm.stage,
            status=orm.status,
            score=orm.score or 0,
            estimated_value=orm.estimated_value or 0,
            probability=orm.probability or 50,
            expected_close_date=orm.expected_close_date,
            responsible_user_id=orm.responsible_id,
            tenant_id=orm.tenant_id,
            historico_atualizacoes=orm.historico_atualizacoes or [],
            historico_transicoes=orm.historico_transicoes or [],
            criado_por=orm.criado_por,
            atualizado_por=orm.atualizado_por,
            criado_em=orm.criado_em,
            atualizado_em=orm.atualizado_em,
        )

    @staticmethod
    def to_orm(entity: OpportunityEntity) -> OpportunityORM:
        """Convert domain entity to ORM model."""
        orm = OpportunityORM()
        orm.id = entity.id
        orm.title = entity.title
        orm.description = entity.description
        orm.client_id = entity.client_id
        orm.funding_source_id = entity.funding_source_id
        orm.stage = entity.stage
        orm.status = entity.status
        orm.score = entity.score
        orm.estimated_value = entity.estimated_value
        orm.probability = entity.probability
        orm.expected_close_date = entity.expected_close_date
        orm.responsible_id = entity.responsible_user_id
        orm.tenant_id = entity.tenant_id
        orm.historico_atualizacoes = entity.historico_atualizacoes
        orm.historico_transicoes = entity.historico_transicoes
        orm.criado_por = entity.criado_por
        orm.atualizado_por = entity.atualizado_por
        orm.criado_em = entity.criado_em
        orm.atualizado_em = entity.atualizado_em
        return orm


class InteractionMapper:
    """Mapper between Interaction ORM and InteractionEntity domain model."""

    @staticmethod
    def to_entity(orm: InteractionORM) -> InteractionEntity:
        """Convert ORM model to domain entity."""
        return InteractionEntity(
            id=orm.id,
            client_id=orm.client_id,
            title=orm.title,
            description=orm.description,
            interaction_type=orm.interaction_type,
            date=orm.date,
            status=orm.status,
            outcome=orm.outcome,
            participants=orm.participants or [],
            next_steps=orm.next_steps,
            tenant_id=orm.tenant_id,
            criado_por=orm.criado_por,
            criado_em=orm.criado_em,
        )

    @staticmethod
    def to_orm(entity: InteractionEntity) -> InteractionORM:
        """Convert domain entity to ORM model."""
        orm = InteractionORM()
        orm.id = entity.id
        orm.client_id = entity.client_id
        orm.title = entity.title
        orm.description = entity.description
        orm.interaction_type = entity.interaction_type
        orm.date = entity.date
        orm.status = entity.status
        orm.outcome = entity.outcome
        orm.participants = entity.participants
        orm.next_steps = entity.next_steps
        orm.tenant_id = entity.tenant_id
        orm.criado_por = entity.criado_por
        orm.criado_em = entity.criado_em
        return orm


class FundingSourceMapper:
    """Mapper between FundingSource ORM and FundingSourceEntity domain model."""

    @staticmethod
    def to_entity(orm: FundingSourceORM) -> FundingSourceEntity:
        """Convert ORM model to domain entity."""
        return FundingSourceEntity(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            funding_type=orm.type,
            sectors=orm.sectors or [],
            amount=orm.amount or 0,
            trl_min=orm.trl_min or 1,
            trl_max=orm.trl_max or 9,
            deadline=orm.deadline,
            status=orm.status,
            url=orm.url,
            requirements=orm.requirements,
            tenant_id=orm.tenant_id,
            historico_atualizacoes=orm.historico_atualizacoes or [],
            criado_por=orm.criado_por,
            atualizado_por=orm.atualizado_por,
            criado_em=orm.criado_em,
            atualizado_em=orm.atualizado_em,
        )

    @staticmethod
    def to_orm(entity: FundingSourceEntity) -> FundingSourceORM:
        """Convert domain entity to ORM model."""
        orm = FundingSourceORM()
        orm.id = entity.id
        orm.name = entity.name
        orm.description = entity.description
        orm.type = entity.funding_type
        orm.sectors = entity.sectors
        orm.amount = entity.amount
        orm.trl_min = entity.trl_min
        orm.trl_max = entity.trl_max
        orm.deadline = entity.deadline
        orm.status = entity.status
        orm.url = entity.url
        orm.requirements = entity.requirements
        orm.tenant_id = entity.tenant_id
        orm.historico_atualizacoes = entity.historico_atualizacoes
        orm.criado_por = entity.criado_por
        orm.atualizado_por = entity.atualizado_por
        orm.criado_em = entity.criado_em
        orm.atualizado_em = entity.atualizado_em
        return orm


class InstituteMapper:
    """Mapper between Institute ORM and InstituteEntity domain model."""

    @staticmethod
    def to_entity(orm: InstituteORM) -> InstituteEntity:
        """Convert ORM model to domain entity."""
        return InstituteEntity(
            id=orm.id,
            name=orm.name,
            description=orm.description,
            status=orm.status,
            acronym=orm.acronym,
            website=orm.website,
            contact_email=orm.contact_email,
            contact_phone=orm.contact_phone,
            established_year=getattr(orm, "established_year", None),
            headquarters_city=getattr(orm, "headquarters_city", None),
            tenant_id=orm.tenant_id,
            historico_atualizacoes=orm.historico_atualizacoes or [],
            criado_por=orm.criado_por,
            atualizado_por=orm.atualizado_por,
            criado_em=orm.criado_em,
            atualizado_em=orm.atualizado_em,
        )

    @staticmethod
    def to_orm(entity: InstituteEntity) -> InstituteORM:
        """Convert domain entity to ORM model."""
        orm = InstituteORM()
        orm.id = entity.id
        orm.name = entity.name
        orm.description = entity.description
        orm.status = entity.status
        orm.acronym = entity.acronym
        orm.website = entity.website
        orm.contact_email = entity.contact_email
        orm.contact_phone = entity.contact_phone
        if hasattr(orm, "established_year"):
            orm.established_year = entity.established_year
        if hasattr(orm, "headquarters_city"):
            orm.headquarters_city = entity.headquarters_city
        orm.tenant_id = entity.tenant_id
        orm.historico_atualizacoes = entity.historico_atualizacoes
        orm.criado_por = entity.criado_por
        orm.atualizado_por = entity.atualizado_por
        orm.criado_em = entity.criado_em
        orm.atualizado_em = entity.atualizado_em
        return orm


class ProjectMapper:
    """Mapper between Project ORM and ProjectEntity domain model."""

    @staticmethod
    def to_entity(orm: ProjectORM) -> ProjectEntity:
        """Convert ORM model to domain entity."""
        return ProjectEntity(
            id=orm.id,
            institute_id=orm.institute_id,
            title=orm.title,
            description=orm.description,
            objectives=orm.objectives,
            trl=orm.trl,
            status=orm.status,
            budget=orm.budget,
            start_date=orm.start_date,
            end_date=orm.end_date,
            team_size=orm.team_size or 1,
            tenant_id=orm.tenant_id,
            historico_atualizacoes=orm.historico_atualizacoes or [],
            criado_por=orm.criado_por,
            atualizado_por=orm.atualizado_por,
            criado_em=orm.criado_em,
            atualizado_em=orm.atualizado_em,
        )

    @staticmethod
    def to_orm(entity: ProjectEntity) -> ProjectORM:
        """Convert domain entity to ORM model."""
        orm = ProjectORM()
        orm.id = entity.id
        orm.institute_id = entity.institute_id
        orm.title = entity.title
        orm.description = entity.description
        orm.objectives = entity.objectives
        orm.trl = entity.trl
        orm.status = entity.status
        orm.budget = entity.budget
        orm.start_date = entity.start_date
        orm.end_date = entity.end_date
        orm.team_size = entity.team_size
        orm.tenant_id = entity.tenant_id
        orm.historico_atualizacoes = entity.historico_atualizacoes
        orm.criado_por = entity.criado_por
        orm.atualizado_por = entity.atualizado_por
        orm.criado_em = entity.criado_em
        orm.atualizado_em = entity.atualizado_em
        return orm
