# Aggressive Refactoring Strategy - Micro-Services Architecture

**Date**: November 11, 2025  
**Goal**: Break down monolithic files into small, focused modules (50-150 lines each)  
**Target Audience**: Large teams with parallel development  
**Status**: Strategy Document

## Philosophy

**One File = One Feature = One Team Member**

Each file should be:
- ✅ Small enough to review in 5 minutes
- ✅ Focused on a single responsibility
- ✅ Independently testable
- ✅ Independently deployable
- ✅ Easy for one person to own and maintain

---

## Current State vs Target

### Before (Monolithic)
```
api.py (2,293 lines)
├── Dashboard (100 lines)
├── Calendar (50 lines)
├── Series (400 lines)
├── Volumes (200 lines)
├── Chapters (150 lines)
├── Settings (100 lines)
├── Collections (300 lines)
└── Integrations (100 lines)
```

### After (Micro-Services)
```
api/
├── dashboard/
│   ├── __init__.py
│   ├── stats.py (50 lines)
│   ├── events.py (40 lines)
│   └── routes.py (30 lines)
├── calendar/
│   ├── __init__.py
│   ├── events.py (60 lines)
│   ├── refresh.py (40 lines)
│   └── routes.py (30 lines)
├── series/
│   ├── __init__.py
│   ├── crud.py (80 lines)
│   ├── search.py (60 lines)
│   ├── move.py (50 lines)
│   ├── scan.py (50 lines)
│   └── routes.py (40 lines)
├── volumes/
│   ├── __init__.py
│   ├── crud.py (70 lines)
│   ├── formats.py (50 lines)
│   └── routes.py (40 lines)
├── chapters/
│   ├── __init__.py
│   ├── crud.py (70 lines)
│   └── routes.py (40 lines)
├── settings/
│   ├── __init__.py
│   ├── general.py (50 lines)
│   ├── groq_keys.py (50 lines)
│   └── routes.py (40 lines)
├── collection/
│   ├── __init__.py
│   ├── items.py (60 lines)
│   ├── stats.py (50 lines)
│   ├── formats.py (50 lines)
│   └── routes.py (40 lines)
└── integrations/
    ├── __init__.py
    ├── home_assistant.py (50 lines)
    ├── homarr.py (50 lines)
    └── routes.py (30 lines)
```

---

## Proposed Structure

### Level 1: Feature Modules (Directories)

```
frontend/api/
├── __init__.py (registers all blueprints)
├── dashboard/
├── calendar/
├── series/
├── volumes/
├── chapters/
├── settings/
├── collection/
└── integrations/
```

### Level 2: Sub-modules (Files)

Each feature directory contains:

```
feature/
├── __init__.py (exports blueprint)
├── models.py (data models, if needed)
├── services.py (business logic)
├── routes.py (API endpoints)
└── utils.py (helpers, if needed)
```

**File Size Guidelines**:
- `routes.py`: 30-50 lines (just endpoint definitions)
- `services.py`: 60-100 lines (business logic)
- `models.py`: 30-50 lines (data structures)
- `utils.py`: 40-80 lines (helper functions)

---

## Detailed Breakdown

### 1. Dashboard Module

```
frontend/api/dashboard/
├── __init__.py
├── stats.py (50 lines)
│   - get_manga_count()
│   - get_books_count()
│   - get_authors_count()
│   - get_collection_stats()
├── events.py (40 lines)
│   - get_today_events()
│   - format_events()
└── routes.py (30 lines)
    - GET /api/dashboard
```

**Total**: ~120 lines across 4 files

---

### 2. Calendar Module

```
frontend/api/calendar/
├── __init__.py
├── events.py (60 lines)
│   - get_events_for_range()
│   - filter_by_series()
│   - format_calendar_data()
├── refresh.py (40 lines)
│   - refresh_calendar()
│   - validate_refresh()
└── routes.py (30 lines)
    - GET /api/calendar
    - POST /api/calendar/refresh
```

**Total**: ~130 lines across 4 files

---

### 3. Series Module

```
frontend/api/series/
├── __init__.py
├── crud.py (80 lines)
│   - create_series()
│   - read_series()
│   - update_series()
│   - delete_series()
├── search.py (60 lines)
│   - search_by_title()
│   - filter_by_type()
│   - get_series_list()
├── move.py (50 lines)
│   - move_series()
│   - validate_move()
│   - plan_move()
├── scan.py (50 lines)
│   - scan_for_ebooks()
│   - update_ebook_list()
│   - validate_scan()
├── paths.py (40 lines)
│   - get_folder_path()
│   - set_custom_path()
│   - validate_path()
└── routes.py (40 lines)
    - GET /api/series
    - POST /api/series
    - PUT /api/series/<id>
    - DELETE /api/series/<id>
    - POST /api/series/<id>/move
    - POST /api/series/<id>/scan
```

**Total**: ~320 lines across 7 files

---

### 4. Volumes Module

