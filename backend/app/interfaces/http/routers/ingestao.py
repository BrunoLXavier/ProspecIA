"""
HTTP endpoints for data ingestion (RF-01).

Implements:
- POST /ingestoes: Upload and process file
- GET /ingestoes: List ingestions with filters
- GET /ingestoes/{id}: Get ingestion details
- GET /ingestoes/{id}/linhagem: Get data lineage
- GET /ingestoes/{id}/lgpd-report: Get LGPD compliance report
"""

import io
import base64
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import qrcode
import structlog

from app.adapters.postgres.connection import get_session
from app.adapters.neo4j.connection import get_neo4j_connection
from app.domain.models.ingestao import Ingestao, StatusIngestao, MetodoIngestao, FonteIngestao
from app.domain.repositories.ingestao_repository import IngestaoRepository
from app.domain.repositories.consentimento_repository import ConsentimentoRepository
from app.infrastructure.middleware.auth_middleware import get_current_user, require_roles
from app.use_cases.lgpd_agent import get_lgpd_agent
from app.interfaces.http.schemas.ingestao import (
    IngestaoCreateRequest,
    IngestaoCreateResponse,
    IngestaoListResponse,
    IngestaoListItem,
    IngestaoDetailResponse,
    LinhagemResponse,
    LinhagemNode,
    LinhagemEdge,
    LGPDReportResponse
)


logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ingestoes", tags=["Ingestão"])


