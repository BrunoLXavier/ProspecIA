"""ARCHIVED: wave2: create portfolio tables

Original Revision ID: 006_wave2_portfolio
Archived on 2026-01-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '006_wave2_portfolio'
down_revision = '000_squashed_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: consolidated in 000_squashed_initial
    op.execute('SELECT 1')


def downgrade() -> None:
    op.execute('SELECT 1')
    op.create_index('idx_institutes_status', 'institutes', ['status'])
    op.create_index('idx_projects_institute_id', 'projects', ['institute_id'])
    op.create_index('idx_projects_tenant_id', 'projects', ['tenant_id'])
    op.create_index('idx_projects_status', 'projects', ['status'])
    op.create_index('idx_projects_trl', 'projects', ['trl'])
    op.create_index('idx_competences_tenant_id', 'competences', ['tenant_id'])


def downgrade() -> None:
    """Drop portfolio tables."""
    op.drop_index('idx_competences_tenant_id', table_name='competences')
    op.drop_index('idx_projects_trl', table_name='projects')
    op.drop_index('idx_projects_status', table_name='projects')
    op.drop_index('idx_projects_tenant_id', table_name='projects')
    op.drop_index('idx_projects_institute_id', table_name='projects')
    op.drop_index('idx_institutes_status', table_name='institutes')
    op.drop_index('idx_institutes_tenant_id', table_name='institutes')
    
    op.drop_constraint('fk_projects_institute_id', 'projects', type_='foreignkey')
    
    op.drop_table('competences')
    op.drop_table('projects')
    op.drop_table('institutes')
    
    op.execute('DROP TYPE project_status')
    op.execute('DROP TYPE institute_status')
