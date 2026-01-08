"""Pydantic schemas for Opportunities API (RF-05 Pipeline)."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.opportunity import OpportunityStage, OpportunityStatus


class OpportunityCreate(BaseModel):
    """Schema for creating an opportunity."""
    client_id: UUID = Field(..., description="Client UUID")
    funding_source_id: UUID = Field(..., description="Funding source UUID")
    title: str = Field(..., min_length=1, max_length=255, description="Opportunity title")
    description: str = Field(..., min_length=1, description="Detailed description")
    score: int = Field(default=0, ge=0, le=100, description="Opportunity score (0-100)")
    estimated_value: int = Field(..., ge=0, description="Estimated value in cents")
    probability: int = Field(default=50, ge=0, le=100, description="Success probability (0-100)")
    expected_close_date: datetime = Field(..., description="Expected closing date")
    responsible_user_id: UUID = Field(..., description="Responsible user UUID")

    @field_validator('expected_close_date')
    @classmethod
    def validate_future_date(cls, v: datetime) -> datetime:
        """Ensure expected close date is in the future."""
        if v < datetime.utcnow():
            raise ValueError("expected_close_date must be in the future")
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "client_id": "123e4567-e89b-12d3-a456-426614174000",
            "funding_source_id": "987fcdeb-51a2-43f7-b890-123456789abc",
            "title": "Projeto IoT Indústria 4.0 - Sensor Smart",
            "description": "Oportunidade para desenvolver sensor IoT com financiamento EMBRAPII",
            "score": 75,
            "estimated_value": 80000000,
            "probability": 70,
            "expected_close_date": "2024-06-30T23:59:59Z",
            "responsible_user_id": "456e7890-e12b-34d5-a678-987654321def"
        }
    })


class OpportunityUpdate(BaseModel):
    """Schema for updating an opportunity."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    score: Optional[int] = Field(None, ge=0, le=100)
    estimated_value: Optional[int] = Field(None, ge=0)
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    responsible_user_id: Optional[UUID] = None
    status: Optional[OpportunityStatus] = None
    motivo: str = Field(..., min_length=1, description="Reason for the update")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "score": 85,
            "probability": 80,
            "motivo": "Cliente confirmou interesse formal, aumentada probabilidade"
        }
    })


class OpportunityStageTransition(BaseModel):
    """Schema for transitioning opportunity to a new stage."""
    new_stage: OpportunityStage = Field(..., description="New pipeline stage")
    motivo: str = Field(..., min_length=1, description="Reason for the stage transition")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "new_stage": "approach",
            "motivo": "Cliente validou interesse, iniciando abordagem comercial"
        }
    })


class OpportunityResponse(BaseModel):
    """Schema for opportunity response."""
    id: UUID
    client_id: UUID
    funding_source_id: UUID
    title: str
    description: str
    stage: OpportunityStage
    score: int
    estimated_value: int
    probability: int
    expected_close_date: datetime
    responsible_user_id: UUID
    status: OpportunityStatus
    tenant_id: UUID
    historico_atualizacoes: List[Dict[str, Any]] = Field(default_factory=list)
    historico_transicoes: List[Dict[str, Any]] = Field(default_factory=list)
    criado_por: UUID
    atualizado_por: UUID
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityListItem(BaseModel):
    """Schema for opportunity list item (summary)."""
    id: UUID
    client_id: UUID
    funding_source_id: UUID
    title: str
    stage: OpportunityStage
    score: int
    estimated_value: int
    probability: int
    expected_close_date: datetime
    responsible_user_id: UUID
    status: OpportunityStatus
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityListResponse(BaseModel):
    """Schema for paginated opportunity list."""
    items: List[OpportunityListItem]
    total: int
    skip: int
    limit: int


class OpportunityTransitionsResponse(BaseModel):
    """Schema for opportunity stage transitions history."""
    id: UUID
    title: str
    stage: OpportunityStage
    historico_transicoes: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
