"""Unit tests for InteractionsRepository."""
from datetime import datetime, UTC
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interaction import Interaction, InteractionType, InteractionOutcome, InteractionStatus
from app.infrastructure.repositories.interactions_repository import InteractionsRepository


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
    return InteractionsRepository(mock_session, mock_kafka)


@pytest.fixture
def sample_interaction():
    """Sample interaction entity."""
    return Interaction(
        id=uuid4(),
        client_id=uuid4(),
        title="Reunião de alinhamento técnico",
        description="Discussão sobre requisitos do projeto de IA",
        type=InteractionType.MEETING,
        date=datetime.now(UTC),
        participants=["João Silva", "Maria Santos", "Pedro Costa"],
        outcome=InteractionOutcome.POSITIVE,
        next_steps="Enviar proposta técnica até sexta-feira",
        status=InteractionStatus.COMPLETED,
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        criado_por=UUID("00000000-0000-0000-0000-000000000123"),
        criado_em=datetime.now(UTC),
    )


class TestInteractionsRepositoryCreate:
    """Tests for create operation."""
    
    @pytest.mark.asyncio
    async def test_create_success(self, repository, mock_session, mock_kafka, sample_interaction):
        """Test successful interaction creation."""
        # Arrange
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Act
        result = await repository.create(sample_interaction)
        
        # Assert
        assert result == sample_interaction
        mock_session.add.assert_called_once_with(sample_interaction)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_interaction)
        mock_kafka.send_event.assert_called_once()
        
        # Verify Kafka event
        kafka_call = mock_kafka.send_event.call_args
        assert kafka_call.kwargs["event_type"] == "interaction.created"
        assert kafka_call.kwargs["entity_id"] == str(sample_interaction.id)
    
    @pytest.mark.asyncio
    async def test_create_with_participants_list(self, repository, sample_interaction):
        """Test creating interaction with participants."""
        # Assert participants are stored as list
        assert isinstance(sample_interaction.participants, list)
        assert len(sample_interaction.participants) == 3
        assert "João Silva" in sample_interaction.participants


