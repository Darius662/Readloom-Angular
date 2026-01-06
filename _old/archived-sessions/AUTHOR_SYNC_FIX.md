# Author Sync Fix

## Issue
Authors were not being automatically created and linked to series when importing books/manga. The Authors tab remained empty even after adding new content.

## Root Cause
The `sync_author_for_series()` function in `backend/features/authors_sync.py` was trying to query a `photo_url` column that doesn't exist in the authors table schema. This caused the query to fail silently, preventing author creation and linking.

**Error:**
```
sqlite3.OperationalError: no such column: a.photo_url
```

## Solution
Removed the non-existent `photo_url` column from the SELECT query. The author sync now:
1. Checks if author exists by name only
2. Creates author if it doesn't exist
3. Links author to series via `author_books` table
4. Attempts to enrich metadata (photo, biography) separately

## Changes Made

**File:** `backend/features/authors_sync.py`

### Before:
```python
author = execute_query("SELECT id, photo_url FROM authors WHERE name = ?", (author_name,))

if author:
    author_id = author[0]['id']
    # If author exists but has no photo, try to fetch it
    if not author[0]['photo_url']:
        _enrich_author_metadata(author_id, author_name)
```

### After:
```python
author = execute_query("SELECT id FROM authors WHERE name = ?", (author_name,))

if author:
    author_id = author[0]['id']
    # Try to enrich author metadata (photo, biography)
    _enrich_author_metadata(author_id, author_name)
```

## How It Works Now

When you import a book/manga:

1. **Series is created** with author information from metadata
2. **Author sync is triggered** via `sync_author_for_series()`
3. **Author is created or retrieved** from the authors table
4. **Author-series link is created** in the `author_books` table
5. **Metadata is enriched** (photo from OpenLibrary, biography from Groq AI)
6. **Author appears in Authors tab** with all linked works

## Testing

To verify the fix works:

1. Add a new book or manga to your library
2. Go to the **Authors** tab
3. The author should now appear in the list
4. Click on the author to see their works

## Database Schema

The system uses these tables:
- `authors` - Author information (id, name, biography, birth_date, created_at, updated_at)
- `author_books` - Links authors to series (author_id, series_id)
- `series` - Series/book information (includes author field)

## Files Modified

| File | Changes | Type |
|------|---------|------|
| `backend/features/authors_sync.py` | Removed photo_url column reference | Backend |

## Related Features

- **Author Import**: Automatically extracts author names from metadata
- **Author Enrichment**: Fetches author photos and biographies from external sources
- **Author Linking**: Creates relationships between authors and series
- **Authors Tab**: Displays all authors and their works

## Future Enhancements

1. Add migration to create `photo_url` column if needed
2. Add author photo display in Authors tab
3. Add author biography preview
4. Add author statistics (total works, content types)
5. Add ability to manually edit author information
