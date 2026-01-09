"""Compatibility re-exports for legacy imports.

Portfolio ORM definitions moved to infrastructure/models.
This module forwards imports to maintain backward compatibility.
"""

from app.infrastructure.models.portfolio import (
    Competence,
    Institute,
    InstituteStatus,
    Project,
    ProjectStatus,
)

__all__ = [
    "Competence",
    "Institute",
    "InstituteStatus",
    "Project",
    "ProjectStatus",
]
