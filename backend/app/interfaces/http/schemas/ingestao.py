"""
Pydantic schemas for ingestion HTTP endpoints.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.domain.models.ingestao import IngestionStatus, IngestionMethod, IngestionSource


class IngestionCreateRequest(BaseModel):
    """Request schema for creating ingestion."""
    fonte: IngestionSource = Field(..., title="Source", description="Data source")
    metodo: IngestionMethod = Field(..., title="Method", description="Ingestion method")
    consentimento_id: Optional[UUID] = Field(None, title="Consent Id", description="LGPD consent UUID")
    descricao: Optional[str] = Field(None, max_length=5000, title="Description", description="Description")
    tags: Optional[List[str]] = Field(None, title="Tags", description="Tags array")
    metadata_adicional: Optional[Dict[str, Any]] = Field(None, title="Additional Metadata", description="Additional metadata")

    model_config = ConfigDict(use_enum_values=True, title="IngestionCreateRequest")


class IngestionCreateResponse(BaseModel):
    """Response schema for created ingestion."""
    id: UUID = Field(..., title="Id", description="Ingestion UUID")
    fonte: str = Field(..., title="Source", description="Data source")
    status: str = Field(..., title="Status", description="Current status")
    arquivo_storage_path: Optional[str] = Field(None, title="Storage Path", description="MinIO storage path")
    qr_code_base64: Optional[str] = Field(None, title="QR Code Base64", description="QR code for tracking")
    confiabilidade_score: int = Field(..., title="Reliability Score", description="Reliability score 0-100")
    data_ingestao: datetime = Field(..., title="Ingestion Time", description="Ingestion timestamp")
    
    model_config = ConfigDict(from_attributes=True, title="IngestionCreateResponse")


class IngestionDetailResponse(BaseModel):
    """Detailed ingestion response."""
    id: UUID = Field(..., title="Id")
    fonte: str = Field(..., title="Source")
    metodo: str = Field(..., title="Method")
    arquivo_original: Optional[str] = Field(None, title="Original File")
    arquivo_storage_path: Optional[str] = Field(None, title="Storage Path")
    arquivo_size_bytes: Optional[int] = Field(None, title="File Size Bytes")
    arquivo_mime_type: Optional[str] = Field(None, title="File MIME Type")
    confiabilidade_score: int = Field(..., title="Reliability Score")
    total_registros: Optional[int] = Field(None, title="Total Records")
    registros_validos: Optional[int] = Field(None, title="Valid Records")
    registros_invalidos: Optional[int] = Field(None, title="Invalid Records")
    status: str = Field(..., title="Status")
    erros_encontrados: Optional[List[Dict[str, Any]]] = Field(None, title="Errors Found")
    pii_detectado: Optional[Dict[str, Any]] = Field(None, title="PII Detected")
    acoes_lgpd: Optional[List[str]] = Field(None, title="LGPD Actions")
    consentimento_id: Optional[UUID] = Field(None, title="Consent Id")
    criado_por: UUID = Field(..., title="Created By")
    tenant_id: str = Field(..., title="Tenant Id")
    data_ingestao: datetime = Field(..., title="Ingestion Time")
    data_processamento: Optional[datetime] = Field(None, title="Processing Time")
    data_criacao: datetime = Field(..., title="Created At")
    data_atualizacao: datetime = Field(..., title="Updated At")
    descricao: Optional[str] = Field(None, title="Description")
    tags: Optional[List[str]] = Field(None, title="Tags")
    metadata_adicional: Optional[Dict[str, Any]] = Field(None, title="Additional Metadata")
    dados_brutos_sample: Optional[List[Dict[str, Any]]] = Field(None, title="Raw Data Sample", description="Sample of raw data")
    
    model_config = ConfigDict(from_attributes=True, title="IngestionDetailResponse")


class IngestionListItem(BaseModel):
    """Simplified ingestion item for list view."""
    id: UUID = Field(..., title="Id")
    fonte: str = Field(..., title="Source")
    status: str = Field(..., title="Status")
    confiabilidade_score: int = Field(..., title="Reliability Score")
    total_registros: Optional[int] = Field(None, title="Total Records")
    data_ingestao: datetime = Field(..., title="Ingestion Time")
    criado_por: UUID = Field(..., title="Created By")
    consentimento_id: Optional[UUID] = Field(None, title="Consent Id")
    
    model_config = ConfigDict(from_attributes=True, title="IngestionListItem")


class IngestionListResponse(BaseModel):
    """Paginated list response."""
    items: List[IngestionListItem] = Field(..., title="Items", description="Ingestion items")
    total: int = Field(..., title="Total", description="Total count")
    offset: int = Field(..., title="Offset", description="Offset")
    limit: int = Field(..., title="Limit", description="Limit")

    model_config = ConfigDict(title="IngestionListResponse")


class LineageNode(BaseModel):
    """Lineage graph node."""
    id: str = Field(..., title="Id", description="Node UUID")
    type: str = Field(..., title="Type", description="Node type (ingestion, transformation, dataset)")
    label: str = Field(..., title="Label", description="Node label")
    properties: Dict[str, Any] = Field(default_factory=dict, title="Properties", description="Node properties")

    model_config = ConfigDict(title="LineageNode")


class LineageEdge(BaseModel):
    """Lineage graph edge."""
    source: str = Field(..., title="Source", description="Source node UUID")
    target: str = Field(..., title="Target", description="Target node UUID")
    type: str = Field(..., title="Type", description="Relationship type")
    properties: Dict[str, Any] = Field(default_factory=dict, title="Properties", description="Edge properties")

    model_config = ConfigDict(title="LineageEdge")


class LineageResponse(BaseModel):
    """Data lineage response."""
    ingestao_id: UUID = Field(..., title="Ingestion Id", description="Root ingestion UUID")
    nodes: List[LineageNode] = Field(..., title="Nodes", description="Graph nodes")
    edges: List[LineageEdge] = Field(..., title="Edges", description="Graph edges")
    dados_brutos_sample: Optional[List[Dict[str, Any]]] = Field(None, title="Raw Data Sample", description="First 100 rows")
    transformacoes: List[str] = Field(..., title="Transformations", description="Transformation steps")
    confiabilidade_score: int = Field(..., title="Reliability Score", description="Reliability score")
    data_ingestao: datetime = Field(..., title="Ingestion Time", description="Ingestion timestamp")

    model_config = ConfigDict(title="LineageResponse")


class PIITypeStat(BaseModel):
    """PII type statistics."""
    type: str = Field(..., description="PII type name")
    count: int = Field(..., description="Number of instances")
    samples: List[str] = Field(default_factory=list, description="Sample values (masked)")
    detected: bool = Field(..., description="Whether this PII type was detected")


class ConsentRecord(BaseModel):
    """Consent record details."""
    tipo_consentimento: str = Field(..., title="Consent Type", description="Consent type")
    finalidade: str = Field(..., title="Purpose", description="Purpose")
    status: str = Field(..., title="Status", description="Status")
    data_consentimento: Optional[datetime] = Field(None, title="Consent Date", description="Grant date")
    data_revogacao: Optional[datetime] = Field(None, title="Revocation Date", description="Revocation date")


class LGPDReportResponse(BaseModel):
    """LGPD compliance report."""
    ingestao_id: UUID = Field(..., title="Ingestion Id", description="Ingestion UUID")
    pii_types_detected: Dict[str, int] = Field(..., title="PII Types Detected", description="PII counts by type")
    pii_details: List[PIITypeStat] = Field(default_factory=list, title="PII Details", description="Detailed PII statistics")
    total_pii_instances: int = Field(..., title="Total PII Instances", description="Total number of PII instances")
    masking_actions: List[str] = Field(..., title="Masking Actions", description="Actions taken")
    consent_status: str = Field(..., title="Consent Status", description="Consent validation status")
    consent_records: List[ConsentRecord] = Field(default_factory=list, title="Consent Records", description="Consent details")
    consentimento_id: Optional[UUID] = Field(None, title="Consent Id", description="Consent UUID")
    compliance_score: int = Field(..., title="Compliance Score", description="Compliance score 0-100")
    risk_level: str = Field(..., title="Risk Level", description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    recommendations: List[str] = Field(..., title="Recommendations", description="Compliance recommendations")
    lgpd_articles_applicable: List[str] = Field(default_factory=list, title="LGPD Articles Applicable", description="Applicable LGPD articles")
    data_analysis: str = Field(..., title="Data Analysis", description="Detailed analysis text")
    data_processamento: Optional[datetime] = Field(None, title="Processing Time", description="Processing timestamp")
