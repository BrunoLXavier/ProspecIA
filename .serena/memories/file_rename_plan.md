# File Rename Plan: Portuguese → English

## Objective
Complete the English naming transition by renaming files and updating all imports throughout the codebase.

## Scope

### Ingestao → Ingestion Files
1. **Domain Layer**
   - `backend/app/domain/models/ingestao.py` → `ingestion.py`
     - Contains: `Ingestao` class (alias `Ingestion` exists), `IngestionStatus`, `IngestionMethod`, `IngestionSource` enums
   - `backend/app/domain/repositories/ingestao_protocol.py` → `ingestion_protocol.py`
     - Contains: `IngestaoRepositoryProtocol` → rename to `IngestionRepositoryProtocol`
   - `backend/app/domain/repositories/ingestao_repository.py` → DEPRECATE (already wrapper with alias)

2. **Infrastructure Layer**
   - `backend/app/infrastructure/repositories/ingestao_repository.py` → `ingestion_repository.py`
     - Contains: `IngestaoRepository` → rename to `IngestionRepository`

3. **Interface Layer**
   - `backend/app/interfaces/http/routers/ingestao.py` → `ingestion.py`
     - Router prefix already `/ingestions`, functions use `ingestao` names
   - `backend/app/interfaces/http/schemas/ingestao.py` → `ingestion.py`
     - Already has English schema names: `IngestionCreateResponse`, etc.

4. **Tests**
   - `backend/tests/integration/test_ingestao_routes.py` → `test_ingestion_routes.py`

### Consentimento → Consent Files
1. **Domain Layer**
   - `backend/app/domain/models/consentimento.py` → `consent.py`
     - Contains: `Consentimento` class (alias `Consent` exists)
   - `backend/app/domain/repositories/consentimento_protocol.py` → `consent_protocol.py`
     - Contains: `ConsentimentoRepositoryProtocol` → rename to `ConsentRepositoryProtocol`
   - `backend/app/domain/repositories/consentimento_repository.py` → DEPRECATE (already wrapper with alias)

2. **Infrastructure Layer**
   - `backend/app/infrastructure/repositories/consentimento_repository.py` → `consent_repository.py`
     - Contains: `ConsentimentoRepository` → rename to `ConsentRepository`

3. **Interface Layer**
   - `backend/app/interfaces/http/routers/consentimento.py` → `consent.py`
     - Router prefix already `/consents`, functions use `consentimento` names

### Table Renames (Alembic Migration)
- `ingestoes` → `ingestions` (with backward-compatible view)
- `consentimentos` → `consents` (with backward-compatible view)

## Import Update Locations (from search)
Files importing these modules:
1. `backend/app/domain/models/__init__.py` - re-exports
2. `backend/app/domain/repositories/__init__.py` - re-exports
3. `backend/app/domain/repositories/consent_repository.py` - wrapper (deprecate)
4. `backend/app/domain/repositories/ingestion_repository.py` - wrapper (deprecate)
5. `backend/app/infrastructure/repositories/consentimento_repository.py` - implementation
6. `backend/app/infrastructure/repositories/ingestao_repository.py` - implementation
7. `backend/app/interfaces/http/routers/consentimento.py` - HTTP layer
8. `backend/app/interfaces/http/routers/ingestao.py` - HTTP layer
9. `backend/app/interfaces/http/schemas/ingestao.py` - schemas
10. `backend/app/use_cases/lgpd_agent.py` - use case
11. `backend/scripts/seed_wave1_data.py` - seed script
12. `backend/tests/integration/test_ingestao_routes.py` - tests
13. `backend/tests/unit/test_repositories.py` - tests

## Implementation Steps

### Phase 1: File Renames
1. Rename domain models: `ingestao.py` → `ingestion.py`, `consentimento.py` → `consent.py`
2. Rename protocols: `ingestao_protocol.py` → `ingestion_protocol.py`, `consentimento_protocol.py` → `consent_protocol.py`
3. Rename infrastructure repos: same pattern
4. Rename routers and schemas: same pattern
5. Rename tests: same pattern

### Phase 2: Symbol Renames (within files)
1. `Ingestao` → `Ingestion` (remove alias, make primary)
2. `Consentimento` → `Consent` (remove alias, make primary)
3. `IngestaoRepository` → `IngestionRepository`
4. `ConsentimentoRepository` → `ConsentRepository`
5. `IngestaoRepositoryProtocol` → `IngestionRepositoryProtocol`
6. `ConsentimentoRepositoryProtocol` → `ConsentRepositoryProtocol`
7. Function names: `create_ingestao` → `create_ingestion`, etc.

### Phase 3: Import Path Updates
Update all import statements in consuming files:
- `from app.domain.models.ingestao import` → `from app.domain.models.ingestion import`
- `from app.domain.models.consentimento import` → `from app.domain.models.consent import`
- And all other variations

### Phase 4: Re-export Updates
Update `__init__.py` files to export new names:
- `backend/app/domain/models/__init__.py`
- `backend/app/domain/repositories/__init__.py`

### Phase 5: Alembic Migration
Create migration to:
1. Rename table `ingestoes` → `ingestions`
2. Rename table `consentimentos` → `consents`
3. Create backward-compatible views if needed for gradual transition
4. Update all foreign key references

### Phase 6: Test Updates
1. Update test imports
2. Update test assertions using old names
3. Verify pytest passes with full coverage
4. Update seed scripts

## Risk Mitigation
- Keep wrapper files (e.g., `ingestion_repository.py` with re-export) temporarily for backward compatibility
- Use deprecation warnings in wrapper files
- Test each layer independently
- Run full test suite after each phase

## Success Criteria
- Zero flake8/mypy errors
- All tests pass (pytest with coverage)
- All imports use English names
- No Portuguese file names remain in codebase
- Database tables renamed with migration
- Documentation updated
