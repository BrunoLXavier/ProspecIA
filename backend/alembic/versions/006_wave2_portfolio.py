"""wave2: create portfolio tables

Revision ID: 006_wave2_portfolio
Revises: 007_wave2_clients
Create Date: 2026-01-08 12:00:00.000000

Wave 2 - RF-03: Gestão do Portfólio Institucional
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '006_wave2_portfolio'
down_revision = '007_wave2_clients'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create institutes, projects, and competences tables."""
    
    # Institutes table
    op.create_table(
        'institutes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('acronym', sa.String(20), nullable=True),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=False),
        sa.Column('contact_phone', sa.String(20), nullable=True),
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'archived', 'excluded', name='institute_status'), nullable=False, server_default='active'),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('historico_atualizacoes', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('criado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('atualizado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    
    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('institute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('objectives', sa.Text, nullable=False),
        sa.Column('trl', sa.SmallInteger, nullable=False),
        sa.Column('budget', sa.BigInteger, nullable=True),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=True),
        sa.Column('team_size', sa.Integer, nullable=False, server_default='1'),
        sa.Column('status', postgresql.ENUM('planning', 'active', 'on_hold', 'completed', 'cancelled', 'archived', 'excluded', name='project_status'), nullable=False, server_default='planning'),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('historico_atualizacoes', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('criado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('atualizado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('trl >= 1 AND trl <= 9', name='check_trl_range'),
    )
    
    # Competences table
    op.create_table(
        'competences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('criado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    
    # Foreign keys
    op.create_foreign_key('fk_projects_institute_id', 'projects', 'institutes', ['institute_id'], ['id'], ondelete='CASCADE')
    
    # Indexes
    op.create_index('idx_institutes_tenant_id', 'institutes', ['tenant_id'])
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
