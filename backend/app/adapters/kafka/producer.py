"""
ProspecIA - Kafka Producer Adapter

Kafka message producer for audit logs, LGPD decisions, and notifications.
Implements async message publishing with error handling.
"""

from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError
import json
import structlog
from datetime import datetime

from app.infrastructure.config.settings import Settings

logger = structlog.get_logger()


class KafkaProducerAdapter:
    """
    Manages Kafka message production for event streaming.
    
    Responsibilities (SRP):
    - Initialize and manage Kafka producer
    - Publish messages to different topics
    - Handle serialization and errors
    - Provide health check capability
    
    Topics:
    - audit-logs: Audit trail events (PT-01)
    - lgpd-decisions: LGPD agent decisions (PT-02, PT-03)
    - notifications: System notifications
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize Kafka producer adapter.
        
        Args:
            settings: Application settings with Kafka configuration
        """
        self.settings = settings
        self._producer: Optional[KafkaProducer] = None
        
    def connect(self) -> None:
        """
        Initialize Kafka producer with JSON serialization.
        
        Raises:
            KafkaError: If connection fails
        """
        if self._producer is not None:
            logger.warning("kafka_already_connected")
            return
        
        logger.info(
            "kafka_connecting",
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
        )
        
        try:
            self._producer = KafkaProducer(
                bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                max_in_flight_requests_per_connection=1,
                compression_type='gzip',
            )
            
            logger.info("kafka_connected")
            
        except KafkaError as e:
            logger.error("kafka_connection_failed", error=str(e))
            raise
    
    def disconnect(self) -> None:
        """Close Kafka producer and cleanup resources."""
        if self._producer is None:
            return
        
        logger.info("kafka_disconnecting")
        self._producer.flush()
        self._producer.close()
        self._producer = None
        logger.info("kafka_disconnected")
    
    def health_check(self) -> bool:
        """
        Check Kafka connectivity.
        
        Returns:
            bool: True if Kafka is accessible, False otherwise
        """
        if self._producer is None:
            return False
        
        try:
            # Bootstrap check
            self._producer.bootstrap_connected()
            return True
        except Exception as e:
            logger.error("kafka_health_check_failed", error=str(e))
            return False
    
    def publish_audit_log(
        self,
        usuario_id: str,
        acao: str,
        tabela: str,
        record_id: str,
        valor_antigo: Optional[Dict[str, Any]] = None,
        valor_novo: Optional[Dict[str, Any]] = None,
        ip_cliente: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_id: str = "nacional",
    ) -> bool:
        """
        Publish audit log event to Kafka.
        
        Args:
            usuario_id: User who performed the action
            acao: Action type (CREATE, UPDATE, DELETE, READ)
            tabela: Table name affected
            record_id: Record ID affected
            valor_antigo: Previous value (for UPDATE/DELETE)
            valor_novo: New value (for CREATE/UPDATE)
            ip_cliente: Client IP address
            user_agent: User agent string
            tenant_id: Tenant identifier
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "usuario_id": usuario_id,
            "acao": acao,
            "tabela": tabela,
            "record_id": record_id,
            "valor_antigo": valor_antigo,
            "valor_novo": valor_novo,
            "ip_cliente": ip_cliente,
            "user_agent": user_agent,
            "tenant_id": tenant_id,
        }
        
        return self._publish(
            topic=self.settings.KAFKA_TOPIC_AUDIT,
            key=record_id,
            value=event,
        )
    
    def publish_lgpd_decision(
        self,
        ingestao_id: str,
        pii_detectado: Dict[str, Any],
        acoes_tomadas: Dict[str, Any],
        consentimento_validado: bool,
        score_confiabilidade: float,
        modelo_usado: str = "bertimbau-pii-detector",
    ) -> bool:
        """
        Publish LGPD agent decision to Kafka.
        
        Args:
            ingestao_id: Ingestion ID
            pii_detectado: Detected PII information
            acoes_tomadas: Actions taken (masking, tokenization)
            consentimento_validado: Whether consent was validated
            score_confiabilidade: Confidence score (0-100)
            modelo_usado: Model used for PII detection
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "ingestao_id": ingestao_id,
            "pii_detectado": pii_detectado,
            "acoes_tomadas": acoes_tomadas,
            "consentimento_validado": consentimento_validado,
            "score_confiabilidade": score_confiabilidade,
            "modelo_usado": modelo_usado,
        }
        
        return self._publish(
            topic=self.settings.KAFKA_TOPIC_LGPD,
            key=ingestao_id,
            value=event,
        )
    
    def publish_notification(
        self,
        usuario_id: str,
        tipo: str,
        titulo: str,
        mensagem: str,
        prioridade: str = "normal",
        dados_adicionais: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Publish notification event to Kafka.
        
        Args:
            usuario_id: Target user ID
            tipo: Notification type (info, warning, error, success)
            titulo: Notification title
            mensagem: Notification message
            prioridade: Priority (low, normal, high, urgent)
            dados_adicionais: Additional data (optional)
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "usuario_id": usuario_id,
            "tipo": tipo,
            "titulo": titulo,
            "mensagem": mensagem,
            "prioridade": prioridade,
            "dados_adicionais": dados_adicionais or {},
            "lido": False,
        }
        
        return self._publish(
            topic=self.settings.KAFKA_TOPIC_NOTIFICATIONS,
            key=usuario_id,
            value=event,
        )
    
    def _publish(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
    ) -> bool:
        """
        Internal method to publish message to Kafka.
        
        Args:
            topic: Target topic
            value: Message value (will be JSON serialized)
            key: Message key (optional)
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        if self._producer is None:
            logger.error("kafka_publish_failed_not_connected", topic=topic)
            return False
        
        try:
            future = self._producer.send(topic, key=key, value=value)
            
            # Wait for confirmation (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                "kafka_message_published",
                topic=topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset,
            )
            
            return True
            
        except KafkaTimeoutError as e:
            logger.error(
                "kafka_publish_timeout",
                topic=topic,
                error=str(e),
            )
            return False
            
        except KafkaError as e:
            logger.error(
                "kafka_publish_failed",
                topic=topic,
                error=str(e),
            )
            return False
            
        except Exception as e:
            logger.error(
                "kafka_publish_unexpected_error",
                topic=topic,
                error=str(e),
                error_type=type(e).__name__,
            )
            return False
    
    @property
    def producer(self) -> KafkaProducer:
        """
        Get the underlying Kafka producer.
        
        Returns:
            KafkaProducer: Kafka producer instance
            
        Raises:
            RuntimeError: If producer not connected
        """
        if self._producer is None:
            raise RuntimeError("Kafka not connected. Call connect() first.")
        return self._producer


# Global Kafka producer instance (initialized in main.py)
kafka_producer: KafkaProducerAdapter | None = None


def get_kafka_producer() -> KafkaProducerAdapter:
    """
    Get global Kafka producer instance.
    
    Returns:
        KafkaProducerAdapter: Global Kafka producer
        
    Raises:
        RuntimeError: If Kafka not initialized
    """
    if kafka_producer is None:
        raise RuntimeError("Kafka not initialized. Initialize in app startup.")
    return kafka_producer
