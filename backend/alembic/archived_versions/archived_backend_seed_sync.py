"""Simple Wave 2 Seed Script - Synchronous version"""

import json
from datetime import datetime, timedelta
from uuid import uuid4
import psycopg2
from psycopg2.extras import execute_values

# Database connection
conn = psycopg2.connect(
    host="postgres",
    database="prospecai",
    user="prospecai_user",
    password="prospecai_password"
)

cursor = conn.cursor()

try:
    # 5 Funding Sources
    funding_sources_data = [
        (
            str(uuid4()),
            'FINEP - Financiadora de Inovação e Pesquisa',
            'Programa de apoio à inovação e desenvolvimento tecnológico',
            'grant',
            json.dumps(['tecnologia', 'saúde', 'energia']),
            500000000,
            4, 9,
            (datetime.now() + timedelta(days=120)).date(),
            'active',
            str(uuid4()),
            str(uuid4()),
            str(uuid4()),
        ),
        (
            str(uuid4()),
            'EMBRAPII - Associação Brasileira de Pesquisa e Inovação Industrial',
            'Programa de apoio a projetos de inovação em parceria universidade-empresa',
            'financing',
            json.dumps(['manufatura', 'tecnologia', 'químico']),
            300000000,
            5, 8,
            (datetime.now() + timedelta(days=90)).date(),
            'active',
            str(uuid4()),
            str(uuid4()),
            str(uuid4()),
        ),
        (
            str(uuid4()),
            'FAPSP - Fundação de Amparo à Pesquisa do Estado de São Paulo',
            'Auxílio para pesquisa científica e tecnológica',
            'grant',
            json.dumps(['pesquisa', 'educação', 'tecnologia']),
            200000000,
            1, 7,
            (datetime.now() + timedelta(days=60)).date(),
            'active',
            str(uuid4()),
            str(uuid4()),
            str(uuid4()),
        ),
        (
            str(uuid4()),
            'CNPq - Conselho Nacional de Desenvolvimento Científico e Tecnológico',
            'Bolsas de pesquisa e produtividade',
            'non_refundable',
            json.dumps(['educação', 'pesquisa', 'ciência']),
            150000000,
            1, 6,
            (datetime.now() + timedelta(days=45)).date(),
            'active',
            str(uuid4()),
            str(uuid4()),
            str(uuid4()),
        ),
        (
            str(uuid4()),
            'BNDES - Banco Nacional de Desenvolvimento Econômico e Social',
            'Financiamento de longo prazo para modernização industrial',
            'financing',
            json.dumps(['indústria', 'infraestrutura', 'energia']),
            1000000000,
            6, 9,
            (datetime.now() + timedelta(days=150)).date(),
            'active',
            str(uuid4()),
            str(uuid4()),
            str(uuid4()),
        ),
    ]
    
    # Insert funding sources
    insert_sql = """
        INSERT INTO funding_sources (
            id, name, description, type, sectors, amount, trl_min, trl_max, 
            deadline, status, tenant_id, criado_por, atualizado_por, historico_atualizacoes, 
            criado_em, atualizado_em
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '[]'::jsonb, NOW(), NOW())
    """
    
    cursor.executemany(insert_sql, funding_sources_data)
    conn.commit()
    print("✅ 5 Funding Sources seeded successfully")
    
    # 10 Clients
    clients_data = [
        (
            str(uuid4()),
            f'Empresa Inovação {i}',
            '12.345.678/0001-91',
            f'contato@empresa{i}.com.br',
            '(11) 3000-0000',
            'Setor Tecnológico',
            'large',
            ['prospect', 'lead', 'opportunity', 'client', 'advocate'][i % 5],
            'São Paulo, SP',
            f'Empresa do setor de {["tecnologia", "saúde", "manufatura", "energia", "educação"][i % 5]}',
            'active',
            str(uuid4()),
            str(uuid4()),
            str(uuid4()),
        )
        for i in range(1, 11)
    ]
    
    insert_clients_sql = """
        INSERT INTO clients (
            id, name, cnpj, email, phone, sector, size, maturity, address, notes,
            status, tenant_id, criado_por, atualizado_por, historico_atualizacoes,
            criado_em, atualizado_em
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '[]'::jsonb, NOW(), NOW())
    """
    
    cursor.executemany(insert_clients_sql, clients_data)
    conn.commit()
    print("✅ 10 Clients seeded successfully")
    
    # 3 Institutes
    institutes_data = [
        (
            str(uuid4()),
            'SENAI',
            'Serviço Nacional de Aprendizagem Industrial',
            'Instituto líder em educação e pesquisa industrial',
            'https://www.senai.br',
            'contato@senai.br',
            '(11) 3000-0000',
            'active',
            str(uuid4()),
            str(uuid4()),
            str(uuid4()),
        ),
        (
            str(uuid4()),
            'IPT',
            'Instituto de Pesquisas Tecnológicas',
            'Centro de pesquisa aplicada e inovação',
            'https://www.ipt.br',
            'contato@ipt.br',
            '(11) 3000-0001',
            'active',
            str(uuid4()),
            str(uuid4()),
            str(uuid4()),
        ),
        (
            str(uuid4()),
            'LACTEC',
            'Instituto de Tecnologia para o Desenvolvimento',
            'Laboratório de tecnologia e pesquisa',
            'https://www.lactec.org.br',
            'contato@lactec.org.br',
            '(41) 3000-0000',
            'active',
            str(uuid4()),
            str(uuid4()),
            str(uuid4()),
        ),
    ]
    
    insert_institutes_sql = """
        INSERT INTO institutes (
            id, name, acronym, description, website, contact_email, contact_phone,
            status, tenant_id, criado_por, atualizado_por, historico_atualizacoes,
            criado_em, atualizado_em
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '[]'::jsonb, NOW(), NOW())
    """
    
    cursor.executemany(insert_institutes_sql, institutes_data)
    conn.commit()
    print("✅ 3 Institutes seeded successfully")
    
    print("\n🎉 Wave 2 seed data loaded successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    cursor.close()
    conn.close()
