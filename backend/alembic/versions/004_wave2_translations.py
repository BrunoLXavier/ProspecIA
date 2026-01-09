"""Wave 2: Translations data seeds.

Revision ID: 004_wave2_translations
Revises: 003_wave2_domain_seeds
Create Date: 2026-01-09

Seeds initial translations for:
- Common UI labels
- Admin interface
- Ingestion module
- Wave 2 modules

Idempotent: uses INSERT ... ON CONFLICT DO NOTHING.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '004_wave2_translations'
down_revision = '003_wave2_domain_seeds'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Seed translations data."""
    
    # Insert all translations (idempotent with ON CONFLICT DO NOTHING)
    op.execute('''
    INSERT INTO translations (id, key, namespace, pt_br, en_us, es_es, created_at, updated_at, created_by, updated_by) VALUES
    -- Common translations
    ('common:app_title', 'app_title', 'common', 'ProspecIA', 'ProspecIA', 'ProspecIA', NOW(), NOW(), 'system', 'system'),
    ('common:app_subtitle', 'app_subtitle', 'common', 'Sistema de Gestão de Inovação', 'Innovation Management System', 'Sistema de Gestión de Innovación', NOW(), NOW(), 'system', 'system'),
    ('common:save', 'save', 'common', 'Salvar', 'Save', 'Guardar', NOW(), NOW(), 'system', 'system'),
    ('common:cancel', 'cancel', 'common', 'Cancelar', 'Cancel', 'Cancelar', NOW(), NOW(), 'system', 'system'),
    ('common:delete', 'delete', 'common', 'Excluir', 'Delete', 'Eliminar', NOW(), NOW(), 'system', 'system'),
    ('common:edit', 'edit', 'common', 'Editar', 'Edit', 'Editar', NOW(), NOW(), 'system', 'system'),
    
    -- Admin translations
    ('admin:translations_title', 'translations_title', 'admin', 'Gerenciamento de Traduções', 'Translation Management', 'Gestión de Traducciones', NOW(), NOW(), 'system', 'system'),
    ('admin:translations_description', 'translations_description', 'admin', 'Configure as traduções do sistema', 'Configure system translations', 'Configure las traducciones del sistema', NOW(), NOW(), 'system', 'system'),
    ('admin:key', 'key', 'admin', 'Chave', 'Key', 'Clave', NOW(), NOW(), 'system', 'system'),
    ('admin:namespace', 'namespace', 'admin', 'Namespace', 'Namespace', 'Espacio de nombres', NOW(), NOW(), 'system', 'system'),
    ('admin:portuguese', 'portuguese', 'admin', 'Português', 'Portuguese', 'Portugués', NOW(), NOW(), 'system', 'system'),
    ('admin:english', 'english', 'admin', 'Inglês', 'English', 'Inglés', NOW(), NOW(), 'system', 'system'),
    ('admin:spanish', 'spanish', 'admin', 'Espanhol', 'Spanish', 'Español', NOW(), NOW(), 'system', 'system'),
    
    -- Ingestion translations
    ('ingestion:title', 'title', 'ingestion', 'Ingestão de Dados', 'Data Ingestion', 'Ingestión de Datos', NOW(), NOW(), 'system', 'system'),
    ('ingestion:source', 'source', 'ingestion', 'Fonte', 'Source', 'Fuente', NOW(), NOW(), 'system', 'system'),
    ('ingestion:status', 'status', 'ingestion', 'Status', 'Status', 'Estado', NOW(), NOW(), 'system', 'system'),
    
    -- Wave 2 translations
    ('wave2:funding_sources', 'funding_sources', 'wave2', 'Fontes de Fomento', 'Funding Sources', 'Fuentes de Financiamiento', NOW(), NOW(), 'system', 'system'),
    ('wave2:clients', 'clients', 'wave2', 'Clientes', 'Clients', 'Clientes', NOW(), NOW(), 'system', 'system'),
    ('wave2:opportunities', 'opportunities', 'wave2', 'Oportunidades', 'Opportunities', 'Oportunidades', NOW(), NOW(), 'system', 'system'),
    ('wave2:portfolio', 'portfolio', 'wave2', 'Portfólio', 'Portfolio', 'Portafolio', NOW(), NOW(), 'system', 'system')
    ON CONFLICT (id) DO NOTHING;
    ''')


def downgrade() -> None:
    """Remove seed translations."""
    op.execute('''
    DELETE FROM translations WHERE id IN (
        'common:app_title', 'common:app_subtitle', 'common:save', 'common:cancel', 'common:delete', 'common:edit',
        'admin:translations_title', 'admin:translations_description', 'admin:key', 'admin:namespace', 
        'admin:portuguese', 'admin:english', 'admin:spanish',
        'ingestion:title', 'ingestion:source', 'ingestion:status',
        'wave2:funding_sources', 'wave2:clients', 'wave2:opportunities', 'wave2:portfolio'
    )
    ''')
