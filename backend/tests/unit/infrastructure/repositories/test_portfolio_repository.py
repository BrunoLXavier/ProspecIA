"""Unit tests for Portfolio Repositories."""
from datetime import date, datetime, UTC
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.portfolio import (
    Institute,
    Project,
    Competence,
    InstituteStatus,
    ProjectStatus,
)
from app.infrastructure.repositories.portfolio_repository import (
    InstitutesRepository,
    ProjectsRepository,
    CompetencesRepository,
)


@pytest.fixture
def mock_session():
    """Mock async database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_kafka():
    """Mock Kafka producer."""
    kafka = AsyncMock()
    kafka.send_event = AsyncMock()
    return kafka


@pytest.fixture
def sample_institute():
    """Sample institute entity."""
    return Institute(
        id=uuid4(),
        name="Instituto de Pesquisa em IA",
        acronym="IPAI",
        description="Centro de excelência em Inteligência Artificial",
        website="https://ipai.org.br",
        contact_email="contato@ipai.org.br",
        contact_phone="+55 11 3333-4444",
        status=InstituteStatus.ACTIVE,
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        historico_atualizacoes=[],
        criado_por=UUID("00000000-0000-0000-0000-000000000123"),
        atualizado_por=UUID("00000000-0000-0000-0000-000000000123"),
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC),
    )


@pytest.fixture
def sample_project(sample_institute):
    """Sample project entity."""
    return Project(
        id=uuid4(),
        institute_id=sample_institute.id,
        title="Sistema de Predição de Demanda com IA",
        description="Desenvolvimento de modelo preditivo para indústria",
        objectives="Protótipo funcional Q4 2024 com acurácia >85%",
        trl=5,
        budget=80000000,  # R$800k em centavos
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        team_size=8,
        status=ProjectStatus.ACTIVE,
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        historico_atualizacoes=[],
        criado_por=UUID("00000000-0000-0000-0000-000000000123"),
        atualizado_por=UUID("00000000-0000-0000-0000-000000000123"),
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC),
    )


@pytest.fixture
def sample_competence():
    """Sample competence entity."""
    return Competence(
        id=uuid4(),
        name="Machine Learning",
        category="Inteligência Artificial",
        description="Desenvolvimento de modelos supervisionados e não-supervisionados",
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        criado_por=UUID("00000000-0000-0000-0000-000000000123"),
        criado_em=datetime.now(UTC),
    )


# =======================
# InstitutesRepository Tests
# =======================

class TestInstitutesRepositoryCreate:
    """Tests for institute create operation."""
    
    @pytest.fixture
    def institutes_repo(self, mock_session, mock_kafka):
        return InstitutesRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_create_success(self, institutes_repo, mock_session, mock_kafka, sample_institute):
        """Test successful institute creation."""
        # Arrange
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Act
        result = await institutes_repo.create(sample_institute)
        
        # Assert
        assert result == sample_institute
        mock_session.add.assert_called_once_with(sample_institute)
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()


class TestInstitutesRepositoryGet:
    """Tests for institute get operations."""
    
    @pytest.fixture
    def institutes_repo(self, mock_session, mock_kafka):
        return InstitutesRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, institutes_repo, mock_session, sample_institute):
        """Test getting institute by ID."""
        # Arrange
        tenant_id = sample_institute.tenant_id
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_institute)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await institutes_repo.get(sample_institute.id, tenant_id)
        
        # Assert
        assert result == sample_institute
        mock_session.execute.assert_called_once()


class TestInstitutesRepositoryList:
    """Tests for institute list operation."""
    
    @pytest.fixture
    def institutes_repo(self, mock_session, mock_kafka):
        return InstitutesRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_list_with_pagination(self, institutes_repo, mock_session, sample_institute):
        """Test listing institutes with pagination."""
        # Arrange
        tenant_id = sample_institute.tenant_id
        institutes = [sample_institute]
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=institutes)
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_institutes, total = await institutes_repo.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
        )
        
        # Assert
        assert result_institutes == institutes
        assert total == 1


class TestInstitutesRepositoryUpdate:
    """Tests for institute update operation."""
    
    @pytest.fixture
    def institutes_repo(self, mock_session, mock_kafka):
        return InstitutesRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_update_success(self, institutes_repo, mock_session, mock_kafka, sample_institute):
        """Test successful institute update."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_institute)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        updates = {"website": "https://new-ipai.org.br", "contact_email": "novo@ipai.org.br"}
        user_id = UUID("00000000-0000-0000-0000-000000000456")
        
        # Act
        result = await institutes_repo.update(
            sample_institute.id,
            sample_institute.tenant_id,
            updates,
            user_id,
        )
        
        # Assert
        assert result is not None
        assert len(result.historico_atualizacoes) == 2
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()


