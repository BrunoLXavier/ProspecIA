"""
Prometheus metrics for ingestion and LGPD processing.
Define counters, gauges, and histograms used by Grafana dashboard.
"""

from prometheus_client import Counter, Gauge, Histogram

# Ingestions created total by source
ingestoes_created_total = Counter(
    "ingestoes_created_total",
    "Total ingestions created",
    labelnames=("fonte",),
)

# Active ingestions by status (use gauge; increment/decrement as states change)
ingestoes_status = Gauge(
    "ingestoes_status",
    "Active ingestions by status",
    labelnames=("status",),
)

# Reliability score gauge (set per event; Grafana aggregates avg)
ingestao_confiabilidade_score = Gauge(
    "ingestao_confiabilidade_score",
    "Reliability score for ingestion events",
    labelnames=("fonte",),
)

# PII detected counter by type
lgpd_pii_detected_total = Counter(
    "lgpd_pii_detected_total",
    "Total PII entities detected by type",
    labelnames=("pii_type",),
)

# Consent validation counts by status (granted, missing, revoked)
lgpd_consent_validation = Counter(
    "lgpd_consent_validation",
    "Consent validation outcomes by status",
    labelnames=("status",),
)

# Processing time histogram by source (Grafana expects *_bucket suffix)
ingestao_processing_time = Histogram(
    "ingestao_processing_time",
    "Ingestion processing time in seconds",
    labelnames=("fonte",),
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
)

# Error counter
ingestao_errors_total = Counter(
    "ingestao_errors_total",
    "Total ingestion errors",
)
