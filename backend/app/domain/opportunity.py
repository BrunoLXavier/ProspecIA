"""Compatibility re-exports for legacy imports.

The opportunity ORM definitions now live in infrastructure/models.
This module forwards imports to maintain backward compatibility.
"""

from app.infrastructure.models.opportunity import Opportunity, OpportunityStage, OpportunityStatus

__all__ = ["Opportunity", "OpportunityStage", "OpportunityStatus"]
