"""ARCHIVED: Create English-named compatibility views for existing Portuguese tables.

Original Revision ID: 009_en_us_table_aliases
Archived on 2026-01-09
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "009_en_us_table_aliases"
down_revision = "000_squashed_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: views created/handled in squashed migration
    op.execute('SELECT 1')


def downgrade() -> None:
    op.execute('SELECT 1')
