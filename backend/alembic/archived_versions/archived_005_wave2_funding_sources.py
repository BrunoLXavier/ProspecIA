"""ARCHIVED: wave2: create funding_sources table

Original Revision ID: 005_wave2_funding_sources
Archived on 2026-01-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_wave2_funding_sources'
down_revision = '000_squashed_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: schema consolidated in 000_squashed_initial
    op.execute('SELECT 1')


def downgrade() -> None:
    op.execute('SELECT 1')
