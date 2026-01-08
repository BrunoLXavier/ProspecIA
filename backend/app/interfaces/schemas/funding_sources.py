"""
HTTP schemas for Funding Sources API.

Pydantic v2 schemas for request/response validation.
All field labels use i18n keys (Regra 9: Multilingua).

Wave 2 - RF-02: Gestão de Fontes de Fomento
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.domain.funding_source import FundingSourceStatus, FundingSourceType


class FundingSourceCreate(BaseModel):
    """Schema for creating a funding source."""
    
    name: str = Field(..., min_length=3, max_length=255, description="Funding source name")
    description: str = Field(..., min_length=10, description="Detailed description")
    type: FundingSourceType = Field(..., description="Type of funding")
    sectors: List[str] = Field(..., min_items=1, description="Applicable sectors (e.g., ['TI', 'Saúde'])")
    amount: int = Field(..., gt=0, description="Funding amount in BRL cents")
    trl_min: int = Field(..., ge=1, le=9, description="Minimum TRL (1-9)")
    trl_max: int = Field(..., ge=1, le=9, description="Maximum TRL (1-9)")
    deadline: date = Field(..., description="Application deadline")
    url: Optional[str] = Field(None, max_length=500, description="Official URL")
    requirements: Optional[str] = Field(None, description="Eligibility requirements")

    @field_validator('trl_min', 'trl_max')
    @classmethod
    def validate_trl_range(cls, v: int) -> int:
        """Validate TRL is in range 1-9."""
        if not (1 <= v <= 9):
            raise ValueError(f'TRL must be between 1 and 9, got {v}')
        return v

    @field_validator('deadline')
    @classmethod
    def validate_deadline_future(cls, v: date) -> date:
        """Validate deadline is in the future."""
        if v < date.today():
            raise ValueError(f'Deadline must be in the future, got {v}')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Programa FINEP Subvenção 2026",
                "description": "Programa de subvenção para empresas inovadoras em TI e Saúde",
                "type": "grant",
                "sectors": ["TI", "Saúde"],
                "amount": 10000000000,  # R$ 100M in cents
                "trl_min": 3,
                "trl_max": 7,
                "deadline": "2026-12-31",
                "url": "https://finep.gov.br/programas/subvencao-2026",
                "requirements": "Empresa com mínimo 2 anos de operação, faturamento mínimo R$500K/ano"
            }
        }
    )


class FundingSourceUpdate(BaseModel):
    """Schema for updating a funding source (partial updates allowed)."""
    
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    type: Optional[FundingSourceType] = None
    sectors: Optional[List[str]] = Field(None, min_items=1)
    amount: Optional[int] = Field(None, gt=0)
    trl_min: Optional[int] = Field(None, ge=1, le=9)
    trl_max: Optional[int] = Field(None, ge=1, le=9)
    deadline: Optional[date] = None
    url: Optional[str] = Field(None, max_length=500)
    requirements: Optional[str] = None
    status: Optional[FundingSourceStatus] = None
    motivo: str = Field(..., min_length=5, description="Reason for update (required for transparency)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "amount": 15000000000,  # Increase to R$ 150M
                "deadline": "2027-06-30",
                "motivo": "Orçamento aumentado devido a demanda alta"
            }
        }
    )


class FundingSourceResponse(BaseModel):
    """Schema for funding source response (full entity)."""
    
    id: UUID
    name: str
    description: str
    type: FundingSourceType
    sectors: List[str]
    amount: int
    trl_min: int
    trl_max: int
    deadline: date
    url: Optional[str]
    requirements: Optional[str]
    status: FundingSourceStatus
    tenant_id: UUID
    historico_atualizacoes: List[Dict[str, Any]] = Field(default_factory=list)
    criado_por: UUID
    atualizado_por: UUID
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class FundingSourceListItem(BaseModel):
    """Schema for funding source list item (summary, no history)."""
    
    id: UUID
    name: str
    type: FundingSourceType
    sectors: List[str]
    amount: int
    trl_min: int
    trl_max: int
    deadline: date
    status: FundingSourceStatus
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class FundingSourceListResponse(BaseModel):
    """Schema for paginated funding source list."""
    
    items: List[FundingSourceListItem]
    total: int
    skip: int
    limit: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Programa FINEP 2026",
                        "type": "grant",
                        "sectors": ["TI", "Saúde"],
                        "amount": 10000000000,
                        "trl_min": 3,
                        "trl_max": 7,
                        "deadline": "2026-12-31",
                        "status": "active",
                        "criado_em": "2026-01-08T10:00:00Z"
                    }
                ],
                "total": 1,
                "skip": 0,
                "limit": 100
            }
        }
    )


class FundingSourceHistoryEntry(BaseModel):
    """Schema for a single history entry in audit trail."""
    
    campo: str
    valor_antigo: Any
    valor_novo: Any
    motivo: str
    usuario_id: str
    timestamp: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "campo": "amount",
                "valor_antigo": 10000000000,
                "valor_novo": 15000000000,
                "motivo": "Orçamento aumentado devido a demanda alta",
                "usuario_id": "550e8400-e29b-41d4-a716-446655440001",
                "timestamp": "2026-01-08T15:30:00.000Z"
            }
        }
    )


class FundingSourceHistoryResponse(BaseModel):
    """Schema for funding source history (audit trail only)."""
    
    funding_source_id: UUID
    name: str
    historico: List[FundingSourceHistoryEntry]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "funding_source_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Programa FINEP 2026",
                "historico": [
                    {
                        "campo": "amount",
                        "valor_antigo": 10000000000,
                        "valor_novo": 15000000000,
                        "motivo": "Orçamento aumentado",
                        "usuario_id": "550e8400-e29b-41d4-a716-446655440001",
                        "timestamp": "2026-01-08T15:30:00.000Z"
                    }
                ]
            }
        }
    )
