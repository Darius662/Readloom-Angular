# Readloom Database and README File Structure

## Overview
Readloom stores metadata in two places:
1. **SQLite Database** - Primary storage for all structured data
2. **README Files** - Portable metadata files stored alongside content folders

This dual-storage approach ensures metadata portability and recovery capabilities.

---

## Database Schema

### Series Table
Stores information about manga, books, and comics.

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique series identifier |
| `title` | TEXT NOT NULL | Series/book title |
| `description` | TEXT | Series/book description |
| `author` | TEXT | Author name |
| `publisher` | TEXT | Publisher name |
| `cover_url` | TEXT | URL to cover image |
| `status` | TEXT | Series status (ONGOING, COMPLETED, ANNOUNCED, CANCELLED) |
| `content_type` | TEXT DEFAULT 'MANGA' | Type: MANGA, MANHWA, MANHUA, COMICS, NOVEL, BOOK, OTHER |
| `metadata_source` | TEXT | Source provider (AniList, GoogleBooks, OpenLibrary, etc.) |
| `metadata_id` | TEXT | ID from metadata provider |
| `custom_path` | TEXT | Custom folder path for series |
| `isbn` | TEXT | ISBN number (for books) |
| `published_date` | TEXT | Publication date |
| `subjects` | TEXT | Comma-separated subjects/genres |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

### Volumes Table
Stores volume/book information within a series.

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique volume identifier |
| `series_id` | INTEGER NOT NULL | Foreign key to series |
| `volume_number` | TEXT NOT NULL | Volume number (e.g., "1", "2.5") |
| `title` | TEXT | Volume title |
| `description` | TEXT | Volume description |
| `cover_url` | TEXT | Volume cover URL |
| `release_date` | TEXT | Release date |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

### Chapters Table
Stores chapter information.

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique chapter identifier |
| `series_id` | INTEGER NOT NULL | Foreign key to series |
| `volume_id` | INTEGER | Foreign key to volume |
| `chapter_number` | TEXT NOT NULL | Chapter number |
| `title` | TEXT | Chapter title |
| `description` | TEXT | Chapter description |
| `release_date` | TEXT | Release date |
| `status` | TEXT | Chapter status |
| `read_status` | TEXT DEFAULT 'UNREAD' | Read status (UNREAD, READING, READ) |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

### Authors Table
Stores author information.

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique author identifier |
| `name` | TEXT NOT NULL | Author name |
| `description` | TEXT | Short description |
| `biography` | TEXT | Full biography |
| `birth_date` | TEXT | Birth date |
| `death_date` | TEXT | Death date |
| `photo_url` | TEXT | Author photo URL |
| `provider` | TEXT | Metadata provider (OpenLibrary, etc.) |
| `provider_id` | TEXT | ID from metadata provider |
| `folder_path` | TEXT | Path to author folder |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

### Collections Table
Stores collection information.

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique collection identifier |
| `name` | TEXT NOT NULL | Collection name |
| `description` | TEXT | Collection description |
| `content_type` | TEXT | Type of content (MANGA, BOOK, COMIC) |
| `is_default` | BOOLEAN | Is this the default collection |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

### Root Folders Table
Stores root folder paths for collections.

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY | Unique root folder identifier |
| `name` | TEXT NOT NULL | Root folder name |
| `path` | TEXT NOT NULL | Absolute path to folder |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

---

## README File Structures

### Book/Manga Series README.txt
Located in: `{RootFolder}/{Author}/{SeriesTitle}/README.txt`

**Format:**
```
Series: {title}
ID: {series_id}
Type: {BOOK|MANGA|COMIC}
Provider: {metadata_source}
MetadataID: {metadata_id}
Author: {author}
Publisher: {publisher}
ISBN: {isbn}
Genres: {genre1,genre2,genre3}
CoverURL: {cover_url}
PublishedDate: {published_date}
Subjects: {subject1,subject2,subject3}
Description: {description}
Created: {YYYY-MM-DD HH:MM:SS}


This folder is managed by Readloom. Place your e-book files here.
```

**Example:**
```
Series: Behind the Net
ID: 160
Type: BOOK
Provider: GoogleBooks
MetadataID: Ra8tEQAAQBAJ
Author: Stephanie Archer
Publisher: Random House
ISBN: 9798217091126
Genres: Fiction / Romance / Contemporary,Fiction / Romance / Sports,Fiction / Women
CoverURL: https://books.google.com/books/publisher/content?id=Ra8tEQAAQBAJ&...
PublishedDate: 2025-01-14
Subjects: Fiction / Romance / Contemporary,Fiction / Romance / Sports,Fiction / Women
Description: He's the hot hockey player she had a crush on in high school...
Created: 2025-11-13 00:17:37


This folder is managed by Readloom. Place your e-book files here.
```

### Author README.md
Located in: `{RootFolder}/{AuthorName}/README.md`

**Format:**
```
ID: {author_id}
Type: AUTHOR
Provider: {provider}
MetadataID: {provider_id}
Author: {name}
CoverURL: {photo_url}
BirthDate: {birth_date}
Description: {description}
Biography: {biography}
Created: {DD.MM.YYYY}
Source: {source_url}
NotableWorks:
    {work1}
    {work2}
    {work3}
    {work4}
    {work5}
OpenLibraryURL: {openlibrary_url}

This folder is managed by Readloom. Place your e-book files here.
```

