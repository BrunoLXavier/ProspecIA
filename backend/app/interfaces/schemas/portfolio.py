"""Pydantic schemas for Portfolio API (RF-03)."""
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr

from app.domain.portfolio import InstituteStatus, ProjectStatus


class InstituteCreate(BaseModel):
    """Schema for creating an institute."""
    name: str = Field(..., min_length=1, max_length=255, description="Institute name")
    acronym: Optional[str] = Field(None, max_length=20, description="Institute acronym/abbreviation")
    description: str = Field(..., min_length=1, description="Detailed description")
    website: Optional[str] = Field(None, max_length=255, description="Website URL")
    contact_email: EmailStr = Field(..., description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Contact phone")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Instituto de Pesquisa em Tecnologia Aplicada",
            "acronym": "IPTA",
            "description": "Instituto focado em P&D para indústria 4.0",
            "website": "https://ipta.org.br",
            "contact_email": "contato@ipta.org.br",
            "contact_phone": "+55 11 3333-4444"
        }
    })


class InstituteUpdate(BaseModel):
    """Schema for updating an institute."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    acronym: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, min_length=1)
    website: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    status: Optional[InstituteStatus] = None
    motivo: str = Field(..., min_length=1, description="Reason for the update")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "website": "https://ipta.org.br",
            "contact_phone": "+55 11 3333-5555",
            "motivo": "Atualização de informações de contato"
        }
    })


class InstituteResponse(BaseModel):
    """Schema for institute response."""
    id: UUID
    name: str
    acronym: Optional[str]
    description: str
    website: Optional[str]
    contact_email: EmailStr
    contact_phone: Optional[str]
    status: InstituteStatus
    tenant_id: UUID
    historico_atualizacoes: List[Dict[str, Any]] = Field(default_factory=list)
    criado_por: UUID
    atualizado_por: UUID
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class InstituteListItem(BaseModel):
    """Schema for institute list item."""
    id: UUID
    name: str
    acronym: Optional[str]
    contact_email: EmailStr
    status: InstituteStatus
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class InstituteListResponse(BaseModel):
    """Schema for paginated institute list."""
    items: List[InstituteListItem]
    total: int
    skip: int
    limit: int


class ProjectCreate(BaseModel):
    """Schema for creating a project."""
    institute_id: UUID = Field(..., description="Institute UUID")
    title: str = Field(..., min_length=1, max_length=255, description="Project title")
    description: str = Field(..., min_length=1, description="Detailed description")
    objectives: str = Field(..., min_length=1, description="Project objectives")
    trl: int = Field(..., ge=1, le=9, description="Technology Readiness Level (1-9)")
    budget: Optional[int] = Field(None, ge=0, description="Budget in cents")
    start_date: date = Field(..., description="Project start date")
    end_date: Optional[date] = Field(None, description="Expected end date")
    team_size: int = Field(default=1, ge=1, description="Number of team members")

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
        """Ensure end date is after start date."""
        if v and 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("end_date must be after start_date")
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "institute_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Desenvolvimento de Sensor IoT para Indústria 4.0",
            "description": "Projeto de P&D para criar sensor de baixo custo",
            "objectives": "Desenvolver protótipo funcional até Q4 2024",
            "trl": 4,
            "budget": 50000000,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "team_size": 5
        }
    })


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    objectives: Optional[str] = Field(None, min_length=1)
    trl: Optional[int] = Field(None, ge=1, le=9)
    budget: Optional[int] = Field(None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    team_size: Optional[int] = Field(None, ge=1)
    status: Optional[ProjectStatus] = None
    motivo: str = Field(..., min_length=1, description="Reason for the update")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "trl": 5,
            "status": "active",
            "motivo": "Projeto avançou para fase de testes"
        }
    })


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: UUID
    institute_id: UUID
    title: str
    description: str
    objectives: str
    trl: int
    budget: Optional[int]
    start_date: date
    end_date: Optional[date]
    team_size: int
    status: ProjectStatus
    tenant_id: UUID
    historico_atualizacoes: List[Dict[str, Any]] = Field(default_factory=list)
    criado_por: UUID
    atualizado_por: UUID
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListItem(BaseModel):
    """Schema for project list item."""
    id: UUID
    institute_id: UUID
    title: str
    trl: int
    status: ProjectStatus
    start_date: date
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Schema for paginated project list."""
    items: List[ProjectListItem]
    total: int
    skip: int
    limit: int


class CompetenceCreate(BaseModel):
    """Schema for creating a competence."""
    name: str = Field(..., min_length=1, max_length=255, description="Competence name")
    category: str = Field(..., min_length=1, max_length=100, description="Category")
    description: str = Field(..., min_length=1, description="Detailed description")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Machine Learning",
            "category": "Inteligência Artificial",
            "description": "Desenvolvimento de modelos de aprendizado de máquina supervisionado e não-supervisionado"
        }
    })


class CompetenceResponse(BaseModel):
    """Schema for competence response."""
    id: UUID
    name: str
    category: str
    description: str
    tenant_id: UUID
    criado_por: UUID
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class CompetenceListResponse(BaseModel):
    """Schema for paginated competence list."""
    items: List[CompetenceResponse]
    total: int
    skip: int
    limit: int
