"""Squashed initial migration: reconciles current DB state.

Revision ID: 000_squashed_initial
Revises: 
Create Date: 2026-01-09

This migration creates the canonical schema expected by the application
in an idempotent way. It is intended to be the single source of truth
for fresh setups and to reconcile existing databases to a consistent state.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '000_squashed_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm";')

    # Core tables (idempotent)
    op.execute('''
    CREATE TABLE IF NOT EXISTS feature_flags (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        key VARCHAR(100) UNIQUE NOT NULL,
        enabled BOOLEAN DEFAULT false,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    op.execute('''
    CREATE TABLE IF NOT EXISTS configuracoes_sistema (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        chave VARCHAR(100) UNIQUE NOT NULL,
        valor JSONB NOT NULL,
        versao INTEGER DEFAULT 1,
        data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usuario_responsavel VARCHAR(255),
        motivo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    op.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        usuario_id VARCHAR(255),
        acao VARCHAR(50) NOT NULL,
        tabela VARCHAR(100) NOT NULL,
        record_id VARCHAR(255),
        valor_antigo JSONB,
        valor_novo JSONB,
        ip_cliente VARCHAR(45),
        user_agent TEXT,
        tenant_id VARCHAR(100) DEFAULT 'nacional'
    );
    ''')

    op.execute('''
    CREATE TABLE IF NOT EXISTS tenants (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        codigo VARCHAR(50) UNIQUE NOT NULL,
        nome VARCHAR(255) NOT NULL,
        regiao VARCHAR(100),
        ativo BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Ingestion & consent tables (as in original migrations)
    op.execute('''
    CREATE TABLE IF NOT EXISTS ingestoes (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        fonte VARCHAR(50) NOT NULL,
        metodo VARCHAR(50) NOT NULL,
        arquivo_original VARCHAR(500),
        arquivo_storage_path VARCHAR(1000),
        arquivo_size_bytes INTEGER,
        arquivo_mime_type VARCHAR(100),
        confiabilidade_score INTEGER DEFAULT 50,
        total_registros INTEGER,
        registros_validos INTEGER,
        registros_invalidos INTEGER,
        status VARCHAR(50) DEFAULT 'pendente',
        erros_encontrados JSONB,
        pii_detectado JSONB,
        acoes_lgpd JSONB,
        consentimento_id UUID,
        historico_atualizacoes JSONB DEFAULT '[]'::jsonb,
        criado_por UUID,
        tenant_id VARCHAR(50) DEFAULT 'nacional',
        data_ingestao TIMESTAMP,
        data_processamento TIMESTAMP,
        data_criacao TIMESTAMP,
        data_atualizacao TIMESTAMP,
        descricao TEXT,
        tags JSONB,
        metadata_adicional JSONB
    );
    ''')

    op.execute('''
    CREATE TABLE IF NOT EXISTS consentimentos (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        versao INTEGER NOT NULL DEFAULT 1,
        consent_id_base UUID,
        titular_id UUID,
        titular_email VARCHAR(255),
        titular_documento VARCHAR(100),
        finalidade TEXT NOT NULL,
        categorias_dados JSONB DEFAULT '[]'::jsonb,
        consentimento_dado BOOLEAN NOT NULL DEFAULT false,
        data_consentimento TIMESTAMP,
        revogado BOOLEAN NOT NULL DEFAULT false,
        data_revogacao TIMESTAMP,
        motivo_revogacao TEXT,
        origem_coleta VARCHAR(100) DEFAULT 'sistema',
        ip_origem VARCHAR(45),
        user_agent TEXT,
        consentimento_marketing BOOLEAN NOT NULL DEFAULT false,
        consentimento_compartilhamento BOOLEAN NOT NULL DEFAULT false,
        consentimento_analise BOOLEAN NOT NULL DEFAULT false,
        base_legal VARCHAR(100) NOT NULL DEFAULT 'consentimento',
        historico_alteracoes JSONB DEFAULT '[]'::jsonb,
        coletado_por UUID,
        tenant_id VARCHAR(50) DEFAULT 'nacional',
        data_criacao TIMESTAMP,
        data_atualizacao TIMESTAMP,
        data_expiracao TIMESTAMP,
        metadata_adicional JSONB
    );
    ''')

    # Model field configurations and ACL rules
    op.execute('''
    CREATE TABLE IF NOT EXISTS model_field_configurations (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        model_name VARCHAR(100) NOT NULL,
        field_name VARCHAR(100) NOT NULL,
        field_type VARCHAR(50) NOT NULL DEFAULT 'string',
        label_key VARCHAR(100),
        validators JSONB,
        visibility_rule VARCHAR(100) NOT NULL DEFAULT 'all',
        required BOOLEAN NOT NULL DEFAULT false,
        default_value TEXT,
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        created_by UUID,
        CONSTRAINT uq_model_field UNIQUE (model_name, field_name)
    );
    ''')

    op.execute('CREATE INDEX IF NOT EXISTS ix_model_field_configurations_model_name ON model_field_configurations(model_name);')
    op.execute('CREATE INDEX IF NOT EXISTS ix_model_field_configurations_visibility ON model_field_configurations(visibility_rule);')

    op.execute('''
    CREATE TABLE IF NOT EXISTS acl_rules (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        role VARCHAR(100) NOT NULL,
        resource VARCHAR(100) NOT NULL,
        action VARCHAR(50) NOT NULL,
        condition TEXT,
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        created_by UUID,
        CONSTRAINT uq_acl_role_resource_action UNIQUE (role, resource, action)
    );
    ''')
    op.execute('CREATE INDEX IF NOT EXISTS ix_acl_rules_role ON acl_rules(role);')
    op.execute('CREATE INDEX IF NOT EXISTS ix_acl_rules_resource ON acl_rules(resource);')

    # Enums and additional domain tables (funding_sources, portfolio, clients, interactions, opportunities, translations)
    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'funding_source_type') THEN
        CREATE TYPE funding_source_type AS ENUM ('grant', 'financing', 'equity', 'non_refundable', 'tax_incentive', 'mixed');
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'funding_source_status') THEN
        CREATE TYPE funding_source_status AS ENUM ('active', 'inactive', 'archived', 'excluded');
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'project_status') THEN
        CREATE TYPE project_status AS ENUM ('planning', 'active', 'on_hold', 'completed', 'cancelled', 'archived', 'excluded');
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'client_maturity') THEN
        CREATE TYPE client_maturity AS ENUM ('prospect', 'lead', 'opportunity', 'client', 'advocate');
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'client_status') THEN
        CREATE TYPE client_status AS ENUM ('active', 'inactive', 'archived', 'excluded');
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interaction_type') THEN
        CREATE TYPE interaction_type AS ENUM ('meeting', 'email', 'call', 'visit', 'event', 'other');
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interaction_outcome') THEN
        CREATE TYPE interaction_outcome AS ENUM ('positive', 'neutral', 'negative', 'pending');
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interaction_status') THEN
        CREATE TYPE interaction_status AS ENUM ('active', 'archived', 'excluded');
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'opportunity_stage') THEN
        CREATE TYPE opportunity_stage AS ENUM ('intelligence', 'validation', 'approach', 'registration', 'conversion', 'post_sale');
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'opportunity_status') THEN
        CREATE TYPE opportunity_status AS ENUM ('active', 'won', 'lost', 'archived', 'excluded');
      END IF;
    END
    $$;
    """)

    op.execute('''
    CREATE TABLE IF NOT EXISTS institutes (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        acronym VARCHAR(20),
        description TEXT NOT NULL,
        website VARCHAR(255),
        contact_email VARCHAR(255) NOT NULL,
        contact_phone VARCHAR(20),
        status project_status DEFAULT 'active',
        tenant_id UUID,
        historico_atualizacoes JSONB DEFAULT '[]'::jsonb,
        criado_por UUID,
        atualizado_por UUID,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT now(),
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    ''')

    op.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        institute_id UUID,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        objectives TEXT NOT NULL,
        trl SMALLINT,
        budget BIGINT,
        start_date DATE,
        end_date DATE,
        team_size INTEGER DEFAULT 1,
        status project_status DEFAULT 'planning',
        tenant_id UUID,
        historico_atualizacoes JSONB DEFAULT '[]'::jsonb,
        criado_por UUID,
        atualizado_por UUID,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT now(),
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    ''')

    op.execute('''
    CREATE TABLE IF NOT EXISTS competences (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        category VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        tenant_id UUID,
        criado_por UUID,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    ''')

    op.execute('''
    CREATE TABLE IF NOT EXISTS funding_sources (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        type funding_source_type NOT NULL,
        sectors JSONB DEFAULT '[]'::jsonb,
        amount BIGINT DEFAULT 0,
        trl_min SMALLINT,
        trl_max SMALLINT,
        deadline DATE,
        url VARCHAR(500),
        requirements TEXT,
        status funding_source_status DEFAULT 'active',
        tenant_id UUID,
        historico_atualizacoes JSONB DEFAULT '[]'::jsonb,
        criado_por UUID,
        atualizado_por UUID,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT now(),
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    ''')

    op.execute('CREATE INDEX IF NOT EXISTS idx_funding_sources_tenant_id ON funding_sources(tenant_id);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_funding_sources_status ON funding_sources(status);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_funding_sources_deadline ON funding_sources(deadline);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_funding_sources_type ON funding_sources(type);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_funding_sources_tenant_status ON funding_sources(tenant_id, status);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_funding_sources_sectors_gin ON funding_sources USING gin(sectors);')

    op.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        cnpj VARCHAR(18) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone VARCHAR(20),
        website VARCHAR(255),
        sector VARCHAR(100) NOT NULL,
        size VARCHAR(20) NOT NULL,
        maturity client_maturity DEFAULT 'prospect',
        address TEXT,
        notes TEXT,
        status client_status DEFAULT 'active',
        tenant_id UUID,
        historico_atualizacoes JSONB DEFAULT '[]'::jsonb,
        criado_por UUID,
        atualizado_por UUID,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT now(),
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    ''')

    op.execute('''
    CREATE TABLE IF NOT EXISTS interactions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        client_id UUID,
        type interaction_type,
        date TIMESTAMP WITH TIME ZONE,
        subject VARCHAR(255),
        summary TEXT,
        outcome interaction_outcome DEFAULT 'pending',
        next_steps TEXT,
        participants JSONB DEFAULT '[]'::jsonb,
        status interaction_status DEFAULT 'active',
        tenant_id UUID,
        historico_atualizacoes JSONB DEFAULT '[]'::jsonb,
        criado_por UUID,
        atualizado_por UUID,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT now(),
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    ''')

    op.execute('CREATE INDEX IF NOT EXISTS idx_clients_tenant_id ON clients(tenant_id);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_clients_status ON clients(status);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_clients_maturity ON clients(maturity);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_clients_cnpj ON clients(cnpj);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_clients_tenant_status ON clients(tenant_id, status);')

    op.execute('''
    CREATE TABLE IF NOT EXISTS opportunities (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        client_id UUID,
        funding_source_id UUID,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        stage opportunity_stage DEFAULT 'intelligence',
        score SMALLINT DEFAULT 0,
        estimated_value BIGINT DEFAULT 0,
        probability SMALLINT DEFAULT 50,
        expected_close_date TIMESTAMP WITH TIME ZONE,
        responsible_user_id UUID,
        status opportunity_status DEFAULT 'active',
        tenant_id UUID,
        historico_atualizacoes JSONB DEFAULT '[]'::jsonb,
        historico_transicoes JSONB DEFAULT '[]'::jsonb,
        criado_por UUID,
        atualizado_por UUID,
        criado_em TIMESTAMP WITH TIME ZONE DEFAULT now(),
        atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    ''')

    op.execute('CREATE INDEX IF NOT EXISTS idx_opportunities_client_id ON opportunities(client_id);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_opportunities_funding_source_id ON opportunities(funding_source_id);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_opportunities_tenant_id ON opportunities(tenant_id);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_opportunities_stage ON opportunities(stage);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_opportunities_responsible ON opportunities(responsible_user_id);')
    op.execute('CREATE INDEX IF NOT EXISTS idx_opportunities_tenant_stage ON opportunities(tenant_id, stage);')

    op.execute('''
    CREATE TABLE IF NOT EXISTS translations (
        id VARCHAR PRIMARY KEY,
        key VARCHAR NOT NULL,
        namespace VARCHAR NOT NULL,
        pt_br VARCHAR,
        en_us VARCHAR,
        es_es VARCHAR,
        created_at TIMESTAMP WITH TIME ZONE,
        updated_at TIMESTAMP WITH TIME ZONE,
        created_by VARCHAR,
        updated_by VARCHAR
    );
    ''')
    op.execute('CREATE INDEX IF NOT EXISTS ix_translations_key ON translations(key);')
    op.execute('CREATE INDEX IF NOT EXISTS ix_translations_namespace ON translations(namespace);')
    op.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_translations_key_namespace ON translations(key, namespace);')
    op.execute('CREATE INDEX IF NOT EXISTS ix_translations_pt_br_fts ON translations USING gin(to_tsvector(\'portuguese\', pt_br));')
    op.execute('CREATE INDEX IF NOT EXISTS ix_translations_en_us_fts ON translations USING gin(to_tsvector(\'english\', en_us));')
    op.execute('CREATE INDEX IF NOT EXISTS ix_translations_es_es_fts ON translations USING gin(to_tsvector(\'spanish\', es_es));')


def downgrade() -> None:
    # This squashed migration is intended to be the canonical root; downgrading is intentionally left as a no-op.
    op.execute('SELECT 1')
