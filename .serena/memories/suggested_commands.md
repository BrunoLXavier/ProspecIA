# Suggested Commands
## Docker/Infra
- Start stack: `docker-compose up -d`
- Apply migrations: `docker exec prospecai-backend alembic upgrade head`
- Seed wave1 data: `docker exec prospecai-backend python scripts/seed_wave1_data.py`
- Check health: `curl http://localhost:8000/health/ready`
- Metrics: `curl http://localhost:8000/system/metrics`
- i18n endpoints: `curl http://localhost:8000/i18n/locales` and `curl http://localhost:8000/i18n/translations/en-US`

## Backend (inside container)
- Tests with coverage: `docker exec -e PYTHONPATH=/app prospecai-backend pytest tests/ --cov=app --cov-report=term-missing --cov-report=html`
- Lint: `docker exec prospecai-backend flake8 app`
- Format: `docker exec prospecai-backend black .` and `docker exec prospecai-backend isort .`
- Type check (optional): `docker exec prospecai-backend mypy app`

## Frontend (run from ./frontend)
- Install deps: `npm ci`
- Dev server: `npm run dev`
- Build / Start: `npm run build` then `npm run start`
- Lint: `npm run lint` (auto-fix: `npm run lint:fix`)
- Format: `npm run format`
- Type check: `npm run type-check`
- Tests: `npm run test` (Vitest)

## Quick wave0 verification (from docs)
- Script (PowerShell): `scripts/quick-verify-wave0.ps1`
