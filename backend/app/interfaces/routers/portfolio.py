"""REST API router for Portfolio (RF-03)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from prometheus_client import Counter, Histogram
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.kafka.producer import KafkaProducerAdapter, get_kafka_producer
from app.domain.portfolio import InstituteStatus, ProjectStatus
from app.infrastructure.database import get_async_session
from app.infrastructure.repositories.portfolio_repository import (
    CompetencesRepository,
    InstitutesRepository,
    ProjectsRepository,
)
from app.interfaces.schemas.portfolio import (
    CompetenceCreate,
    CompetenceListResponse,
    CompetenceResponse,
    InstituteCreate,
    InstituteListResponse,
    InstituteResponse,
    InstituteUpdate,
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

# Prometheus metrics
institutes_created_total = Counter("institutes_created_total", "Total institutes created")
institutes_updated_total = Counter("institutes_updated_total", "Total institutes updated")
projects_created_total = Counter("projects_created_total", "Total projects created")
projects_updated_total = Counter("projects_updated_total", "Total projects updated")
competences_created_total = Counter("competences_created_total", "Total competences created")
portfolio_request_duration_seconds = Histogram(
    "portfolio_request_duration_seconds", "Request duration for portfolio endpoints"
)


async def get_institutes_repository(
    session: AsyncSession = Depends(get_async_session),
    kafka_producer: KafkaProducerAdapter = Depends(get_kafka_producer),
) -> InstitutesRepository:
    """Dependency injection for institutes repository."""
    return InstitutesRepository(session, kafka_producer)


async def get_projects_repository(
    session: AsyncSession = Depends(get_async_session),
    kafka_producer: KafkaProducerAdapter = Depends(get_kafka_producer),
) -> ProjectsRepository:
    """Dependency injection for projects repository."""
    return ProjectsRepository(session, kafka_producer)


async def get_competences_repository(
    session: AsyncSession = Depends(get_async_session),
    kafka_producer: KafkaProducerAdapter = Depends(get_kafka_producer),
) -> CompetencesRepository:
    """Dependency injection for competences repository."""
    return CompetencesRepository(session, kafka_producer)


async def get_current_user() -> dict:
    """Placeholder for ACL user extraction (Wave 3)."""
    return {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "tenant_id": UUID("00000000-0000-0000-0000-000000000001"),
    }


async def require_portfolio_write():
    """ACL placeholder: check write permission for portfolio."""
    pass


async def require_portfolio_read():
    """ACL placeholder: check read permission for portfolio."""
    pass


# ==================== Institutes ====================


@router.post(
    "/institutes",
    response_model=InstituteResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_portfolio_write)],
)
@portfolio_request_duration_seconds.time()
async def create_institute(
    data: InstituteCreate,
    repository: InstitutesRepository = Depends(get_institutes_repository),
    current_user: dict = Depends(get_current_user),
):
    """Create a new institute."""
    from datetime import datetime
    from uuid import uuid4

    from app.domain.portfolio import Institute

    institute = Institute(
        id=uuid4(),
        name=data.name,
        acronym=data.acronym,
        description=data.description,
        website=data.website,
        contact_email=data.contact_email,
        contact_phone=data.contact_phone,
        status=InstituteStatus.ACTIVE,
        tenant_id=current_user["tenant_id"],
        historico_atualizacoes=[],
        criado_por=current_user["id"],
        atualizado_por=current_user["id"],
        criado_em=datetime.now(datetime.UTC),
        atualizado_em=datetime.now(datetime.UTC),
    )

    created = await repository.create(institute)
    institutes_created_total.inc()

    return created


@router.get(
    "/institutes",
    response_model=InstituteListResponse,
    dependencies=[Depends(require_portfolio_read)],
)
@portfolio_request_duration_seconds.time()
async def list_institutes(
    status: Optional[InstituteStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in name/description"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Max results per page"),
    repository: InstitutesRepository = Depends(get_institutes_repository),
    current_user: dict = Depends(get_current_user),
):
    """List institutes with filters and pagination."""
    institutes, total = await repository.list(
        tenant_id=current_user["tenant_id"],
        status=status,
        search=search,
        skip=skip,
        limit=limit,
    )

    return InstituteListResponse(items=institutes, total=total, skip=skip, limit=limit)


@router.get(
    "/institutes/{institute_id}",
    response_model=InstituteResponse,
    dependencies=[Depends(require_portfolio_read)],
)
@portfolio_request_duration_seconds.time()
async def get_institute(
    institute_id: UUID,
    repository: InstitutesRepository = Depends(get_institutes_repository),
    current_user: dict = Depends(get_current_user),
):
    """Get institute by ID."""
    institute = await repository.find_by_id(institute_id, current_user["tenant_id"])

    if not institute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institute not found")

    return institute


@router.patch(
    "/institutes/{institute_id}",
    response_model=InstituteResponse,
    dependencies=[Depends(require_portfolio_write)],
)
@portfolio_request_duration_seconds.time()
async def update_institute(
    institute_id: UUID,
    data: InstituteUpdate,
    repository: InstitutesRepository = Depends(get_institutes_repository),
    current_user: dict = Depends(get_current_user),
):
    """Update institute."""
    updates = data.model_dump(exclude_unset=True, exclude={"motivo"})

    updated = await repository.update(
        institute_id=institute_id,
        tenant_id=current_user["tenant_id"],
        updates=updates,
        updated_by=current_user["id"],
        motivo=data.motivo,
    )

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institute not found")

    institutes_updated_total.inc()
    return updated


@router.delete(
    "/institutes/{institute_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_portfolio_write)],
)
@portfolio_request_duration_seconds.time()
async def delete_institute(
    institute_id: UUID,
    motivo: str = Query(..., min_length=1, description="Reason for deletion"),
    repository: InstitutesRepository = Depends(get_institutes_repository),
    current_user: dict = Depends(get_current_user),
):
    """Soft delete an institute."""
    success = await repository.soft_delete(
        institute_id=institute_id,
        tenant_id=current_user["tenant_id"],
        deleted_by=current_user["id"],
        motivo=motivo,
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institute not found")


# ==================== Projects ====================


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_portfolio_write)],
)
@portfolio_request_duration_seconds.time()
async def create_project(
    data: ProjectCreate,
    repository: ProjectsRepository = Depends(get_projects_repository),
    current_user: dict = Depends(get_current_user),
):
    """Create a new project."""
    from datetime import datetime
    from uuid import uuid4

    from app.domain.portfolio import Project

    project = Project(
        id=uuid4(),
        institute_id=data.institute_id,
        title=data.title,
        description=data.description,
        objectives=data.objectives,
        trl=data.trl,
        budget=data.budget,
        start_date=data.start_date,
        end_date=data.end_date,
        team_size=data.team_size,
        status=ProjectStatus.PLANNING,
        tenant_id=current_user["tenant_id"],
        historico_atualizacoes=[],
        criado_por=current_user["id"],
        atualizado_por=current_user["id"],
        criado_em=datetime.now(datetime.UTC),
        atualizado_em=datetime.now(datetime.UTC),
    )

    created = await repository.create(project)
    projects_created_total.inc()

    return created


@router.get(
    "/projects", response_model=ProjectListResponse, dependencies=[Depends(require_portfolio_read)]
)
@portfolio_request_duration_seconds.time()
async def list_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filter by status"),
    institute_id: Optional[UUID] = Query(None, description="Filter by institute"),
    trl_min: Optional[int] = Query(None, ge=1, le=9, description="Minimum TRL"),
    trl_max: Optional[int] = Query(None, ge=1, le=9, description="Maximum TRL"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Max results per page"),
    repository: ProjectsRepository = Depends(get_projects_repository),
    current_user: dict = Depends(get_current_user),
):
    """List projects with filters and pagination."""
    projects, total = await repository.list(
        tenant_id=current_user["tenant_id"],
        status=status,
        institute_id=institute_id,
        trl_min=trl_min,
        trl_max=trl_max,
        skip=skip,
        limit=limit,
    )

    return ProjectListResponse(items=projects, total=total, skip=skip, limit=limit)


@router.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    dependencies=[Depends(require_portfolio_read)],
)
@portfolio_request_duration_seconds.time()
async def get_project(
    project_id: UUID,
    repository: ProjectsRepository = Depends(get_projects_repository),
    current_user: dict = Depends(get_current_user),
):
    """Get project by ID."""
    project = await repository.find_by_id(project_id, current_user["tenant_id"])

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return project


@router.patch(
    "/projects/{project_id}",
    response_model=ProjectResponse,
    dependencies=[Depends(require_portfolio_write)],
)
@portfolio_request_duration_seconds.time()
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    repository: ProjectsRepository = Depends(get_projects_repository),
    current_user: dict = Depends(get_current_user),
):
    """Update project."""
    updates = data.model_dump(exclude_unset=True, exclude={"motivo"})

    updated = await repository.update(
        project_id=project_id,
        tenant_id=current_user["tenant_id"],
        updates=updates,
        updated_by=current_user["id"],
        motivo=data.motivo,
    )

    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    projects_updated_total.inc()
    return updated


@router.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_portfolio_write)],
)
@portfolio_request_duration_seconds.time()
async def delete_project(
    project_id: UUID,
    motivo: str = Query(..., min_length=1, description="Reason for deletion"),
    repository: ProjectsRepository = Depends(get_projects_repository),
    current_user: dict = Depends(get_current_user),
):
    """Soft delete a project."""
    success = await repository.soft_delete(
        project_id=project_id,
        tenant_id=current_user["tenant_id"],
        deleted_by=current_user["id"],
        motivo=motivo,
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")


# ==================== Competences ====================


@router.post(
    "/competences",
    response_model=CompetenceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_portfolio_write)],
)
@portfolio_request_duration_seconds.time()
async def create_competence(
    data: CompetenceCreate,
    repository: CompetencesRepository = Depends(get_competences_repository),
    current_user: dict = Depends(get_current_user),
):
    """Create a new competence."""
    from datetime import datetime
    from uuid import uuid4

    from app.domain.portfolio import Competence

    competence = Competence(
        id=uuid4(),
        name=data.name,
        category=data.category,
        description=data.description,
        tenant_id=current_user["tenant_id"],
        criado_por=current_user["id"],
        criado_em=datetime.now(datetime.UTC),
    )

    created = await repository.create(competence)
    competences_created_total.inc()

    return created


@router.get(
    "/competences",
    response_model=CompetenceListResponse,
    dependencies=[Depends(require_portfolio_read)],
)
@portfolio_request_duration_seconds.time()
async def list_competences(
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Max results per page"),
    repository: CompetencesRepository = Depends(get_competences_repository),
    current_user: dict = Depends(get_current_user),
):
    """List competences with filters and pagination."""
    competences, total = await repository.list(
        tenant_id=current_user["tenant_id"],
        category=category,
        skip=skip,
        limit=limit,
    )

    return CompetenceListResponse(items=competences, total=total, skip=skip, limit=limit)


@router.get(
    "/competences/{competence_id}",
    response_model=CompetenceResponse,
    dependencies=[Depends(require_portfolio_read)],
)
@portfolio_request_duration_seconds.time()
async def get_competence(
    competence_id: UUID,
    repository: CompetencesRepository = Depends(get_competences_repository),
    current_user: dict = Depends(get_current_user),
):
    """Get competence by ID."""
    competence = await repository.find_by_id(competence_id, current_user["tenant_id"])

    if not competence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competence not found")

    return competence


@router.delete(
    "/competences/{competence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_portfolio_write)],
)
@portfolio_request_duration_seconds.time()
async def delete_competence(
    competence_id: UUID,
    repository: CompetencesRepository = Depends(get_competences_repository),
    current_user: dict = Depends(get_current_user),
):
    """Hard delete a competence (catalog item)."""
    success = await repository.delete(
        competence_id=competence_id,
        tenant_id=current_user["tenant_id"],
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competence not found")
