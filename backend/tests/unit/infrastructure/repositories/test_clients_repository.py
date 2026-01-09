"""Unit tests for ClientsRepository."""
from datetime import datetime, UTC
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.client import Client, ClientStatus, ClientMaturity
from app.infrastructure.repositories.clients_repository import ClientsRepository


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
    return ClientsRepository(mock_session, mock_kafka)


@pytest.fixture
def sample_client():
    """Sample client entity."""
    return Client(
        id=uuid4(),
        name="TechCorp Ltda",
        cnpj="12345678000195",
        email="contato@techcorp.com.br",
        phone="+55 11 98765-4321",
        website="https://techcorp.com.br",
        address="Av. Paulista, 1000 - São Paulo, SP",
        maturity=ClientMaturity.LEAD,
        notes="Cliente potencial para projeto de IA",
        status=ClientStatus.ACTIVE,
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        historico_atualizacoes=[],
        criado_por=UUID("00000000-0000-0000-0000-000000000123"),
        atualizado_por=UUID("00000000-0000-0000-0000-000000000123"),
        criado_em=datetime.now(UTC),
        atualizado_em=datetime.now(UTC),
    )


class TestClientsRepositoryCreate:
    """Tests for create operation."""
    
    @pytest.mark.asyncio
    async def test_create_success(self, repository, mock_session, mock_kafka, sample_client):
        """Test successful client creation."""
        # Arrange
        mock_session.add = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Act
        result = await repository.create(sample_client)
        
        # Assert
        assert result == sample_client
        mock_session.add.assert_called_once_with(sample_client)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_client)
        mock_kafka.send_event.assert_called_once()
        
        # Verify Kafka event
        kafka_call = mock_kafka.send_event.call_args
        assert kafka_call.kwargs["event_type"] == "client.created"
        assert kafka_call.kwargs["entity_id"] == str(sample_client.id)
        assert kafka_call.kwargs["tenant_id"] == str(sample_client.tenant_id)
    
    @pytest.mark.asyncio
    async def test_create_validates_cnpj(self, repository, sample_client):
        """Test CNPJ validation during creation."""
        # Invalid CNPJ (13 digits)
        sample_client.cnpj = "1234567800019"
        
        # Should raise validation error from domain
        with pytest.raises(ValueError, match="CNPJ deve ter 14 dígitos"):
            Client.validate_cnpj(sample_client.cnpj)


class TestClientsRepositoryGet:
    """Tests for get operations."""
    
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, mock_session, sample_client):
        """Test getting client by ID when found."""
        # Arrange
        tenant_id = sample_client.tenant_id
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_client)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.get(sample_client.id, tenant_id)
        
        # Assert
        assert result == sample_client
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_session):
        """Test getting non-existent client."""
        # Arrange
        tenant_id = UUID("00000000-0000-0000-0000-000000000001")
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.get(uuid4(), tenant_id)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_filters_by_status(self, repository, mock_session, sample_client):
        """Test get filters excluded clients."""
        # Arrange
        sample_client.status = ClientStatus.EXCLUDED
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.get(sample_client.id, sample_client.tenant_id)
        
        # Assert
        assert result is None


class TestClientsRepositoryList:
    """Tests for list operation."""
    
    @pytest.mark.asyncio
    async def test_list_with_pagination(self, repository, mock_session, sample_client):
        """Test listing clients with pagination."""
        # Arrange
        tenant_id = sample_client.tenant_id
        clients = [sample_client]
        total = 1
        
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=clients)
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=total)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_clients, result_total = await repository.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
        )
        
        # Assert
        assert result_clients == clients
        assert result_total == total
        assert mock_session.execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_list_with_search(self, repository, mock_session, sample_client):
        """Test listing with search filter."""
        # Arrange
        tenant_id = sample_client.tenant_id
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_client])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_clients, total = await repository.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            search="TechCorp",
        )
        
        # Assert
        assert len(result_clients) == 1
        assert total == 1
    
    @pytest.mark.asyncio
    async def test_list_with_maturity_filter(self, repository, mock_session, sample_client):
        """Test listing with maturity filter."""
        # Arrange
        tenant_id = sample_client.tenant_id
        mock_scalars = AsyncMock()
        mock_scalars.all = AsyncMock(return_value=[sample_client])
        
        mock_count_result = AsyncMock()
        mock_count_result.scalar = AsyncMock(return_value=1)
        
        mock_session.execute = AsyncMock(side_effect=[
            AsyncMock(scalars=AsyncMock(return_value=mock_scalars)),
            mock_count_result,
        ])
        
        # Act
        result_clients, total = await repository.list(
            tenant_id=tenant_id,
            skip=0,
            limit=10,
            maturity=ClientMaturity.LEAD,
        )
        
        # Assert
        assert len(result_clients) == 1
        assert result_clients[0].maturity == ClientMaturity.LEAD


