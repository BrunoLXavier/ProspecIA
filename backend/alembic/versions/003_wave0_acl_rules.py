"""Wave 0: ACL Rules

Revision ID: 003_wave0_acl_rules
Revises: 002_wave0_model_configs
Create Date: 2026-01-07 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from uuid import uuid4

# revision identifiers, used by Alembic.
revision = '003_wave0_acl_rules'
down_revision = '002_wave0_model_configs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create acl_rules table for dynamic access control."""

    op.create_table(
        'acl_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid4),
        sa.Column('role', sa.String(100), nullable=False),
        sa.Column('resource', sa.String(100), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),  # read, create, update, delete, export, import
        sa.Column('condition', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role', 'resource', 'action', name='uq_acl_role_resource_action'),
    )

    op.create_index('ix_acl_rules_role', 'acl_rules', ['role'])
    op.create_index('ix_acl_rules_resource', 'acl_rules', ['resource'])

    # Seed minimal defaults
    op.execute(
        """
        INSERT INTO acl_rules (id, role, resource, action, description, created_at, updated_at)
        VALUES
        ('{}', 'admin', 'system', 'read', 'Admin can read system info', NOW(), NOW()),
        ('{}', 'admin', 'model_config', 'update', 'Admin can update model configs', NOW(), NOW()),
        ('{}', 'gestor', 'model_config', 'read', 'Gestor can view model configs', NOW(), NOW());
        """.format(str(uuid4()), str(uuid4()), str(uuid4()))
    )


def downgrade() -> None:
    op.drop_index('ix_acl_rules_resource', table_name='acl_rules')
    op.drop_index('ix_acl_rules_role', table_name='acl_rules')
    op.drop_table('acl_rules')
