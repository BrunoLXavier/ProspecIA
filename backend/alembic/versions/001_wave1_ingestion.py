"""Wave 1: Create ingestoes and consentimentos tables

Revision ID: 001_wave1_ingestion
Revises: 
Create Date: 2026-01-07

Implements RF-01 (Data Ingestion) and LGPD compliance tables.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision = '001_wave1_ingestion'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ingestoes and consentimentos tables with indexes."""
    
    # Create ingestoes table
    op.create_table(
        'ingestoes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('fonte', sa.String(50), nullable=False, comment='Data source'),
        sa.Column('metodo', sa.String(50), nullable=False, comment='Ingestion method'),
        sa.Column('arquivo_original', sa.String(500), nullable=True, comment='Original filename'),
        sa.Column('arquivo_storage_path', sa.String(1000), nullable=True, comment='MinIO storage path'),
        sa.Column('arquivo_size_bytes', sa.Integer, nullable=True, comment='File size in bytes'),
        sa.Column('arquivo_mime_type', sa.String(100), nullable=True, comment='MIME type'),
        sa.Column('confiabilidade_score', sa.Integer, nullable=False, default=50, comment='Reliability score 0-100'),
        sa.Column('total_registros', sa.Integer, nullable=True, comment='Total records'),
        sa.Column('registros_validos', sa.Integer, nullable=True, comment='Valid records'),
        sa.Column('registros_invalidos', sa.Integer, nullable=True, comment='Invalid records'),
        sa.Column('status', sa.String(50), nullable=False, default='pendente', comment='Status'),
        sa.Column('erros_encontrados', JSON, nullable=True, comment='Array of errors'),
        sa.Column('pii_detectado', JSON, nullable=True, comment='PII detected by LGPD agent'),
        sa.Column('acoes_lgpd', JSON, nullable=True, comment='LGPD actions taken'),
        sa.Column('consentimento_id', UUID(as_uuid=True), nullable=True, comment='Consent reference'),
        sa.Column('historico_atualizacoes', JSON, nullable=False, default=list, comment='Immutable audit trail'),
        sa.Column('criado_por', UUID(as_uuid=True), nullable=False, comment='Creator user UUID'),
        sa.Column('tenant_id', sa.String(50), nullable=False, default='nacional', comment='Tenant identifier'),
        sa.Column('data_ingestao', sa.DateTime, nullable=False, comment='Ingestion timestamp'),
        sa.Column('data_processamento', sa.DateTime, nullable=True, comment='Processing completion timestamp'),
        sa.Column('data_criacao', sa.DateTime, nullable=False, comment='Record creation timestamp'),
        sa.Column('data_atualizacao', sa.DateTime, nullable=False, comment='Last update timestamp'),
        sa.Column('descricao', sa.Text, nullable=True, comment='Description'),
        sa.Column('tags', JSON, nullable=True, comment='Tags array'),
        sa.Column('metadata_adicional', JSON, nullable=True, comment='Additional metadata'),
        comment='Data ingestion records with LGPD compliance'
    )
    
    # Create indexes for ingestoes
    op.create_index('ix_ingestoes_id', 'ingestoes', ['id'])
    op.create_index('ix_ingestoes_status', 'ingestoes', ['status'])
    op.create_index('ix_ingestoes_criado_por', 'ingestoes', ['criado_por'])
    op.create_index('ix_ingestoes_tenant_id', 'ingestoes', ['tenant_id'])
    op.create_index('ix_ingestoes_data_ingestao', 'ingestoes', ['data_ingestao'])
    op.create_index('ix_ingestoes_tenant_data', 'ingestoes', ['tenant_id', 'data_ingestao'])
    
    # Create consentimentos table
    op.create_table(
        'consentimentos',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('versao', sa.Integer, nullable=False, default=1, comment='Consent version'),
        sa.Column('consent_id_base', UUID(as_uuid=True), nullable=True, comment='Base consent ID'),
        sa.Column('titular_id', UUID(as_uuid=True), nullable=True, comment='Data subject UUID'),
        sa.Column('titular_email', sa.String(255), nullable=True, comment='Data subject email'),
        sa.Column('titular_documento', sa.String(100), nullable=True, comment='Data subject document (encrypted)'),
        sa.Column('finalidade', sa.Text, nullable=False, comment='Purpose for data processing'),
        sa.Column('categorias_dados', JSON, nullable=False, default=list, comment='Data categories array'),
        sa.Column('consentimento_dado', sa.Boolean, nullable=False, default=False, comment='Consent given flag'),
        sa.Column('data_consentimento', sa.DateTime, nullable=True, comment='Consent timestamp'),
        sa.Column('revogado', sa.Boolean, nullable=False, default=False, comment='Revoked flag'),
        sa.Column('data_revogacao', sa.DateTime, nullable=True, comment='Revocation timestamp'),
        sa.Column('motivo_revogacao', sa.Text, nullable=True, comment='Revocation reason'),
        sa.Column('origem_coleta', sa.String(100), nullable=False, default='sistema', comment='Collection origin'),
        sa.Column('ip_origem', sa.String(45), nullable=True, comment='Origin IP address'),
        sa.Column('user_agent', sa.Text, nullable=True, comment='User agent'),
        sa.Column('consentimento_marketing', sa.Boolean, nullable=False, default=False, comment='Marketing consent'),
        sa.Column('consentimento_compartilhamento', sa.Boolean, nullable=False, default=False, comment='Sharing consent'),
        sa.Column('consentimento_analise', sa.Boolean, nullable=False, default=False, comment='Analysis consent'),
        sa.Column('base_legal', sa.String(100), nullable=False, default='consentimento', comment='Legal basis'),
        sa.Column('historico_alteracoes', JSON, nullable=False, default=list, comment='Immutable change history'),
        sa.Column('coletado_por', UUID(as_uuid=True), nullable=False, comment='Collector user UUID'),
        sa.Column('tenant_id', sa.String(50), nullable=False, default='nacional', comment='Tenant identifier'),
        sa.Column('data_criacao', sa.DateTime, nullable=False, comment='Record creation'),
        sa.Column('data_atualizacao', sa.DateTime, nullable=False, comment='Last update'),
        sa.Column('data_expiracao', sa.DateTime, nullable=True, comment='Expiration date'),
        sa.Column('metadata_adicional', JSON, nullable=True, comment='Additional metadata'),
        comment='LGPD consent records with versioning'
    )
    
    # Create indexes for consentimentos
    op.create_index('ix_consentimentos_id', 'consentimentos', ['id'])
    op.create_index('ix_consentimentos_consent_id_base', 'consentimentos', ['consent_id_base'])
    op.create_index('ix_consentimentos_titular_id', 'consentimentos', ['titular_id'])
    op.create_index('ix_consentimentos_consentimento_dado', 'consentimentos', ['consentimento_dado'])
    op.create_index('ix_consentimentos_revogado', 'consentimentos', ['revogado'])
    op.create_index('ix_consentimentos_tenant_id', 'consentimentos', ['tenant_id'])
    op.create_index('ix_consentimentos_version_base', 'consentimentos', ['consent_id_base', 'versao'])


def downgrade() -> None:
    """Drop ingestoes and consentimentos tables."""
    op.drop_index('ix_consentimentos_version_base', table_name='consentimentos')
    op.drop_index('ix_consentimentos_tenant_id', table_name='consentimentos')
    op.drop_index('ix_consentimentos_revogado', table_name='consentimentos')
    op.drop_index('ix_consentimentos_consentimento_dado', table_name='consentimentos')
    op.drop_index('ix_consentimentos_titular_id', table_name='consentimentos')
    op.drop_index('ix_consentimentos_consent_id_base', table_name='consentimentos')
    op.drop_index('ix_consentimentos_id', table_name='consentimentos')
    op.drop_table('consentimentos')
    
    op.drop_index('ix_ingestoes_tenant_data', table_name='ingestoes')
    op.drop_index('ix_ingestoes_data_ingestao', table_name='ingestoes')
    op.drop_index('ix_ingestoes_tenant_id', table_name='ingestoes')
    op.drop_index('ix_ingestoes_criado_por', table_name='ingestoes')
    op.drop_index('ix_ingestoes_status', table_name='ingestoes')
    op.drop_index('ix_ingestoes_id', table_name='ingestoes')
    op.drop_table('ingestoes')
