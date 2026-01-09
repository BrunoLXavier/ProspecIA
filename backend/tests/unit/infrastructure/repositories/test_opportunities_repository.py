"""Unit tests for OpportunitiesRepository."""
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.opportunity import Opportunity, OpportunityStage, OpportunityStatus
from app.infrastructure.repositories.opportunities_repository import OpportunitiesRepository


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
def repository(mock_session, mock_kafka):
    """Create repository instance with mocks."""
    return OpportunitiesRepository(mock_session, mock_kafka)


@pytest.fixture
def sample_opportunity():
    """Sample opportunity entity."""
    return Opportunity(
        id=uuid4(),
        client_id=uuid4(),
        funding_source_id=uuid4(),
        title="Projeto IA para Indústria 4.0",
        description="Desenvolvimento de sistema de manutenção preditiva com IA",
        stage=OpportunityStage.VALIDATION,
        score=75,
        estimated_value=50000000,  # R$500k em centavos
        probability=60,
        expected_close_date=datetime.now(UTC) + timedelta(days=60),
        responsible_user_id=UUID("00000000-0000-0000-0000-000000000123"),
        status=OpportunityStatus.ACTIVE,
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        historico_atualizacoes=[],
        historico_transicoes=[],
        criado_por=UUID("00000000-0000-0000-0000-000000000123"),
        atualizado_por=UUID("00000000-0000-0000-0000-000000000123"),
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC),
    )


class TestOpportunitiesRepositoryCreate:
    """Tests for create operation."""
    
    @pytest.mark.asyncio
    async def test_create_success(self, repository, mock_session, mock_kafka, sample_opportunity):
        """Test successful opportunity creation."""
        # Arrange
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Act
        result = await repository.create(sample_opportunity)
        
        # Assert
        assert result == sample_opportunity
        mock_session.add.assert_called_once_with(sample_opportunity)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_opportunity)
        mock_kafka.send_event.assert_called_once()
        
        # Verify Kafka event
        kafka_call = mock_kafka.send_event.call_args
        assert kafka_call.kwargs["event_type"] == "opportunity.created"
        assert kafka_call.kwargs["entity_id"] == str(sample_opportunity.id)
    
    @pytest.mark.asyncio
    async def test_create_validates_score_range(self, repository, sample_opportunity):
        """Test score validation (0-100)."""
        # Valid range
        sample_opportunity.score = 85
        assert sample_opportunity.score == 85
        
        # Invalid range should be caught by domain validation
        with pytest.raises(ValueError):
            sample_opportunity.score = 150


class TestOpportunitiesRepositoryGet:
    """Tests for get operations."""
    
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_opportunity):
        """Test getting opportunity by ID when found."""
        # Arrange
        tenant_id = sample_opportunity.tenant_id
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_opportunity)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.get(sample_opportunity.id, tenant_id)
        
        # Assert
        assert result == sample_opportunity
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_filters_by_status(self, repository, mock_session, sample_opportunity):
        """Test get filters excluded opportunities."""
        # Arrange
        sample_opportunity.status = OpportunityStatus.EXCLUDED
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.get(sample_opportunity.id, sample_opportunity.tenant_id)
        
        # Assert
        assert result is None


class TestOpportunitiesRepositoryList:
    """Tests for list operation with filters."""
    
    @pytest.mark.asyncio
    async def test_list_with_pagination(self, repository, mock_session, sample_opportunity):
        """Test listing opportunities with pagination."""
        # Arrange
        tenant_id = sample_opportunity.tenant_id
        opportunities = [sample_opportunity]
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=opportunities)
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_opportunities, total = await repository.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
        )
        
        # Assert
        assert result_opportunities == opportunities
        assert total == 1
    
    @pytest.mark.asyncio
    async def test_list_with_stage_filter(self, repository, mock_session, sample_opportunity):
        """Test filtering by stage (for Kanban view)."""
        # Arrange
        tenant_id = sample_opportunity.tenant_id
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_opportunity])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_opportunities, total = await repository.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            stage=OpportunityStage.VALIDATION,
        )
        
        # Assert
        assert len(result_opportunities) == 1
        assert result_opportunities[0].stage == OpportunityStage.VALIDATION
    
    @pytest.mark.asyncio
    async def test_list_with_client_filter(self, repository, mock_session, sample_opportunity):
        """Test filtering by client."""
        # Arrange
        tenant_id = sample_opportunity.tenant_id
        client_id = sample_opportunity.client_id
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_opportunity])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_opportunities, total = await repository.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            client_id=client_id,
        )
        
        # Assert
        assert len(result_opportunities) == 1
        assert result_opportunities[0].client_id == client_id
    
    @pytest.mark.asyncio
    async def test_list_with_score_range_filter(self, repository, mock_session, sample_opportunity):
        """Test filtering by score range."""
        # Arrange
        tenant_id = sample_opportunity.tenant_id
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_opportunity])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_opportunities, total = await repository.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            min_score=70,
            max_score=80,
        )
        
        # Assert
        assert len(result_opportunities) == 1
        assert 70 <= result_opportunities[0].score <= 80


