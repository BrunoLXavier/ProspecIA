"""
Compatibility layer for database dependencies.

Provides legacy imports (`get_async_session`, `get_db_session`) that now
proxy to the PostgreSQL adapter in `app.adapters.postgres.connection`.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.postgres.connection import (
    DatabaseConnection,
    db_connection,
    get_db_connection,
    get_session,
)

# Alias to match existing router dependencies
get_async_session = get_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Backward-compatible alias used by older routers."""
    async for session in get_session():
        yield session


__all__ = [
    "DatabaseConnection",
    "db_connection",
    "get_db_connection",
    "get_session",
    "get_async_session",
    "get_db_session",
]
