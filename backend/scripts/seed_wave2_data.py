"""
Wave 2 Seed Script: Populates funding sources, portfolio, clients, interactions, and opportunities.

Includes:
- 5 FundingSources (FINEP, EMBRAPII, FAPSP, CNPq, BNDES)
- 3 Institutes (SENAI, IPT, LACTEC)
- 5 Projects associated to institutes
- 10 Clients with different maturity levels
- 20 Interactions distributed across clients
- 20 Opportunities in various pipeline stages
- 42 ACL rules (7 resources × 6 actions + extras)
- 13 model_field_configurations for entities

Data is seeded with realistic Brazilian context.
"""

import asyncio
import json
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.config.settings import get_settings
settings = get_settings()
from app.domain.entities.client import Client, ClientMaturityEnum
from app.domain.entities.funding_source import (
    FundingSource,
    FundingSourceStatusEnum,
    FundingSourceTypeEnum,
)
from app.domain.entities.institute import Institute, InstituteStatusEnum
from app.domain.entities.interaction import (
    Interaction,
    InteractionOutcomeEnum,
    InteractionTypeEnum,
)
from app.domain.entities.opportunity import (
    Opportunity,
    OpportunityStatusEnum,
    OpportunityStageEnum,
)
from app.domain.entities.project import Project, ProjectStatusEnum
from app.infrastructure.persistence.models import (
    ACLRule,
    ModelFieldConfiguration,
    Base,
)

# Database setup
engine = create_async_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_acl_rules(session: AsyncSession) -> None:
    """Seed 42 ACL rules covering all Wave 2 resources."""
    rules = [
        # FundingSources (6 actions)
        ACLRule(
            resource="funding_sources",
            action="create",
            role="admin",
            description="Create funding sources",
        ),
        ACLRule(
            resource="funding_sources",
            action="create",
            role="gestor",
            description="Create funding sources",
        ),
        ACLRule(
            resource="funding_sources",
            action="read",
            role="admin",
            description="Read all funding sources",
        ),
        ACLRule(
            resource="funding_sources",
            action="read",
            role="gestor",
            description="Read all funding sources",
        ),
        ACLRule(
            resource="funding_sources",
            action="read",
            role="analista",
            description="Read all funding sources",
        ),
        ACLRule(
            resource="funding_sources",
            action="read",
            role="viewer",
            description="Read all funding sources",
        ),
        ACLRule(
            resource="funding_sources",
            action="update",
            role="admin",
            description="Update funding sources",
        ),
        ACLRule(
            resource="funding_sources",
            action="update",
            role="gestor",
            description="Update funding sources",
        ),
        ACLRule(
            resource="funding_sources",
            action="exclude",
            role="admin",
            description="Soft delete funding sources",
        ),
        ACLRule(
            resource="funding_sources",
            action="export",
            role="admin",
            description="Export funding sources to CSV",
        ),
        ACLRule(
            resource="funding_sources",
            action="export",
            role="gestor",
            description="Export funding sources to CSV",
        ),
        ACLRule(
            resource="funding_sources",
            action="export",
            role="analista",
            description="Export funding sources to CSV",
        ),
        # Portfolio (6 actions per subresource: institutes, projects, competences)
        ACLRule(
            resource="portfolio.institutes",
            action="create",
            role="admin",
            description="Create institutes",
        ),
        ACLRule(
            resource="portfolio.institutes",
            action="read",
            role="admin",
            description="Read institutes",
        ),
        ACLRule(
            resource="portfolio.institutes",
            action="read",
            role="gestor",
            description="Read institutes",
        ),
        ACLRule(
            resource="portfolio.institutes",
            action="read",
            role="analista",
            description="Read institutes",
        ),
        ACLRule(
            resource="portfolio.institutes",
            action="update",
            role="admin",
            description="Update institutes",
        ),
        ACLRule(
            resource="portfolio.institutes",
            action="exclude",
            role="admin",
            description="Soft delete institutes",
        ),
        ACLRule(
            resource="portfolio.projects",
            action="create",
            role="admin",
            description="Create projects",
        ),
        ACLRule(
            resource="portfolio.projects",
            action="read",
            role="admin",
            description="Read projects",
        ),
        ACLRule(
            resource="portfolio.projects",
            action="read",
            role="gestor",
            description="Read projects",
        ),
        ACLRule(
            resource="portfolio.projects",
            action="update",
            role="admin",
            description="Update projects",
        ),
        ACLRule(
            resource="portfolio.projects",
            action="exclude",
            role="admin",
            description="Soft delete projects",
        ),
        ACLRule(
            resource="portfolio.competences",
            action="create",
            role="admin",
            description="Create competences",
        ),
        ACLRule(
            resource="portfolio.competences",
            action="read",
            role="admin",
            description="Read competences",
        ),
        ACLRule(
            resource="portfolio.competences",
            action="read",
            role="gestor",
            description="Read competences",
        ),
        # Clients (6 actions)
        ACLRule(
            resource="clients",
            action="create",
            role="admin",
            description="Create clients",
        ),
        ACLRule(
            resource="clients",
            action="create",
            role="gestor",
            description="Create clients",
        ),
        ACLRule(
            resource="clients",
            action="read",
            role="admin",
            description="Read all clients",
        ),
        ACLRule(
            resource="clients",
            action="read",
            role="gestor",
            description="Read all clients",
        ),
        ACLRule(
            resource="clients",
            action="read",
            role="analista",
            description="Read all clients",
        ),
        ACLRule(
            resource="clients",
            action="update",
            role="admin",
            description="Update clients",
        ),
        ACLRule(
            resource="clients",
            action="update",
            role="gestor",
            description="Update clients",
        ),
        ACLRule(
            resource="clients",
            action="exclude",
            role="admin",
            description="Soft delete clients",
        ),
        ACLRule(
            resource="clients",
            action="export",
            role="admin",
            description="Export clients",
        ),
        # Pipeline/Opportunities (6 actions)
        ACLRule(
            resource="pipeline",
            action="create",
            role="admin",
            description="Create opportunities",
        ),
        ACLRule(
            resource="pipeline",
            action="create",
            role="gestor",
            description="Create opportunities",
        ),
        ACLRule(
            resource="pipeline",
            action="read",
            role="admin",
            description="Read opportunities",
        ),
        ACLRule(
            resource="pipeline",
            action="read",
            role="gestor",
            description="Read opportunities",
        ),
        ACLRule(
            resource="pipeline",
            action="read",
            role="analista",
            description="Read opportunities",
        ),
        ACLRule(
            resource="pipeline",
            action="transition",
            role="admin",
            description="Move opportunity between stages",
        ),
        ACLRule(
            resource="pipeline",
            action="transition",
            role="gestor",
            description="Move opportunity between stages",
        ),
        ACLRule(
            resource="pipeline",
            action="exclude",
            role="admin",
            description="Soft delete opportunities",
        ),
        ACLRule(
            resource="pipeline",
            action="export",
            role="admin",
            description="Export opportunities",
        ),
    ]

    session.add_all(rules)
    await session.commit()
    print(f"✓ Seeded {len(rules)} ACL rules")