```
frontend/api/volumes/
├── __init__.py
├── crud.py (70 lines)
│   - create_volume()
│   - read_volume()
│   - update_volume()
│   - delete_volume()
├── formats.py (50 lines)
│   - update_format()
│   - update_digital_format()
│   - validate_format()
└── routes.py (40 lines)
    - POST /api/series/<id>/volumes
    - PUT /api/volumes/<id>
    - DELETE /api/volumes/<id>
    - PUT /api/collection/volume/<id>/format
```

**Total**: ~160 lines across 4 files

---

### 5. Chapters Module

```
frontend/api/chapters/
├── __init__.py
├── crud.py (70 lines)
│   - create_chapter()
│   - read_chapter()
│   - update_chapter()
│   - delete_chapter()
└── routes.py (40 lines)
    - POST /api/series/<id>/chapters
    - PUT /api/chapters/<id>
    - DELETE /api/chapters/<id>
```

**Total**: ~110 lines across 3 files

---

### 6. Settings Module

```
frontend/api/settings/
├── __init__.py
├── general.py (50 lines)
│   - get_settings()
│   - update_settings()
│   - validate_settings()
├── groq_keys.py (50 lines)
│   - get_groq_key_status()
│   - set_groq_key()
│   - delete_groq_key()
│   - validate_key()
└── routes.py (40 lines)
    - GET /api/settings
    - PUT /api/settings
    - GET /api/settings/groq-api-key
    - PUT /api/settings/groq-api-key
    - DELETE /api/settings/groq-api-key
```

**Total**: ~140 lines across 4 files

---

### 7. Collection Module

```
frontend/api/collection/
├── __init__.py
├── items.py (60 lines)
│   - add_to_collection()
│   - remove_from_collection()
│   - update_item()
│   - get_collection_items()
├── stats.py (50 lines)
│   - get_collection_stats()
│   - calculate_value()
│   - calculate_progress()
├── formats.py (50 lines)
│   - update_volume_format()
│   - update_digital_format()
│   - validate_format()
└── routes.py (40 lines)
    - GET /api/collection
    - POST /api/collection
    - PUT /api/collection/<id>
    - DELETE /api/collection/<id>
    - GET /api/collection/stats
```

**Total**: ~200 lines across 5 files

---

### 8. Integrations Module

```
frontend/api/integrations/
├── __init__.py
├── home_assistant.py (50 lines)
│   - get_ha_sensor_data()
│   - get_ha_setup_instructions()
│   - format_ha_data()
├── homarr.py (50 lines)
│   - get_homarr_data()
│   - get_homarr_setup_instructions()
│   - format_homarr_data()
└── routes.py (30 lines)
    - GET /api/integrations/home-assistant
    - GET /api/integrations/home-assistant/setup
    - GET /api/integrations/homarr
    - GET /api/integrations/homarr/setup
```

**Total**: ~130 lines across 4 files

---

## Implementation Plan

### Phase 1: Create Directory Structure
```bash
mkdir -p frontend/api/{dashboard,calendar,series,volumes,chapters,settings,collection,integrations}
touch frontend/api/__init__.py
touch frontend/api/*//__init__.py
```

### Phase 2: Extract Services (Business Logic)
1. Extract dashboard stats → `dashboard/stats.py`
2. Extract calendar logic → `calendar/events.py`
3. Extract series operations → `series/crud.py`, `series/search.py`, etc.
4. ... (continue for all modules)

### Phase 3: Create Routes
1. Create `dashboard/routes.py` with endpoint definitions
2. Create `calendar/routes.py` with endpoint definitions
3. ... (continue for all modules)

### Phase 4: Update Imports
1. Update `frontend/api/__init__.py` to register all blueprints
2. Update `backend/internals/server.py` to import from new structure

### Phase 5: Remove Old Files
1. Delete old `api.py` (after verification)
2. Delete old `api_dashboard.py`, `api_calendar.py`, `api_integrations.py`

---

## Benefits of Micro-Services Architecture

### For Large Teams
✅ **Parallel Development**: 8+ developers can work simultaneously on different modules  
✅ **Clear Ownership**: Each team member owns one module  
✅ **Reduced Conflicts**: Minimal git merge conflicts  
✅ **Faster Reviews**: Small files = quick code reviews  
✅ **Easy Onboarding**: New developers can understand one module quickly  

### For Code Quality
✅ **Single Responsibility**: Each file has one clear purpose  
✅ **Easier Testing**: Small files = easier unit tests  
✅ **Better Maintainability**: Reduced cognitive load  
✅ **Scalability**: Easy to add new features  
✅ **Reusability**: Services can be imported elsewhere  

### For DevOps
✅ **Independent Deployment**: Deploy one module without affecting others  
✅ **Easier Rollback**: Revert one module without full rollback  
✅ **Better Monitoring**: Monitor individual modules  
✅ **Faster Debugging**: Isolate issues to specific modules  

---

## File Size Comparison

### Current (Monolithic)
| File | Lines | Complexity |
|------|-------|-----------|
| api.py | 2,293 | ⚠️ Very High |
| **Total** | **2,293** | |

