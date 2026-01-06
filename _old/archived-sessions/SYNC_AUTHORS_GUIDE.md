# Sync Authors Guide

## Problem

Authors are stored in the `series.author` field, but the Authors page displays authors from the `authors` table. This means:
- Authors from existing books don't appear in the Authors page
- No links exist between authors and their books in the `author_books` table

## Solution

Use the `sync_authors.py` script to:
1. Extract unique authors from the `series.author` field
2. Create entries in the `authors` table
3. Link authors to their books via `author_books` table

## How to Use

### Run the Sync Script

```bash
cd /home/darius/Documents/Git/Readloom
python tests/sync_authors.py
```

### Output Example

```
Found 2 unique authors in series table:
  - Navessa Allen
  - Yukinobu Tatsu

Syncing authors...
  ✓ Author 'Navessa Allen' already exists (ID: 1)
    → Linked to series ID 3
  ✓ Created author 'Yukinobu Tatsu' (ID: 2)
    → Linked to series ID 2

✓ Author sync completed successfully!

Final stats:
  Authors: 2
  Author_books links: 2
```

## What the Script Does

1. **Finds all unique authors** from the `series.author` field
2. **Creates author entries** in the `authors` table (if not exists)
3. **Links authors to books** via the `author_books` table
4. **Reports statistics** on what was synced

## After Syncing

- Refresh the Authors page: http://127.0.0.1:7227/authors
- You should now see all authors from your books
- Click on an author to see their books

## Automatic Syncing

To automatically sync authors when adding new books:

1. When a book is added with an author name
2. Check if author exists in `authors` table
3. If not, create it
4. Link via `author_books` table

This can be implemented in the book import/add functionality.

## Database Structure

### Authors Table
```
id | name | biography | birth_date | ...
```

### Author_Books Table
```
id | author_id | series_id
```

### Series Table
```
id | title | author | ...
```

## Troubleshooting

### Authors still not showing?
1. Run the sync script again
2. Restart the server
3. Hard refresh browser (Ctrl+F5)

### Script says "Database not found"?
1. Make sure you're in the correct directory
2. Check that `data/db/readloom.db` exists

### Authors showing but no books linked?
1. Check that `author_books` table has entries
2. Run sync script again
3. Verify series have author names set

## Next Steps

1. Run the sync script: `python tests/sync_authors.py`
2. Restart server: `Ctrl+C` then `python run_dev.py`
3. Go to Authors page: http://127.0.0.1:7227/authors
4. See your authors!

---

**Status**: ✅ Ready to use
