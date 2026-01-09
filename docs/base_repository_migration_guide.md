# BaseRepository Migration Guide

This guide explains how to refactor existing Wave 2 repositories to inherit from `BaseRepository[T]` and `SoftDeleteMixin`.

## Overview

The `BaseRepository[T]` provides a generic foundation for repository classes with:
- Type-safe generic operations using SQLAlchemy models
- Soft delete support (status field: 'active', 'inactive', 'deleted')
- Hard delete (admin-only permanent deletion)
- Status filtering (non-admins cannot see deleted records)
- Automatic Kafka audit events

## Repositories to Refactor

1. `ClientsRepository` (backend/app/infrastructure/repositories/clients_repository.py)
2. `FundingSourcesRepository` (backend/app/infrastructure/repositories/funding_sources_repository.py)
3. `InteractionsRepository` (backend/app/infrastructure/repositories/interactions_repository.py)
4. `OpportunitiesRepository` (backend/app/infrastructure/repositories/opportunities_repository.py)
5. `InstitutesRepository` (backend/app/infrastructure/repositories/portfolio_repository.py)
6. `ProjectsRepository` (backend/app/infrastructure/repositories/portfolio_repository.py)
7. `CompetencesRepository` (backend/app/infrastructure/repositories/portfolio_repository.py)

## Migration Steps

### 1. Update Imports

```python
from app.infrastructure.repositories.base_repository import BaseRepository
```

### 2. Update Class Definition

**Before:**
```python
class ClientsRepository(ClientsRepositoryProtocol):
    def __init__(self, session: AsyncSession, kafka_producer: KafkaProducer):
        self.session = session
        self.kafka_producer = kafka_producer
```

**After:**
```python
class ClientsRepository(BaseRepository[Client], ClientsRepositoryProtocol):
    def __init__(self, session: AsyncSession, kafka_producer: KafkaProducer):
        super().__init__(session=session, kafka_producer=kafka_producer, model=Client)
```

### 3. Replace Soft Delete Logic

If your repository has custom soft delete logic using a `status` or `excluded` field, replace it with the inherited `soft_delete()` method.

**Before (ClientsRepository):**
```python
async def delete(
    self,
    client_id: UUID,
    tenant_id: UUID,
    deleted_by: UUID,
    motivo: str,
) -> bool:
    """Soft delete a client (status -> excluded)."""
    existing = await self.get(client_id, tenant_id)
    if not existing:
        return False
    existing.status = ClientStatus.EXCLUDED
    existing.add_history(
        {"status": ClientStatus.EXCLUDED.value},
        usuario_id=deleted_by,
        acao="exclusao",
        motivo=motivo,
    )
    existing.atualizado_por = deleted_by
    existing.atualizado_em = datetime.now(UTC)
    
    await self.session.add(existing)
    await self.session.commit()
    
    await self.kafka_producer.send_event(
        topic="clients",
        event_type="client.deleted",
        entity_id=str(client_id),
        tenant_id=str(tenant_id),
        user_id=str(deleted_by),
        data={"motivo": motivo},
    )
    return True
```

**After:**
```python
async def delete(
    self,
    client_id: UUID,
    tenant_id: UUID,
    deleted_by: UUID,
    motivo: str,
) -> bool:
    """Soft delete a client (sets status='deleted')."""
    # Add custom history tracking if needed
    existing = await self.get_by_id(client_id, tenant_id)
    if existing:
        existing.add_history(
            {"status": "deleted"},
            usuario_id=deleted_by,
            acao="exclusao",
            motivo=motivo,
        )
        await self.session.flush()  # Save history before soft delete
    
    # Use inherited soft_delete method
    return await self.soft_delete(
        entity_id=client_id,
        tenant_id=tenant_id,
        user_id=deleted_by,
        topic="clients",
        event_type="client.deleted",
        metadata={"motivo": motivo}
    )
```

### 4. Add Hard Delete for Admins

Add a new method for permanent deletion (admin-only):

```python
async def hard_delete_client(
    self,
    client_id: UUID,
    tenant_id: UUID,
    deleted_by: UUID,
    user_roles: List[str],
) -> bool:
    """Permanently delete a client (admin-only)."""
    if "admin" not in user_roles:
        raise PermissionError("Only admins can hard delete clients")
    
    return await self.hard_delete(
        entity_id=client_id,
        tenant_id=tenant_id,
        user_id=deleted_by,
        topic="clients",
        event_type="client.hard_deleted",
    )
```

### 5. Update List Methods with Status Filtering

Replace custom list methods to use the inherited `filter_by_status()` method:

**Before:**
```python
async def list(
    self,
    tenant_id: UUID,
    status: Optional[ClientStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[Sequence[Client], int]:
    """List clients with filters."""
    base_query = select(Client).where(
        Client.tenant_id == tenant_id,
        Client.status != ClientStatus.EXCLUDED
    )
    # ... rest of query
```