class TestOpportunitiesRepositoryUpdate:
    """Tests for update operation."""
    
    @pytest.mark.asyncio
    async def test_update_success(self, repository, mock_session, mock_kafka, sample_opportunity):
        """Test successful opportunity update."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_opportunity)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        updates = {"score": 85, "probability": 75}
        user_id = UUID("00000000-0000-0000-0000-000000000456")
        
        # Act
        result = await repository.update(
            sample_opportunity.id,
            sample_opportunity.tenant_id,
            updates,
            user_id,
        )
        
        # Assert
        assert result is not None
        assert result.score == 85
        assert result.probability == 75
        assert len(result.historico_atualizacoes) == 1
        
        # Verify history entry
        history = result.historico_atualizacoes[0]
        assert history["usuario_id"] == str(user_id)
        assert history["campos"] == updates
        
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()


class TestOpportunitiesRepositoryTransitionStage:
    """Tests for stage transition (human-in-the-loop)."""
    
    @pytest.mark.asyncio
    async def test_transition_stage_success(self, repository, mock_session, mock_kafka, sample_opportunity):
        """Test successful stage transition."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_opportunity)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        new_stage = OpportunityStage.APPROACH
        user_id = UUID("00000000-0000-0000-0000-000000000456")
        reason = "Cliente demonstrou interesse após apresentação"
        
        # Act
        result = await repository.transition_stage(
            sample_opportunity.id,
            sample_opportunity.tenant_id,
            new_stage,
            user_id,
            reason,
        )
        
        # Assert
        assert result is not None
        assert result.stage == new_stage
        assert len(result.historico_transicoes) == 1
        
        # Verify transition history
        transition = result.historico_transicoes[0]
        assert transition["from_stage"] == OpportunityStage.VALIDATION.value
        assert transition["to_stage"] == new_stage.value
        assert transition["usuario_id"] == str(user_id)
        assert transition["motivo"] == reason
        
        # Verify general history also updated
        assert len(result.historico_atualizacoes) == 1
        
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()
        
        # Verify Kafka event for transition
        kafka_call = mock_kafka.send_event.call_args
        assert kafka_call.kwargs["event_type"] == "opportunity.stage_transition"
    
    @pytest.mark.asyncio
    async def test_transition_stage_invalid(self, repository, sample_opportunity):
        """Test invalid stage transition."""
        # Arrange - VALIDATION can't go directly to CONVERSION
        new_stage = OpportunityStage.CONVERSION
        
        # Should be validated by domain logic
        assert not sample_opportunity.can_transition_to(new_stage)
    
    @pytest.mark.asyncio
    async def test_transition_tracks_dual_history(self, repository, mock_session, sample_opportunity):
        """Test that transition is tracked in both histories."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_opportunity)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Act
        await repository.transition_stage(
            sample_opportunity.id,
            sample_opportunity.tenant_id,
            OpportunityStage.APPROACH,
            UUID("00000000-0000-0000-0000-000000000123"),
            "Test transition",
        )
        
        # Assert - both histories should be updated
        assert len(sample_opportunity.historico_transicoes) == 1
        assert len(sample_opportunity.historico_atualizacoes) == 1
        
        # Verify historico_atualizacoes contains stage change
        update_history = sample_opportunity.historico_atualizacoes[0]
        assert "stage" in update_history["campos"]


class TestOpportunitiesRepositoryDelete:
    """Tests for delete (soft delete) operation."""
    
    @pytest.mark.asyncio
    async def test_delete_soft_success(self, repository, mock_session, mock_kafka, sample_opportunity):
        """Test successful soft delete."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_opportunity)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        
        user_id = UUID("00000000-0000-0000-0000-000000000456")
        motivo = "Oportunidade perdida para concorrente"
        
        # Act
        result = await repository.delete(
            sample_opportunity.id,
            sample_opportunity.tenant_id,
            user_id,
            motivo,
        )
        
        # Assert
        assert result is True
        assert sample_opportunity.status == OpportunityStatus.EXCLUDED
        assert len(sample_opportunity.historico_atualizacoes) == 1
        
        # Verify history
        history = sample_opportunity.historico_atualizacoes[0]
        assert history["usuario_id"] == str(user_id)
        assert history["acao"] == "exclusao"
        assert history["motivo"] == motivo
        
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()


class TestOpportunitiesRepositoryGetTransitions:
    """Tests for retrieving transition history."""
    
    @pytest.mark.asyncio
    async def test_get_transitions_success(self, repository, mock_session, sample_opportunity):
        """Test retrieving transition history."""
        # Arrange
        sample_opportunity.historico_transicoes = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "from_stage": OpportunityStage.INTELLIGENCE.value,
                "to_stage": OpportunityStage.VALIDATION.value,
                "usuario_id": str(uuid4()),
                "motivo": "Dados suficientes coletados",
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "from_stage": OpportunityStage.VALIDATION.value,
                "to_stage": OpportunityStage.APPROACH.value,
                "usuario_id": str(uuid4()),
                "motivo": "Cliente qualificado",
            },
        ]
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_opportunity)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        transitions = await repository.get_transitions(
            sample_opportunity.id,
            sample_opportunity.tenant_id,
        )
        
        # Assert
        assert transitions is not None
        assert len(transitions) == 2
        assert transitions[0]["from_stage"] == OpportunityStage.INTELLIGENCE.value
        assert transitions[1]["to_stage"] == OpportunityStage.APPROACH.value


class TestOpportunitiesRepositoryHistory:
    """Tests for general history retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_history_success(self, repository, mock_session, sample_opportunity):
        """Test retrieving opportunity history."""
        # Arrange
        sample_opportunity.historico_atualizacoes = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "usuario_id": str(uuid4()),
                "acao": "atualizacao",
                "campos": {"score": 70},
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "usuario_id": str(uuid4()),
                "acao": "atualizacao",
                "campos": {"probability": 65},
            },
        ]
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_opportunity)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        history = await repository.get_history(
            sample_opportunity.id,
            sample_opportunity.tenant_id,
        )
        
        # Assert
        assert history is not None
        assert len(history) == 2
