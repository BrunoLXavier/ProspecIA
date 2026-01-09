"""Pydantic schemas for Clients API (RF-04 CRM)."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.domain.client import ClientMaturity, ClientStatus


class ClientCreate(BaseModel):
    """Schema for creating a client."""

    name: str = Field(..., min_length=1, max_length=255, description="Client name")
    cnpj: str = Field(..., pattern=r"^\d{14}$", description="CNPJ (14 digits)")
    email: EmailStr = Field(..., description="Client email")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    website: Optional[str] = Field(None, max_length=255, description="Website URL")
    address: Optional[str] = Field(None, description="Physical address")
    maturity: ClientMaturity = Field(
        default=ClientMaturity.PROSPECT, description="Client maturity level"
    )
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj_digits(cls, v: str) -> str:
        """Validate CNPJ is exactly 14 digits."""
        if not v.isdigit() or len(v) != 14:
            raise ValueError("CNPJ must be exactly 14 digits")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Empresa Exemplo LTDA",
                "cnpj": "12345678000195",
                "email": "contato@exemplo.com.br",
                "phone": "+55 11 98765-4321",
                "website": "https://exemplo.com.br",
                "maturity": "lead",
                "notes": "Prospect identificado na feira de tecnologia",
            }
        }
    )


class ClientUpdate(BaseModel):
    """Schema for updating a client."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    maturity: Optional[ClientMaturity] = None
    notes: Optional[str] = None
    status: Optional[ClientStatus] = None
    motivo: str = Field(..., min_length=1, description="Reason for the update (required)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "maturity": "opportunity",
                "notes": "Cliente demonstrou interesse em parceria",
                "motivo": "Atualização após reunião comercial",
            }
        }
    )


class ClientResponse(BaseModel):
    """Schema for client response."""

    id: UUID
    name: str
    cnpj: str
    email: EmailStr
    phone: Optional[str]
    website: Optional[str]
    address: Optional[str]
    maturity: ClientMaturity
    notes: Optional[str]
    status: ClientStatus
    tenant_id: UUID
    historico_atualizacoes: List[Dict[str, Any]] = Field(default_factory=list)
    criado_por: UUID
    atualizado_por: UUID
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientListItem(BaseModel):
    """Schema for client list item (summary without history)."""

    id: UUID
    name: str
    cnpj: str
    email: EmailStr
    phone: Optional[str]
    maturity: ClientMaturity
    status: ClientStatus
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ClientListResponse(BaseModel):
    """Schema for paginated client list."""

    items: List[ClientListItem]
    total: int
    skip: int
    limit: int


class ClientHistoryResponse(BaseModel):
    """Schema for client history only."""

    id: UUID
    name: str
    historico_atualizacoes: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
