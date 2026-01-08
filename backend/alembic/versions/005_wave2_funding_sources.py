"""wave2: create funding_sources table

Revision ID: 005_wave2_funding_sources
Revises: 003_wave0_acl_rules
Create Date: 2026-01-08 10:00:00.000000

Wave 2 - RF-02: Gestão de Fontes de Fomento
Creates table for funding sources with:
- Soft delete (status column, never hard DELETE)
- Multi-tenancy support (tenant_id for RLS in Wave 4)
- Versioning (historico_atualizacoes JSONB)
- Full audit trail
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_wave2_funding_sources'
down_revision = '003_wave0_acl_rules'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create funding_sources table with all required columns and indexes."""
    
    # Create table
    op.create_table(
        'funding_sources',
        
        # Primary key
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        
        # Core fields
        sa.Column('name', sa.String(255), nullable=False, comment='Funding source name'),
        sa.Column('description', sa.Text, nullable=False, comment='Detailed description'),
        sa.Column('type', postgresql.ENUM('grant', 'financing', 'equity', 'non_refundable', 'tax_incentive', 'mixed', name='funding_source_type'), nullable=False, comment='Type of funding'),
        sa.Column('sectors', postgresql.JSONB, nullable=False, server_default='[]', comment='List of applicable sectors'),
        sa.Column('amount', sa.BigInteger, nullable=False, comment='Funding amount in BRL cents'),
        sa.Column('trl_min', sa.SmallInteger, nullable=False, comment='Minimum TRL (1-9)'),
        sa.Column('trl_max', sa.SmallInteger, nullable=False, comment='Maximum TRL (1-9)'),
        sa.Column('deadline', sa.Date, nullable=False, comment='Application deadline'),
        sa.Column('url', sa.String(500), nullable=True, comment='Official URL'),
        sa.Column('requirements', sa.Text, nullable=True, comment='Eligibility requirements'),
        
        # Status and soft delete
        sa.Column('status', postgresql.ENUM('active', 'inactive', 'archived', 'excluded', name='funding_source_status'), nullable=False, server_default='active', comment='Current status (soft delete via excluded)'),
        
        # Multi-tenancy (Wave 4 will add RLS policies)
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Tenant identifier for multi-tenancy'),
        
        # Versioning and audit
        sa.Column('historico_atualizacoes', postgresql.JSONB, nullable=False, server_default='[]', comment='Immutable audit trail of all changes'),
        sa.Column('criado_por', postgresql.UUID(as_uuid=True), nullable=False, comment='User ID who created this record'),
        sa.Column('atualizado_por', postgresql.UUID(as_uuid=True), nullable=False, comment='User ID who last updated this record'),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Creation timestamp'),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='Last update timestamp'),
        
        # Constraints
        sa.CheckConstraint('trl_min >= 1 AND trl_min <= 9', name='check_trl_min_range'),
        sa.CheckConstraint('trl_max >= 1 AND trl_max <= 9', name='check_trl_max_range'),
        sa.CheckConstraint('trl_min <= trl_max', name='check_trl_min_lte_max'),
        sa.CheckConstraint('amount >= 0', name='check_amount_positive'),
    )
    
    # Indexes for performance
    op.create_index('idx_funding_sources_tenant_id', 'funding_sources', ['tenant_id'])
    op.create_index('idx_funding_sources_status', 'funding_sources', ['status'])
    op.create_index('idx_funding_sources_deadline', 'funding_sources', ['deadline'])
    op.create_index('idx_funding_sources_type', 'funding_sources', ['type'])
    op.create_index('idx_funding_sources_tenant_status', 'funding_sources', ['tenant_id', 'status'])
    
    # GIN index for JSONB sectors (allows array containment queries)
    op.create_index('idx_funding_sources_sectors_gin', 'funding_sources', ['sectors'], postgresql_using='gin')
    
    # Full-text search index for name and description
    op.execute("""
        CREATE INDEX idx_funding_sources_fulltext 
        ON funding_sources 
        USING gin(to_tsvector('portuguese', name || ' ' || description))
    """)


def downgrade() -> None:
    """Drop funding_sources table and ENUM types."""
    op.drop_index('idx_funding_sources_fulltext', table_name='funding_sources')
    op.drop_index('idx_funding_sources_sectors_gin', table_name='funding_sources')
    op.drop_index('idx_funding_sources_tenant_status', table_name='funding_sources')
    op.drop_index('idx_funding_sources_type', table_name='funding_sources')
    op.drop_index('idx_funding_sources_deadline', table_name='funding_sources')
    op.drop_index('idx_funding_sources_status', table_name='funding_sources')
    op.drop_index('idx_funding_sources_tenant_id', table_name='funding_sources')
    
    op.drop_table('funding_sources')
    
    op.execute('DROP TYPE funding_source_type')
    op.execute('DROP TYPE funding_source_status')
