"""Rename tables from Portuguese to English with backward-compatible views.

Revision ID: 122efdda150d
Revises: 009_en_us_table_aliases
Create Date: 2026-01-08

Renames tables from Portuguese to English:
- ingestoes → ingestions
- consentimentos → consents

Includes backward-compatible views for gradual migration.

"""

from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '122efdda150d'
down_revision: Union[str, None] = '000_squashed_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename tables to English with backward-compatible views."""
    # No-op: renames handled/normalized by 000_squashed_initial
    op.execute('SELECT 1')


def downgrade() -> None:
    """Revert table renames."""
    op.execute('SELECT 1')
