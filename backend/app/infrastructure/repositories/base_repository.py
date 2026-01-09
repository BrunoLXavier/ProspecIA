"""
Base repository with generic typing and soft delete support.

Provides reusable CRUD operations and soft delete functionality for all domain repositories.
Follows Clean Architecture principles with type safety via Python TypeVar generics.
"""

from datetime import datetime, UTC
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from sqlalchemy import select, update, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from app.adapters.kafka.producer import KafkaProducer


# TypeVar for generic SQLAlchemy models
T = TypeVar('T', bound=DeclarativeMeta)


class SoftDeleteMixin(Generic[T]):
    """
    Mixin providing soft delete and hard delete functionality.
    
    Soft delete sets status='deleted' and hides records from non-admin users.
    Hard delete permanently removes records from database (admin-only).
    """
    
    def __init__(self, session: AsyncSession, kafka_producer: Optional[KafkaProducer] = None):
        """
        Initialize the mixin.
        
        Args:
            session: Async SQLAlchemy session
            kafka_producer: Optional Kafka producer for audit events
        """
        self.session = session
        self.kafka_producer = kafka_producer
    
    async def soft_delete(
        self,
        model_class: type[T],
        record_id: UUID,
        tenant_id: UUID,
        deleted_by: UUID,
        reason: str,
        kafka_topic: Optional[str] = None
    ) -> bool:
        """
        Soft delete a record by setting status='deleted'.
        
        Args:
            model_class: SQLAlchemy model class
            record_id: ID of the record to soft delete
            tenant_id: Tenant ID for RLS filtering
            deleted_by: UUID of user performing the delete
            reason: Reason for deletion (audit trail)
            kafka_topic: Optional Kafka topic for audit event
            
        Returns:
            True if record was soft deleted, False if not found
        """
        stmt = (
            update(model_class)
            .where(model_class.id == record_id)
            .where(model_class.tenant_id == tenant_id)
            .where(model_class.status != 'deleted')  # Don't re-delete
            .values(
                status='deleted',
                updated_at=datetime.now(UTC),
                updated_by=deleted_by
            )
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        if result.rowcount > 0 and self.kafka_producer and kafka_topic:
            await self.kafka_producer.send_event(
                topic=kafka_topic,
                event_type=f"{model_class.__tablename__}.soft_deleted",
                entity_id=str(record_id),
                tenant_id=str(tenant_id),
                user_id=str(deleted_by),
                data={"reason": reason}
            )
        
        return result.rowcount > 0
    
    async def hard_delete(
        self,
        model_class: type[T],
        record_id: UUID,
        tenant_id: UUID,
        deleted_by: UUID,
        kafka_topic: Optional[str] = None
    ) -> bool:
        """
        Permanently delete a record from database (admin-only operation).
        
        CAUTION: This operation is irreversible!
        
        Args:
            model_class: SQLAlchemy model class
            record_id: ID of the record to permanently delete
            tenant_id: Tenant ID for RLS filtering
            deleted_by: UUID of admin user performing the delete
            kafka_topic: Optional Kafka topic for audit event
            
        Returns:
            True if record was permanently deleted, False if not found
        """
        stmt = (
            sql_delete(model_class)
            .where(model_class.id == record_id)
            .where(model_class.tenant_id == tenant_id)
        )
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        
        if result.rowcount > 0 and self.kafka_producer and kafka_topic:
            await self.kafka_producer.send_event(
                topic=kafka_topic,
                event_type=f"{model_class.__tablename__}.hard_deleted",
                entity_id=str(record_id),
                tenant_id=str(tenant_id),
                user_id=str(deleted_by),
                data={"warning": "PERMANENT_DELETE"}
            )
        
        return result.rowcount > 0
    
    def filter_by_status(
        self,
        query: select,
        model_class: type[T],
        user_roles: List[str],
        include_deleted: bool = False
    ) -> select:
        """
        Filter query by status, hiding 'deleted' records from non-admin users.
        
        Args:
            query: SQLAlchemy select query to filter
            model_class: SQLAlchemy model class
            user_roles: List of user roles (e.g., ['admin', 'gestor'])
            include_deleted: Force include deleted items (overrides role check)
            
        Returns:
            Filtered query
        """
        is_admin = 'admin' in user_roles
        
        if not is_admin and not include_deleted:
            # Non-admin users only see active and inactive records
            query = query.where(model_class.status.in_(['active', 'inactive']))
        elif include_deleted and not is_admin:
            # Include deleted but non-admin: still hide them
            query = query.where(model_class.status.in_(['active', 'inactive']))
        # Admin sees all statuses if include_deleted=True or by default
        
        return query


class BaseRepository(Generic[T], SoftDeleteMixin[T]):
    """
    Generic base repository for CRUD operations with soft delete support.
    
    Type parameter T should be bound to a SQLAlchemy model class.
    All Wave 2 repositories should inherit from this class.
    
    Example:
        class ClientsRepository(BaseRepository[Client]):
            def __init__(self, session: AsyncSession, kafka: KafkaProducer):
                super().__init__(session, kafka)
    """
    
    def __init__(self, session: AsyncSession, kafka_producer: Optional[KafkaProducer] = None):
        """
        Initialize repository.
        
        Args:
            session: Async SQLAlchemy session
            kafka_producer: Optional Kafka producer for audit trails
        """
        super().__init__(session, kafka_producer)
        self.session = session
        self.kafka_producer = kafka_producer
    
    async def get_by_id(
        self,
        model_class: type[T],
        record_id: UUID,
        tenant_id: UUID,
        user_roles: Optional[List[str]] = None
    ) -> Optional[T]:
        """
        Get a single record by ID with status filtering.
        
        Args:
            model_class: SQLAlchemy model class
            record_id: Record ID
            tenant_id: Tenant ID for RLS
            user_roles: Optional user roles for status filtering
            
        Returns:
            Record if found and accessible, None otherwise
        """
        query = select(model_class).where(
            model_class.id == record_id,
            model_class.tenant_id == tenant_id
        )
        
        if user_roles:
            query = self.filter_by_status(query, model_class, user_roles)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_all(
        self,
        model_class: type[T],
        tenant_id: UUID,
        user_roles: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """
        List all records for a tenant with status filtering and pagination.
        
        Args:
            model_class: SQLAlchemy model class
            tenant_id: Tenant ID for RLS
            user_roles: Optional user roles for status filtering
            limit: Maximum records to return
            offset: Number of records to skip
            
        Returns:
            List of records
        """
        query = select(model_class).where(model_class.tenant_id == tenant_id)
        
        if user_roles:
            query = self.filter_by_status(query, model_class, user_roles)
        
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
