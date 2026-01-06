# Calendar Entry Creation: Search Import vs File System Import

## Overview
Calendar entries are created through volumes with `release_date` values. Both paths now follow the same logic, but here's the detailed comparison.

---

## SEARCH IMPORT PATH (Adding via Search)
**Entry Point**: `frontend/api_enhanced_book_import.py` → Search and add "The New Gate"

### Step 1: User Searches and Adds Series
```
User clicks "Add to Library" on search result
↓
api_enhanced_book_import.py calls import_manga_to_collection()
```

### Step 2: Series Creation
**File**: `backend/features/metadata_service/facade.py` - `import_manga_to_collection()` (lines 508-1009)

```python
# 1. Get manga details from provider (AniList, MangaDex, etc.)
manga_details = get_manga_details(manga_id, provider)

# 2. Create series in database
INSERT INTO series (
    title, description, author, publisher, cover_url, status, 
    content_type, metadata_source, metadata_id, ...
) VALUES (...)
series_id = cursor.lastrowid

# 3. Sync author (if applicable)
sync_author_for_series(series_id, author_name)
```

### Step 3: Volume Creation (CRITICAL FOR CALENDAR)
**File**: `backend/features/metadata_service/facade.py` (lines 697-769)

#### Option A: Provider Has Volumes
```python
if "volumes" in manga_details and manga_details["volumes"]:
    for volume in manga_details["volumes"]:
        INSERT INTO volumes (
            series_id, volume_number, title, description, 
            cover_url, release_date
        ) VALUES (
            series_id,
            volume.get("number"),
            volume.get("title"),
            volume.get("description"),
            volume.get("cover_url"),
            volume.get("release_date") or volume.get("date")  # ← RELEASE DATE
        )
```

**Example for "The New Gate"**:
- Volume 1: release_date = "2025-12-20"
- Volume 2: release_date = "2026-01-10"
- Volume 3: release_date = "2026-02-15"
- etc.

#### Option B: Provider Has No Volumes (Fallback)
```python
if create_volumes:  # No volumes from provider
    for i in range(1, 5):  # Create 4 default volumes
        volume_date = start_date + timedelta(days=i * 90)
        release_date_str = volume_date.strftime("%Y-%m-%d")
        
        INSERT INTO volumes (
            series_id, volume_number, title, description, 
            cover_url, release_date
        ) VALUES (
            series_id,
            str(i),
            f"Volume {i}",
            "",
            "",
            release_date_str  # ← SPACED 90 DAYS APART
        )
```

**Example for Ongoing Series**:
- Volume 1: release_date = "2025-09-20" (90 days ago)
- Volume 2: release_date = "2025-12-20" (today)
- Volume 3: release_date = "2026-03-20" (90 days from now)
- Volume 4: release_date = "2026-06-20" (180 days from now)

### Step 4: Chapter Creation
**File**: `backend/features/metadata_service/facade.py` (lines 771-824)

```python
for chapter in chapter_list:
    INSERT INTO chapters (
        series_id, volume_id, chapter_number, title, 
        description, release_date, status, read_status
    ) VALUES (
        series_id,
        volume_id,
        chapter.get("number"),
        chapter.get("title"),
        "",
        chapter.get("date") or chapter.get("release_date"),  # ← CHAPTER DATE
        "ANNOUNCED",
        "UNREAD"
    )
```

### Step 5: Calendar Update
**File**: `frontend/api_enhanced_book_import.py` (lines 273-285)

```python
try:
    from backend.features.calendar import update_calendar
    update_calendar(series_id=result.get('series_id'))
except Exception as e:
    LOGGER.error(f"Error updating calendar after import: {e}")
```

---

## FILE SYSTEM IMPORT PATH (Importing from Disk)
**Entry Point**: `backend/features/ebook_files.py` → Scan for e-books

### Step 1: Series Discovery
**File**: `backend/features/ebook_files.py` - `discover_and_create_series()` / `_process_series_directory()`

```
User clicks "Scan for E-books"
↓
scan_for_ebooks() is called
↓
discover_and_create_series() finds series folders
↓
_process_series_directory() processes each series
↓
Series created in database with metadata from README.txt
```

### Step 2: Series Creation
**File**: `backend/features/ebook_files.py` (lines 685-695)

```python
# Read metadata from README.txt
readme_metadata = read_metadata_from_readme(series_dir)

# Create series in database
INSERT INTO series (
    title, description, author, publisher, cover_url, status, 
    content_type, metadata_source, metadata_id, isbn, 
    published_date, subjects, star_rating, reading_progress, 
    user_description, created_at, updated_at
) VALUES (...)
series_id = new_series[0]['id']

# Sync author
sync_author_for_series(series_id, author)
```

### Step 3: Metadata Enrichment (NEW - CRITICAL FOR CALENDAR)
**File**: `backend/features/ebook_files.py` (lines 728-729)

```python
# Call enrichment to fetch provider metadata
enrich_series_metadata(series_id, series_dir_name, content_type)
```

### Step 4: Volume & Chapter Population (NEW - SAME AS SEARCH)
**File**: `backend/features/ebook_files.py` (lines 560-586)

Inside `enrich_series_metadata()`:

```python
# 1. Fetch full manga details from provider
if content_type == 'MANGA':
    provider_instance = AniListProvider()
    manga_details = provider_instance.get_manga_details(metadata_id)
elif content_type == 'BOOK':
    provider_instance = OpenLibraryProvider()
    manga_details = provider_instance.get_manga_details(metadata_id)

# 2. Use the SAME helper function as search import
from backend.features.metadata_service.facade import populate_volumes_and_chapters
chapters_added = populate_volumes_and_chapters(
    series_id, 
    manga_details, 
    metadata_source
)
```

