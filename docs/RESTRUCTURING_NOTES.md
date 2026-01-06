# Backend Restructuring - Angular Migration

## Current Status
- Created `backend/api/` directory structure
- Subdirectories created for: collections, series, authors, root_folders, calendar, metadata, notifications, ai_providers

## Migration Strategy

### Phase 1: Copy API files to new structure
Move all `frontend/api_*.py` files to `backend/api/*/routes.py`:
- `frontend/api_collections.py` → `backend/api/collections/routes.py`
- `frontend/api_series.py` → `backend/api/series/routes.py`
- `frontend/api_authors.py` → `backend/api/authors/routes.py`
- `frontend/api_rootfolders.py` → `backend/api/root_folders/routes.py`
- `frontend/api_metadata_fixed.py` → `backend/api/metadata/routes.py`
- `frontend/api_ai_providers.py` → `backend/api/ai_providers/routes.py`
- etc.

### Phase 2: Create __init__.py files
Each API module needs:
- `__init__.py` - exports the blueprint
- `routes.py` - API endpoints
- `schemas.py` - request/response validation (future)
- `crud.py` - database operations (future)

### Phase 3: Update server initialization
Update `backend/internals/server.py` and `run_dev.py` to import from new structure:
```python
from backend.api import api_bp
```

### Phase 4: Remove old frontend folder
Delete `frontend/` folder entirely once all APIs are migrated.

## Final Structure
```
backend/
├── api/
│   ├── __init__.py
│   ├── collections/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── schemas.py (future)
│   │   └── crud.py (future)
│   ├── series/
│   ├── authors/
│   ├── root_folders/
│   ├── calendar/
│   ├── metadata/
│   ├── notifications/
│   └── ai_providers/
├── features/
├── internals/
├── models/
└── base/
```

## Notes
- Keep all business logic in `backend/features/`
- API routes are thin wrappers around feature functions
- Database operations stay in features or move to crud.py files
- Schemas for validation can be added incrementally
