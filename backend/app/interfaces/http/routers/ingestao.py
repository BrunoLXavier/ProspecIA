"""
HTTP endpoints for data ingestion (RF-01).

Implements:
- POST /ingestions: Upload and process file
- GET /ingestions: List ingestions with filters
- GET /ingestions/{id}: Get ingestion details
- GET /ingestions/{id}/lineage: Get data lineage
- GET /ingestions/{id}/lgpd-report: Get LGPD compliance report
"""

import io
import base64
from typing import Optional
import time
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
import qrcode
import structlog

from app.adapters.postgres.connection import get_session
from app.adapters.neo4j.connection import get_neo4j_connection
from app.domain.models.ingestao import Ingestao, IngestionStatus, IngestionMethod, IngestionSource
from app.domain.repositories.ingestao_repository import IngestaoRepository
from app.domain.repositories.consentimento_repository import ConsentimentoRepository
from app.infrastructure.middleware.auth_middleware import get_current_user, require_roles
from app.adapters.minio.client import get_minio_client
from app.infrastructure.monitoring.metrics import (
    ingestoes_created_total,
    ingestoes_status,
    ingestao_confiabilidade_score,
    lgpd_pii_detected_total,
    lgpd_consent_validation,
    ingestao_processing_time,
    ingestao_errors_total,
)
from app.use_cases.lgpd_agent import get_lgpd_agent
from app.interfaces.http.schemas.ingestao import (
    IngestionCreateRequest,
    IngestionCreateResponse,
    IngestionListResponse,
    IngestionListItem,
    IngestionDetailResponse,
    LineageResponse,
    LineageNode,
    LineageEdge,
    LGPDReportResponse
)


logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ingestions", tags=["Ingestion"])


