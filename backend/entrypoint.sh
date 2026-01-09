#!/bin/bash
# Entrypoint script for FastAPI backend
# Runs Alembic migrations before starting the application

set -e

echo "🔄 Running Alembic migrations..."
alembic upgrade head

echo "✅ Migrations completed"
echo "🚀 Starting FastAPI application..."

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000
