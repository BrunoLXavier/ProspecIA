"""
Pydantic schemas for ingestion HTTP endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.domain.models.ingestao import StatusIngestao, MetodoIngestao, FonteIngestao


class IngestaoCreateRequest(BaseModel):
    """Request schema for creating ingestion."""
    fonte: FonteIngestao = Field(..., description="Data source")
    metodo: MetodoIngestao = Field(..., description="Ingestion method")
    consentimento_id: Optional[UUID] = Field(None, description="LGPD consent UUID")
    descricao: Optional[str] = Field(None, max_length=5000, description="Description")
    tags: Optional[List[str]] = Field(None, description="Tags array")
    metadata_adicional: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    model_config = ConfigDict(use_enum_values=True)


class IngestaoCreateResponse(BaseModel):
    """Response schema for created ingestion."""
    id: UUID = Field(..., description="Ingestion UUID")
    fonte: str = Field(..., description="Data source")
    status: str = Field(..., description="Current status")
    arquivo_storage_path: Optional[str] = Field(None, description="MinIO storage path")
    qr_code_base64: Optional[str] = Field(None, description="QR code for tracking")
    confiabilidade_score: int = Field(..., description="Reliability score 0-100")
    data_ingestao: datetime = Field(..., description="Ingestion timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class IngestaoDetailResponse(BaseModel):
    """Detailed ingestion response."""
    id: UUID
    fonte: str
    metodo: str
    arquivo_original: Optional[str]
    arquivo_storage_path: Optional[str]
    arquivo_size_bytes: Optional[int]
    arquivo_mime_type: Optional[str]
    confiabilidade_score: int
    total_registros: Optional[int]
    registros_validos: Optional[int]
    registros_invalidos: Optional[int]
    status: str
    erros_encontrados: Optional[List[Dict[str, Any]]]
    pii_detectado: Optional[Dict[str, Any]]
    acoes_lgpd: Optional[List[str]]
    consentimento_id: Optional[UUID]
    criado_por: UUID
    tenant_id: str
    data_ingestao: datetime
    data_processamento: Optional[datetime]
    data_criacao: datetime
    data_atualizacao: datetime
    descricao: Optional[str]
    tags: Optional[List[str]]
    metadata_adicional: Optional[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True)


class IngestaoListItem(BaseModel):
    """Simplified ingestion item for list view."""
    id: UUID
    fonte: str
    status: str
    confiabilidade_score: int
    total_registros: Optional[int]
    data_ingestao: datetime
    criado_por: UUID
    
    model_config = ConfigDict(from_attributes=True)


class IngestaoListResponse(BaseModel):
    """Paginated list response."""
    items: List[IngestaoListItem] = Field(..., description="Ingestion items")
    total: int = Field(..., description="Total count")
    offset: int = Field(..., description="Offset")
    limit: int = Field(..., description="Limit")


class LinhagemNode(BaseModel):
    """Lineage graph node."""
    id: str = Field(..., description="Node UUID")
    type: str = Field(..., description="Node type (ingestao, transformation, dataset)")
    label: str = Field(..., description="Node label")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Node properties")


class LinhagemEdge(BaseModel):
    """Lineage graph edge."""
    source: str = Field(..., description="Source node UUID")
    target: str = Field(..., description="Target node UUID")
    type: str = Field(..., description="Relationship type")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties")


class LinhagemResponse(BaseModel):
    """Data lineage response."""
    ingestao_id: UUID = Field(..., description="Root ingestion UUID")
    nodes: List[LinhagemNode] = Field(..., description="Graph nodes")
    edges: List[LinhagemEdge] = Field(..., description="Graph edges")
    dados_brutos_sample: Optional[List[Dict[str, Any]]] = Field(None, description="First 100 rows")
    transformacoes: List[str] = Field(..., description="Transformation steps")
    confiabilidade_score: int = Field(..., description="Reliability score")
    data_ingestao: datetime = Field(..., description="Ingestion timestamp")


class LGPDReportResponse(BaseModel):
    """LGPD compliance report."""
    ingestao_id: UUID = Field(..., description="Ingestion UUID")
    pii_types_detected: Dict[str, int] = Field(..., description="PII counts by type")
    masking_actions: List[str] = Field(..., description="Actions taken")
    consent_status: str = Field(..., description="Consent validation status")
    consentimento_id: Optional[UUID] = Field(None, description="Consent UUID")
    compliance_score: int = Field(..., description="Compliance score 0-100")
    recommendations: List[str] = Field(..., description="Compliance recommendations")
    data_processamento: Optional[datetime] = Field(None, description="Processing timestamp")
