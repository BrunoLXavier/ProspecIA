"""
Simple Wave 2 Seed Script - Direct SQL approach
"""

import asyncio
import json
from datetime import datetime, timedelta
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Database URL
DATABASE_URL = "postgresql+psycopg://prospecai_user:prospecai_password@postgres:5432/prospecai"

async def seed_data():
    """Seed Wave 2 data"""
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # 5 Funding Sources
            funding_sources = [
                {
                    'id': str(uuid4()),
                    'name': 'FINEP - Financiadora de Inovação e Pesquisa',
                    'description': 'Programa de apoio à inovação e desenvolvimento tecnológico',
                    'type': 'grant',
                    'sectors': json.dumps(['tecnologia', 'saúde', 'energia']),
                    'amount': 500000000,  # 500M BRL in cents
                    'trl_min': 4,
                    'trl_max': 9,
                    'deadline': (datetime.now() + timedelta(days=120)).date(),
                    'status': 'active',
                    'tenant_id': str(uuid4()),
                    'criado_por': str(uuid4()),
                    'atualizado_por': str(uuid4()),
                },
                {
                    'id': str(uuid4()),
                    'name': 'EMBRAPII - Associação Brasileira de Pesquisa e Inovação Industrial',
                    'description': 'Programa de apoio a projetos de inovação em parceria universidade-empresa',
                    'type': 'financing',
                    'sectors': json.dumps(['manufatura', 'tecnologia', 'químico']),
                    'amount': 300000000,  # 300M BRL
                    'trl_min': 5,
                    'trl_max': 8,
                    'deadline': (datetime.now() + timedelta(days=90)).date(),
                    'status': 'active',
                    'tenant_id': str(uuid4()),
                    'criado_por': str(uuid4()),
                    'atualizado_por': str(uuid4()),
                },
                {
                    'id': str(uuid4()),
                    'name': 'FAPSP - Fundação de Amparo à Pesquisa do Estado de São Paulo',
                    'description': 'Auxílio para pesquisa científica e tecnológica',
                    'type': 'grant',
                    'sectors': json.dumps(['pesquisa', 'educação', 'tecnologia']),
                    'amount': 200000000,  # 200M BRL
                    'trl_min': 1,
                    'trl_max': 7,
                    'deadline': (datetime.now() + timedelta(days=60)).date(),
                    'status': 'active',
                    'tenant_id': str(uuid4()),
                    'criado_por': str(uuid4()),
                    'atualizado_por': str(uuid4()),
                },
                {
                    'id': str(uuid4()),
                    'name': 'CNPq - Conselho Nacional de Desenvolvimento Científico e Tecnológico',
                    'description': 'Bolsas de pesquisa e produtividade',
                    'type': 'non_refundable',
                    'sectors': json.dumps(['educação', 'pesquisa', 'ciência']),
                    'amount': 150000000,  # 150M BRL
                    'trl_min': 1,
                    'trl_max': 6,
                    'deadline': (datetime.now() + timedelta(days=45)).date(),
                    'status': 'active',
                    'tenant_id': str(uuid4()),
                    'criado_por': str(uuid4()),
                    'atualizado_por': str(uuid4()),
                },
                {
                    'id': str(uuid4()),
                    'name': 'BNDES - Banco Nacional de Desenvolvimento Econômico e Social',
                    'description': 'Financiamento de longo prazo para modernização industrial',
                    'type': 'financing',
                    'sectors': json.dumps(['indústria', 'infraestrutura', 'energia']),
                    'amount': 1000000000,  # 1B BRL
                    'trl_min': 6,
                    'trl_max': 9,
                    'deadline': (datetime.now() + timedelta(days=150)).date(),
                    'status': 'active',
                    'tenant_id': str(uuid4()),
                    'criado_por': str(uuid4()),
                    'atualizado_por': str(uuid4()),
                },
            ]
            
            # Insert funding sources
            insert_stmt = sa.text("""
                INSERT INTO funding_sources (
                    id, name, description, type, sectors, amount, trl_min, trl_max, 
                    deadline, status, tenant_id, historico_atualizacoes, criado_por, 
                    atualizado_por, criado_em, atualizado_em
                ) VALUES (
                    :id, :name, :description, :type, :sectors::jsonb, :amount, :trl_min, :trl_max,
                    :deadline, :status, :tenant_id, '[]'::jsonb, :criado_por, :atualizado_por,
                    NOW(), NOW()
                )
            """)
            
            for fs in funding_sources:
                await session.execute(insert_stmt, fs)
            
            await session.commit()
            print("✅ 5 Funding Sources seeded successfully")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding funding sources: {e}")
            import traceback
            traceback.print_exc()
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_data())
