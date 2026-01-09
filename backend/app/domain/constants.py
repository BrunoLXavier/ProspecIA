"""
Domain-wide constants to avoid magic strings and improve consistency.

These names intentionally preserve current database table names
to avoid migrations. Future migrations can update these values.
"""

# Audit action names
AUDIT_ACTION_CREATE = "CREATE"
AUDIT_ACTION_UPDATE = "UPDATE"
AUDIT_ACTION_DELETE = "DELETE"

# Legacy Portuguese action labels used in some business logs
ACTION_CONCESSAO = "concessao"
ACTION_NEGACAO = "negacao"
ACTION_ATUALIZACAO = "atualizacao"
ACTION_REVOGACAO = "revogacao"

# Database table names (current schema)
TABLE_CONSENTS = "consentimentos"
TABLE_INGESTIONS = "ingestoes"
