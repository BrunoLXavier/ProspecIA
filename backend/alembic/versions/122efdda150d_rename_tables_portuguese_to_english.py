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
down_revision: Union[str, None] = '009_en_us_table_aliases'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename tables to English with backward-compatible views."""
    
    # Rename ingestoes to ingestions
    op.rename_table('ingestoes', 'ingestions')
    
    # Create backward-compatible view for ingestoes
    op.execute("""
        CREATE VIEW ingestoes AS SELECT * FROM ingestions;
    """)
    
    # Rename consentimentos to consents
    op.rename_table('consentimentos', 'consents')
    
    # Create backward-compatible view for consentimentos
    op.execute("""
        CREATE VIEW consentimentos AS SELECT * FROM consents;
    """)


def downgrade() -> None:
    """Revert table renames."""
    
    # Drop views
    op.execute("DROP VIEW IF EXISTS ingestoes;")
    op.execute("DROP VIEW IF EXISTS consentimentos;")
    
    # Rename tables back
    op.rename_table('ingestions', 'ingestoes')
    op.rename_table('consents', 'consentimentos')
