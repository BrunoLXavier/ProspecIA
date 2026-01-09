"""Wave 0: System configuration and feature flags seeds.

Revision ID: 002_wave0_system_config
Revises: 000_squashed_initial
Create Date: 2026-01-09

Seeds initial system configuration and feature flags data.
Idempotent: uses INSERT ... ON CONFLICT DO NOTHING.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '002_wave0_system_config'
down_revision = '000_squashed_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Seed feature flags and system configurations."""
    
    # Seed feature flags (idempotent with ON CONFLICT DO NOTHING)
    op.execute('''
    INSERT INTO feature_flags (id, key, enabled, description, created_at, updated_at) VALUES
    (gen_random_uuid(), 'ai_suggestions', true, 'Enable AI-powered suggestions', NOW(), NOW()),
    (gen_random_uuid(), 'jwt_required', false, 'Require JWT authentication', NOW(), NOW()),
    (gen_random_uuid(), 'rls_enabled', false, 'Enable Row-Level Security', NOW(), NOW()),
    (gen_random_uuid(), 'audit_logging', true, 'Enable audit logging', NOW(), NOW()),
    (gen_random_uuid(), 'lgpd_agent', true, 'Enable LGPD compliance agent', NOW(), NOW())
    ON CONFLICT (key) DO NOTHING;
    ''')
    
    # Seed system configurations (idempotent with ON CONFLICT DO NOTHING)
    op.execute('''
    INSERT INTO configuracoes_sistema (id, chave, valor, versao, data_alteracao, usuario_responsavel, motivo, created_at) VALUES
    (gen_random_uuid(), 'estagios_pipeline', '["Inteligencia", "Validacao", "Abordagem", "Registro", "Conversao", "Pos-venda"]'::jsonb, 1, NOW(), 'system', 'Configuracao inicial', NOW()),
    (gen_random_uuid(), 'setores_validos', '["TI", "Saude", "Energia", "Agricultura", "Manufatura", "Educacao"]'::jsonb, 1, NOW(), 'system', 'Configuracao inicial', NOW()),
    (gen_random_uuid(), 'trl_minimo', '1'::jsonb, 1, NOW(), 'system', 'Configuracao inicial', NOW()),
    (gen_random_uuid(), 'trl_maximo', '9'::jsonb, 1, NOW(), 'system', 'Configuracao inicial', NOW())
    ON CONFLICT (chave) DO NOTHING;
    ''')


def downgrade() -> None:
    """Remove seed data."""
    op.execute('DELETE FROM feature_flags WHERE key IN (\'ai_suggestions\', \'jwt_required\', \'rls_enabled\', \'audit_logging\', \'lgpd_agent\')')
    op.execute('DELETE FROM configuracoes_sistema WHERE chave IN (\'estagios_pipeline\', \'setores_validos\', \'trl_minimo\', \'trl_maximo\')')
