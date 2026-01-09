"""
Unit tests for FundingSourcesRepository.

Tests CRUD operations, RLS filtering, soft delete, and versioning.
Following patterns from Wave 1 test_repositories.py

Wave 2 - RF-02: Gestão de Fontes de Fomento
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from datetime import date, datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.funding_source import FundingSource, FundingSourceStatus, FundingSourceType
from app.infrastructure.repositories.funding_sources_repository import FundingSourcesRepository


@pytest.fixture
def mock_session():
    """Mock async SQLAlchemy session."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer."""
    producer = MagicMock()
    producer.send_message = AsyncMock()
    return producer


@pytest.fixture
def sample_funding_source_data():
    """Sample data for testing."""
    return {
        "name": "Programa FINEP 2026",
        "description": "Programa de subvenção para empresas inovadoras",
        "type": FundingSourceType.GRANT,
        "sectors": ["TI", "Saúde"],
        "amount": 10000000000,  # R$ 100M in cents
        "trl_min": 3,
        "trl_max": 7,
        "deadline": date(2026, 12, 31),
        "url": "https://finep.gov.br",
        "requirements": "Empresa com mínimo 2 anos",
        "tenant_id": UUID("00000000-0000-0000-0000-000000000100"),
        "criado_por": UUID("00000000-0000-0000-0000-000000000001"),
    }


@pytest.mark.asyncio
async def test_create_funding_source(mock_session, mock_kafka_producer, sample_funding_source_data):
    """Test creating a funding source."""
    # Arrange
    repo = FundingSourcesRepository(mock_session, mock_kafka_producer)
    
    # Mock database response
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (
        uuid4(),  # id
        datetime.now(UTC),  # criado_em
        datetime.now(UTC),  # atualizado_em
    )
    mock_session.execute.return_value = mock_result
    
    # Act
    entity = await repo.create(**sample_funding_source_data)
    
    # Assert
    assert entity is not None
    assert entity.name == sample_funding_source_data["name"]
    assert entity.type == sample_funding_source_data["type"]
    assert entity.status == FundingSourceStatus.ACTIVE
    assert entity.historico_atualizacoes == []
    mock_session.commit.assert_called_once()
    mock_kafka_producer.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_create_funding_source_invalid_trl(mock_session, mock_kafka_producer, sample_funding_source_data):
    """Test creating funding source with invalid TRL raises ValueError."""
    # Arrange
    repo = FundingSourcesRepository(mock_session, mock_kafka_producer)
    sample_funding_source_data["trl_min"] = 10  # Invalid (must be 1-9)
    
    # Act & Assert
    with pytest.raises(ValueError, match="trl_min must be between 1 and 9"):
        await repo.create(**sample_funding_source_data)


@pytest.mark.asyncio
async def test_find_by_id_with_rls(mock_session, mock_kafka_producer):
    """Test finding funding source by ID with RLS filtering."""
    # Arrange
    repo = FundingSourcesRepository(mock_session, mock_kafka_producer)
    funding_source_id = uuid4()
    tenant_id = UUID("00000000-0000-0000-0000-000000000100")
    
    # Mock database response
    mock_result = MagicMock()
    mock_result.fetchone.return_value = (
        funding_source_id,
        "Programa FINEP",
        "Descrição",
        "grant",
        ["TI"],
        10000000000,
        3,
        7,
        date(2026, 12, 31),
        "https://finep.gov.br",
        "Requirements",
        "active",
        tenant_id,
        [],
        UUID("00000000-0000-0000-0000-000000000001"),
        UUID("00000000-0000-0000-0000-000000000001"),
        datetime.now(UTC),
        datetime.now(UTC),
    )
    mock_session.execute.return_value = mock_result
    
    # Act
    entity = await repo.find_by_id(funding_source_id, tenant_id)
    
    # Assert
    assert entity is not None
    assert entity.id == funding_source_id
    assert entity.tenant_id == tenant_id
    
    # Verify RLS filter was applied
    call_args = mock_session.execute.call_args
    assert "tenant_id = :tenant_id" in str(call_args[0][0])


