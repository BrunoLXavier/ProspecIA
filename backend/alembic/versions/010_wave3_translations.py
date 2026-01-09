"""Add translations table

Revision ID: 010_wave3_translations
Revises: 009_en_us_table_aliases
Create Date: 2026-01-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '010_wave3_translations'
down_revision = '122efdda150d'
branch_labels = None
depends_on = None


def upgrade():
    # Create translations table
    op.create_table(
        'translations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('namespace', sa.String(), nullable=False),
        sa.Column('pt_br', sa.String(), nullable=False),
        sa.Column('en_us', sa.String(), nullable=False),
        sa.Column('es_es', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('ix_translations_key', 'translations', ['key'])
    op.create_index('ix_translations_namespace', 'translations', ['namespace'])
    op.create_index('ix_translations_key_namespace', 'translations', ['key', 'namespace'], unique=True)
    
    # Create full-text search indexes for translations
    op.execute("""
        CREATE INDEX ix_translations_pt_br_fts ON translations 
        USING gin(to_tsvector('portuguese', pt_br))
    """)
    op.execute("""
        CREATE INDEX ix_translations_en_us_fts ON translations 
        USING gin(to_tsvector('english', en_us))
    """)
    op.execute("""
        CREATE INDEX ix_translations_es_es_fts ON translations 
        USING gin(to_tsvector('spanish', es_es))
    """)


def downgrade():
    # Drop indexes
    op.drop_index('ix_translations_es_es_fts', table_name='translations')
    op.drop_index('ix_translations_en_us_fts', table_name='translations')
    op.drop_index('ix_translations_pt_br_fts', table_name='translations')
    op.drop_index('ix_translations_key_namespace', table_name='translations')
    op.drop_index('ix_translations_namespace', table_name='translations')
    op.drop_index('ix_translations_key', table_name='translations')
    
    # Drop table
    op.drop_table('translations')