class TestInteractionsRepositoryGet:
    """Tests for get operations."""
    
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_interaction):
        """Test getting interaction by ID when found."""
        # Arrange
        tenant_id = sample_interaction.tenant_id
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_interaction)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.get(sample_interaction.id, tenant_id)
        
        # Assert
        assert result == sample_interaction
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting non-existent interaction."""
        # Arrange
        tenant_id = UUID("00000000-0000-0000-0000-000000000001")
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.get(uuid4(), tenant_id)
        
        # Assert
        assert result is None


class TestInteractionsRepositoryListByClient:
    """Tests for list_by_client operation (timeline)."""
    
    @pytest.mark.asyncio
    async def test_list_by_client_ordered_by_date(self, repository, mock_session, sample_interaction):
        """Test listing interactions for a client ordered by date desc."""
        # Arrange
        client_id = sample_interaction.client_id
        tenant_id = sample_interaction.tenant_id
        
        # Create multiple interactions with different dates
        interaction1 = sample_interaction
        interaction2 = Interaction(
            id=uuid4(),
            client_id=client_id,
            title="Follow-up por email",
            description="Envio de proposta",
            type=InteractionType.EMAIL,
            date=datetime.now(UTC),
            participants=["Maria Santos"],
            outcome=InteractionOutcome.POSITIVE,
            status=InteractionStatus.COMPLETED,
            tenant_id=tenant_id,
            criado_por=UUID("00000000-0000-0000-0000-000000000123"),
            criado_em=datetime.now(UTC),
        )
        
        interactions = [interaction2, interaction1]  # Ordered by date desc
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=interactions)
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=2)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_interactions, total = await repository.list_by_client(
            client_id=client_id,
            tenant_id=tenant_id,
            skip=0,
            limit=10,
        )
        
        # Assert
        assert len(result_interactions) == 2
        assert total == 2
        # Verify order (most recent first)
        assert result_interactions[0].id == interaction2.id
        assert result_interactions[1].id == interaction1.id
    
    @pytest.mark.asyncio
    async def test_list_by_client_with_type_filter(self, repository, mock_session, sample_interaction):
        """Test filtering interactions by type."""
        # Arrange
        client_id = sample_interaction.client_id
        tenant_id = sample_interaction.tenant_id
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_interaction])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_interactions, total = await repository.list_by_client(
            client_id=client_id,
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            interaction_type=InteractionType.MEETING,
        )
        
        # Assert
        assert len(result_interactions) == 1
        assert result_interactions[0].type == InteractionType.MEETING
    
    @pytest.mark.asyncio
    async def test_list_by_client_with_pagination(self, repository, mock_session, sample_interaction):
        """Test pagination in client timeline."""
        # Arrange
        client_id = sample_interaction.client_id
        tenant_id = sample_interaction.tenant_id
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_interaction])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=25)  # Total 25, page size 10
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act - get page 2
        result_interactions, total = await repository.list_by_client(
            client_id=client_id,
            tenant_id=tenant_id,
            skip=10,
            limit=10,
        )
        
        # Assert
        assert total == 25
        assert len(result_interactions) == 1


class TestInteractionsRepositoryList:
    """Tests for general list operation."""
    
    @pytest.mark.asyncio
    async def test_list_all_interactions(self, repository, mock_session, sample_interaction):
        """Test listing all interactions with pagination."""
        # Arrange
        tenant_id = sample_interaction.tenant_id
        interactions = [sample_interaction]
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=interactions)
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_interactions, total = await repository.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
        )
        
        # Assert
        assert result_interactions == interactions
        assert total == 1


class TestInteractionsRepositoryUpdate:
    """Tests for update operation."""
    
    @pytest.mark.asyncio
    async def test_update_success(self, repository, mock_session, mock_kafka, sample_interaction):
        """Test successful interaction update."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_interaction)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        updates = {
            "outcome": InteractionOutcome.NEUTRAL,
            "next_steps": "Aguardar retorno do cliente",
        }
        
        # Act
        result = await repository.update(
            sample_interaction.id,
            sample_interaction.tenant_id,
            updates,
        )
        
        # Assert
        assert result is not None
        assert result.outcome == InteractionOutcome.NEUTRAL
        assert result.next_steps == "Aguardar retorno do cliente"
        
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_not_found(self, repository, mock_session):
        """Test updating non-existent interaction."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.update(
            uuid4(),
            UUID("00000000-0000-0000-0000-000000000001"),
            {"title": "New Title"},
        )
        
        # Assert
        assert result is None


class TestInteractionsRepositoryDelete:
    """Tests for delete (soft delete) operation."""
    
    @pytest.mark.asyncio
    async def test_delete_soft_success(self, repository, mock_session, mock_kafka, sample_interaction):
        """Test successful soft delete."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_interaction)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        
        # Act
        result = await repository.delete(
            sample_interaction.id,
            sample_interaction.tenant_id,
        )
        
        # Assert
        assert result is True
        assert sample_interaction.status == InteractionStatus.CANCELLED
        
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository, mock_session):
        """Test deleting non-existent interaction."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.delete(
            uuid4(),
            UUID("00000000-0000-0000-0000-000000000001"),
        )
        
        # Assert
        assert result is False


class TestInteractionsRepositoryFilters:
    """Tests for various filters."""
    
    @pytest.mark.asyncio
    async def test_filter_by_outcome(self, repository, mock_session, sample_interaction):
        """Test filtering by outcome."""
        # Arrange
        tenant_id = sample_interaction.tenant_id
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_interaction])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_interactions, total = await repository.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            outcome=InteractionOutcome.POSITIVE,
        )
        
        # Assert
        assert len(result_interactions) == 1
        assert result_interactions[0].outcome == InteractionOutcome.POSITIVE
    
    @pytest.mark.asyncio
    async def test_filter_by_status(self, repository, mock_session, sample_interaction):
        """Test filtering by status."""
        # Arrange
        tenant_id = sample_interaction.tenant_id
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_interaction])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_interactions, total = await repository.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            status=InteractionStatus.COMPLETED,
        )
        
        # Assert
        assert len(result_interactions) == 1
        assert result_interactions[0].status == InteractionStatus.COMPLETED
