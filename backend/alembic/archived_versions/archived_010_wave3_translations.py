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
down_revision = '000_squashed_initial'
branch_labels = None
depends_on = None


def upgrade():
    # No-op: consolidated in 000_squashed_initial
    op.execute('SELECT 1')


def downgrade():
    op.execute('SELECT 1')