async def seed_model_field_configurations(session: AsyncSession) -> None:
    """Seed 13 model_field_configurations for Wave 2 entities."""
    configs = [
        # FundingSource
        ModelFieldConfiguration(
            model_name="FundingSource",
            field_name="name",
            label_key="fields.funding_source.name",
            field_type="text",
            visible=True,
            required=True,
            validators={"minLength": 3, "maxLength": 255},
        ),
        ModelFieldConfiguration(
            model_name="FundingSource",
            field_name="type",
            label_key="fields.funding_source.type",
            field_type="enum",
            visible=True,
            required=True,
            validators={"enum": ["grant", "loan", "subsidy", "equity"]},
        ),
        ModelFieldConfiguration(
            model_name="FundingSource",
            field_name="trl_min",
            label_key="fields.funding_source.trl_min",
            field_type="number",
            visible=True,
            required=True,
            validators={"min": 1, "max": 9},
        ),
        ModelFieldConfiguration(
            model_name="FundingSource",
            field_name="sectors",
            label_key="fields.funding_source.sectors",
            field_type="array",
            visible=True,
            required=False,
            validators={"items": {"type": "string"}},
        ),
        # Client
        ModelFieldConfiguration(
            model_name="Client",
            field_name="name",
            label_key="fields.client.name",
            field_type="text",
            visible=True,
            required=True,
            validators={"minLength": 3, "maxLength": 255},
        ),
        ModelFieldConfiguration(
            model_name="Client",
            field_name="cnpj",
            label_key="fields.client.cnpj",
            field_type="text",
            visible=True,
            required=True,
            validators={"pattern": r"^\d{14}$"},
        ),
        ModelFieldConfiguration(
            model_name="Client",
            field_name="maturity",
            label_key="fields.client.maturity",
            field_type="enum",
            visible=True,
            required=True,
            validators={"enum": ["lead", "prospect", "customer", "champion"]},
        ),
        # Interaction
        ModelFieldConfiguration(
            model_name="Interaction",
            field_name="interaction_type",
            label_key="fields.interaction.type",
            field_type="enum",
            visible=True,
            required=True,
            validators={"enum": ["meeting", "email", "phone", "visit", "proposal"]},
        ),
        ModelFieldConfiguration(
            model_name="Interaction",
            field_name="notes",
            label_key="fields.interaction.notes",
            field_type="textarea",
            visible=True,
            required=False,
            validators={"maxLength": 2000},
        ),
        # Project
        ModelFieldConfiguration(
            model_name="Project",
            field_name="name",
            label_key="fields.project.name",
            field_type="text",
            visible=True,
            required=True,
            validators={"minLength": 3, "maxLength": 255},
        ),
        ModelFieldConfiguration(
            model_name="Project",
            field_name="trl",
            label_key="fields.project.trl",
            field_type="number",
            visible=True,
            required=True,
            validators={"min": 1, "max": 9},
        ),
        # Opportunity
        ModelFieldConfiguration(
            model_name="Opportunity",
            field_name="title",
            label_key="fields.opportunity.title",
            field_type="text",
            visible=True,
            required=True,
            validators={"minLength": 5, "maxLength": 255},
        ),
        ModelFieldConfiguration(
            model_name="Opportunity",
            field_name="score",
            label_key="fields.opportunity.score",
            field_type="number",
            visible=True,
            required=True,
            validators={"min": 0, "max": 100},
        ),
    ]

    session.add_all(configs)
    await session.commit()
    print(f"✓ Seeded {len(configs)} model field configurations")


