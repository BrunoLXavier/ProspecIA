# ProspecIA Backend - Optimized Multi-stage Docker Build
# Following Docker best practices for Python applications

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies - minimal set
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better layer caching
COPY requirements.txt .

# Create wheels directory and build wheels
RUN pip install --upgrade pip setuptools wheel && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.11-slim

# Set environment variables for optimal Python performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH=/app/.local/bin:$PATH

# Install runtime dependencies only - minimal set
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create non-root application user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy pre-built wheels from builder stage
COPY --from=builder /build/wheels /tmp/wheels

# Install packages from wheels (faster and no build needed)
RUN pip install --no-index --find-links=/tmp/wheels -r /dev/stdin << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
sqlalchemy==2.0.25
psycopg2-binary==2.9.10
asyncpg==0.29.0
alembic==1.13.1
neo4j==5.16.0
kafka-python==2.0.2
confluent-kafka==2.3.0
python-jose[cryptography]==3.3.0
PyJWT[crypto]==2.8.0
passlib[bcrypt]==1.7.4
python-keycloak==3.8.0
bcrypt==4.1.2
cryptography==42.0.1
httpx==0.26.0
aiohttp==3.9.1
minio==7.2.3
numpy==1.26.3
pandas==2.1.4
prometheus-client==0.19.0
python-json-logger==2.0.7
structlog==24.1.0
python-dotenv==1.0.0
pydantic-core==2.14.6
email-validator==2.1.0
qrcode[pil]==7.4.2
EOF

# Clean up wheels
RUN rm -rf /tmp/wheels

# Copy application code (do this last for better caching)
COPY --chown=appuser:appuser . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8000

# Health check with increased timeout
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER appuser

# Run application with entrypoint that handles migrations
ENTRYPOINT ["./entrypoint.sh"]
