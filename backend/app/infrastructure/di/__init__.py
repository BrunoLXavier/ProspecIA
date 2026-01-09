"""
Dependency Injection Container

Provides centralized dependency composition and resolution.
Implements the Composition Root pattern for clean architecture.

Usage:
    from app.infrastructure.di.container import DIContainer

    container = DIContainer(settings, session)
    repo = container.get_client_repository()
"""

from typing import Any, Callable, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.config.settings import Settings
from app.infrastructure.repositories.clients_repository import ClientsRepository
from app.infrastructure.repositories.funding_sources_repository import FundingSourcesRepository
from app.infrastructure.repositories.interactions_repository import InteractionsRepository
from app.infrastructure.repositories.opportunities_repository import OpportunitiesRepository
from app.infrastructure.repositories.portfolio_repository import (
    CompetencesRepository,
    InstitutesRepository,
    ProjectsRepository,
)


class DIContainer:
    """
    Centralized dependency container for managing application dependencies.

    Follows the Service Locator pattern (though prefer injection where possible).
    Lazy-loads dependencies on first access.
    """

    def __init__(self, settings: Settings, session: AsyncSession):
        """
        Initialize DI container.

        Args:
            settings: Application settings singleton
            session: Async SQLAlchemy session
        """
        self.settings = settings
        self.session = session
        self._cache: Dict[str, Any] = {}

    def get_client_repository(self) -> ClientsRepository:
        """Get or create ClientsRepository instance."""
        key = "client_repository"
        if key not in self._cache:
            self._cache[key] = ClientsRepository(self.session)
        return self._cache[key]

    def get_opportunity_repository(self) -> OpportunitiesRepository:
        """Get or create OpportunitiesRepository instance."""
        key = "opportunity_repository"
        if key not in self._cache:
            self._cache[key] = OpportunitiesRepository(self.session)
        return self._cache[key]

    def get_interaction_repository(self) -> InteractionsRepository:
        """Get or create InteractionsRepository instance."""
        key = "interaction_repository"
        if key not in self._cache:
            self._cache[key] = InteractionsRepository(self.session)
        return self._cache[key]

    def get_funding_source_repository(self) -> FundingSourcesRepository:
        """Get or create FundingSourcesRepository instance."""
        key = "funding_source_repository"
        if key not in self._cache:
            self._cache[key] = FundingSourcesRepository(self.session)
        return self._cache[key]

    def get_institutes_repository(self) -> InstitutesRepository:
        """Get or create InstitutesRepository instance."""
        key = "institutes_repository"
        if key not in self._cache:
            self._cache[key] = InstitutesRepository(self.session)
        return self._cache[key]

    def get_projects_repository(self) -> ProjectsRepository:
        """Get or create ProjectsRepository instance."""
        key = "projects_repository"
        if key not in self._cache:
            self._cache[key] = ProjectsRepository(self.session)
        return self._cache[key]

    def get_competences_repository(self) -> CompetencesRepository:
        """Get or create CompetencesRepository instance."""
        key = "competences_repository"
        if key not in self._cache:
            self._cache[key] = CompetencesRepository(self.session)
        return self._cache[key]

    def clear_cache(self) -> None:
        """Clear cached instances (useful for testing)."""
        self._cache.clear()

    def register(self, key: str, factory: Callable) -> None:
        """
        Register a custom factory function.

        Args:
            key: Unique identifier for the dependency
            factory: Callable that returns the dependency instance
        """
        self._cache[key] = factory()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a registered dependency by key.

        Args:
            key: Identifier of the dependency

        Returns:
            Dependency instance or None if not found
        """
        return self._cache.get(key)


# Global container instance (initialized in main.py)
_container: Optional[DIContainer] = None


def initialize_container(settings: Settings, session: AsyncSession) -> DIContainer:
    """
    Initialize the global DI container.

    Should be called once during application startup.

    Args:
        settings: Application settings
        session: Async database session

    Returns:
        Initialized DIContainer instance
    """
    global _container
    _container = DIContainer(settings, session)
    return _container


def get_container() -> DIContainer:
    """
    Get the global DI container.

    Returns:
        Global DIContainer instance

    Raises:
        RuntimeError: If container not initialized
    """
    if _container is None:
        raise RuntimeError(
            "DI container not initialized. Call initialize_container() during startup."
        )
    return _container