@pytest.mark.asyncio
async def test_find_by_id_not_found(mock_session, mock_kafka_producer):
    """Test finding non-existent funding source returns None."""
    # Arrange
    repo = FundingSourcesRepository(mock_session, mock_kafka_producer)
    
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Act
    entity = await repo.find_by_id(uuid4(), uuid4())
    
    # Assert
    assert entity is None


@pytest.mark.asyncio
async def test_list_with_filters(mock_session, mock_kafka_producer):
    """Test listing funding sources with filters."""
    # Arrange
    repo = FundingSourcesRepository(mock_session, mock_kafka_producer)
    tenant_id = UUID("00000000-0000-0000-0000-000000000100")
    
    # Mock empty result
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_session.execute.return_value = mock_result
    
    # Act
    entities = await repo.list(
        tenant_id=tenant_id,
        status_filter=[FundingSourceStatus.ACTIVE],
        type_filter=[FundingSourceType.GRANT],
        sector_filter=["TI"],
    )
    
    # Assert
    assert isinstance(entities, list)
    
    # Verify filters were applied
    call_args = mock_session.execute.call_args
    query_str = str(call_args[0][0])
    assert "tenant_id = :tenant_id" in query_str
    assert "status" in query_str


@pytest.mark.asyncio
async def test_soft_delete(mock_session, mock_kafka_producer):
    """Test soft delete sets status=excluded and adds audit entry."""
    # Arrange
    repo = FundingSourcesRepository(mock_session, mock_kafka_producer)
    funding_source_id = uuid4()
    tenant_id = UUID("00000000-0000-0000-0000-000000000100")
    user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    # Mock find_by_id to return entity
    with patch.object(repo, 'find_by_id', new_callable=AsyncMock) as mock_find:
        mock_entity = MagicMock()
        mock_entity.status = FundingSourceStatus.ACTIVE
        mock_entity.can_transition_to.return_value = True
        mock_find.return_value = mock_entity
        
        # Mock update to return updated entity
        with patch.object(repo, 'update', new_callable=AsyncMock) as mock_update:
            mock_updated = MagicMock()
            mock_update.return_value = mock_updated
            
            # Act
            success = await repo.soft_delete(
                funding_source_id=funding_source_id,
                tenant_id=tenant_id,
                motivo="Programa cancelado",
                atualizado_por=user_id,
            )
            
            # Assert
            assert success is True
            mock_update.assert_called_once()
            call_kwargs = mock_update.call_args[1]
            assert call_kwargs["updates"]["status"] == FundingSourceStatus.EXCLUDED
            assert call_kwargs["motivo"] == "Programa cancelado"


@pytest.mark.asyncio
async def test_update_with_versioning(mock_session, mock_kafka_producer):
    """Test update adds entries to historico_atualizacoes."""
    # Arrange
    repo = FundingSourcesRepository(mock_session, mock_kafka_producer)
    funding_source_id = uuid4()
    tenant_id = UUID("00000000-0000-0000-0000-000000000100")
    user_id = UUID("00000000-0000-0000-0000-000000000001")
    
    # Mock find_by_id to return current entity
    current_entity = MagicMock()
    current_entity.id = funding_source_id
    current_entity.name = "Old Name"
    current_entity.amount = 10000000000
    current_entity.status = FundingSourceStatus.ACTIVE
    current_entity.can_transition_to.return_value = True
    
    with patch.object(repo, 'find_by_id', new_callable=AsyncMock) as mock_find:
        mock_find.return_value = current_entity
        
        # Mock database update
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (datetime.now(UTC),)
        mock_session.execute.return_value = mock_result
        
        # Act
        updates = {"name": "New Name", "amount": 15000000000}
        entity = await repo.update(
            funding_source_id=funding_source_id,
            tenant_id=tenant_id,
            updates=updates,
            motivo="Orçamento aumentado",
            atualizado_por=user_id,
        )
        
        # Assert
        mock_session.commit.assert_called_once()
        mock_kafka_producer.send_message.assert_called_once()
        
        # Verify audit entries were created
        call_args = mock_session.execute.call_args
        # call_args[0] is the positional args tuple, call_args[1] is kwargs
        # The execute() call is execute(query, params), so params is at args[1]
        params = call_args[0][1]
        assert "audit_entries" in params
        # Should have 2 audit entries (name + amount)
        assert len(params["audit_entries"]) == 2
