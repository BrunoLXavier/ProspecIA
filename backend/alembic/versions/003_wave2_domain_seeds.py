"""Wave 2: Core domain data seeds (funding sources, clients, institutes).

Revision ID: 003_wave2_domain_seeds
Revises: 002_wave0_system_config
Create Date: 2026-01-09

Seeds sample data for:
- Funding sources (5 items)
- Clients (10 items)
- Institutes (3 items)

Idempotent: uses INSERT ... ON CONFLICT DO NOTHING for cnpj/acronym uniqueness.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '003_wave2_domain_seeds'
down_revision = '002_wave0_system_config'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Seed Wave 2 core domain data."""
    
    # Seed funding sources
    op.execute('''
    INSERT INTO funding_sources 
    (id, name, description, type, sectors, amount, trl_min, trl_max, deadline, status, tenant_id, criado_por, atualizado_por, criado_em, atualizado_em) 
    VALUES
    (gen_random_uuid(), 'FINEP - Financiadora de Inovação e Pesquisa', 
     'Programa de apoio à inovação e desenvolvimento tecnológico', 
     'grant', '[\"tecnologia\",\"saúde\",\"energia\"]'::jsonb, 500000000, 4, 9, 
     CURRENT_DATE + interval '120 days', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    
    (gen_random_uuid(), 'EMBRAPII - Associação Brasileira de Pesquisa e Inovação Industrial', 
     'Programa de apoio a projetos de inovação em parceria universidade-empresa', 
     'financing', '[\"manufatura\",\"tecnologia\",\"químico\"]'::jsonb, 300000000, 5, 8, 
     CURRENT_DATE + interval '90 days', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    
    (gen_random_uuid(), 'FAPSP - Fundação de Amparo à Pesquisa do Estado de São Paulo', 
     'Auxílio para pesquisa científica e tecnológica', 
     'grant', '[\"pesquisa\",\"educação\",\"tecnologia\"]'::jsonb, 200000000, 1, 7, 
     CURRENT_DATE + interval '60 days', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    
    (gen_random_uuid(), 'CNPq - Conselho Nacional de Desenvolvimento Científico e Tecnológico', 
     'Bolsas de pesquisa e produtividade', 
     'non_refundable', '[\"educação\",\"pesquisa\",\"ciência\"]'::jsonb, 150000000, 1, 6, 
     CURRENT_DATE + interval '45 days', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    
    (gen_random_uuid(), 'BNDES - Banco Nacional de Desenvolvimento Econômico e Social', 
     'Financiamento de longo prazo para modernização industrial', 
     'financing', '[\"indústria\",\"infraestrutura\",\"energia\"]'::jsonb, 1000000000, 6, 9, 
     CURRENT_DATE + interval '150 days', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW())
    ON CONFLICT DO NOTHING;
    ''')
    
    # Seed clients (with unique CNPJ per client)
    op.execute('''
    INSERT INTO clients 
    (id, name, cnpj, email, phone, sector, size, maturity, address, notes, status, tenant_id, criado_por, atualizado_por, criado_em, atualizado_em) 
    VALUES
    (gen_random_uuid(), 'Empresa Inovação 1', '12.345.678/0001-91', 'contato@empresa1.com.br', '(11) 3000-0000', 'Tecnologia', 'large', 'prospect', 'São Paulo, SP', 'Empresa do setor de tecnologia', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'Empresa Inovação 2', '12.345.678/0001-92', 'contato@empresa2.com.br', '(11) 3000-0001', 'Saúde', 'large', 'lead', 'Rio de Janeiro, RJ', 'Empresa do setor de saúde', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'Empresa Inovação 3', '12.345.678/0001-93', 'contato@empresa3.com.br', '(11) 3000-0002', 'Manufatura', 'medium', 'opportunity', 'Belo Horizonte, MG', 'Empresa do setor de manufatura', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'Empresa Inovação 4', '12.345.678/0001-94', 'contato@empresa4.com.br', '(11) 3000-0003', 'Energia', 'large', 'client', 'Salvador, BA', 'Empresa do setor de energia', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'Empresa Inovação 5', '12.345.678/0001-95', 'contato@empresa5.com.br', '(11) 3000-0004', 'Educação', 'small', 'advocate', 'Brasília, DF', 'Empresa do setor de educação', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'Empresa Inovação 6', '12.345.678/0001-96', 'contato@empresa6.com.br', '(11) 3000-0005', 'Tecnologia', 'large', 'prospect', 'Curitiba, PR', 'Empresa do setor de tecnologia', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'Empresa Inovação 7', '12.345.678/0001-97', 'contato@empresa7.com.br', '(11) 3000-0006', 'Saúde', 'medium', 'lead', 'Fortaleza, CE', 'Empresa do setor de saúde', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'Empresa Inovação 8', '12.345.678/0001-98', 'contato@empresa8.com.br', '(11) 3000-0007', 'Manufatura', 'large', 'opportunity', 'Porto Alegre, RS', 'Empresa do setor de manufatura', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'Empresa Inovação 9', '12.345.678/0001-99', 'contato@empresa9.com.br', '(11) 3000-0008', 'Energia', 'small', 'client', 'Recife, PE', 'Empresa do setor de energia', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'Empresa Inovação 10', '12.345.678/0001-00', 'contato@empresa10.com.br', '(11) 3000-0009', 'Educação', 'large', 'advocate', 'Manaus, AM', 'Empresa do setor de educação', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW())
    ON CONFLICT DO NOTHING;
    ''')
    
    # Seed institutes
    op.execute('''
    INSERT INTO institutes 
    (id, name, acronym, description, website, contact_email, contact_phone, status, tenant_id, criado_por, atualizado_por, criado_em, atualizado_em) 
    VALUES
    (gen_random_uuid(), 'SENAI', 'SENAI', 'Serviço Nacional de Aprendizagem Industrial - Instituto líder em educação e pesquisa industrial', 'https://www.senai.br', 'contato@senai.br', '(11) 3000-0000', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'IPT', 'IPT', 'Instituto de Pesquisas Tecnológicas - Centro de pesquisa aplicada e inovação', 'https://www.ipt.br', 'contato@ipt.br', '(11) 3000-0001', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW()),
    (gen_random_uuid(), 'LACTEC', 'LACTEC', 'Instituto de Tecnologia para o Desenvolvimento - Laboratório de tecnologia e pesquisa', 'https://www.lactec.org.br', 'contato@lactec.org.br', '(41) 3000-0000', 'active', gen_random_uuid(), gen_random_uuid(), gen_random_uuid(), NOW(), NOW())
    ON CONFLICT DO NOTHING;
    ''')


def downgrade() -> None:
    """Remove seed data (all records from seeded sources)."""
    op.execute('DELETE FROM funding_sources WHERE name IN (\'FINEP - Financiadora de Inovação e Pesquisa\', \'EMBRAPII - Associação Brasileira de Pesquisa e Inovação Industrial\', \'FAPSP - Fundação de Amparo à Pesquisa do Estado de São Paulo\', \'CNPq - Conselho Nacional de Desenvolvimento Científico e Tecnológico\', \'BNDES - Banco Nacional de Desenvolvimento Econômico e Social\')')
    op.execute('DELETE FROM clients WHERE name LIKE \'Empresa Inovação%\'')
    op.execute('DELETE FROM institutes WHERE acronym IN (\'SENAI\', \'IPT\', \'LACTEC\')')