@router.post("", response_model=IngestaoCreateResponse, dependencies=[Depends(require_roles(["admin", "gestor"]))])
async def create_ingestao(
    file: UploadFile = File(..., description="File to ingest"),
    fonte: FonteIngestao = Query(..., description="Data source"),
    metodo: MetodoIngestao = Query(..., description="Ingestion method"),
    consentimento_id: Optional[UUID] = Query(None, description="LGPD consent UUID"),
    descricao: Optional[str] = Query(None, description="Description"),
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    """
    Create new data ingestion with file upload.
    
    - Validates file size (≤100MB)
    - Uploads file to MinIO
    - Processes with LGPD agent
    - Creates lineage node in Neo4j
    - Generates QR code for tracking
    """
    try:
        # Validate file size
        MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File size exceeds 100MB limit")
        
        # Generate UUID for ingestion
        ingestao_id = uuid4()
        
        # MinIO storage path: ingestoes/{uuid}.{extension}
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
        storage_path = f"ingestoes/{ingestao_id}.{file_extension}"
        
        # TODO: Upload to MinIO (implement MinIO adapter)
        # For now, we'll just store the path
        logger.info("file_uploaded", storage_path=storage_path, size_bytes=len(file_content))
        
        # Process with LGPD agent
        lgpd_agent = get_lgpd_agent()
        consent_repo = ConsentimentoRepository(session)
        
        # Convert file content to text (simple approach, could use pandas for CSV/Excel)
        try:
            text_content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            text_content = ""  # Binary file, skip LGPD processing
        
        lgpd_result = await lgpd_agent.process_ingestao(
            text_content=text_content,
            consentimento_id=consentimento_id,
            titular_id=None,  # Extract from file if available
            finalidade="Análise de dados econômicos",
            ingestao_id=ingestao_id,
            repository=consent_repo
        )
        
        # Create ingestion entity
        ingestao = Ingestao(
            id=ingestao_id,
            fonte=fonte,
            metodo=metodo,
            arquivo_original=file.filename,
            arquivo_storage_path=storage_path,
            arquivo_size_bytes=len(file_content),
            arquivo_mime_type=file.content_type,
            confiabilidade_score=lgpd_result["compliance_score"],
            status=StatusIngestao.PROCESSANDO,
            pii_detectado=lgpd_result["pii_detected"],
            acoes_lgpd=lgpd_result["masked_data"]["actions_taken"],
            consentimento_id=consentimento_id,
            historico_atualizacoes=[],
            criado_por=UUID(user["sub"]),
            tenant_id=user.get("tenant_id", "nacional"),
            data_ingestao=datetime.utcnow(),
            data_criacao=datetime.utcnow(),
            data_atualizacao=datetime.utcnow(),
            descricao=descricao
        )
        
        # Save to database
        ingestao_repo = IngestaoRepository(session)
        created_ingestao = await ingestao_repo.create(ingestao)
        
        # Create lineage node in Neo4j
        neo4j = get_neo4j_connection()
        if neo4j:
            try:
                await neo4j.create_lineage_node(
                    node_id=str(ingestao_id),
                    node_type="ingestao",
                    properties={
                        "fonte": fonte.value,
                        "metodo": metodo.value,
                        "arquivo": file.filename,
                        "data_ingestao": ingestao.data_ingestao.isoformat(),
                        "confiabilidade": lgpd_result["compliance_score"]
                    }
                )
                logger.info("lineage_node_created", ingestao_id=str(ingestao_id))
            except Exception as e:
                logger.error("lineage_creation_failed", error=str(e))
        
        # Generate QR code for tracking
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"https://prospecai.senai.br/ingestoes/{ingestao_id}")
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        logger.info("ingestao_created", ingestao_id=str(ingestao_id), fonte=fonte.value, compliance_score=lgpd_result["compliance_score"])
        
        return IngestaoCreateResponse(
            id=created_ingestao.id,
            fonte=created_ingestao.fonte.value,
            status=created_ingestao.status.value,
            arquivo_storage_path=created_ingestao.arquivo_storage_path,
            qr_code_base64=qr_code_base64,
            confiabilidade_score=created_ingestao.confiabilidade_score,
            data_ingestao=created_ingestao.data_ingestao
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("ingestao_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create ingestion: {str(e)}")


@router.get("", response_model=IngestaoListResponse)
async def list_ingestoes(
    fonte: Optional[FonteIngestao] = Query(None, description="Filter by source"),
    status: Optional[StatusIngestao] = Query(None, description="Filter by status"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    """
    List ingestions with filters and pagination.
    
    Applies RLS filtering by tenant_id.
    """
    try:
        ingestao_repo = IngestaoRepository(session)
        
        filters = {}
        if fonte:
            filters["fonte"] = fonte
        if status:
            filters["status"] = status
        
        # Apply tenant filtering (RLS)
        tenant_id = user.get("tenant_id", "nacional")
        
        items, total = await ingestao_repo.list_with_filters(
            tenant_id=tenant_id,
            offset=offset,
            limit=limit,
            **filters
        )
        
        logger.info("ingestoes_listed", total=total, offset=offset, limit=limit, tenant_id=tenant_id)
        
        return IngestaoListResponse(
            items=[IngestaoListItem.model_validate(item) for item in items],
            total=total,
            offset=offset,
            limit=limit
        )
    
    except Exception as e:
        logger.error("list_ingestoes_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list ingestions: {str(e)}")


@router.get("/{id}", response_model=IngestaoDetailResponse)
async def get_ingestao(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    """Get ingestion details by ID."""
    try:
        ingestao_repo = IngestaoRepository(session)
        tenant_id = user.get("tenant_id", "nacional")
        
        ingestao = await ingestao_repo.get_by_id(id, tenant_id=tenant_id)
        
        if not ingestao:
            raise HTTPException(status_code=404, detail="Ingestion not found")
        
        logger.info("ingestao_retrieved", ingestao_id=str(id))
        
        return IngestaoDetailResponse.model_validate(ingestao)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_ingestao_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get ingestion: {str(e)}")


@router.get("/{id}/linhagem", response_model=LinhagemResponse)
async def get_linhagem(
    id: UUID,
    max_depth: int = Query(5, ge=1, le=10, description="Maximum graph depth"),
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    """
    Get data lineage graph for ingestion.
    
    Returns nodes and edges for visualization.
    """
    try:
        # Get ingestion
        ingestao_repo = IngestaoRepository(session)
        tenant_id = user.get("tenant_id", "nacional")
        ingestao = await ingestao_repo.get_by_id(id, tenant_id=tenant_id)
        
        if not ingestao:
            raise HTTPException(status_code=404, detail="Ingestion not found")
        
        # Query Neo4j lineage
        neo4j = get_neo4j_connection()
        if not neo4j:
            raise HTTPException(status_code=503, detail="Lineage service unavailable")
        
        lineage_path = await neo4j.get_lineage_path(str(id), max_depth=max_depth)
        
        # Parse lineage into nodes and edges
        nodes = []
        edges = []
        
        # Add root ingestion node
        nodes.append(LinhagemNode(
            id=str(ingestao.id),
            type="ingestao",
            label=f"{ingestao.fonte.value} - {ingestao.arquivo_original or 'Unknown'}",
            properties={
                "fonte": ingestao.fonte.value,
                "metodo": ingestao.metodo.value,
                "confiabilidade": ingestao.confiabilidade_score,
                "status": ingestao.status.value
            }
        ))
        
        # Add transformation nodes from lineage_path
        for i, item in enumerate(lineage_path):
            if item.get("type") == "transformation":
                node_id = f"transform_{i}"
                nodes.append(LinhagemNode(
                    id=node_id,
                    type="transformation",
                    label=item.get("name", "Transformation"),
                    properties=item.get("properties", {})
                ))
                edges.append(LinhagemEdge(
                    source=str(ingestao.id),
                    target=node_id,
                    type="TRANSFORMED_BY",
                    properties={}
                ))
        
        # Transformation steps
        transformacoes = ["upload", "lgpd_processing"]
        if ingestao.pii_detectado:
            transformacoes.append("pii_detection")
        if ingestao.acoes_lgpd:
            transformacoes.append("pii_masking")
        
        logger.info("lineage_retrieved", ingestao_id=str(id), nodes_count=len(nodes), edges_count=len(edges))
        
        return LinhagemResponse(
            ingestao_id=ingestao.id,
            nodes=nodes,
            edges=edges,
            dados_brutos_sample=None,  # TODO: Sample from MinIO
            transformacoes=transformacoes,
            confiabilidade_score=ingestao.confiabilidade_score,
            data_ingestao=ingestao.data_ingestao
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_lineage_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get lineage: {str(e)}")


@router.get("/{id}/lgpd-report", response_model=LGPDReportResponse)
async def get_lgpd_report(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    """
    Get LGPD compliance report for ingestion.
    
    Returns PII detection results, consent status, compliance score.
    """
    try:
        # Get ingestion
        ingestao_repo = IngestaoRepository(session)
        tenant_id = user.get("tenant_id", "nacional")
        ingestao = await ingestao_repo.get_by_id(id, tenant_id=tenant_id)
        
        if not ingestao:
            raise HTTPException(status_code=404, detail="Ingestion not found")
        
        # Count PII types
        pii_types_detected = {}
        if ingestao.pii_detectado:
            for pii_type, entities in ingestao.pii_detectado.items():
                if entities:
                    pii_types_detected[pii_type] = len(entities)
        
        # Determine consent status
        consent_status = "missing"
        if ingestao.consentimento_id:
            consent_repo = ConsentimentoRepository(session)
            consent = await consent_repo.get_by_id(ingestao.consentimento_id, tenant_id=tenant_id)
            if consent:
                if consent.is_valido():
                    consent_status = "granted"
                else:
                    consent_status = "revoked"
        
        # Generate recommendations
        recommendations = []
        if not ingestao.consentimento_id:
            recommendations.append("Obter consentimento do titular antes do processamento (LGPD Art. 7º)")
        if ingestao.confiabilidade_score < 50:
            recommendations.append("Score de conformidade baixo. Revisar processos de LGPD.")
        if pii_types_detected.get("cpf", 0) > 0 or pii_types_detected.get("cnpj", 0) > 0:
            recommendations.append("Dados sensíveis detectados. Aplicar criptografia adicional (LGPD Art. 46º)")
        if not ingestao.acoes_lgpd:
            recommendations.append("Nenhuma ação LGPD registrada. Verificar processamento.")
        
        logger.info("lgpd_report_generated", ingestao_id=str(id), compliance_score=ingestao.confiabilidade_score)
        
        return LGPDReportResponse(
            ingestao_id=ingestao.id,
            pii_types_detected=pii_types_detected,
            masking_actions=ingestao.acoes_lgpd or [],
            consent_status=consent_status,
            consentimento_id=ingestao.consentimento_id,
            compliance_score=ingestao.confiabilidade_score,
            recommendations=recommendations,
            data_processamento=ingestao.data_processamento
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_lgpd_report_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get LGPD report: {str(e)}")