class TestInstitutesRepositoryDelete:
    """Tests for institute soft delete operation."""
    
    @pytest.fixture
    def institutes_repo(self, mock_session, mock_kafka):
        return InstitutesRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_delete_soft_success(self, institutes_repo, mock_session, mock_kafka, sample_institute):
        """Test successful soft delete."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_institute)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        
        user_id = UUID("00000000-0000-0000-0000-000000000456")
        motivo = "Instituto encerrou atividades"
        
        # Act
        result = await institutes_repo.delete(
            sample_institute.id,
            sample_institute.tenant_id,
            user_id,
            motivo,
        )
        
        # Assert
        assert result is True
        assert sample_institute.status == InstituteStatus.EXCLUDED
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()


# =======================
# ProjectsRepository Tests
# =======================

class TestProjectsRepositoryCreate:
    """Tests for project create operation."""
    
    @pytest.fixture
    def projects_repo(self, mock_session, mock_kafka):
        return ProjectsRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_create_success(self, projects_repo, mock_session, mock_kafka, sample_project):
        """Test successful project creation."""
        # Arrange
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Act
        result = await projects_repo.create(sample_project)
        
        # Assert
        assert result == sample_project
        mock_session.add.assert_called_once_with(sample_project)
        mock_kafka.send_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_validates_trl_range(self, projects_repo, sample_project):
        """Test TRL validation (1-9)."""
        # Valid TRL
        sample_project.trl = 7
        assert sample_project.trl == 7
        
        # Invalid TRL (domain should validate)
        with pytest.raises(ValueError):
            Project.validate_trl(10)


class TestProjectsRepositoryList:
    """Tests for project list operation."""
    
    @pytest.fixture
    def projects_repo(self, mock_session, mock_kafka):
        return ProjectsRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_list_with_institute_filter(self, projects_repo, mock_session, sample_project):
        """Test listing projects filtered by institute."""
        # Arrange
        tenant_id = sample_project.tenant_id
        institute_id = sample_project.institute_id
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_project])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_projects, total = await projects_repo.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            institute_id=institute_id,
        )
        
        # Assert
        assert len(result_projects) == 1
        assert result_projects[0].institute_id == institute_id
    
    @pytest.mark.asyncio
    async def test_list_with_trl_range_filter(self, projects_repo, mock_session, sample_project):
        """Test listing projects with TRL range filter."""
        # Arrange
        tenant_id = sample_project.tenant_id
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_project])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_projects, total = await projects_repo.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            min_trl=4,
            max_trl=6,
        )
        
        # Assert
        assert len(result_projects) == 1
        assert 4 <= result_projects[0].trl <= 6


class TestProjectsRepositoryUpdate:
    """Tests for project update operation."""
    
    @pytest.fixture
    def projects_repo(self, mock_session, mock_kafka):
        return ProjectsRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_update_success(self, projects_repo, mock_session, mock_kafka, sample_project):
        """Test successful project update."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_project)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        updates = {"trl": 6, "budget": 90000000}
        user_id = UUID("00000000-0000-0000-0000-000000000456")
        
        # Act
        result = await projects_repo.update(
            sample_project.id,
            sample_project.tenant_id,
            updates,
            user_id,
        )
        
        # Assert
        assert result is not None
        assert result.trl == 6
        assert len(result.historico_atualizacoes) == 2
        mock_kafka.send_event.assert_called_once()


class TestProjectsRepositoryDelete:
    """Tests for project soft delete operation."""
    
    @pytest.fixture
    def projects_repo(self, mock_session, mock_kafka):
        return ProjectsRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_delete_soft_success(self, projects_repo, mock_session, mock_kafka, sample_project):
        """Test successful soft delete."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_project)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        
        user_id = UUID("00000000-0000-0000-0000-000000000456")
        motivo = "Projeto cancelado por falta de recursos"
        
        # Act
        result = await projects_repo.delete(
            sample_project.id,
            sample_project.tenant_id,
            user_id,
            motivo,
        )
        
        # Assert
        assert result is True
        assert sample_project.status == ProjectStatus.EXCLUDED
        mock_kafka.send_event.assert_called_once()


# =======================
# CompetencesRepository Tests
# =======================

class TestCompetencesRepositoryCreate:
    """Tests for competence create operation."""
    
    @pytest.fixture
    def competences_repo(self, mock_session, mock_kafka):
        return CompetencesRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_create_success(self, competences_repo, mock_session, mock_kafka, sample_competence):
        """Test successful competence creation."""
        # Arrange
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Act
        result = await competences_repo.create(sample_competence)
        
        # Assert
        assert result == sample_competence
        mock_session.add.assert_called_once_with(sample_competence)
        mock_kafka.send_event.assert_called_once()


class TestCompetencesRepositoryList:
    """Tests for competence list operation."""
    
    @pytest.fixture
    def competences_repo(self, mock_session, mock_kafka):
        return CompetencesRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_list_all_competences(self, competences_repo, mock_session, sample_competence):
        """Test listing all competences."""
        # Arrange
        tenant_id = sample_competence.tenant_id
        competences = [sample_competence]
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=competences)
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_competences, total = await competences_repo.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
        )
        
        # Assert
        assert result_competences == competences
        assert total == 1
    
    @pytest.mark.asyncio
    async def test_list_with_category_filter(self, competences_repo, mock_session, sample_competence):
        """Test filtering competences by category."""
        # Arrange
        tenant_id = sample_competence.tenant_id
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_competence])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_competences, total = await competences_repo.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            category="Inteligência Artificial",
        )
        
        # Assert
        assert len(result_competences) == 1
        assert result_competences[0].category == "Inteligência Artificial"


class TestCompetencesRepositoryDelete:
    """Tests for competence hard delete operation."""
    
    @pytest.fixture
    def competences_repo(self, mock_session, mock_kafka):
        return CompetencesRepository(mock_session, mock_kafka)
    
    @pytest.mark.asyncio
    async def test_delete_hard_success(self, competences_repo, mock_session, mock_kafka, sample_competence):
        """Test successful hard delete (no versioning for competences)."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_competence)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.delete = AsyncMock()
        mock_session.commit = AsyncMock()
        
        # Act
        result = await competences_repo.delete(
            sample_competence.id,
            sample_competence.tenant_id,
        )
        
        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(sample_competence)
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()
