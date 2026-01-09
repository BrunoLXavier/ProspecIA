"""Wave 0: Model field configurations seed data.

Revision ID: 006_model_field_configs_seed
Revises: 005_acl_rules_seed
Create Date: 2026-01-09

Seeds initial model field configurations for Ingestao and Consentimento models.
Idempotent: uses INSERT ... ON CONFLICT DO NOTHING.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '006_model_field_configs_seed'
down_revision = '005_acl_rules_seed'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Seed model field configurations."""
    
    # Seed model field configurations for Ingestao model
    op.execute('''
    INSERT INTO model_field_configurations (id, model_name, field_name, field_type, label_key, validators, visibility_rule, required, description, created_at, updated_at) VALUES
    (gen_random_uuid(), 'Ingestao', 'fonte', 'string', 'fields.source', '{"required": true, "options": ["rais", "ibge", "inpi", "finep", "bndes", "customizada"]}'::jsonb, 'all', true, 'Data source type', NOW(), NOW()),
    (gen_random_uuid(), 'Ingestao', 'metodo', 'string', 'fields.method', '{"required": true, "options": ["batch_upload", "api_pull", "manual", "scheduled"]}'::jsonb, 'all', true, 'Ingestion method', NOW(), NOW()),
    (gen_random_uuid(), 'Ingestao', 'descricao', 'text', 'fields.description', '{"max_length": 500}'::jsonb, 'all', false, 'Description', NOW(), NOW()),
    (gen_random_uuid(), 'Ingestao', 'arquivo', 'file', 'fields.file', '{"max_size_bytes": 104857600, "allowed_types": ["csv", "xlsx", "json", "parquet"]}'::jsonb, 'all', false, 'File to ingest', NOW(), NOW()),
    (gen_random_uuid(), 'Ingestao', 'consentimento_id', 'uuid', 'fields.consent_id', '{"required": false}'::jsonb, 'advanced', false, 'LGPD Consent UUID', NOW(), NOW())
    ON CONFLICT (model_name, field_name) DO NOTHING;
    ''')
    
    # Seed model field configurations for Consentimento model
    op.execute('''
    INSERT INTO model_field_configurations (id, model_name, field_name, field_type, label_key, validators, visibility_rule, required, description, created_at, updated_at) VALUES
    (gen_random_uuid(), 'Consentimento', 'finalidade', 'text', 'fields.purpose', '{"required": true, "max_length": 1000}'::jsonb, 'all', true, 'Consent purpose', NOW(), NOW()),
    (gen_random_uuid(), 'Consentimento', 'categorias_dados', 'array', 'fields.data_categories', '{"options": ["cpf", "email", "phone", "address", "biometric"]}'::jsonb, 'all', true, 'Data categories', NOW(), NOW()),
    (gen_random_uuid(), 'Consentimento', 'consentimento_dado', 'boolean', 'fields.consent_granted', '{"required": true}'::jsonb, 'all', true, 'Consent granted', NOW(), NOW()),
    (gen_random_uuid(), 'Consentimento', 'data_consentimento', 'timestamp', 'fields.consent_date', '{"required": false}'::jsonb, 'all', false, 'Consent date', NOW(), NOW()),
    (gen_random_uuid(), 'Consentimento', 'base_legal', 'string', 'fields.legal_basis', '{"options": ["consentimento", "interesse_legitimo", "obrigacao_legal"]}'::jsonb, 'all', true, 'Legal basis', NOW(), NOW())
    ON CONFLICT (model_name, field_name) DO NOTHING;
    ''')


def downgrade() -> None:
    """Remove model field configurations seed data."""
    op.execute('DELETE FROM model_field_configurations WHERE model_name IN (\'Ingestao\', \'Consentimento\');')
