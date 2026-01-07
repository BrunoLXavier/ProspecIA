"""
ProspecIA - PostgreSQL Database Adapter

SQLAlchemy async connection management following Repository Pattern.
Implements connection pooling, session management, and health checks.
"""

from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import text
import structlog

from app.infrastructure.config.settings import Settings

logger = structlog.get_logger()

# Declarative base for all SQLAlchemy models
Base = declarative_base()


class DatabaseConnection:
    """
    Manages PostgreSQL database connections with async SQLAlchemy.
    
    Responsibilities (SRP):
    - Create and manage async engine
    - Provide session factory
    - Handle connection lifecycle
    - Implement connection pooling
    - Provide health check capability
    
    Follows DIP: Depends on Settings abstraction, not concrete implementation
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize database connection manager.
        
        Args:
            settings: Application settings with database configuration
        """
        self.settings = settings
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        
    async def connect(self) -> None:
        """
        Initialize database engine and session factory.
        
        Raises:
            Exception: If connection fails
        """
        if self._engine is not None:
            logger.warning("database_already_connected")
            return
        
        # Convert sync postgres:// URL to async postgresql+asyncpg://
        database_url = self.settings.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        
        logger.info(
            "database_connecting",
            host=self.settings.POSTGRES_HOST,
            port=self.settings.POSTGRES_PORT,
            database=self.settings.POSTGRES_DB,
        )
        
        # Create async engine with connection pooling
        self._engine = create_async_engine(
            database_url,
            echo=self.settings.DEBUG,
            pool_size=self.settings.DB_POOL_SIZE,
            max_overflow=self.settings.DB_MAX_OVERFLOW,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
            poolclass=QueuePool if self.settings.ENV == "production" else NullPool,
        )
        
        # Create session factory
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        logger.info("database_connected")
    
    async def disconnect(self) -> None:
        """Close database engine and cleanup resources."""
        if self._engine is None:
            return
        
        logger.info("database_disconnecting")
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None
        logger.info("database_disconnected")
    
    async def health_check(self) -> bool:
        """
        Check database connectivity.
        
        Returns:
            bool: True if database is accessible, False otherwise
        """
        if self._engine is None:
            return False
        
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error("database_health_check_failed", error=str(e))
            return False
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get async database session with automatic transaction management.
        
        Usage:
            async with db.get_session() as session:
                result = await session.execute(query)
                await session.commit()
        
        Yields:
            AsyncSession: Database session
            
        Raises:
            RuntimeError: If database not connected
        """
        if self._session_factory is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @property
    def engine(self) -> AsyncEngine:
        """
        Get the underlying async engine.
        
        Returns:
            AsyncEngine: SQLAlchemy async engine
            
        Raises:
            RuntimeError: If database not connected
        """
        if self._engine is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._engine
    
    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """
        Get the session factory.
        
        Returns:
            async_sessionmaker: Session factory for creating sessions
            
        Raises:
            RuntimeError: If database not connected
        """
        if self._session_factory is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._session_factory


# Global database instance (initialized in main.py)
db_connection: DatabaseConnection | None = None


def get_db_connection() -> DatabaseConnection:
    """
    Get global database connection instance.
    
    Returns:
        DatabaseConnection: Global database connection
        
    Raises:
        RuntimeError: If database not initialized
    """
    if db_connection is None:
        raise RuntimeError("Database not initialized. Initialize in app startup.")
    return db_connection


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get database session.
    
    Usage in routes:
        @router.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    
    Yields:
        AsyncSession: Database session
    """
    db = get_db_connection()
    async with db.get_session() as session:
        yield session
