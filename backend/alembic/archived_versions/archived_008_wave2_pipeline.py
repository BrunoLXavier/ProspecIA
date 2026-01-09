"""ARCHIVED: wave2: create opportunities table

Original Revision ID: 008_wave2_pipeline
Archived on 2026-01-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '008_wave2_pipeline'
down_revision = '000_squashed_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: consolidated in 000_squashed_initial
    op.execute('SELECT 1')


def downgrade() -> None:
    op.execute('SELECT 1')