class TestClientsRepositoryUpdate:
    """Tests for update operation."""
    
    @pytest.mark.asyncio
    async def test_update_success(self, repository, mock_session, mock_kafka, sample_client):
        """Test successful client update."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_client)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        updates = {"name": "TechCorp Inovação Ltda", "phone": "+55 11 99999-8888"}
        user_id = UUID("00000000-0000-0000-0000-000000000456")
        
        # Act
        result = await repository.update(
            sample_client.id,
            sample_client.tenant_id,
            updates,
            user_id,
        )
        
        # Assert
        assert result is not None
        assert result.name == "TechCorp Inovação Ltda"
        assert result.atualizado_por == user_id
        assert len(result.historico_atualizacoes) == 1
        
        # Verify history entry
        history = result.historico_atualizacoes[0]
        assert history["usuario_id"] == str(user_id)
        assert history["campos"] == updates
        
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_not_found(self, repository, mock_session):
        """Test updating non-existent client."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.update(
            uuid4(),
            UUID("00000000-0000-0000-0000-000000000001"),
            {"name": "New Name"},
            UUID("00000000-0000-0000-0000-000000000123"),
        )
        
        # Assert
        assert result is None


class TestClientsRepositoryDelete:
    """Tests for delete (soft delete) operation."""
    
    @pytest.mark.asyncio
    async def test_delete_soft_success(self, repository, mock_session, mock_kafka, sample_client):
        """Test successful soft delete."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_client)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        
        user_id = UUID("00000000-0000-0000-0000-000000000456")
        motivo = "Cliente inativo por 12 meses"
        
        # Act
        result = await repository.delete(
            sample_client.id,
            sample_client.tenant_id,
            user_id,
            motivo,
        )
        
        # Assert
        assert result is True
        assert sample_client.status == ClientStatus.EXCLUDED
        assert len(sample_client.historico_atualizacoes) == 1
        
        # Verify history
        history = sample_client.historico_atualizacoes[0]
        assert history["usuario_id"] == str(user_id)
        assert history["acao"] == "exclusao"
        assert history["motivo"] == motivo
        
        mock_session.commit.assert_called_once()
        mock_kafka.send_event.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository, mock_session):
        """Test deleting non-existent client."""
        # Arrange
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await repository.delete(
            uuid4(),
            UUID("00000000-0000-0000-0000-000000000001"),
            UUID("00000000-0000-0000-0000-000000000123"),
            "Test deletion",
        )
        
        # Assert
        assert result is False


class TestClientsRepositoryHistory:
    """Tests for history retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_history_success(self, repository, mock_session, sample_client):
        """Test retrieving client history."""
        # Arrange
        sample_client.historico_atualizacoes = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "usuario_id": str(uuid4()),
                "acao": "atualizacao",
                "campos": {"name": "Old Name"},
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "usuario_id": str(uuid4()),
                "acao": "atualizacao",
                "campos": {"phone": "+55 11 88888-7777"},
            },
        ]
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = AsyncMock(return_value=sample_client)
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        history = await repository.get_history(
            sample_client.id,
            sample_client.tenant_id,
        )
        
        # Assert
        assert history is not None
        assert len(history) == 2
        assert history[0]["acao"] == "atualizacao"
