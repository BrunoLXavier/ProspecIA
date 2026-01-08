"""wave2: create clients and interactions tables

Revision ID: 007_wave2_clients
Revises: 005_wave2_funding_sources
Create Date: 2026-01-08 11:00:00.000000

Wave 2 - RF-04: Gestão de CRM
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '007_wave2_clients'
down_revision = '005_wave2_funding_sources'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create clients and interactions tables."""
    
    # Create clients table
    op.create_table(
        'clients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('cnpj', sa.String(18), nullable=False, comment='Brazilian tax ID (encrypted)'),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('sector', sa.String(100), nullable=False),
        sa.Column('size', sa.String(20), nullable=False, comment='micro/small/medium/large'),
        sa.Column('maturity', postgresql.ENUM('prospect', 'lead', 'opportunity', 'client', 'advocate', name='client_maturity'), nullable=False, server_default='prospect'),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'archived', 'excluded', name='client_status'), nullable=False, server_default='active'),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('historico_atualizacoes', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('criado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('atualizado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    
    # Create interactions table
    op.create_table(
        'interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Foreign key to clients'),
        sa.Column('type', postgresql.ENUM('meeting', 'email', 'call', 'visit', 'event', 'other', name='interaction_type'), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('summary', sa.Text, nullable=False),
        sa.Column('outcome', postgresql.ENUM('positive', 'neutral', 'negative', 'pending', name='interaction_outcome'), nullable=False, server_default='pending'),
        sa.Column('next_steps', sa.Text, nullable=True),
        sa.Column('participants', postgresql.JSONB, nullable=False, server_default='[]', comment='List of participants'),
        sa.Column('status', postgresql.ENUM('active', 'archived', 'excluded', name='interaction_status'), nullable=False, server_default='active'),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('historico_atualizacoes', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('criado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('atualizado_por', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    
    # Foreign key constraint
    op.create_foreign_key(
        'fk_interactions_client_id',
        'interactions', 'clients',
        ['client_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Indexes for clients
    op.create_index('idx_clients_tenant_id', 'clients', ['tenant_id'])
    op.create_index('idx_clients_status', 'clients', ['status'])
    op.create_index('idx_clients_maturity', 'clients', ['maturity'])
    op.create_index('idx_clients_cnpj', 'clients', ['cnpj'])
    op.create_index('idx_clients_tenant_status', 'clients', ['tenant_id', 'status'])
    
    # Full-text search for clients
    op.execute("""
        CREATE INDEX idx_clients_fulltext 
        ON clients 
        USING gin(to_tsvector('portuguese', name || ' ' || COALESCE(notes, '')))
    """)
    
    # Indexes for interactions
    op.create_index('idx_interactions_client_id', 'interactions', ['client_id'])
    op.create_index('idx_interactions_tenant_id', 'interactions', ['tenant_id'])
    op.create_index('idx_interactions_date', 'interactions', ['date'])
    op.create_index('idx_interactions_type', 'interactions', ['type'])
    op.create_index('idx_interactions_client_date', 'interactions', ['client_id', 'date'])


def downgrade() -> None:
    """Drop clients and interactions tables."""
    op.drop_index('idx_interactions_client_date', table_name='interactions')
    op.drop_index('idx_interactions_type', table_name='interactions')
    op.drop_index('idx_interactions_date', table_name='interactions')
    op.drop_index('idx_interactions_tenant_id', table_name='interactions')
    op.drop_index('idx_interactions_client_id', table_name='interactions')
    
    op.drop_constraint('fk_interactions_client_id', 'interactions', type_='foreignkey')
    
    op.drop_index('idx_clients_fulltext', table_name='clients')
    op.drop_index('idx_clients_tenant_status', table_name='clients')
    op.drop_index('idx_clients_cnpj', table_name='clients')
    op.drop_index('idx_clients_maturity', table_name='clients')
    op.drop_index('idx_clients_status', table_name='clients')
    op.drop_index('idx_clients_tenant_id', table_name='clients')
    
    op.drop_table('interactions')
    op.drop_table('clients')
    
    op.execute('DROP TYPE interaction_status')
    op.execute('DROP TYPE interaction_outcome')
    op.execute('DROP TYPE interaction_type')
    op.execute('DROP TYPE client_maturity')
    op.execute('DROP TYPE client_status')
