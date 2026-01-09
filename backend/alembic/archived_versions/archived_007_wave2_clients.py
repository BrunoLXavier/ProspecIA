"""ARCHIVED: wave2: create clients and interactions tables

Original Revision ID: 007_wave2_clients
Archived on 2026-01-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '007_wave2_clients'
down_revision = '000_squashed_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: consolidated in 000_squashed_initial
    op.execute('SELECT 1')


def downgrade() -> None:
    op.execute('SELECT 1')
    
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
