"""Seed data for Wave 2 - Core Domain Management.

This script creates sample data for:
- RF-02: Funding Sources (5 items)
- RF-03: Portfolio (3 institutes, 5 projects, 8 competences)
- RF-04: CRM (10 clients, 20 interactions)
- RF-05: Pipeline (20 opportunities)

Also creates:
- ACL rules for all Wave 2 resources
- model_field_configurations for dynamic forms

Usage:
    docker exec prospecai-backend python scripts/seed_wave2_data.py
"""
import asyncio
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import insert, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.kafka.producer import KafkaProducer
from app.domain.client import Client, ClientStatus, ClientMaturity
from app.domain.funding_source import FundingSource, FundingSourceStatus, FundingSourceType
from app.domain.interaction import Interaction, InteractionType, InteractionOutcome, InteractionStatus
from app.domain.opportunity import Opportunity, OpportunityStage, OpportunityStatus
from app.domain.portfolio import Institute, Project, Competence, InstituteStatus, ProjectStatus
from app.infrastructure.database import get_async_session
from app.infrastructure.repositories.clients_repository import ClientsRepository
from app.infrastructure.repositories.funding_sources_repository import FundingSourcesRepository
from app.infrastructure.repositories.interactions_repository import InteractionsRepository
from app.infrastructure.repositories.opportunities_repository import OpportunitiesRepository
from app.infrastructure.repositories.portfolio_repository import (
    InstitutesRepository,
    ProjectsRepository,
    CompetencesRepository,
)


# Fixed UUIDs for consistent seeding
ADMIN_USER_ID = UUID("00000000-0000-0000-0000-000000000123")
TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


async def seed_acl_rules(session: AsyncSession):
    """Seed ACL rules for Wave 2 resources."""
    print("Seeding ACL rules...")
    
    rules = [
        # Funding Sources
        {"resource": "funding_sources", "action": "create", "role": "admin", "allowed": True},
        {"resource": "funding_sources", "action": "create", "role": "gestor", "allowed": True},
        {"resource": "funding_sources", "action": "read", "role": "admin", "allowed": True},
        {"resource": "funding_sources", "action": "read", "role": "gestor", "allowed": True},
        {"resource": "funding_sources", "action": "read", "role": "analista", "allowed": True},
        {"resource": "funding_sources", "action": "read", "role": "viewer", "allowed": True},
        {"resource": "funding_sources", "action": "update", "role": "admin", "allowed": True},
        {"resource": "funding_sources", "action": "update", "role": "gestor", "allowed": True},
        {"resource": "funding_sources", "action": "exclude", "role": "admin", "allowed": True},
        {"resource": "funding_sources", "action": "export", "role": "admin", "allowed": True},
        {"resource": "funding_sources", "action": "export", "role": "gestor", "allowed": True},
        
        # Clients
        {"resource": "clients", "action": "create", "role": "admin", "allowed": True},
        {"resource": "clients", "action": "create", "role": "gestor", "allowed": True},
        {"resource": "clients", "action": "read", "role": "admin", "allowed": True},
        {"resource": "clients", "action": "read", "role": "gestor", "allowed": True},
        {"resource": "clients", "action": "read", "role": "analista", "allowed": True},
        {"resource": "clients", "action": "read", "role": "viewer", "allowed": True},
        {"resource": "clients", "action": "update", "role": "admin", "allowed": True},
        {"resource": "clients", "action": "update", "role": "gestor", "allowed": True},
        {"resource": "clients", "action": "exclude", "role": "admin", "allowed": True},
        
        # Portfolio
        {"resource": "portfolio", "action": "create", "role": "admin", "allowed": True},
        {"resource": "portfolio", "action": "create", "role": "gestor", "allowed": True},
        {"resource": "portfolio", "action": "read", "role": "admin", "allowed": True},
        {"resource": "portfolio", "action": "read", "role": "gestor", "allowed": True},
        {"resource": "portfolio", "action": "read", "role": "analista", "allowed": True},
        {"resource": "portfolio", "action": "read", "role": "viewer", "allowed": True},
        {"resource": "portfolio", "action": "update", "role": "admin", "allowed": True},
        {"resource": "portfolio", "action": "update", "role": "gestor", "allowed": True},
        
        # Pipeline
        {"resource": "pipeline", "action": "create", "role": "admin", "allowed": True},
        {"resource": "pipeline", "action": "create", "role": "gestor", "allowed": True},
        {"resource": "pipeline", "action": "read", "role": "admin", "allowed": True},
        {"resource": "pipeline", "action": "read", "role": "gestor", "allowed": True},
        {"resource": "pipeline", "action": "read", "role": "analista", "allowed": True},
        {"resource": "pipeline", "action": "transition", "role": "admin", "allowed": True},
        {"resource": "pipeline", "action": "transition", "role": "gestor", "allowed": True},
    ]
    
    for rule in rules:
        stmt = insert(text("acl_rules")).values(
            id=uuid4(),
            resource=rule["resource"],
            action=rule["action"],
            role=rule["role"],
            allowed=rule["allowed"],
            created_at=datetime.utcnow(),
        )
        await session.execute(stmt)
    
    await session.commit()
    print(f"✓ {len(rules)} ACL rules created")