async def seed_funding_sources(session: AsyncSession) -> dict[str, str]:
    """Seed 5 funding sources and return ID mapping."""
    base_date = datetime.now(datetime.UTC)
    funding_sources = [
        FundingSource(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="FINEP Subvenção Econômica 2026",
            description="Programa de subvenção econômica para inovação tecnológica",
            type=FundingSourceTypeEnum.SUBSIDY,
            status=FundingSourceStatusEnum.ACTIVE,
            trl_min=3,
            trl_max=8,
            total_budget=Decimal("100000000.00"),
            available_budget=Decimal("75000000.00"),
            deadline=base_date + timedelta(days=365),
            sectors=["technology", "healthcare", "energy"],
            contact_email="finep@finep.gov.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        FundingSource(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="EMBRAPII Projetos Cooperativos",
            description="Empreendimento com Taxa Zero para P&D",
            type=FundingSourceTypeEnum.LOAN,
            status=FundingSourceStatusEnum.ACTIVE,
            trl_min=4,
            trl_max=7,
            total_budget=Decimal("50000000.00"),
            available_budget=Decimal("40000000.00"),
            deadline=base_date + timedelta(days=180),
            sectors=["manufacturing", "agriculture", "technology"],
            contact_email="suporte@embrapii.org.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        FundingSource(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="FAPESP Auxílio à Pesquisa",
            description="Apoio a projetos de pesquisa em instituições paulistas",
            type=FundingSourceTypeEnum.GRANT,
            status=FundingSourceStatusEnum.ACTIVE,
            trl_min=1,
            trl_max=5,
            total_budget=Decimal("30000000.00"),
            available_budget=Decimal("25000000.00"),
            deadline=base_date + timedelta(days=90),
            sectors=["research", "education", "technology"],
            contact_email="info@fapesp.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        FundingSource(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="CNPq Edital Universal",
            description="Apoio integral a projetos de pesquisa científica e tecnológica",
            type=FundingSourceTypeEnum.GRANT,
            status=FundingSourceStatusEnum.ACTIVE,
            trl_min=1,
            trl_max=6,
            total_budget=Decimal("80000000.00"),
            available_budget=Decimal("60000000.00"),
            deadline=base_date + timedelta(days=120),
            sectors=["research", "technology", "agriculture"],
            contact_email="universal@cnpq.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        FundingSource(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="BNDES Inovação em Setores Tradicionais",
            description="Financiamento para empresas que investem em inovação",
            type=FundingSourceTypeEnum.LOAN,
            status=FundingSourceStatusEnum.ACTIVE,
            trl_min=5,
            trl_max=9,
            total_budget=Decimal("200000000.00"),
            available_budget=Decimal("150000000.00"),
            deadline=base_date + timedelta(days=300),
            sectors=["manufacturing", "agriculture", "healthcare"],
            contact_email="inovacao@bndes.gov.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
    ]

    session.add_all(funding_sources)
    await session.flush()

    mapping = {fs.name: fs.id for fs in funding_sources}
    await session.commit()
    print(f"✓ Seeded {len(funding_sources)} funding sources")
    return mapping


async def seed_portfolio(session: AsyncSession) -> tuple[dict[str, str], dict[str, str]]:
    """Seed 3 institutes and 5 projects. Return ID mappings."""
    base_date = datetime.now(datetime.UTC)

    institutes = [
        Institute(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="SENAI São Paulo",
            description="Serviço Nacional de Aprendizagem Industrial",
            status=InstituteStatusEnum.ACTIVE,
            established_year=1942,
            headquarters_city="São Paulo",
            contact_email="contato@sp.senai.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Institute(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="IPT - Instituto de Pesquisas Tecnológicas",
            description="Instituto de pesquisa vinculado à Secretaria de Desenvolvimento de SP",
            status=InstituteStatusEnum.ACTIVE,
            established_year=1899,
            headquarters_city="São Paulo",
            contact_email="pesquisa@ipt.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Institute(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="LACTEC - Instituo de Tecnologia para o Desenvolvimento",
            description="Centro de excelência em pesquisa e desenvolvimento",
            status=InstituteStatusEnum.ACTIVE,
            established_year=1989,
            headquarters_city="Curitiba",
            contact_email="info@lactec.org.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
    ]

    session.add_all(institutes)
    await session.flush()
    institute_mapping = {inst.name: inst.id for inst in institutes}

    projects = [
        Project(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            institute_id=institutes[0].id,
            name="Automação Industrial com IA",
            description="Desenvolvimento de sistemas de IA para otimizar produção",
            status=ProjectStatusEnum.ACTIVE,
            trl=5,
            start_date=base_date - timedelta(days=180),
            end_date=base_date + timedelta(days=365),
            budget=Decimal("500000.00"),
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Project(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            institute_id=institutes[0].id,
            name="Sustentabilidade em Manufatura",
            description="Redução de emissões através de processos inteligentes",
            status=ProjectStatusEnum.ACTIVE,
            trl=4,
            start_date=base_date - timedelta(days=90),
            end_date=base_date + timedelta(days=450),
            budget=Decimal("750000.00"),
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Project(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            institute_id=institutes[1].id,
            name="Materiais Avançados para Saúde",
            description="Pesquisa em novos materiais biocompatíveis",
            status=ProjectStatusEnum.ACTIVE,
            trl=6,
            start_date=base_date - timedelta(days=200),
            end_date=base_date + timedelta(days=300),
            budget=Decimal("1000000.00"),
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Project(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            institute_id=institutes[2].id,
            name="Smart Grid para Eficiência Energética",
            description="Rede elétrica inteligente com ML",
            status=ProjectStatusEnum.PLANNING,
            trl=3,
            start_date=base_date + timedelta(days=30),
            end_date=base_date + timedelta(days=730),
            budget=Decimal("2000000.00"),
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Project(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            institute_id=institutes[1].id,
            name="Blockchain para Rastreabilidade Agrícola",
            description="Sistema distribuído para rastreamento de commodities",
            status=ProjectStatusEnum.ACTIVE,
            trl=4,
            start_date=base_date - timedelta(days=120),
            end_date=base_date + timedelta(days=240),
            budget=Decimal("600000.00"),
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
    ]

    session.add_all(projects)
    await session.flush()
    project_mapping = {proj.name: proj.id for proj in projects}

    await session.commit()
    print(f"✓ Seeded {len(institutes)} institutes and {len(projects)} projects")
    return institute_mapping, project_mapping


async def seed_clients(session: AsyncSession) -> dict[str, str]:
    """Seed 10 clients with different maturity levels. Return ID mapping."""
    clients = [
        Client(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="TechCorp Brasil",
            cnpj="12345678000195",
            maturity=ClientMaturityEnum.CHAMPION,
            contact_name="João Silva",
            contact_email="joao@techcorp.com.br",
            phone="1133334444",
            website="https://techcorp.com.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Client(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="Indústrias de Precisão SA",
            cnpj="98765432000123",
            maturity=ClientMaturityEnum.CUSTOMER,
            contact_name="Maria Santos",
            contact_email="maria@industriasprecisao.com.br",
            phone="1144445555",
            website="https://industriasprecisao.com.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Client(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="AgriTech Solutions",
            cnpj="55555555000166",
            maturity=ClientMaturityEnum.PROSPECT,
            contact_name="Carlos Oliveira",
            contact_email="carlos@agritech.com.br",
            phone="1155556666",
            website="https://agritech.com.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Client(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="HealthTech Inovação",
            cnpj="11111111000111",
            maturity=ClientMaturityEnum.LEAD,
            contact_name="Ana Costa",
            contact_email="ana@healthtech.com.br",
            phone="1166667777",
            website="https://healthtech.com.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Client(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="Logística Inteligente",
            cnpj="22222222000122",
            maturity=ClientMaturityEnum.CUSTOMER,
            contact_name="Pedro Ferreira",
            contact_email="pedro@logisticaint.com.br",
            phone="1177778888",
            website="https://logisticaint.com.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Client(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="Construção Digital",
            cnpj="33333333000133",
            maturity=ClientMaturityEnum.PROSPECT,
            contact_name="Rafael Mendes",
            contact_email="rafael@construcaodigital.com.br",
            phone="1188889999",
            website="https://construcaodigital.com.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Client(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="Energia Renovável Plus",
            cnpj="44444444000144",
            maturity=ClientMaturityEnum.LEAD,
            contact_name="Juliana Lima",
            contact_email="juliana@energiarenovavel.com.br",
            phone="1199990000",
            website="https://energiarenovavel.com.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Client(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="Varejo Inteligente",
            cnpj="66666666000166",
            maturity=ClientMaturityEnum.CHAMPION,
            contact_name="Roberto Dias",
            contact_email="roberto@varejoInt.com.br",
            phone="1111112222",
            website="https://varejoInt.com.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Client(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="Educação Conectada",
            cnpj="77777777000177",
            maturity=ClientMaturityEnum.PROSPECT,
            contact_name="Fernanda Alves",
            contact_email="fernanda@educacaoconectada.com.br",
            phone="1122223333",
            website="https://educacaoconectada.com.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
        Client(
            id=str(uuid4()),
            tenant_id="00000000-0000-0000-0000-000000000001",
            name="Turismo Digital",
            cnpj="88888888000188",
            maturity=ClientMaturityEnum.LEAD,
            contact_name="Gustavo Pereira",
            contact_email="gustavo@turismodigital.com.br",
            phone="1133334444",
            website="https://turismodigital.com.br",
            created_by="00000000-0000-0000-0000-000000000123",
            version=1,
        ),
    ]

    session.add_all(clients)
    await session.flush()
    mapping = {c.name: c.id for c in clients}
    await session.commit()
    print(f"✓ Seeded {len(clients)} clients")
    return mapping


async def seed_interactions(session: AsyncSession, client_mapping: dict[str, str]) -> None:
    """Seed 20 interactions distributed across clients."""
    base_date = datetime.now(datetime.UTC)
    interactions = []

    client_ids = list(client_mapping.values())
    base_notes = [
        "Discussão sobre necessidades de automação",
        "Apresentação de soluções disponíveis",
        "Proposta técnica e orçamentária enviada",
        "Validação de requisitos de integração",
        "Feedback positivo, próximos passos agendados",
        "Análise de viabilidade técnica em andamento",
        "Cliente interessado em prototipagem",
        "Contato perdido, necessário reabordagem",
        "Negociação de termos comerciais",
        "Assinatura de contrato prevista",
    ]

    for i in range(20):
        client_id = client_ids[i % len(client_ids)]
        interaction_type = [
            InteractionTypeEnum.MEETING,
            InteractionTypeEnum.EMAIL,
            InteractionTypeEnum.PHONE,
            InteractionTypeEnum.VISIT,
        ][i % 4]
        outcome = [
            InteractionOutcomeEnum.POSITIVE,
            InteractionOutcomeEnum.NEUTRAL,
            InteractionOutcomeEnum.NEGATIVE,
        ][i % 3]

        interactions.append(
            Interaction(
                id=str(uuid4()),
                tenant_id="00000000-0000-0000-0000-000000000001",
                client_id=client_id,
                interaction_type=interaction_type,
                outcome=outcome,
                date=base_date - timedelta(days=30 - i),
                participants=["comercial@prospecai.com", "gestor@prospecai.com"],
                notes=base_notes[i % len(base_notes)],
                created_by="00000000-0000-0000-0000-000000000123",
                version=1,
            )
        )

    session.add_all(interactions)
    await session.commit()
    print(f"✓ Seeded {len(interactions)} interactions")


async def seed_opportunities(
    session: AsyncSession,
    client_mapping: dict[str, str],
    funding_mapping: dict[str, str],
) -> None:
    """Seed 20 opportunities in various pipeline stages."""
    base_date = datetime.now(datetime.UTC)
    opportunities = []

    client_ids = list(client_mapping.values())
    funding_ids = list(funding_mapping.values())

    stages = [
        OpportunityStageEnum.INTELLIGENCE,
        OpportunityStageEnum.VALIDATION,
        OpportunityStageEnum.APPROACH,
        OpportunityStageEnum.REGISTRATION,
        OpportunityStageEnum.CONVERSION,
        OpportunityStageEnum.POST_SALE,
    ]

    stage_scores = {
        OpportunityStageEnum.INTELLIGENCE: 30,
        OpportunityStageEnum.VALIDATION: 45,
        OpportunityStageEnum.APPROACH: 60,
        OpportunityStageEnum.REGISTRATION: 75,
        OpportunityStageEnum.CONVERSION: 85,
        OpportunityStageEnum.POST_SALE: 95,
    }

    titles = [
        "Proposta de Automação Industrial",
        "Projeto de Sustentabilidade Energética",
        "Sistema de Rastreabilidade Agrícola",
        "Solução de IoT para Manufatura",
        "Platform de IA para Saúde",
        "Sistema de Gestão Logística",
        "Transformação Digital Retail",
        "Projeto de Smart City",
        "Sistema de Educação Online",
        "Plataforma de Turismo Digital",
        "Análise de Dados em Tempo Real",
        "Cybersegurança para Indústria 4.0",
        "Blockchain para Supply Chain",
        "Automação de Processos com RPA",
        "Machine Learning para Previsão",
        "BI e Analytics Avançado",
        "Cloud Computing para PME",
        "Transformação Cultural Digital",
        "Inovação em Modelos de Negócio",
        "Eficiência Operacional com IA",
    ]

    for i in range(20):
        stage = stages[i % len(stages)]
        opportunities.append(
            Opportunity(
                id=str(uuid4()),
                tenant_id="00000000-0000-0000-0000-000000000001",
                title=titles[i],
                description=f"Oportunidade de {titles[i].lower()} com grande potencial",
                client_id=client_ids[i % len(client_ids)],
                funding_source_id=funding_ids[i % len(funding_ids)],
                stage=stage,
                status=OpportunityStatusEnum.ACTIVE,
                score=stage_scores[stage] + (i % 10),
                probability=stage_scores[stage],
                expected_close_date=base_date + timedelta(days=30 + i * 5),
                responsible_id="00000000-0000-0000-0000-000000000123",
                created_by="00000000-0000-0000-0000-000000000123",
                version=1,
            )
        )

    session.add_all(opportunities)
    await session.commit()
    print(f"✓ Seeded {len(opportunities)} opportunities")


async def main() -> None:
    """Execute all seeds."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        try:
            # Check if data already seeded (avoid duplicates)
            result = await session.execute(
                sa.select(sa.func.count(FundingSource.id))
            )
            count = result.scalar() or 0
            if count > 0:
                print("⚠️  Wave 2 data already seeded. Skipping...")
                return

            print("\n🌱 Starting Wave 2 Seed...\n")

            await seed_acl_rules(session)
            await seed_model_field_configurations(session)
            funding_mapping = await seed_funding_sources(session)
            institute_mapping, project_mapping = await seed_portfolio(session)
            client_mapping = await seed_clients(session)
            await seed_interactions(session, client_mapping)
            await seed_opportunities(session, client_mapping, funding_mapping)

            print("\n✅ Wave 2 seed completed successfully!\n")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error during seeding: {e}\n")
            raise


if __name__ == "__main__":
    asyncio.run(main())
