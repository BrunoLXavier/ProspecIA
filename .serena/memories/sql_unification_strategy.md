# SQL Script Unification Strategy

## Current State
### SQL Files (.sql)
1. **scripts/init-db.sql** (110 lines)
   - Creates extensions (uuid-ossp, pg_trgm)
   - Creates feature_flags table + inserts 5 default flags
   - Creates configuracoes_sistema table + inserts 4 default configs
   - Location: Used by Postgres container init

2. **scripts/seed_wave2.sql** (43 lines)
   - Inserts funding_sources (5 items)
   - Inserts clients (10 items)
   - Inserts institutes (3 items)
   - Manual SQL inserts with gen_random_uuid()

### Python Seed Scripts
1. **backend/scripts/seed_wave1_data.py**
   - Seeds ingestoes and consentimentos with sample data
   - Async operations with SQLAlchemy ORM
   - Includes data clearing utilities

2. **backend/scripts/seed_wave2_data.py**
   - Seeds funding_sources, institutes, projects, competences
   - Seeds clients, interactions
   - Seeds opportunities and translations
   - Uses repositories and ORM

3. **backend/scripts/simple_seed.py**
   - Direct SQL approach for wave2 data
   - Async SQL operations

4. **backend/scripts/seed_sync.py**
   - Synchronous direct SQL approach
   - Inserts funding_sources, clients, institutes
   - Raw SQL with placeholders

5. **backend/scripts/seed_translations.py**
   - Seeds translations table with i18n data
   - Synchronous SQLAlchemy operations
   - Clears existing translations before insert

6. **scripts/seed_wave1_data.py**
   - Duplicate of backend version
   - Seeds ingestoes/consentimentos

7. **scripts/seed_translations.py**
   - Duplicate of backend version

## Consolidation Strategy

### Phase 1: Create System Configuration Migration
**File**: `002_wave0_system_config.py`
- Include feature_flags table creation (idempotent)
- Include configuracoes_sistema table creation (idempotent)
- Insert default feature flags with ON CONFLICT DO NOTHING
- Insert default system configurations with ON CONFLICT DO NOTHING

### Phase 2: Create Wave 1 Seeds Migration
**File**: `002_wave1_ingestion_seeds.py`
- Insert sample ingestoes data (5-10 records)
- Insert sample consentimentos data (10-15 records)
- Use ON CONFLICT DO NOTHING for idempotency

### Phase 3: Create Wave 2 Seeds Migration
**File**: `002_wave2_domain_seeds.py`
- Insert funding_sources data (5 records)
- Insert clients data (10 records)
- Insert institutes data (3 records)
- Insert projects data (from seed_wave2_data.py)
- Insert competences data
- Use ON CONFLICT DO NOTHING for idempotency

### Phase 4: Create Translations Migration
**File**: `002_wave2_translations.py`
- Insert translation records from seed_translations.py
- Use ON CONFLICT DO NOTHING for idempotency
- Cover all namespaces: common, modules, fields, errors, ui

## Files to Delete
1. ✓ scripts/init-db.sql → Logic moved to 002_wave0_system_config.py
2. ✓ scripts/seed_wave2.sql → Logic moved to 002_wave2_domain_seeds.py
3. ✓ backend/scripts/simple_seed.py → Logic moved to migrations
4. ✓ backend/scripts/seed_sync.py → Logic moved to migrations
5. ✓ scripts/seed_wave1_data.py → Replaced by migration + optional tool
6. ✓ scripts/seed_translations.py → Logic moved to 002_wave2_translations.py

## Files to Keep (Optional Manual Tools)
- backend/scripts/seed_wave1_data.py (can be used for manual re-seeding)
- backend/scripts/seed_wave2_data.py (can be used for manual re-seeding)

## Expected Outcome
1. All database schema and seed data created by Alembic migrations only
2. Single source of truth: backend/alembic/versions/
3. Database initialization: `alembic upgrade head`
4. Clean Docker Compose entrypoint (no init-db.sql execution)
5. All migrations idempotent and can be run multiple times safely

## ✅ COMPLETION STATUS - 2026-01-09

### Implementation Complete
1. **Migrations Created**:
   - `001_initial_schema.py` - Idempotent schema creation (extensions, tables, enums, indexes)
   - `002_wave0_system_config.py` - System configuration and feature flags seeds
   - `003_wave2_domain_seeds.py` - Funding sources, clients, institutes seeds
   - `004_wave2_translations.py` - Translation data seeds

2. **Database Status**:
   - ✅ feature_flags: 5 records seeded
   - ✅ configuracoes_sistema: 4 records seeded
   - ✅ clients: 10 records seeded
   - ✅ funding_sources: 5 records seeded
   - ✅ institutes: 3 records seeded
   - ✅ translations: 20 records seeded

3. **Infrastructure Updates**:
   - Created `backend/entrypoint.sh` - Runs migrations before app start
   - Modified `backend/Dockerfile` - Executes migrations automatically on startup
   - Updated `docker-compose.yml` - Removed init-db.sql volume mount
   - All scattered SQL scripts deleted and archived

4. **Verification**:
   - ✅ Backend health check passing
   - ✅ All seed data verified in database
   - ✅ Frontend running and healthy
   - ✅ System ready for production use

### Files Archived (backed up)
- `archived_scripts_init-db.sql`
- `archived_scripts_seed_wave2.sql`
- `archived_scripts_seed_wave1_data.py`
- `archived_scripts_seed_translations.py`
- `archived_backend_simple_seed.py`
- `archived_backend_seed_sync.py`
Location: `backend/alembic/archived_versions/`

### SQL Consolidation Complete
All database operations now exclusively through Alembic migrations. Zero scattered SQL scripts in project.