**Example:**
```
ID: 42
Type: AUTHOR
Provider: OpenLibrary
MetadataID: OL123456A
Author: Stephanie Archer
CoverURL: https://covers.openlibrary.org/a/OL123456A-M.jpg
BirthDate: 1985-03-15
Description: Contemporary romance author known for sports romance novels
Biography: Stephanie Archer is a bestselling contemporary romance author...
Created: 13.11.2025
Source: https://openlibrary.org/authors/OL123456A
NotableWorks:
    Behind the Net
    The Fake Out
    The Wingman
    Love on Ice
    Scoring Goals
OpenLibraryURL: https://openlibrary.org/authors/OL123456A

This folder is managed by Readloom. Place your e-book files here.
```

---

## Data Flow

### When Importing a Book/Manga:

1. **User searches** for a book/manga in the app
2. **Metadata is fetched** from provider (GoogleBooks, AniList, OpenLibrary, etc.)
3. **Series is created** in database with all metadata:
   - Title, Author, Publisher, ISBN, Published Date
   - Description, Cover URL, Subjects/Genres
   - Metadata Source and ID for future lookups
4. **Folder structure is created**:
   - `{RootFolder}/{Author}/{SeriesTitle}/`
5. **README.txt is created** with all metadata fields
6. **Author is auto-created** if not already in database
7. **Author README.md is created** with author metadata

### When Scanning Folders:

1. **Folders are discovered** from root paths
2. **README.txt is read** from each series folder
3. **Metadata is extracted** from README.txt
4. **Series is created** in database with README metadata
5. **Author is auto-created** from author folder structure
6. **E-book files are scanned** and added to volumes

### When Updating Series Metadata:

1. **Database is updated** with new metadata
2. **README.txt is automatically synced** with new values
3. **Author README.md is synced** if author data changes
4. **All changes are logged** for audit trail

---

## Metadata Fields by Content Type

### Books
- **Required**: Title, Author, ISBN, Published Date
- **Optional**: Publisher, Description, Subjects, Cover URL
- **Provider**: GoogleBooks, OpenLibrary, Amazon, Goodreads

### Manga/Comics
- **Required**: Title, Author
- **Optional**: Publisher, Description, Genres, Cover URL, Status
- **Provider**: AniList, MyAnimeList, MangaDex, MangaUpdates

### Authors
- **Required**: Name
- **Optional**: Biography, Birth Date, Death Date, Photo URL
- **Notable Works**: Top 5 works by the author
- **Provider**: OpenLibrary

---

## Key Features

### Metadata Portability
- README files can be manually edited and reorganized
- Metadata is preserved when folders are moved
- README files survive database resets

### Duplicate Prevention
- Metadata IDs are used to prevent duplicate imports
- Case-insensitive title matching as fallback
- Author deduplication across all import methods

### Automatic Enrichment
- If README has complete metadata (description, author, cover), provider enrichment is skipped
- Saves API calls and speeds up imports
- README metadata takes priority over provider defaults

### Folder Structure Support
- **Books**: `{RootFolder}/{Author}/{BookTitle}/`
- **Manga**: `{RootFolder}/{SeriesTitle}/` or `{RootFolder}/{Author}/{SeriesTitle}/`
- **Authors**: `{RootFolder}/{AuthorName}/`

---

## File Encoding

- **README.txt**: UTF-8 encoding with error replacement
- **README.md**: UTF-8 encoding with error replacement
- Supports international characters, em-dashes, and special Unicode characters
- Resolves Windows cp1252 encoding limitations

---

## Timestamps

- **Database**: ISO 8601 format with timezone (CURRENT_TIMESTAMP)
- **README.txt**: `YYYY-MM-DD HH:MM:SS` format
- **README.md**: `DD.MM.YYYY` format
- **Created timestamps** are preserved during updates

---

## Related Functions

### Database Operations
- `backend/internals/db.py`: `setup_db()` - Creates/updates schema
- `backend/internals/db.py`: `execute_query()` - Executes SQL queries

### README Operations
- `backend/base/helpers.py`: `ensure_readme_file()` - Creates/updates series README.txt
- `backend/base/helpers.py`: `read_metadata_from_readme()` - Reads series metadata
- `backend/features/author_readme_sync.py`: `ensure_author_readme_file()` - Creates/updates author README.md
- `backend/features/author_readme_sync.py`: `read_metadata_from_author_readme()` - Reads author metadata

### Import Operations
- `backend/features/ebook_files.py`: `discover_and_create_series()` - Discovers and imports series
- `backend/features/ebook_files.py`: `_process_series_directory()` - Processes individual series
- `backend/features/ebook_files.py`: `scan_for_ebooks()` - Main scan function

---

## Maintenance

### Updating All README Files
```bash
python update_readme_files.py
```
Or via API:
```
POST /api/readme/update-all
```

### Database Cleanup
- Orphaned authors are automatically deleted
- Series deletion preserves README files
- Manual recovery possible from README files

### Verification
- Check database schema: `PRAGMA table_info(series)`
- Check README files: Look in series/author folders
- Verify metadata: Compare database values with README content
