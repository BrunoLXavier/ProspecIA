"""ARCHIVED: Wave 1: Create ingestoes and consentimentos tables

Original Revision ID: 001_wave1_ingestion
Archived on 2026-01-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision = '001_wave1_ingestion'
down_revision = '000_squashed_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: schema consolidated in 000_squashed_initial
    op.execute('SELECT 1')


def downgrade() -> None:
    op.execute('SELECT 1')
