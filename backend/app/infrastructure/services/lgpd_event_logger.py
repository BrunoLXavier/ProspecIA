"""Kafka implementation of LgpdEventLogger."""

from __future__ import annotations

import structlog

from app.adapters.kafka.producer import get_kafka_producer
from app.domain.services.lgpd_event_logger import LgpdEventLogger

logger = structlog.get_logger(__name__)


class KafkaLgpdEventLogger(LgpdEventLogger):
    def __init__(self):
        try:
            self._producer = get_kafka_producer()
        except Exception:
            self._producer = None

    def log_decision(
        self,
        ingestao_id: str,
        pii_detectado,
        acoes_tomadas,
        consentimento_validado: bool,
        score_confiabilidade: int,
    ) -> None:
        producer = self._producer
        if producer is None:
            try:
                producer = get_kafka_producer()
            except Exception:
                producer = None
        if not producer:
            logger.warning(
                "lgpd_event_skipped", reason="no_kafka_producer", ingestao_id=ingestao_id
            )
            return None
        try:
            producer.publish_lgpd_decision(
                ingestao_id=ingestao_id,
                pii_detectado=pii_detectado,
                acoes_tomadas=acoes_tomadas,
                consentimento_validado=consentimento_validado,
                score_confiabilidade=score_confiabilidade,
            )
        except Exception as exc:
            logger.error("lgpd_event_failed", error=str(exc), ingestao_id=ingestao_id)
            return None
