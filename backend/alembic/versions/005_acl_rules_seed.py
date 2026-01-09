"""Wave 0: ACL rules seed data.

Revision ID: 005_acl_rules_seed
Revises: 004_wave2_translations
Create Date: 2026-01-09

Seeds initial ACL rules for basic role-based access control.
Idempotent: uses INSERT ... ON CONFLICT DO NOTHING.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '005_acl_rules_seed'
down_revision = '004_wave2_translations'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Seed ACL rules for common roles and resources."""
    
    # Seed ACL rules (idempotent with ON CONFLICT DO NOTHING)
    op.execute('''
    INSERT INTO acl_rules (id, role, resource, action, description, created_at, updated_at) VALUES
    -- Admin: full access to all resources
    (gen_random_uuid(), 'admin', 'model_config', 'read', 'Admin can read model configs', NOW(), NOW()),
    (gen_random_uuid(), 'admin', 'model_config', 'update', 'Admin can update model configs', NOW(), NOW()),
    (gen_random_uuid(), 'admin', 'system.model_configs', 'read', 'Admin can read system model configs', NOW(), NOW()),
    (gen_random_uuid(), 'admin', 'system.model_configs', 'update', 'Admin can update system model configs', NOW(), NOW()),
    (gen_random_uuid(), 'admin', 'ingestions', 'read', 'Admin can read ingestions', NOW(), NOW()),
    (gen_random_uuid(), 'admin', 'ingestions', 'create', 'Admin can create ingestions', NOW(), NOW()),
    (gen_random_uuid(), 'admin', 'ingestions', 'delete', 'Admin can delete ingestions', NOW(), NOW()),
    
    -- Gestor (Manager): can read and update most resources
    (gen_random_uuid(), 'gestor', 'model_config', 'read', 'Gestor can read model configs', NOW(), NOW()),
    (gen_random_uuid(), 'gestor', 'model_config', 'update', 'Gestor can update model configs', NOW(), NOW()),
    (gen_random_uuid(), 'gestor', 'system.model_configs', 'read', 'Gestor can read system model configs', NOW(), NOW()),
    (gen_random_uuid(), 'gestor', 'system.model_configs', 'update', 'Gestor can update system model configs', NOW(), NOW()),
    (gen_random_uuid(), 'gestor', 'ingestions', 'read', 'Gestor can read ingestions', NOW(), NOW()),
    (gen_random_uuid(), 'gestor', 'ingestions', 'create', 'Gestor can create ingestions', NOW(), NOW()),
    
    -- Analista (Analyst): can read most resources
    (gen_random_uuid(), 'analista', 'model_config', 'read', 'Analista can read model configs', NOW(), NOW()),
    (gen_random_uuid(), 'analista', 'system.model_configs', 'read', 'Analista can read system model configs', NOW(), NOW()),
    (gen_random_uuid(), 'analista', 'ingestions', 'read', 'Analista can read ingestions', NOW(), NOW()),
    
    -- Viewer (Read-only): limited read access
    (gen_random_uuid(), 'viewer', 'model_config', 'read', 'Viewer can read model configs', NOW(), NOW()),
    (gen_random_uuid(), 'viewer', 'system.model_configs', 'read', 'Viewer can read system model configs', NOW(), NOW())
    ON CONFLICT (role, resource, action) DO NOTHING;
    ''')


def downgrade() -> None:
    """Remove ACL rules seed data."""
    op.execute('''
    DELETE FROM acl_rules WHERE role IN ('admin', 'gestor', 'analista', 'viewer');
    ''')