### Proposed (Micro-Services)
| Module | Files | Total Lines | Avg per File |
|--------|-------|------------|-------------|
| Dashboard | 4 | 120 | 30 |
| Calendar | 4 | 130 | 32 |
| Series | 7 | 320 | 45 |
| Volumes | 4 | 160 | 40 |
| Chapters | 3 | 110 | 36 |
| Settings | 4 | 140 | 35 |
| Collection | 5 | 200 | 40 |
| Integrations | 4 | 130 | 32 |
| **Total** | **35** | **1,310** | **37** |

### Reduction
- **Files**: 1 → 35 (+3,400% more files)
- **Lines per file**: 2,293 → 37 (-98% smaller)
- **Complexity**: Very High → Low
- **Team capacity**: 1 developer → 8+ developers

---

## Example: Dashboard Module

### Before (in api.py)
```python
# 100+ lines mixed with other code
@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    # ... 80 lines of code ...
```

### After (Micro-Services)

**`frontend/api/dashboard/__init__.py`**
```python
from flask import Blueprint
from .routes import dashboard_routes

dashboard_bp = Blueprint('dashboard', __name__)
dashboard_bp.register_blueprint(dashboard_routes)

__all__ = ['dashboard_bp']
```

**`frontend/api/dashboard/stats.py`**
```python
from backend.internals.db import execute_query

def get_manga_count():
    result = execute_query("SELECT COUNT(*) as count FROM series WHERE content_type = 'manga'")
    return result[0]["count"] if result else 0

def get_books_count():
    result = execute_query("SELECT COUNT(*) as count FROM series WHERE content_type = 'book'")
    return result[0]["count"] if result else 0

def get_authors_count():
    result = execute_query("SELECT COUNT(*) as count FROM authors")
    return result[0]["count"] if result else 0

def get_collection_stats():
    owned = execute_query("SELECT COUNT(*) as count FROM collection_items WHERE ownership_status = 'OWNED'")
    read = execute_query("SELECT COUNT(*) as count FROM collection_items WHERE read_status = 'READ'")
    value = execute_query("SELECT SUM(purchase_price) as total FROM collection_items")
    
    return {
        "owned_volumes": owned[0]["count"] if owned else 0,
        "read_volumes": read[0]["count"] if read else 0,
        "collection_value": value[0]["total"] if value and value[0]["total"] else 0
    }
```

**`frontend/api/dashboard/events.py`**
```python
from backend.features.calendar import get_calendar_events
from datetime import datetime

def get_today_events():
    today = datetime.now().strftime('%Y-%m-%d')
    return get_calendar_events(today, today)

def format_events(events):
    return [
        {
            "id": e["id"],
            "title": e["title"],
            "date": e["date"],
            "type": e["type"]
        }
        for e in events
    ]
```

**`frontend/api/dashboard/routes.py`**
```python
from flask import Blueprint, jsonify
from .stats import *
from .events import *

dashboard_routes = Blueprint('dashboard_routes', __name__)

@dashboard_routes.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    return jsonify({
        "stats": {
            "manga_series_count": get_manga_count(),
            "books_count": get_books_count(),
            "authors_count": get_authors_count(),
            **get_collection_stats()
        },
        "today_events": format_events(get_today_events())
    })
```

**Total**: 4 files, ~120 lines (vs 100+ lines in monolithic api.py)

---

## Estimated Effort

| Phase | Task | Hours | Difficulty |
|-------|------|-------|-----------|
| 1 | Create directory structure | 0.5 | Easy |
| 2 | Extract dashboard | 1 | Easy |
| 2 | Extract calendar | 1 | Easy |
| 2 | Extract series | 2 | Medium |
| 2 | Extract volumes | 1 | Easy |
| 2 | Extract chapters | 1 | Easy |
| 2 | Extract settings | 1 | Easy |
| 2 | Extract collection | 1.5 | Medium |
| 2 | Extract integrations | 1 | Easy |
| 3 | Update imports | 1 | Easy |
| 4 | Testing | 2 | Medium |
| **Total** | | **12 hours** | **Medium** |

---

## Team Collaboration Example

With this structure, 8 developers can work in parallel:

```
Developer 1: Dashboard module
Developer 2: Calendar module
Developer 3: Series module (CRUD)
Developer 4: Series module (Search, Move, Scan)
Developer 5: Volumes & Chapters
Developer 6: Settings & Groq keys
Developer 7: Collection module
Developer 8: Integrations module
```

**No conflicts!** Each developer works on a separate directory.

---

## Next Steps

1. **Decide**: Do you want to implement this aggressive refactoring?
2. **Plan**: Create a timeline for implementation
3. **Assign**: Assign modules to team members
4. **Execute**: Implement in parallel
5. **Test**: Comprehensive testing
6. **Deploy**: Roll out gradually

---

## Questions?

- Should we implement this now?
- Do you want to start with one module (e.g., Dashboard)?
- Should we keep backward compatibility?
- Any other preferences?

---

**Status**: Strategy Ready  
**Recommendation**: ⭐⭐⭐⭐⭐ Highly Recommended for Large Teams
