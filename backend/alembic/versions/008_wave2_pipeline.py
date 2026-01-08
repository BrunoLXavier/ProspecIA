"""wave2: create opportunities table

Revision ID: 008_wave2_pipeline
Revises: 006_wave2_portfolio
Create Date: 2026-01-08 13:00:00.000000

Wave 2 - RF-05: Gestão de Pipeline de Oportunidades
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '008_wave2_pipeline'
down_revision = '006_wave2_portfolio'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create opportunities table."""
    
    # Create opportunities table
    op.create_table(
        'opportunities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('funding_source_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('stage', postgresql.ENUM('intelligence', 'validation', 'approach', 'registration', 'conversion', 'post_sale', name='opportunity_stage'), nullable=False, server_default='intelligence'),
        sa.Column('score', sa.SmallInteger, nullable=False, server_default='0'),
        sa.Column('estimated_value', sa.BigInteger, nullable=False, server_default='0'),
        sa.Column('probability', sa.SmallInteger, nullable=False, server_default='50'),
        sa.Column('expected_close_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('responsible_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('active', 'won', 'lost', 'archived', 'excluded', name='opportunity_status'), nullable=False, server_default='active'),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('historico_atualizacoes', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('historico_transicoes', postgresql.JSONB, nullable=False, server_default='[]', comment='Stage transitions history'),
        sa.Column('criado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('atualizado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.CheckConstraint('score >= 0 AND score <= 100', name='check_score_range'),
        sa.CheckConstraint('probability >= 0 AND probability <= 100', name='check_probability_range'),
    )
    
    # Foreign keys
    op.create_foreign_key('fk_opportunities_client_id', 'opportunities', 'clients', ['client_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_opportunities_funding_source_id', 'opportunities', 'funding_sources', ['funding_source_id'], ['id'], ondelete='RESTRICT')
    
    # Indexes
    op.create_index('idx_opportunities_client_id', 'opportunities', ['client_id'])
    op.create_index('idx_opportunities_funding_source_id', 'opportunities', ['funding_source_id'])
    op.create_index('idx_opportunities_tenant_id', 'opportunities', ['tenant_id'])
    op.create_index('idx_opportunities_stage', 'opportunities', ['stage'])
    op.create_index('idx_opportunities_status', 'opportunities', ['status'])
    op.create_index('idx_opportunities_responsible', 'opportunities', ['responsible_user_id'])
    op.create_index('idx_opportunities_tenant_stage', 'opportunities', ['tenant_id', 'stage'])


def downgrade() -> None:
    """Drop opportunities table."""
    op.drop_index('idx_opportunities_tenant_stage', table_name='opportunities')
    op.drop_index('idx_opportunities_responsible', table_name='opportunities')
    op.drop_index('idx_opportunities_status', table_name='opportunities')
    op.drop_index('idx_opportunities_stage', table_name='opportunities')
    op.drop_index('idx_opportunities_tenant_id', table_name='opportunities')
    op.drop_index('idx_opportunities_funding_source_id', table_name='opportunities')
    op.drop_index('idx_opportunities_client_id', table_name='opportunities')
    
    op.drop_constraint('fk_opportunities_funding_source_id', 'opportunities', type_='foreignkey')
    op.drop_constraint('fk_opportunities_client_id', 'opportunities', type_='foreignkey')
    
    op.drop_table('opportunities')
    
    op.execute('DROP TYPE opportunity_status')
    op.execute('DROP TYPE opportunity_stage')