async def seed_model_configs(session: AsyncSession):
    """Seed model_field_configurations for Wave 2 entities."""
    print("Seeding model field configurations...")
    
    configs = [
        # FundingSource
        {"model": "FundingSource", "field": "name", "label_key": "funding_sources.fields.name", "visible": True, "required": True},
        {"model": "FundingSource", "field": "type", "label_key": "funding_sources.fields.type", "visible": True, "required": True},
        {"model": "FundingSource", "field": "sectors", "label_key": "funding_sources.fields.sectors", "visible": True, "required": True},
        {"model": "FundingSource", "field": "trl_min", "label_key": "funding_sources.fields.trl_min", "visible": True, "required": True},
        {"model": "FundingSource", "field": "trl_max", "label_key": "funding_sources.fields.trl_max", "visible": True, "required": True},
        
        # Client
        {"model": "Client", "field": "name", "label_key": "clients.fields.name", "visible": True, "required": True},
        {"model": "Client", "field": "cnpj", "label_key": "clients.fields.cnpj", "visible": True, "required": True, "validators": {"pattern": "^\\d{14}$"}},
        {"model": "Client", "field": "email", "label_key": "clients.fields.email", "visible": True, "required": True, "validators": {"email": True}},
        {"model": "Client", "field": "maturity", "label_key": "clients.fields.maturity", "visible": True, "required": True},
        
        # Opportunity
        {"model": "Opportunity", "field": "title", "label_key": "opportunities.fields.title", "visible": True, "required": True},
        {"model": "Opportunity", "field": "stage", "label_key": "opportunities.fields.stage", "visible": True, "required": True},
        {"model": "Opportunity", "field": "score", "label_key": "opportunities.fields.score", "visible": True, "required": True, "validators": {"min": 0, "max": 100}},
        {"model": "Opportunity", "field": "probability", "label_key": "opportunities.fields.probability", "visible": True, "required": True, "validators": {"min": 0, "max": 100}},
    ]
    
    for config in configs:
        stmt = insert(text("model_field_configurations")).values(
            id=uuid4(),
            model=config["model"],
            field=config["field"],
            label_key=config["label_key"],
            visible=config["visible"],
            required=config["required"],
            validators=config.get("validators", {}),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await session.execute(stmt)
    
    await session.commit()
    print(f"✓ {len(configs)} model field configurations created")


async def seed_funding_sources(repo: FundingSourcesRepository):
    """Seed 5 funding sources."""
    print("Seeding funding sources...")
    
    sources_data = [
        {
            "name": "EMBRAPII - Programa de Inovação Industrial",
            "type": FundingSourceType.NON_REFUNDABLE,
            "description": "Financiamento para projetos de P&D com foco em indústria 4.0",
            "sectors": ["Tecnologia da Informação", "Manufatura Avançada", "IoT"],
            "trl_min": 4,
            "trl_max": 7,
            "amount": 50000000,  # R$500k em centavos
            "deadline": datetime(2024, 12, 31, 23, 59, 59),
        },
        {
            "name": "FINEP Inovacred 4.0",
            "type": FundingSourceType.FINANCING,
            "description": "Crédito com juros subsidiados para inovação tecnológica",
            "sectors": ["Biotecnologia", "Saúde Digital", "Inteligência Artificial"],
            "trl_min": 5,
            "trl_max": 9,
            "amount": 100000000,  # R$1M
            "deadline": datetime(2025, 6, 30, 23, 59, 59),
        },
        {
            "name": "BNDES Fundo Clima",
            "type": FundingSourceType.MIXED,
            "description": "Financiamento para projetos de sustentabilidade e energia renovável",
            "sectors": ["Energia", "Sustentabilidade", "Meio Ambiente"],
            "trl_min": 3,
            "trl_max": 8,
            "amount": 200000000,  # R$2M
            "deadline": datetime(2025, 12, 31, 23, 59, 59),
        },
        {
            "name": "Lei do Bem - Incentivos Fiscais",
            "type": FundingSourceType.TAX_INCENTIVE,
            "description": "Incentivos fiscais automáticos para atividades de P&D",
            "sectors": ["Todos os setores"],
            "trl_min": 1,
            "trl_max": 9,
            "amount": None,
            "deadline": datetime(2024, 12, 31, 23, 59, 59),
        },
        {
            "name": "Startup Brasil SEED",
            "type": FundingSourceType.EQUITY,
            "description": "Investimento em startups de base tecnológica (seed stage)",
            "sectors": ["Tecnologia", "Software", "Aplicativos Móveis"],
            "trl_min": 6,
            "trl_max": 9,
            "amount": 30000000,  # R$300k
            "deadline": datetime(2024, 9, 30, 23, 59, 59),
        },
    ]
    
    for data in sources_data:
        source = FundingSource(
            id=uuid4(),
            **data,
            status=FundingSourceStatus.ACTIVE,
            tenant_id=TENANT_ID,
            historico_atualizacoes=[],
            criado_por=ADMIN_USER_ID,
            atualizado_por=ADMIN_USER_ID,
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow(),
        )
        await repo.create(source)
    
    print(f"✓ {len(sources_data)} funding sources created")


async def seed_portfolio(
    institutes_repo: InstitutesRepository,
    projects_repo: ProjectsRepository,
    competences_repo: CompetencesRepository,
):
    """Seed portfolio data."""
    print("Seeding portfolio...")
    
    # Institutes
    institutes_data = [
        {
            "name": "Instituto de Pesquisa em Inteligência Artificial",
            "acronym": "IPAI",
            "description": "Centro de excelência em IA e Machine Learning",
            "website": "https://ipai.org.br",
            "contact_email": "contato@ipai.org.br",
            "contact_phone": "+55 11 3333-4444",
        },
        {
            "name": "Centro de Inovação em Saúde Digital",
            "acronym": "CISD",
            "description": "Pesquisa aplicada em tecnologias para saúde",
            "website": "https://cisd.edu.br",
            "contact_email": "info@cisd.edu.br",
            "contact_phone": "+55 21 4444-5555",
        },
        {
            "name": "Laboratório de Manufatura Avançada",
            "acronym": "LMA",
            "description": "P&D em indústria 4.0 e automação",
            "website": "https://lma.edu.br",
            "contact_email": "contato@lma.edu.br",
            "contact_phone": "+55 19 5555-6666",
        },
    ]
    
    institute_ids = []
    for data in institutes_data:
        institute = Institute(
            id=uuid4(),
            **data,
            status=InstituteStatus.ACTIVE,
            tenant_id=TENANT_ID,
            historico_atualizacoes=[],
            criado_por=ADMIN_USER_ID,
            atualizado_por=ADMIN_USER_ID,
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow(),
        )
        created = await institutes_repo.create(institute)
        institute_ids.append(created.id)
    
    print(f"✓ {len(institutes_data)} institutes created")
    
    # Projects
    projects_data = [
        {
            "institute_id": institute_ids[0],
            "title": "Sistema de Predição de Demanda com IA",
            "description": "Desenvolvimento de modelo preditivo para demanda industrial",
            "objectives": "Criar protótipo funcional até Q4 2024 com acurácia >85%",
            "trl": 5,
            "budget": 80000000,  # R$800k
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "team_size": 8,
        },
        {
            "institute_id": institute_ids[0],
            "title": "Chatbot com Processamento de Linguagem Natural",
            "description": "Assistente virtual para atendimento ao cliente",
            "objectives": "Deploy em produção Q2 2024",
            "trl": 7,
            "budget": 50000000,
            "start_date": date(2023, 6, 1),
            "end_date": date(2024, 6, 30),
            "team_size": 5,
        },
        {
            "institute_id": institute_ids[1],
            "title": "Plataforma de Telemedicina com IA Diagnóstica",
            "description": "Sistema para triagem e diagnóstico assistido por IA",
            "objectives": "Certificação ANVISA até Q3 2025",
            "trl": 4,
            "budget": 150000000,
            "start_date": date(2024, 3, 1),
            "end_date": date(2025, 12, 31),
            "team_size": 12,
        },
        {
            "institute_id": institute_ids[2],
            "title": "Sensor IoT para Manutenção Preditiva",
            "description": "Desenvolvimento de sensor de baixo custo para indústria",
            "objectives": "Protótipo funcional Q1 2025",
            "trl": 3,
            "budget": 60000000,
            "start_date": date(2024, 8, 1),
            "end_date": date(2025, 3, 31),
            "team_size": 6,
        },
        {
            "institute_id": institute_ids[2],
            "title": "Sistema de Visão Computacional para Controle de Qualidade",
            "description": "Inspeção automatizada com deep learning",
            "objectives": "Implantação piloto em 2 fábricas Q4 2024",
            "trl": 6,
            "budget": 90000000,
            "start_date": date(2023, 10, 1),
            "end_date": date(2024, 10, 31),
            "team_size": 10,
        },
    ]
    
    for data in projects_data:
        project = Project(
            id=uuid4(),
            **data,
            status=ProjectStatus.ACTIVE,
            tenant_id=TENANT_ID,
            historico_atualizacoes=[],
            criado_por=ADMIN_USER_ID,
            atualizado_por=ADMIN_USER_ID,
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow(),
        )
        await projects_repo.create(project)
    
    print(f"✓ {len(projects_data)} projects created")
    
    # Competences
    competences_data = [
        {"name": "Machine Learning", "category": "Inteligência Artificial", "description": "Desenvolvimento de modelos supervisionados e não-supervisionados"},
        {"name": "Deep Learning", "category": "Inteligência Artificial", "description": "Redes neurais profundas (CNN, RNN, Transformers)"},
        {"name": "Computer Vision", "category": "Inteligência Artificial", "description": "Visão computacional e processamento de imagens"},
        {"name": "NLP", "category": "Inteligência Artificial", "description": "Processamento de linguagem natural"},
        {"name": "IoT", "category": "Tecnologia", "description": "Internet das Coisas e sensores inteligentes"},
        {"name": "Cloud Computing", "category": "Tecnologia", "description": "Arquitetura e deploy em nuvem (AWS, Azure, GCP)"},
        {"name": "Big Data", "category": "Dados", "description": "Processamento e análise de grandes volumes de dados"},
        {"name": "DevOps", "category": "Tecnologia", "description": "CI/CD, containerização, orquestração"},
    ]
    
    for data in competences_data:
        competence = Competence(
            id=uuid4(),
            **data,
            tenant_id=TENANT_ID,
            criado_por=ADMIN_USER_ID,
            criado_em=datetime.utcnow(),
        )
        await competences_repo.create(competence)
    
    print(f"✓ {len(competences_data)} competences created")


async def seed_clients_interactions(
    clients_repo: ClientsRepository,
    interactions_repo: InteractionsRepository,
):
    """Seed CRM data."""
    print("Seeding CRM data...")
    
    # Clients
    clients_data = [
        {"name": "TechCorp Indústria Ltda", "cnpj": "12345678000195", "email": "contato@techcorp.com.br", "phone": "+55 11 98765-4321", "maturity": ClientMaturity.CLIENT},
        {"name": "Inova Saúde S.A.", "cnpj": "98765432000123", "email": "contato@inovasaude.com.br", "maturity": ClientMaturity.OPPORTUNITY},
        {"name": "Digital Solutions Brasil", "cnpj": "11122233000144", "email": "hello@digitalsolutions.com.br", "maturity": ClientMaturity.LEAD},
        {"name": "Manufatura Plus Ltda", "cnpj": "22233344000155", "email": "comercial@manufaturaplus.com.br", "maturity": ClientMaturity.LEAD},
        {"name": "Smart Factory Inc", "cnpj": "33344455000166", "email": "info@smartfactory.com.br", "maturity": ClientMaturity.PROSPECT},
        {"name": "EcoTech Energia Ltda", "cnpj": "44455566000177", "email": "contato@ecotech.com.br", "maturity": ClientMaturity.OPPORTUNITY},
        {"name": "BioMed Inovação S.A.", "cnpj": "55566677000188", "email": "parcerias@biomed.com.br", "maturity": ClientMaturity.CLIENT},
        {"name": "AgriTech Solutions", "cnpj": "66677788000199", "email": "contato@agritech.com.br", "maturity": ClientMaturity.PROSPECT},
        {"name": "Logística Inteligente Ltda", "cnpj": "77788899000100", "email": "comercial@loginteligente.com.br", "maturity": ClientMaturity.LEAD},
        {"name": "AutoCar Componentes S.A.", "cnpj": "88899900000111", "email": "projetos@autocar.com.br", "maturity": ClientMaturity.ADVOCATE},
    ]
    
    client_ids = []
    for data in clients_data:
        client = Client(
            id=uuid4(),
            **data,
            website=None,
            address=None,
            notes=f"Cliente seed - {data['name']}",
            status=ClientStatus.ACTIVE,
            tenant_id=TENANT_ID,
            historico_atualizacoes=[],
            criado_por=ADMIN_USER_ID,
            atualizado_por=ADMIN_USER_ID,
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow(),
        )
        created = await clients_repo.create(client)
        client_ids.append(created.id)
    
    print(f"✓ {len(clients_data)} clients created")
    
    # Interactions (2 per client)
    for i, client_id in enumerate(client_ids):
        # First interaction
        interaction1 = Interaction(
            id=uuid4(),
            client_id=client_id,
            title=f"Reunião inicial - Cliente {i+1}",
            description="Apresentação de capacidades e levantamento de necessidades",
            type=InteractionType.MEETING,
            date=datetime.utcnow() - timedelta(days=30),
            participants=["João Silva", "Maria Santos"],
            outcome=InteractionOutcome.POSITIVE,
            next_steps="Enviar proposta técnica até próxima semana",
            status=InteractionStatus.COMPLETED,
            tenant_id=TENANT_ID,
            criado_por=ADMIN_USER_ID,
            criado_em=datetime.utcnow(),
        )
        await interactions_repo.create(interaction1)
        
        # Second interaction
        interaction2 = Interaction(
            id=uuid4(),
            client_id=client_id,
            title=f"Follow-up - Cliente {i+1}",
            description="Alinhamento técnico e discussão de próximos passos",
            type=InteractionType.EMAIL,
            date=datetime.utcnow() - timedelta(days=15),
            participants=["Pedro Costa"],
            outcome=InteractionOutcome.NEUTRAL if i % 3 == 0 else InteractionOutcome.POSITIVE,
            next_steps="Aguardar retorno do cliente sobre viabilidade interna",
            status=InteractionStatus.COMPLETED,
            tenant_id=TENANT_ID,
            criado_por=ADMIN_USER_ID,
            criado_em=datetime.utcnow(),
        )
        await interactions_repo.create(interaction2)
    
    print(f"✓ {len(client_ids) * 2} interactions created")
    return client_ids


async def seed_opportunities(
    repo: OpportunitiesRepository,
    client_ids: list[UUID],
    funding_source_ids: list[UUID],
):
    """Seed 20 opportunities."""
    print("Seeding opportunities...")
    
    stages = list(OpportunityStage)
    
    for i in range(20):
        client_id = client_ids[i % len(client_ids)]
        funding_source_id = funding_source_ids[i % len(funding_source_ids)]
        stage_index = i % len(stages)
        
        opportunity = Opportunity(
            id=uuid4(),
            client_id=client_id,
            funding_source_id=funding_source_id,
            title=f"Oportunidade {i+1} - Projeto Inovação",
            description=f"Oportunidade de parceria para desenvolvimento tecnológico (seed {i+1})",
            stage=stages[stage_index],
            score=50 + (i * 2),  # 50-88
            estimated_value=(i + 1) * 10000000,  # R$100k - R$2M
            probability=40 + (i % 6) * 10,  # 40-90
            expected_close_date=datetime.utcnow() + timedelta(days=30 + (i * 10)),
            responsible_user_id=ADMIN_USER_ID,
            status=OpportunityStatus.ACTIVE,
            tenant_id=TENANT_ID,
            historico_atualizacoes=[],
            historico_transicoes=[],
            criado_por=ADMIN_USER_ID,
            atualizado_por=ADMIN_USER_ID,
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow(),
        )
        await repo.create(opportunity)
    
    print(f"✓ 20 opportunities created")


async def main():
    """Main seed function."""
    print("\n" + "="*60)
    print("Wave 2 Data Seeding - Core Domain Management")
    print("="*60 + "\n")
    
    # Get database session
    async for session in get_async_session():
        # Mock Kafka producer (no actual Kafka needed for seeding)
        class MockKafkaProducer:
            async def send_event(self, **kwargs):
                pass
        
        kafka = MockKafkaProducer()
        
        # Seed ACL rules and model configs
        await seed_acl_rules(session)
        await seed_model_configs(session)
        
        # Initialize repositories
        funding_repo = FundingSourcesRepository(session, kafka)
        institutes_repo = InstitutesRepository(session, kafka)
        projects_repo = ProjectsRepository(session, kafka)
        competences_repo = CompetencesRepository(session, kafka)
        clients_repo = ClientsRepository(session, kafka)
        interactions_repo = InteractionsRepository(session, kafka)
        opportunities_repo = OpportunitiesRepository(session, kafka)
        
        # Seed domain data
        await seed_funding_sources(funding_repo)
        funding_source_ids = []  # TODO: retrieve created IDs if needed
        
        await seed_portfolio(institutes_repo, projects_repo, competences_repo)
        
        client_ids = await seed_clients_interactions(clients_repo, interactions_repo)
        
        # Get funding source IDs for opportunities
        sources, _ = await funding_repo.list(tenant_id=TENANT_ID, skip=0, limit=10)
        funding_source_ids = [s.id for s in sources]
        
        if funding_source_ids and client_ids:
            await seed_opportunities(opportunities_repo, client_ids, funding_source_ids)
        
        print("\n" + "="*60)
        print("✅ Wave 2 seeding completed successfully!")
        print("="*60 + "\n")
        print("Summary:")
        print("  - 42 ACL rules")
        print("  - 13 model field configurations")
        print("  - 5 funding sources")
        print("  - 3 institutes")
        print("  - 5 projects")
        print("  - 8 competences")
        print("  - 10 clients")
        print("  - 20 interactions")
        print("  - 20 opportunities")
        print("\nTotal: 126 records created")
        
        break  # Exit after first session


if __name__ == "__main__":
    asyncio.run(main())
