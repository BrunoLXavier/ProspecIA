"""Infrastructure repositories package.

Repository implementations live in submodules. This package does not eagerly
import submodules to avoid heavy dependency chains during test collection.
Import specific repositories via their submodules, e.g.:
    from app.infrastructure.repositories.opportunities_repository import OpportunitiesRepository
"""

__all__ = [
    # Names for reference; import from submodules directly in code/tests.
    "ClientsRepository",
    "InteractionsRepository",
    "FundingSourcesRepository",
    "OpportunitiesRepository",
    "InstitutesRepository",
    "ProjectsRepository",
    "CompetencesRepository",
]