**After:**
```python
async def list(
    self,
    tenant_id: UUID,
    user_roles: List[str],
    status_filter: Optional[str] = None,  # 'active', 'inactive', 'deleted'
    skip: int = 0,
    limit: int = 100,
) -> tuple[Sequence[Client], int]:
    """List clients with status filtering."""
    # Use inherited status filtering
    items = await self.list_all(
        tenant_id=tenant_id,
        user_roles=user_roles,
        status_filter=status_filter,
        skip=skip,
        limit=limit,
    )
    
    # For total count
    total = await self.count(tenant_id, user_roles, status_filter)
    
    return items, total
```

### 6. Use Inherited get_by_id

Replace custom `get()` methods:

**Before:**
```python
async def get(
    self,
    client_id: UUID,
    tenant_id: UUID,
    include_excluded: bool = False,
) -> Optional[Client]:
    """Get client by ID."""
    stmt = select(Client).where(
        Client.id == client_id,
        Client.tenant_id == tenant_id
    )
    if not include_excluded:
        stmt = stmt.where(Client.status != ClientStatus.EXCLUDED)
    result = await self.session.execute(stmt)
    return result.scalar_one_or_none()
```

**After:**
```python
async def get(
    self,
    client_id: UUID,
    tenant_id: UUID,
    user_roles: List[str],
) -> Optional[Client]:
    """Get client by ID (soft-delete aware)."""
    return await self.get_by_id(
        entity_id=client_id,
        tenant_id=tenant_id,
        user_roles=user_roles,
    )
```

## Important Notes

### Custom Business Logic

If your repository has custom business logic (like history tracking, validation, or complex queries), keep those methods and only delegate the basic CRUD + soft delete operations to `BaseRepository`.

### Status Field Migration

Ensure all tables have the `status` field added via the Alembic migration `009_add_status_field.py`.

### Backward Compatibility

During migration, you can maintain backward compatibility by creating wrapper methods:

```python
async def get_legacy(
    self,
    client_id: UUID,
    tenant_id: UUID,
    include_excluded: bool = False,
) -> Optional[Client]:
    """Legacy method - use get() instead."""
    user_roles = ["admin"] if include_excluded else []
    return await self.get(client_id, tenant_id, user_roles)
```

### Testing

After refactoring, verify:
1. All existing tests pass
2. Soft delete sets status='deleted' instead of removing records
3. Hard delete is restricted to admins
4. Non-admin users cannot see deleted records
5. Kafka events are emitted correctly

## Example: Complete Refactored Repository

```python
from typing import List, Optional, Sequence
from uuid import UUID
from sqlalchemy import select, func
from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.models.client import Client, ClientStatus

class ClientsRepository(BaseRepository[Client]):
    """Repository for managing clients with soft delete support."""
    
    def __init__(self, session, kafka_producer):
        super().__init__(session=session, kafka_producer=kafka_producer, model=Client)
    
    async def create(self, client: Client) -> Client:
        """Create new client with audit event."""
        self.session.add(client)
        await self.session.commit()
        await self.session.refresh(client)
        
        await self.kafka_producer.send_event(
            topic="clients",
            event_type="client.created",
            entity_id=str(client.id),
            tenant_id=str(client.tenant_id),
            user_id=str(client.criado_por),
            data={"name": client.name, "cnpj": client.cnpj}
        )
        return client
    
    async def get(
        self,
        client_id: UUID,
        tenant_id: UUID,
        user_roles: List[str],
    ) -> Optional[Client]:
        """Get client by ID (soft-delete aware)."""
        return await self.get_by_id(client_id, tenant_id, user_roles)
    
    async def list(
        self,
        tenant_id: UUID,
        user_roles: List[str],
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Client], int]:
        """List clients with status filtering."""
        items = await self.list_all(
            tenant_id=tenant_id,
            user_roles=user_roles,
            status_filter=status_filter,
            skip=skip,
            limit=limit,
        )
        
        total = await self.count(tenant_id, user_roles, status_filter)
        return items, total
    
    async def delete(
        self,
        client_id: UUID,
        tenant_id: UUID,
        deleted_by: UUID,
        motivo: str,
    ) -> bool:
        """Soft delete a client (sets status='deleted')."""
        # Custom history tracking
        existing = await self.get_by_id(client_id, tenant_id, ["admin"])
        if existing:
            existing.add_history(
                {"status": "deleted"},
                usuario_id=deleted_by,
                acao="exclusao",
                motivo=motivo,
            )
            await self.session.flush()
        
        return await self.soft_delete(
            entity_id=client_id,
            tenant_id=tenant_id,
            user_id=deleted_by,
            topic="clients",
            event_type="client.deleted",
            metadata={"motivo": motivo}
        )
    
    async def hard_delete_client(
        self,
        client_id: UUID,
        tenant_id: UUID,
        deleted_by: UUID,
        user_roles: List[str],
    ) -> bool:
        """Permanently delete a client (admin-only)."""
        if "admin" not in user_roles:
            raise PermissionError("Only admins can hard delete clients")
        
        return await self.hard_delete(
            entity_id=client_id,
            tenant_id=tenant_id,
            user_id=deleted_by,
            topic="clients",
            event_type="client.hard_deleted",
        )
```

## Next Steps

1. Refactor each repository one at a time
2. Run tests after each refactoring
3. Update service layer to pass `user_roles` parameter
4. Update API endpoints to use new hard_delete methods with ACL checks
5. Remove old soft delete code once migration is complete