@router.post(
    "",
    response_model=IngestionCreateResponse,
    dependencies=[Depends(require_roles("admin", "gestor"))],
    summary="Create Ingestion",
)
async def create_ingestao(
    request: Request,
    file: UploadFile = File(..., description="File to ingest"),
    fonte: IngestionSource = Query(..., description="Data source"),
    metodo: IngestionMethod = Query(..., description="Ingestion method"),
    consentimento_id: Optional[UUID] = Query(None, description="LGPD consent UUID"),
    descricao: Optional[str] = Query(None, description="Description"),
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
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
        start_time = time.perf_counter()
        # Validate file size (10GB max)
        MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 10GB
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File size exceeds 10GB limit")
        
        # Validate file extension
        ALLOWED_EXTENSIONS = ['csv', 'xlsx', 'xls', 'json', 'xml', 'txt', 'parquet', 'avro', 'pdf', 'doc', 'docx']
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File extension '{file_extension}' not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Generate UUID for ingestion
        ingestao_id = uuid4()
        
        # MinIO storage path: ingestoes/{uuid}.{extension}
        storage_path = f"ingestoes/{ingestao_id}.{file_extension}"
        
        # Upload to MinIO
        minio = get_minio_client()
        minio.upload_bytes(storage_path, file_content, content_type=file.content_type)
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
            status=IngestionStatus.PROCESSANDO,
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
        ip_cliente = request.client.host if request.client else None
        created_ingestao = await ingestao_repo.create(ingestao, usuario_id=str(user["id"]), ip_cliente=ip_cliente)
        
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
        qr.add_data(f"https://prospecai.senai.br/ingestions/{ingestao_id}")
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Metrics instrumentation
        try:
            ingestoes_created_total.labels(fonte=fonte.value).inc()
            ingestoes_status.labels(status=IngestionStatus.PROCESSANDO.value).inc()
            ingestao_confiabilidade_score.labels(fonte=fonte.value).set(lgpd_result["compliance_score"])
            # PII counts
            for pii_type, entities in (lgpd_result.get("pii_detected") or {}).items():
                if entities:
                    lgpd_pii_detected_total.labels(pii_type=pii_type).inc(len(entities))
            # Consent status
            consent_status = "granted" if lgpd_result.get("consent_validation", {}).get("valid") else "missing"
            lgpd_consent_validation.labels(status=consent_status).inc()
        except Exception:
            # Avoid breaking flow on metrics failure
            pass

        # Observe processing time
        try:
            duration = time.perf_counter() - start_time
            ingestao_processing_time.labels(fonte=fonte.value).observe(duration)
        except Exception:
            pass

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
        try:
            ingestao_errors_total.inc()
        except Exception:
            pass
        logger.error("ingestao_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create ingestion: {str(e)}")


@router.get("", response_model=IngestionListResponse, summary="List Ingestions")
async def list_ingestoes(
    fonte: Optional[IngestionSource] = Query(None, description="Filter by source"),
    status: Optional[IngestionStatus] = Query(None, description="Filter by status"),
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
        
        return IngestionListResponse(
            items=[IngestionListItem.model_validate(item) for item in items],
            total=total,
            offset=offset,
            limit=limit
        )
    
    except Exception as e:
        logger.error("list_ingestoes_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list ingestions: {str(e)}")


@router.get("/{id}", response_model=IngestionDetailResponse, summary="Get Ingestion")
async def get_ingestao(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    """Get ingestion details by ID with data sample."""
    try:
        ingestao_repo = IngestaoRepository(session)
        tenant_id = user.get("tenant_id", "nacional")
        
        ingestao = await ingestao_repo.get_by_id(id, tenant_id=tenant_id)
        
        if not ingestao:
            raise HTTPException(status_code=404, detail="Ingestion not found")
        
        # Try to get a sample of the raw data from metadata
        dados_sample = None
        if ingestao.metadata_adicional and isinstance(ingestao.metadata_adicional, dict):
            dados_sample = ingestao.metadata_adicional.get("dados_sample")
        
        logger.info("ingestao_retrieved", ingestao_id=str(id))
        
        # Build response with sample data
        response_data = IngestionDetailResponse.model_validate(ingestao).model_dump()
        response_data["dados_brutos_sample"] = dados_sample
        
        return response_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_ingestao_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get ingestion: {str(e)}")


@router.get("/{id}/lineage", response_model=LineageResponse, summary="Get Lineage")
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
        nodes.append(LineageNode(
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
                nodes.append(LineageNode(
                    id=node_id,
                    type="transformation",
                    label=item.get("name", "Transformation"),
                    properties=item.get("properties", {})
                ))
                edges.append(LineageEdge(
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
        
        # Sample raw data from MinIO (if text)
        dados_sample = None
        try:
            minio = get_minio_client()
            if ingestao.arquivo_storage_path:
                dados_sample = minio.read_sample_text(ingestao.arquivo_storage_path, max_bytes=1024)
        except Exception:
            dados_sample = None

        logger.info("lineage_retrieved", ingestao_id=str(id), nodes_count=len(nodes), edges_count=len(edges))
        
        return LineageResponse(
            ingestao_id=ingestao.id,
            nodes=nodes,
            edges=edges,
            dados_brutos_sample=dados_sample,
            transformacoes=transformacoes,
            confiabilidade_score=ingestao.confiabilidade_score,
            data_ingestao=ingestao.data_ingestao
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_lineage_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get lineage: {str(e)}")


@router.get("/{id}/lgpd-report", response_model=LGPDReportResponse, summary="Get LGPD Report")
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
        
        # Count PII types and build details
        pii_types_detected = {}
        pii_details = []
        total_pii_instances = 0
        
        # Define all expected PII types for comprehensive reporting
        all_pii_types = [
            "cpf", "cnpj", "rg", "pis", "email", "phone",
            "birthdate", "address", "biometric", "person", "location", "organization"
        ]
        
        if ingestao.pii_detectado:
            for pii_type, entities in ingestao.pii_detectado.items():
                if entities and isinstance(entities, list):
                    count = len(entities)
                    pii_types_detected[pii_type] = count
                    total_pii_instances += count
                    
                    # Create masked samples (first 3)
                    samples = []
                    for entity in entities[:3]:
                        if isinstance(entity, dict) and 'value' in entity:
                            value = str(entity['value'])
                            # Mask value
                            if len(value) > 6:
                                masked = value[:3] + '*' * (len(value) - 6) + value[-3:]
                            else:
                                masked = '*' * len(value)
                            samples.append(masked)
                        elif isinstance(entity, str):
                            if len(entity) > 6:
                                masked = entity[:3] + '*' * (len(entity) - 6) + entity[-3:]
                            else:
                                masked = '*' * len(entity)
                            samples.append(masked)
                    
                    pii_details.append({
                        "type": pii_type,
                        "count": count,
                        "samples": samples,
                        "detected": True
                    })
        
        # Add explicit information for PII types NOT detected
        for pii_type in all_pii_types:
            if pii_type not in pii_types_detected:
                pii_details.append({
                    "type": pii_type,
                    "count": 0,
                    "samples": [],
                    "detected": False
                })
        
        # Get consent details
        consent_status = "missing"
        consent_records = []
        
        if ingestao.consentimento_id:
            consent_repo = ConsentimentoRepository(session)
            consent = await consent_repo.get_by_id(ingestao.consentimento_id, tenant_id=tenant_id)
            if consent:
                if consent.is_valido():
                    consent_status = "granted"
                else:
                    consent_status = "revoked"
                
                # Build consent record
                # Note: Consent model has 'finalidade' (purpose), not 'tipo'
                # Using origem_coleta as type proxy
                tipo_consentimento = consent.origem_coleta or "sistema"
                consent_records.append({
                    "tipo_consentimento": tipo_consentimento,
                    "finalidade": consent.finalidade,
                    "status": "válido" if consent.is_valido() else "revogado",
                    "data_consentimento": consent.data_consentimento,
                    "data_revogacao": consent.data_revogacao
                })
        
        # Determine risk level
        risk_level = "BAIXO"
        if ingestao.confiabilidade_score < 40:
            risk_level = "CRÍTICO"
        elif ingestao.confiabilidade_score < 60:
            risk_level = "ALTO"
        elif ingestao.confiabilidade_score < 80:
            risk_level = "MÉDIO"
        
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
        if total_pii_instances > 100:
            recommendations.append("Alto volume de dados pessoais detectados. Considerar minimização de dados.")
        
        # Determine applicable LGPD articles
        lgpd_articles = []
        if total_pii_instances > 0:
            lgpd_articles.append("Art. 6º - Princípios")
            lgpd_articles.append("Art. 7º - Bases Legais")
        if pii_types_detected.get("cpf", 0) > 0 or pii_types_detected.get("email", 0) > 0:
            lgpd_articles.append("Art. 5º - Definições")
        if not ingestao.consentimento_id:
            lgpd_articles.append("Art. 8º - Consentimento")
        if ingestao.acoes_lgpd:
            lgpd_articles.append("Art. 46º - Segurança")
        
        # Generate data analysis
        if total_pii_instances == 0:
            data_analysis = "Nenhuma instância de dados pessoais foi detectada nesta ingestão. "
            data_analysis += "Os seguintes tipos de PII foram verificados: "
            data_analysis += ", ".join(all_pii_types) + ". "
            data_analysis += "Nenhum deles foi encontrado no conteúdo analisado."
        else:
            data_analysis = f"A ingestão contém {total_pii_instances} instâncias de dados pessoais distribuídas em {len(pii_types_detected)} tipos diferentes. "
            detected_types = [pii["type"] for pii in pii_details if pii["detected"]]
            not_detected_types = [pii["type"] for pii in pii_details if not pii["detected"]]
            
            if detected_types:
                data_analysis += f"Tipos detectados: {', '.join(detected_types)}. "
            if not_detected_types:
                data_analysis += f"Tipos verificados mas não detectados: {', '.join(not_detected_types)}. "
        
        if consent_status == "granted":
            data_analysis += "O titular forneceu consentimento válido para o processamento. "
        elif consent_status == "missing":
            data_analysis += "ATENÇÃO: Não há consentimento registrado para esta ingestão. "
        else:
            data_analysis += "ATENÇÃO: O consentimento foi revogado. "
        
        data_analysis += f"O score de conformidade é {ingestao.confiabilidade_score}%, indicando nível de risco {risk_level}. "
        
        if ingestao.acoes_lgpd:
            data_analysis += f"{len(ingestao.acoes_lgpd)} ações de proteção LGPD foram aplicadas durante o processamento."
        else:
            data_analysis += "Nenhuma ação de proteção LGPD foi registrada."
        
        logger.info("lgpd_report_generated", ingestao_id=str(id), compliance_score=ingestao.confiabilidade_score)
        
        return LGPDReportResponse(
            ingestao_id=ingestao.id,
            pii_types_detected=pii_types_detected,
            pii_details=pii_details,
            total_pii_instances=total_pii_instances,
            masking_actions=ingestao.acoes_lgpd or [],
            consent_status=consent_status,
            consent_records=consent_records,
            consentimento_id=ingestao.consentimento_id,
            compliance_score=ingestao.confiabilidade_score,
            risk_level=risk_level,
            recommendations=recommendations,
            lgpd_articles_applicable=lgpd_articles,
            data_analysis=data_analysis,
            data_processamento=ingestao.data_processamento
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_lgpd_report_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get LGPD report: {str(e)}")


@router.get("/{id}/download", summary="Get Presigned Download URL")
async def get_presigned_download_url(
    id: UUID,
    expiry_minutes: int = Query(60, ge=1, le=240, description="URL expiry in minutes"),
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    """
    Return a presigned URL (private access) to download the stored file.
    Default expiry: 60 minutes.
    """
    try:
        ingestao_repo = IngestaoRepository(session)
        tenant_id = user.get("tenant_id", "nacional")
        ingestao = await ingestao_repo.get_by_id(id, tenant_id=tenant_id)

        if not ingestao or not ingestao.arquivo_storage_path:
            raise HTTPException(status_code=404, detail="File not found for this ingestion")

        minio = get_minio_client()
        url = minio.presigned_get_url(ingestao.arquivo_storage_path, expiry_minutes=expiry_minutes)

        return {"url": url, "expires_in_minutes": expiry_minutes}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("presigned_url_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate presigned URL")

@router.get("/{id}/pii", summary="Get PII Details")
async def get_pii_details(
    id: UUID,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user)
):
    """
    Get detailed PII data detected in ingestion.
    Returns masked samples for privacy.
    """
    try:
        ingestao_repo = IngestaoRepository(session)
        tenant_id = user.get("tenant_id", "nacional")
        ingestao = await ingestao_repo.get_by_id(id, tenant_id=tenant_id)
        
        if not ingestao:
            raise HTTPException(status_code=404, detail="Ingestion not found")
        
        # Define all expected PII types
        all_pii_types = [
            "cpf", "cnpj", "rg", "pis", "email", "phone",
            "birthdate", "address", "biometric", "person", "location", "organization"
        ]
        
        # Count PII types
        por_tipo = {}
        detalhes = []
        total_pii_encontrados = 0
        pii_tipos_detectados = []
        pii_tipos_nao_detectados = []
        
        if ingestao.pii_detectado:
            for pii_type, entities in ingestao.pii_detectado.items():
                if entities and isinstance(entities, list):
                    count = len(entities)
                    por_tipo[pii_type] = count
                    total_pii_encontrados += count
                    pii_tipos_detectados.append(pii_type)
                    
                    # Create masked samples (first 5)
                    exemplos_mascarados = []
                    for entity in entities[:5]:
                        if isinstance(entity, dict):
                            campo = entity.get('campo', 'unknown')
                            value = str(entity.get('value', ''))
                        elif isinstance(entity, str):
                            campo = pii_type
                            value = entity
                        else:
                            continue
                        
                        # Mask value
                        if len(value) > 6:
                            masked = value[:3] + '*' * (len(value) - 6) + value[-3:]
                        else:
                            masked = '*' * len(value)
                        exemplos_mascarados.append(masked)
                    
                    # Determine sensitivity level
                    nivel_sensibilidade = 'medio'
                    if pii_type in ['cpf', 'cnpj', 'rg', 'pis', 'biometric', 'birthdate']:
                        nivel_sensibilidade = 'alto'
                    elif pii_type in ['nome', 'email', 'telefone', 'address']:
                        nivel_sensibilidade = 'baixo'
                    
                    detalhes.append({
                        "campo": pii_type,
                        "tipo_pii": pii_type.upper(),
                        "ocorrencias": count,
                        "exemplos_mascarados": exemplos_mascarados,
                        "nivel_sensibilidade": nivel_sensibilidade,
                        "detectado": True
                    })
        
        # Add explicit information for types NOT detected
        for pii_type in all_pii_types:
            if pii_type not in pii_tipos_detectados:
                pii_tipos_nao_detectados.append(pii_type)
                
                # Determine sensitivity level
                nivel_sensibilidade = 'medio'
                if pii_type in ['cpf', 'cnpj', 'rg', 'pis', 'biometric', 'birthdate']:
                    nivel_sensibilidade = 'alto'
                elif pii_type in ['nome', 'email', 'telefone', 'address']:
                    nivel_sensibilidade = 'baixo'
                
                detalhes.append({
                    "campo": pii_type,
                    "tipo_pii": pii_type.upper(),
                    "ocorrencias": 0,
                    "exemplos_mascarados": [],
                    "nivel_sensibilidade": nivel_sensibilidade,
                    "detectado": False
                })
        
        logger.info("pii_details_retrieved", ingestao_id=str(id), total_pii=total_pii_encontrados, detected_types=len(pii_tipos_detectados), not_detected_types=len(pii_tipos_nao_detectados))
        
        return {
            "total_pii_encontrados": total_pii_encontrados,
            "tipos_verificados": len(all_pii_types),
            "tipos_detectados": len(pii_tipos_detectados),
            "tipos_nao_detectados": len(pii_tipos_nao_detectados),
            "pii_tipos_detectados": pii_tipos_detectados,
            "pii_tipos_nao_detectados": pii_tipos_nao_detectados,
            "por_tipo": por_tipo,
            "detalhes": detalhes
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_pii_details_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get PII details: {str(e)}")