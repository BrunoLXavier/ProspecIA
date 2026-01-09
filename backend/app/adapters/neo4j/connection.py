"""
ProspecIA - Neo4j Database Adapter

Neo4j driver management for graph operations and data lineage.
Implements async connection handling and health checks.
"""

from typing import Any, Dict, List, Optional

import structlog
from neo4j import AsyncDriver, AsyncGraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable

from app.infrastructure.config.settings import Settings
from app.infrastructure.patterns.resilience import CircuitBreaker, async_retry

logger = structlog.get_logger()


class Neo4jConnection:
    """
    Manages Neo4j database connections for graph operations.

    Responsibilities (SRP):
    - Initialize and manage Neo4j driver
    - Provide session management
    - Handle connection lifecycle
    - Provide health check capability
    - Execute graph queries

    Use cases:
    - Data lineage tracking (PT-04)
    - Relationship mapping between entities
    - Graph-based analytics
    """

    def __init__(self, settings: Settings):
        """
        Initialize Neo4j connection manager.

        Args:
            settings: Application settings with Neo4j configuration
        """
        self.settings = settings
        self._driver: Optional[AsyncDriver] = None
        self._cb = CircuitBreaker(failure_threshold=3, reset_timeout_sec=20)

    @async_retry(
        exceptions=(AuthError, ServiceUnavailable, Exception), max_attempts=4, base_delay=0.3
    )
    async def connect(self) -> None:
        """
        Initialize Neo4j driver with connection pooling.

        Raises:
            AuthError: If authentication fails
            ServiceUnavailable: If Neo4j service is not available
        """
        if self._driver is not None:
            logger.warning("neo4j_already_connected")
            return

        logger.info(
            "neo4j_connecting",
            uri=self.settings.neo4j_uri,
            database=self.settings.NEO4J_DATABASE,
        )

        try:
            self._driver = AsyncGraphDatabase.driver(
                self.settings.neo4j_uri,
                auth=(self.settings.NEO4J_USER, self.settings.NEO4J_PASSWORD),
                max_connection_lifetime=3600,  # 1 hour
                max_connection_pool_size=50,
                connection_acquisition_timeout=60,
            )

            # Verify connectivity
            await self._driver.verify_connectivity()

            logger.info("neo4j_connected")
            self._cb.record_success()

        except AuthError as e:
            logger.error("neo4j_auth_failed", error=str(e))
            self._cb.record_failure()
            raise
        except ServiceUnavailable as e:
            logger.error("neo4j_service_unavailable", error=str(e))
            self._cb.record_failure()
            raise
        except Exception as e:
            logger.error("neo4j_connection_failed", error=str(e), error_type=type(e).__name__)
            self._cb.record_failure()
            raise

    async def disconnect(self) -> None:
        """Close Neo4j driver and cleanup resources."""
        if self._driver is None:
            return

        logger.info("neo4j_disconnecting")
        await self._driver.close()
        self._driver = None
        logger.info("neo4j_disconnected")

    async def health_check(self) -> bool:
        """
        Check Neo4j connectivity.

        Returns:
            bool: True if Neo4j is accessible, False otherwise
        """
        if self._driver is None:
            return False

        try:
            await self._driver.verify_connectivity()
            return True
        except Exception as e:
            logger.error("neo4j_health_check_failed", error=str(e))
            return False

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters (optional)
            database: Target database (optional, uses default if not specified)

        Returns:
            List of record dictionaries

        Raises:
            RuntimeError: If driver not connected
        """
        if self._driver is None:
            raise RuntimeError("Neo4j not connected. Call connect() first.")

        db_name = database or self.settings.NEO4J_DATABASE

        async with self._driver.session(database=db_name) as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def execute_write_transaction(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a write transaction (CREATE, MERGE, DELETE, etc).

        Args:
            query: Cypher query string
            parameters: Query parameters (optional)
            database: Target database (optional)

        Returns:
            List of record dictionaries

        Raises:
            RuntimeError: If driver not connected
        """
        if self._driver is None:
            raise RuntimeError("Neo4j not connected. Call connect() first.")

        db_name = database or self.settings.NEO4J_DATABASE

        async def _transaction(tx):
            result = await tx.run(query, parameters or {})
            return await result.data()

        async with self._driver.session(database=db_name) as session:
            records = await session.execute_write(_transaction)
            return records

    async def create_lineage_node(
        self,
        node_type: str,
        node_id: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a lineage node in the graph.

        Args:
            node_type: Type of node (e.g., "Ingestao", "Transformacao", "Modelo")
            node_id: Unique identifier for the node
            properties: Node properties

        Returns:
            Created node data
        """
        query = f"""
        MERGE (n:{node_type} {{id: $node_id}})
        SET n += $properties
        SET n.updated_at = datetime()
        RETURN n
        """

        result = await self.execute_write_transaction(
            query, {"node_id": node_id, "properties": properties}
        )

        return result[0]["n"] if result else {}

    async def create_lineage_relationship(
        self,
        from_id: str,
        to_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a relationship between two nodes in the lineage graph.

        Args:
            from_id: Source node ID
            to_id: Target node ID
            relationship_type: Type of relationship (e.g., "DERIVED_FROM", "TRANSFORMED_BY")
            properties: Relationship properties (optional)

        Returns:
            Created relationship data
        """
        query = f"""
        MATCH (a {{id: $from_id}})
        MATCH (b {{id: $to_id}})
        MERGE (a)-[r:{relationship_type}]->(b)
        SET r += $properties
        SET r.created_at = datetime()
        RETURN r
        """

        result = await self.execute_write_transaction(
            query, {"from_id": from_id, "to_id": to_id, "properties": properties or {}}
        )

        return result[0]["r"] if result else {}

    async def get_lineage_path(
        self,
        node_id: str,
        max_depth: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Get the complete lineage path for a node (upstream dependencies).

        Args:
            node_id: Node ID to get lineage for
            max_depth: Maximum depth to traverse (default: 5)

        Returns:
            List of nodes and relationships in the lineage path
        """
        query = f"""
        MATCH path = (n {{id: $node_id}})-[*1..{max_depth}]->(ancestor)
        RETURN path
        """

        result = await self.execute_query(query, {"node_id": node_id})

        return result

    @property
    def driver(self) -> AsyncDriver:
        """
        Get the underlying Neo4j driver.

        Returns:
            AsyncDriver: Neo4j async driver

        Raises:
            RuntimeError: If driver not connected
        """
        if self._driver is None:
            raise RuntimeError("Neo4j not connected. Call connect() first.")
        return self._driver


# Global Neo4j instance (initialized in main.py)
neo4j_connection: Neo4jConnection | None = None


def get_neo4j_connection() -> Neo4jConnection:
    """
    Get global Neo4j connection instance.

    Returns:
        Neo4jConnection: Global Neo4j connection

    Raises:
        RuntimeError: If Neo4j not initialized
    """
    if neo4j_connection is None:
        raise RuntimeError("Neo4j not initialized. Initialize in app startup.")
    return neo4j_connection
