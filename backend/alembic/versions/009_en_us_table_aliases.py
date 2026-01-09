"""
Create English-named compatibility views for existing Portuguese tables.

This migration does NOT rename the underlying tables to avoid breaking
current SQLAlchemy mappings. It introduces read-only views `ingestions`
pointing to `ingestoes` and `consents` pointing to `consentimentos` to
prepare for a future full rename with ORM mapping updates.

Downgrade removes the views.
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "009_en_us_table_aliases"
down_revision = "008_wave2_pipeline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create compatibility views (read-only)
    op.execute(
        """
        CREATE OR REPLACE VIEW ingestions AS
        SELECT * FROM ingestoes;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW consents AS
        SELECT * FROM consentimentos;
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS ingestions;")
    op.execute("DROP VIEW IF EXISTS consents;")
