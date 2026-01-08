"""Wave 0: Model Field Configuration

Revision ID: 002_wave0_model_configs
Revises: 001_wave1_ingestion
Create Date: 2026-01-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from uuid import uuid4

# revision identifiers, used by Alembic.
revision = '002_wave0_model_configs'
down_revision = '001_wave1_ingestion'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create model_field_configurations table for dynamic field configuration."""
    
    # Create model_field_configurations table
    op.create_table(
        'model_field_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid4),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('field_name', sa.String(100), nullable=False),
        sa.Column('field_type', sa.String(50), nullable=False, default='string'),  # string, integer, boolean, datetime, enum
        sa.Column('label_key', sa.String(100), nullable=True),  # i18n key
        sa.Column('validators', postgresql.JSONB(), nullable=True),  # JSON validators config
        sa.Column('visibility_rule', sa.String(100), nullable=False, default='all'),  # all, admin, non_viewer
        sa.Column('required', sa.Boolean(), nullable=False, default=False),
        sa.Column('default_value', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_name', 'field_name', name='uq_model_field')
    )
    
    # Create indexes for performance
    op.create_index('ix_model_field_configurations_model_name', 'model_field_configurations', ['model_name'])
    op.create_index('ix_model_field_configurations_visibility', 'model_field_configurations', ['visibility_rule'])
    
    # Seed default configurations for Ingestao model
    op.execute(f"""
        INSERT INTO model_field_configurations 
        (id, model_name, field_name, field_type, label_key, validators, visibility_rule, required, created_at, updated_at)
        VALUES
        ('{uuid4()}', 'Ingestao', 'nome', 'string', 'ingestion.field.nome', '{{"min_length": 1, "max_length": 255}}', 'all', true, NOW(), NOW()),
        ('{uuid4()}', 'Ingestao', 'arquivo', 'file', 'ingestion.field.arquivo', '{{"max_size_mb": 100, "allowed_formats": ["csv", "xlsx", "xls"]}}', 'all', true, NOW(), NOW()),
        ('{uuid4()}', 'Ingestao', 'fonte', 'enum', 'ingestion.field.source', '{{"enum_values": ["RAIS", "IBGE", "INPI", "FINEP", "BNDES", "CUSTOMIZADA"]}}', 'all', true, NOW(), NOW()),
        ('{uuid4()}', 'Ingestao', 'valor_monetario', 'float', 'ingestion.field.valor', null, 'non_viewer', false, NOW(), NOW()),
        ('{uuid4()}', 'Ingestao', 'descricao', 'string', 'ingestion.field.description', '{{"max_length": 1000}}', 'all', false, NOW(), NOW()),
        ('{uuid4()}', 'Consentimento', 'versao', 'integer', 'consent.field.version', null, 'all', true, NOW(), NOW()),
        ('{uuid4()}', 'Consentimento', 'status', 'enum', 'consent.field.status', '{{"enum_values": ["CONCEDIDO", "REVOGADO", "PENDENTE"]}}', 'all', true, NOW(), NOW()),
        ('{uuid4()}', 'Consentimento', 'data_concessao', 'datetime', 'consent.field.grant_date', null, 'all', false, NOW(), NOW());
    """)


def downgrade() -> None:
    """Drop model_field_configurations table."""
    
    # Drop indexes
    op.drop_index('ix_model_field_configurations_visibility')
    op.drop_index('ix_model_field_configurations_model_name')
    
    # Drop table
    op.drop_table('model_field_configurations')
