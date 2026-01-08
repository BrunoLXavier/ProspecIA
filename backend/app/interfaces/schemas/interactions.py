"""Pydantic schemas for Interactions API (RF-04 CRM)."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.interaction import InteractionType, InteractionOutcome, InteractionStatus


class InteractionCreate(BaseModel):
    """Schema for creating an interaction."""
    client_id: UUID = Field(..., description="Client UUID")
    title: str = Field(..., min_length=1, max_length=255, description="Interaction title")
    description: str = Field(..., min_length=1, description="Detailed description")
    type: InteractionType = Field(..., description="Type of interaction")
    date: datetime = Field(..., description="Interaction date/time")
    participants: List[str] = Field(default_factory=list, description="List of participant names")
    outcome: Optional[InteractionOutcome] = Field(None, description="Outcome of the interaction")
    next_steps: Optional[str] = Field(None, description="Next steps to take")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "client_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Reunião Comercial - Apresentação de Projeto",
            "description": "Apresentação detalhada do projeto de P&D para o diretor técnico",
            "type": "meeting",
            "date": "2024-01-15T14:30:00Z",
            "participants": ["João Silva", "Maria Santos"],
            "outcome": "positive",
            "next_steps": "Enviar proposta técnica detalhada até dia 20/01"
        }
    })


class InteractionUpdate(BaseModel):
    """Schema for updating an interaction."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    type: Optional[InteractionType] = None
    date: Optional[datetime] = None
    participants: Optional[List[str]] = None
    outcome: Optional[InteractionOutcome] = None
    next_steps: Optional[str] = None
    status: Optional[InteractionStatus] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "outcome": "positive",
            "next_steps": "Agendar reunião técnica para próxima semana"
        }
    })


class InteractionResponse(BaseModel):
    """Schema for interaction response."""
    id: UUID
    client_id: UUID
    title: str
    description: str
    type: InteractionType
    date: datetime
    participants: List[str]
    outcome: Optional[InteractionOutcome]
    next_steps: Optional[str]
    status: InteractionStatus
    tenant_id: UUID
    criado_por: UUID
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class InteractionListItem(BaseModel):
    """Schema for interaction list item."""
    id: UUID
    client_id: UUID
    title: str
    type: InteractionType
    date: datetime
    outcome: Optional[InteractionOutcome]
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class InteractionListResponse(BaseModel):
    """Schema for paginated interaction list."""
    items: List[InteractionListItem]
    total: int
    skip: int
    limit: int
