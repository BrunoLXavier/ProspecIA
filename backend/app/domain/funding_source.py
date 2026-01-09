"""Compatibility re-exports for legacy imports.

FundingSource ORM definitions moved to infrastructure/models.
This module forwards imports to maintain backward compatibility.
"""

from app.infrastructure.models.funding_source import (
    FundingSource,
    FundingSourceStatus,
    FundingSourceType,
)

__all__ = ["FundingSource", "FundingSourceStatus", "FundingSourceType"]
