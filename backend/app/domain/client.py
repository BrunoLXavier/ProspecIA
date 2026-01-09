"""Compatibility re-exports for legacy imports.

This module now forwards ORM model definitions to the infrastructure layer
to decouple the domain package from SQLAlchemy and persistence concerns.
"""

from app.infrastructure.models.client import Client, ClientMaturity, ClientStatus

__all__ = ["Client", "ClientMaturity", "ClientStatus"]
