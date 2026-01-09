"""Add status field to Wave 2 tables

Revision ID: 009_add_status_field
Revises: 008_wave2_pipeline
Create Date: 2026-01-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009_add_status_field'
down_revision = '008_wave2_pipeline'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add status field to all Wave 2 domain tables for soft delete support."""
    
    tables = [
        'clients',
        'funding_sources',
        'interactions',
        'opportunities',
        'institutes',
        'projects'
    ]
    
    for table in tables:
        # Add status column with default 'active'
        op.add_column(
            table,
            sa.Column(
                'status',
                sa.String(20),
                nullable=False,
                server_default='active'
            )
        )
        
        # Add CHECK constraint for valid status values
        op.create_check_constraint(
            f'ck_{table}_status',
            table,
            "status IN ('active', 'inactive', 'deleted')"
        )
        
        # Create composite index on (tenant_id, status) for efficient filtering
        op.create_index(
            f'idx_{table}_tenant_status',
            table,
            ['tenant_id', 'status']
        )


def downgrade() -> None:
    """Remove status field and related constraints/indexes."""
    
    tables = [
        'clients',
        'funding_sources',
        'interactions',
        'opportunities',
        'institutes',
        'projects'
    ]
    
    for table in tables:
        # Drop index
        op.drop_index(f'idx_{table}_tenant_status', table_name=table)
        
        # Drop check constraint
        op.drop_constraint(f'ck_{table}_status', table_name=table, type_='check')
        
        # Drop column
        op.drop_column(table, 'status')
