"""Infrastructure implementations of audit logging."""

from __future__ import annotations

import structlog

from app.adapters.kafka.producer import get_kafka_producer
from app.domain.services.audit_logger import AuditLogger

logger = structlog.get_logger(__name__)


class KafkaAuditLogger(AuditLogger):
    """Audit logger that forwards events to Kafka producer adapter."""

    def __init__(self):
        try:
            self._producer = get_kafka_producer()
        except Exception:
            self._producer = None

    def publish_audit_log(
        self,
        usuario_id: str,
        acao: str,
        tabela: str,
        record_id: str,
        valor_novo=None,
        valor_antigo=None,
        tenant_id: str | None = None,
        ip_cliente: str | None = None,
    ) -> None:
        producer = self._producer
        if producer is None:
            try:
                producer = get_kafka_producer()
            except Exception:
                producer = None
        if not producer:
            logger.warning("audit_log_skipped", reason="no_kafka_producer")
            return None

        try:
            producer.publish_audit_log(
                usuario_id=usuario_id,
                acao=acao,
                tabela=tabela,
                record_id=record_id,
                valor_novo=valor_novo,
                valor_antigo=valor_antigo,
                tenant_id=tenant_id,
                ip_cliente=ip_cliente,
            )
        except Exception as exc:  # Defensive: avoid breaking flows on audit failures
            logger.error(
                "audit_log_failed", error=str(exc), acao=acao, tabela=tabela, record_id=record_id
            )
            return None