**This calls**: `backend/features/metadata_service/facade.py` - `populate_volumes_and_chapters()` (lines 26-182)

Which does EXACTLY the same thing as search import:
- Creates volumes with release dates from provider
- Creates default volumes if provider has none
- Creates chapters with release dates
- Spaces default volumes 90 days apart

### Step 5: Calendar Update
**File**: `backend/features/ebook_files.py` (lines 1359-1367)

```python
try:
    from backend.features.calendar import update_calendar
    update_calendar()  # Update ALL series
except Exception as e:
    LOGGER.error(f"Error updating calendar after e-book scan: {e}")
```

---

## CALENDAR EVENT CREATION
**File**: `backend/features/calendar/calendar.py` - `update_calendar()` (lines 18-100)

This is the SAME for both paths:

```python
def update_calendar(series_id=None):
    # Get series to process
    if series_id:
        series_list = execute_query(
            "SELECT id, title FROM series WHERE id = ?", 
            (series_id,)
        )
    else:
        series_list = execute_query("SELECT id, title FROM series")
    
    for series in series_list:
        # Query volumes with release_date
        volumes = execute_query(
            """
            SELECT id, volume_number, title, release_date,
                   (SELECT metadata_source FROM series WHERE id = ?) as provider 
            FROM volumes 
            WHERE series_id = ? AND release_date IS NOT NULL
            """,
            (series_id, series_id)
        )
        
        for volume in volumes:
            release_date = datetime.fromisoformat(volume["release_date"])
            provider = volume.get('provider', '')
            is_anilist = provider == 'AniList'
            
            # For AniList: include ALL volumes
            # For others: only upcoming within calendar_range_days
            now = datetime.now()
            upcoming_days = settings.calendar_range_days
            
            is_valid = is_anilist or (
                release_date >= now and 
                release_date <= now + timedelta(days=upcoming_days)
            )
            
            if is_valid:
                # Check if event already exists
                existing = execute_query(
                    """
                    SELECT id FROM calendar_events 
                    WHERE series_id = ? AND volume_id = ? AND event_date = ?
                    """,
                    (series_id, volume["id"], volume["release_date"])
                )
                
                if not existing:
                    # Create calendar event
                    INSERT INTO calendar_events (
                        series_id, volume_id, title, description, 
                        event_date, event_type
                    ) VALUES (
                        series_id,
                        volume["id"],
                        f"Volume {volume['volume_number']} - {series['title']}",
                        f"Release of volume {volume['volume_number']}: {volume['title']}",
                        volume["release_date"],
                        "VOLUME_RELEASE"
                    )
```

---

## SIDE-BY-SIDE COMPARISON TABLE

| Aspect | Search Import | File System Import |
|--------|---------------|-------------------|
| **Entry Point** | User searches and clicks "Add" | User clicks "Scan for E-books" |
| **Series Creation** | `import_manga_to_collection()` | `discover_and_create_series()` |
| **Metadata Source** | Fetched from provider (AniList, MangaDex) | Read from README.txt |
| **Volume Creation** | Direct in `import_manga_to_collection()` | Via `populate_volumes_and_chapters()` helper |
| **Release Dates** | From provider OR default spaced 90 days | From provider OR default spaced 90 days |
| **Chapter Creation** | Direct in `import_manga_to_collection()` | Via `populate_volumes_and_chapters()` helper |
| **Calendar Update Call** | `update_calendar(series_id=...)` | `update_calendar()` (all series) |
| **Calendar Logic** | Same `update_calendar()` function | Same `update_calendar()` function |
| **Result** | Calendar shows volumes with release dates | Calendar shows volumes with release dates |

---

## KEY DIFFERENCES (Before Fix)

### Search Import (WORKED ✅)
1. Series created
2. **Volumes created with release_date** ← KEY
3. **Chapters created with release_date** ← KEY
4. `update_calendar()` called
5. Calendar events created from volumes

### File System Import (DIDN'T WORK ❌)
1. Series created
2. ~~Volumes created~~ ← MISSING
3. ~~Chapters created~~ ← MISSING
4. `update_calendar()` called
5. No calendar events (no volumes with release_date)

---

## AFTER FIX (Both Work ✅)

Both paths now:
1. Create series
2. **Fetch provider metadata** (AniList for MANGA, OpenLibrary for BOOK)
3. **Create volumes with release_date** (from provider or default)
4. **Create chapters with release_date** (from provider or default)
5. Call `update_calendar()`
6. Calendar events created from volumes

---

## VOLUME RELEASE DATE LOGIC

### From Provider (if available):
```
Dandadan (ONGOING):
- Volume 1: 2024-10-05
- Volume 2: 2024-11-02
- Volume 3: 2024-12-07
- Volume 4: 2025-01-04
- ...
```

### Default (if provider has no volumes):
```
Greatest Estate Developer (ONGOING, no provider volumes):
- Volume 1: 2025-09-20 (90 days ago)
- Volume 2: 2025-12-20 (today)
- Volume 3: 2026-03-20 (90 days from now)
- Volume 4: 2026-06-20 (180 days from now)
```

### Calendar Filtering:
- **AniList**: Shows ALL volumes (no date filtering)
- **Other providers**: Shows only upcoming within `calendar_range_days` setting

---

## SUMMARY

**Search Import**: Volumes + Chapters → Calendar Events ✅

**File System Import (Before)**: No Volumes/Chapters → No Calendar Events ❌

**File System Import (After)**: Volumes + Chapters (via `populate_volumes_and_chapters()`) → Calendar Events ✅

Both now use the **same logic** to create volumes and chapters with release dates, ensuring consistent calendar behavior.
