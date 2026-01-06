# Changelog

All notable changes to Readloom will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-12-18

### Fixed
- **Calendar Entries for File System Imports**:
  - Fixed missing calendar entries for volumes and chapters when importing series via file system
  - File system imports now fetch actual chapter data with real release dates from metadata providers (MangaFire, etc.)
  - Completed series now show correct historical release dates instead of placeholder future dates
  - Unified architecture between search imports and file system imports for consistent release data
  - Added `update_calendar()` call after series enrichment to ensure calendar events are created
  - Files: `backend/features/metadata_service/facade.py`, `backend/features/ebook_files.py`, `backend/features/calendar/calendar.py`

- **Database Schema Issues for Fresh Installations**:
  - Fixed "no such column" errors for `metadata_id`, `refresh_count`, `has_file`, `digital_format`, and `ebook_file_id`
  - Ensured all missing columns are properly created in `collection_items` and `manga_volume_cache` tables
  - Fixed duplicate column errors in database initialization
  - Files: `backend/internals/db.py`, `backend/migrations/0022_fix_manga_volume_cache_schema.py`

- **Function Signature Mismatches**:
  - Fixed `add_to_collection()` function signature to include `digital_format`, `has_file`, and `ebook_file_id` parameters
  - Fixed `NOT NULL constraint failed: collection_items.ownership_status` error in `scan_folder_structure`
  - Fixed `NOT NULL constraint failed: collection_items.read_status` error in folder-based volume creation
  - Files: `backend/features/collection/mutations.py`, `backend/features/ebook_files.py`

- **Chapter Data Handling**:
  - Fixed `TypeError: 'int' object is not iterable` when AniList returns chapter count as integer
  - `populate_volumes_and_chapters()` now properly handles both chapter lists and chapter counts
  - Chapters are created with actual release dates from providers instead of placeholder dates
  - Files: `backend/features/metadata_service/facade.py`

- **Volume Release Dates**:
  - Fixed volumes being created with past release dates, preventing them from appearing in calendar
  - Default volumes now have future release dates (spaced 90 days apart starting from today)
  - Files: `backend/features/metadata_service/facade.py`

## [0.3.0] - 2025-12-17

### Added
- **"Want to read" Collection Feature (#204)**:
  - New "Want to read" button in search results (manga and books)
  - Automatic creation of default "Want to read" collection per content type
  - Series added to "Want to read" collection are tagged with "want_to_read" tag
  - Automatic tag removal when reading progress is added (READING or READ status)
  - Uses same root folder as active/default collection for folder structure
  - Supports all content types: MANGA, MANHWA, MANHUA, COMIC, BOOK
  - Files: `frontend/api_metadata.py`, `backend/features/metadata_service/facade.py`, `frontend/templates/manga/search.html`, `frontend/templates/search.html`, `backend/features/collection/mutations.py`

- **Dynamic Want-to-Read Button with Toggle Functionality**:
  - "Want to Read" button on book and manga detail pages now dynamically reflects current state
  - Button shows filled bookmark icon (`fa-solid fa-bookmark`) when item is in want-to-read
  - Button shows outline bookmark icon (`fa-regular fa-bookmark`) when item is not in want-to-read
  - Button text changes to "Remove from Want to Read" when item is in cache
  - Button text shows "Add to Want to Read" when item is not in cache
  - Toggle functionality allows users to add/remove items directly from detail pages
  - Consistent UI across manga series detail page and book detail page
  - Files: `frontend/templates/manga/series.html`, `frontend/templates/books/book.html`, `frontend/api_metadata_fixed.py`

- **Want-to-Read Modal Enhancements**:
  - Modal now displays "Remove from Want to Read" button with filled bookmark icon for items in cache
  - "Go to Book/Manga" button appears for items already in the library
  - Modal backdrop properly cleans up when closed (fixes lingering gray overlay)
  - Dynamic button state management based on library and cache status
  - Files: `frontend/templates/want_to_read.html`, `frontend/ui_complete.py`

- **NotificationManager Improvements**:
  - All notifications now use consistent 5-second display duration
  - Timer display hidden by default, showing only notification message
  - Improved text clarity with increased font size (15px), font weight (600), and letter spacing
  - Enhanced contrast for all notification types (success, error, warning, info)
  - Better readability with improved line height (1.5)
  - Files: `frontend/static/js/notifications.js`, `frontend/static/css/notifications.css`

- **Persistent Notifications Across Page Navigation (#236)**:
  - Notifications now persist across page reloads and navigation events
  - Automatically stores active notifications before page unload
  - Restores notifications after page navigation or refresh
  - **Timer Continuation**: Notification timers continue from where they left off after refresh
    - Captures remaining time before page unload
    - Calculates elapsed time during page reload
    - Resumes with accurate remaining duration
    - Notifications expire if timer runs out during page transition
  - **Animation Persistence**: Restored notifications appear immediately without replaying animations
    - Slide-in animation skipped for restored notifications
    - Notifications appear in their final state instantly
    - Only new notifications trigger the slide-in animation
  - Supports both traditional page navigation and SPA (Single Page Application) navigation
  - Automatic detection of same-domain link clicks for notification persistence
  - Manual persistence option via `persistent` parameter in notification methods
  - Helper function `showPersistent()` for explicit persistent notifications
  - Graceful error handling with localStorage fallback
  - Notifications can be excluded from persistence with `data-no-persist` attribute on links
  - Files: `frontend/static/js/notifications.js`

### Fixed
- **Want-to-Read Cache Database Structure**:
  - Fixed incorrect `UNIQUE(series_id)` constraint that prevented multiple items from being added
  - Changed to correct `UNIQUE(metadata_source, metadata_id)` constraint
  - Added `content_type` column to track BOOK, MANGA, MANHWA, etc.
  - Automatic migration for existing databases
  - Files: `backend/internals/db.py`

- **Want-to-Read from Search Results**:
  - Fixed silent failures when adding items from search to want-to-read cache
  - Root cause: Incorrect UNIQUE constraint on series_id
  - Now properly stores items with metadata_source and metadata_id
  - Works for both books and manga from search results
  - Files: `backend/features/want_to_read_cache.py`, `backend/features/metadata_service/facade.py`

- **Want-to-Read from Manga Library**:
  - Fixed "Failed to load series data" error when adding manga from library to want-to-read
  - Exposed `seriesId` globally in manga series detail page
  - Properly passes series metadata to want-to-read endpoint
  - Files: `frontend/templates/manga/series.html`

- **Want-to-Read Removal Endpoint**:
  - Added DELETE method support to `/api/metadata/want-to-read/<provider>/<metadata_id>` endpoint
  - Allows removing items from want-to-read cache by metadata source and ID
  - Consistent endpoint for both adding (POST) and removing (DELETE) items
  - Files: `frontend/api_metadata_fixed.py`

- **Modal Backdrop Cleanup**:
  - Fixed lingering gray overlay that persisted after closing want-to-read item details modal
  - Added event listener to remove backdrop elements on modal hide
  - Restores body scroll when modal closes
  - Files: `frontend/templates/want_to_read.html`

- **Missing jsonify Import**:
  - Added missing `jsonify` import to `ui_complete.py`
  - Fixed `NameError: name 'jsonify' is not defined` when getting want-to-read details
  - Files: `frontend/ui_complete.py`

## [0.2.9] - 2025-12-17

### Added
- **Progressive Web App (PWA) Implementation**:
  - Full PWA support for installation on desktop and mobile devices
  - Service worker for offline functionality and caching
  - Offline fallback page with helpful information
  - Automatic cache management with intelligent caching strategies:
    - **Cache First**: Static assets (CSS, JS, images, fonts)
    - **Network First**: API calls and HTML pages with offline fallback
  - Background sync for queued actions when connection is restored
  - Push notification support with subscription management
  - App manifest with metadata, icons, and shortcuts
  - PWA initialization script with:
    - Service worker registration and update detection
    - Install prompt handling and custom install button
    - Offline detection with user notifications
    - Action queuing for offline operations
    - Push notification subscription management
  - Meta tags for mobile web app support (iOS, Android)
  - Separate caches for static assets, dynamic content, and API responses
  - Automatic update notifications when new version available
  - Files: `frontend/static/manifest.json`, `frontend/static/js/service-worker.js`, `frontend/static/js/pwa-init.js`, `frontend/templates/offline.html`, `frontend/ui/core.py`, `docs/features/PWA.md`

### Fixed
- **Service Worker Static Asset Caching**:
  - Modified service worker to gracefully handle missing static files
  - Removed CDN-hosted assets from `STATIC_ASSETS` list to prevent 404 errors
  - Added error handling to `cache.add()` operations to prevent installation failures
  - Service worker now continues installation even if some assets cannot be cached
  - Files: `frontend/static/js/service-worker.js`

- **Dashboard JavaScript Errors**:
  - Removed calls to non-existent functions (`loadAuthorsData()`, `loadBooksData()`, `loadMangaData()`)
  - These functions were attempting to access DOM elements that don't exist in the dashboard template
  - Fixes `TypeError: document.getElementById(...) is null` errors in browser console
  - Files: `frontend/templates/dashboard.html`

## [0.2.8] - 2025-12-15

### Added
- **Folder Browser Modal Implementation**:
  - Interactive folder browser modal for selecting folders across the application
  - Locations: Setup Wizard, Settings (Root Folders), Collections Manager, Collections Modals, Series Detail, Book Detail
  - Backend API endpoints for folder browsing:
    - `POST /api/folders/browse` - Lists folders in a directory with support for Windows drives
    - `POST /api/folders/validate` - Validates folder paths for existence and accessibility
  - Frontend folder browser modal with:
    - Current path display and navigation
    - Up button to navigate to parent directories (fixed path parsing for cross-platform compatibility)
    - Home button to return to home directory
    - Windows drive buttons (on Windows systems)
    - Folder list with clickable items for navigation
    - Select button to confirm folder choice
  - Supports both Windows (`\`) and Unix/Mac (`/`) path separators
  - Event delegation for button handlers ensures proper functionality
  - Validate buttons hidden in favor of folder browser navigation
  - Files: `frontend/api_folder_browser.py`, `run_dev.py`, multiple template files

### Fixed
- **Folder Browser Button Event Handlers**:
  - Changed from direct jQuery selectors to event delegation (`$(document).on()`)
  - Ensures buttons work even when modal is added after script execution
  - Applied to: Up, Home, and Select buttons across all templates

- **Folder Browser Up Button Path Navigation**:
  - Fixed path parsing logic to use `Math.max()` for finding last separator
  - Previous logic failed on Unix/Mac systems due to incorrect handling of `-1` return value
  - Now correctly handles both Windows (`\`) and Unix/Mac (`/`) path separators

- **Root Folder Creation Error Messages**:
  - Updated duplicate path error message to be user-friendly
  - Changed from generic "BAD REQUEST" to: "A root folder with this path already exists. Two root folders cannot have the same path."
  - Fixed error message display in UI by extracting error from API response
  - Applied to: `frontend/api_rootfolders.py`, `backend/features/collection/collections.py`, `frontend/static/js/collections_manager.js`

- **Folder Browser API Blueprint Registration**:
  - Added missing import and registration of `folder_browser_api_bp` in `run_dev.py`
  - Fixed API endpoint returning 400 when path parameter is null by defaulting to home directory
  - Files: `run_dev.py`, `frontend/api_folder_browser.py`

- **Folder Browser Root Directory Access**:
  - Extended folder picker to allow access to filesystem root directories
  - **Linux/Unix/Mac**: Added "Root (/)" button to navigate to filesystem root and access `/mnt`, `/opt`, `/srv`, etc.
  - **Windows**: Drive buttons (C:, D:, E:, etc.) now properly displayed and functional
  - Added `can_go_up` flag to prevent navigation above filesystem root
  - Added `is_root` flag to identify when at filesystem root
  - Improved error handling to skip inaccessible folders instead of failing entire browse
  - Users can now browse entire filesystem, not just home directory and subdirectories
  - Files: `frontend/api_folder_browser.py`, `frontend/static/js/folder-browser.js`

- **Persistent Sorting Preferences for Manga and Books (#200)**:
  - Sorting preferences now retained across page navigation using browser localStorage
  - Created `PersistentPreferences` utility class for managing user preferences
  - **Manga Library**: Sort preference (Name/Release Date) persists when navigating away and back
  - **Books Library**: Sort preference (Author/Title/Release Date) persists across navigation
  - Preferences stored with `readloom_prefs_` prefix in localStorage for namespace isolation
  - Default sort options: Manga defaults to "name", Books defaults to "author"
  - Graceful fallback to defaults if localStorage is unavailable
  - Files: `frontend/static/js/persistent-preferences.js`, `frontend/templates/manga/home.html`, `frontend/templates/books/home.html`, `frontend/templates/manga_layout.html`, `frontend/templates/books_layout.html`

- **Collection Manager Info Icons and Tooltips (#182)**:
  - Replaced all info alert boxes with info icons and tooltips across the application
  - **Collections Manager page**: Removed alert box, added info icon with tooltip to title
  - **Collections page (Settings tab)**: Removed alert box, added info icon with tooltip to title
  - **Setup Wizard**: Replaced description text with info icon and tooltip in Step 1 title
  - **Data Sync tab (Settings)**: Added info icons with tooltips to all 3 sync operations:
    - Author README Sync: Explains synchronization and merge mode behavior
    - Book README Sync: Explains synchronization and merge mode behavior
    - Manga README Sync: Explains synchronization and merge mode behavior
  - Tooltips appear on hover with right placement for better UX
  - Removed redundant alert boxes, keeping UI cleaner and more intuitive
  - Implemented Bootstrap tooltip initialization in all affected templates
  - Files: `frontend/templates/collections_manager.html`, `frontend/templates/collections.html`, `frontend/templates/settings.html`, `frontend/templates/setup_wizard.html`

- **Book Genres Display and Edit Modal Population**:
  - Fixed genres not displaying in book detail page by using `book.subjects` field directly
  - Updated edit modal to populate genres field with `book.subjects` instead of empty `book.genres`
  - Genres now display as badges in book detail page, matching Publisher and Description layout
  - Genres field in edit modal now pre-populates with existing genre data
  - Files: `frontend/templates/books/book.html`, `frontend/ui/books.py`

- **Series Update Success Notification**:
  - Simplified series update flow to remove failing collection assignment call
  - Series updates now complete successfully without collection assignment errors
  - Added NotificationManager success notification for better user feedback
  - Removed confusing "Series updated but collection assignment failed" warning message
  - Files: `frontend/templates/books/book.html`

- **README Sync for Book Edits**:
  - Fixed README.txt files not updating when book information is edited
  - Added custom_path support in sync_series_to_readme() function
  - Improved error handling for folder lookup during README sync
  - README files now properly sync when genres, title, author, and other metadata are updated
  - Files: `backend/features/readme_sync.py`

- **Notification System Migration to NotificationManager (#218)**:
  - Migrated all Bootstrap toast notifications to NotificationManager across entire codebase
  - Replaced 148 `showToast()` calls with `notificationManager` methods (success, error, warning, info)
  - Provides consistent, elegant notification design throughout the application
  - Improved user experience with better visual feedback for all operations
  - Files modified: 17 files across templates and JavaScript
    - Templates: `books/book.html`, `manga/series.html`, `books/authors.html`, `series_detail.html`, `books/search.html`, `manga/search.html`, `search.html`, `search_new.html`, `authors/author_detail.html`, `books/author.html`, `books_layout.html`, `manga_layout.html`, `authors/authors.html`
    - JavaScript: `static/js/ebook-manager.js`, `static/js/authors.js`, `static/js/book-recommendations.js`

- **User Data Persistence in README Files (#196)** - Task 4.1:
  - Star ratings (0-5) now stored in README files as `StarRating: {value}`
  - Reading progress (0-100%) stored as `ReadingProgress: {value}`
  - User notes/comments stored as `UserNotes: {text}`
  - User data automatically syncs to README files when book status is updated
  - User data is restored from README files during series import
  - `read_metadata_from_readme()` parses user data fields with proper type conversion
  - `sync_series_to_readme()` includes user data in README updates
  - Book status endpoint triggers automatic README sync after updates
  - Files: `backend/base/helpers.py`, `backend/features/readme_sync.py`, `frontend/api/series/routes.py`, `backend/features/ebook_files.py`

- **Smart Navigation After Deletion**:
  - **Books**: Redirects back to referrer page (where user came from)
    - Stores referrer in sessionStorage on book detail page load
    - Validates referrer is from same domain for security
    - Falls back to `/books` if no valid referrer
    - Files: `frontend/templates/books/book.html`
  
  - **Manga Series**: Always redirects to `/manga` library after deletion
    - Consistent experience for manga collection management
    - Files: `frontend/templates/manga/series.html`
  
  - **Authors**: Always redirects to `/authors` page after deletion
    - Improved UX with toast notifications instead of browser alerts
    - Shows loading state on delete button during operation
    - Files: `frontend/templates/authors/author_detail.html`

- **Auto-Refresh After Data Import**:
  - Page automatically refreshes 1.5 seconds after successful e-book scan
  - Allows success toast message to display before refresh
  - User sees confirmation that import completed before page updates
  - Applies to both book and manga series detail pages
  - Files: `frontend/templates/books/book.html`, `frontend/templates/manga/series.html`

### Fixed
- **Series Import Status Bug (#197)** - Task 4.2:
  - Fixed imported series defaulting to "Unknown status" (NULL value)
  - Series now created with `status = 'ONGOING'` as default
  - `enrich_series_metadata()` always called during import to fetch real status from provider (AniList for manga, OpenLibrary for books)
  - Status fetched using metadata_id from README metadata
  - `enrich_series_metadata()` preserves existing status unless it's None or 'Unknown', allowing provider status to override defaults
  - All imported series now display proper status values (ONGOING, COMPLETED, ANNOUNCED, CANCELLED) from their respective providers
  - Files: `backend/features/ebook_files.py`

- **Delete Series Modal Content Not Displaying**:
  - Modal now shows proper confirmation message with series name
  - Added checkbox for "Also delete e-book files from disk"
  - Matches design pattern from book deletion modal
  - Files: `frontend/templates/manga/series.html`

- **Delete Button Not Connected for Manga Series**:
  - Added complete delete functionality with event handlers
  - Delete button now properly triggers modal and deletion flow
  - Shows loading state and success feedback
  - Files: `frontend/templates/manga/series.html`

- **Delete Book Modal Not Closing After Deletion**:
  - Fixed modal not closing and user not being redirected to Books tab
  - Removed incorrect `response.success` check (API returns `{"message": "..."}`)
  - Fixed `showToast()` scope issue by defining function at global scope with proper hoisting
  - Changed from `bootstrap.Modal.getInstance()` to `bootstrap.Modal.getOrCreateInstance()` for reliability
  - Simplified redirect logic to always go to Books home page
  - Added inline toast creation in AJAX callbacks to avoid scope issues
  - Added console logging and timeout to AJAX request for better debugging
  - Files: `frontend/templates/books/book.html`

- **Book Series Import Title Bug**:
  - Fixed books being imported with folder names instead of README series titles
  - Example: "Game On" by Navessa Allen was incorrectly imported as "Game On Lincoln Pierce"
  - Root cause: Import logic used `series_dir_name` (folder name) instead of `readme_metadata.get('title')`
  - Solution: Updated both series creation locations to use series title from README metadata
  - Files: `backend/features/ebook_files.py` (lines 631, 797)

- **Book Author Metadata Overwrite Bug**:
  - Fixed author information from README being overwritten by external provider data
  - Example: "Game On" by Navessa Allen was being imported as "Game On" by Lincoln Pierce (from OpenLibrary)
  - Root cause: `enrich_series_metadata()` fetched external provider data without checking if README data already existed
  - Solution: Modified `enrich_series_metadata()` to preserve README metadata (author, description, cover_url)
  - Only status is now fetched from external providers if not already set in README
  - Files: `backend/features/ebook_files.py` (lines 456-464, 494-500, 539-545)

- **Digital Format Column Error on Volume Update**:
  - Added automatic column creation with fallback handling
  - Attempts to update column first, creates if missing
  - Handles race conditions where another process might add column
  - Retries update after column creation
  - Files: `frontend/api/volumes/formats.py`

- **Database Schema Issues**:
  - Added missing columns to series table: `user_description`, `star_rating`, `reading_progress`
  - Added missing tables: `recommendation_cache`, `manga_volume_cache`, `trending_manga`
  - Improved migration system error handling and reliability
  - Ensures both new and existing databases get all required schema elements
  - Files modified: `backend/internals/db.py`, `backend/internals/migrations.py`

### Changed
- **Database Initialization**:
  - `setup_db()` now creates all required tables directly
  - `run_migrations()` handles only schema changes not covered in setup_db()
  - More robust error handling for database operations

- **Delete User Experience**:
  - Replaced browser `alert()` dialogs with professional toast notifications
  - Added loading spinners to delete buttons during operation
  - Consistent 1-second delay before redirect across all deletion flows
  - Better error feedback with toast notifications

## [0.2.7] - 2025-12-14

### Added
- **Collection Form Validation (#185)** - Task 3.1, 3.2, 3.3:
  - **Task 3.1 (Add required indicators)**:
    - Added red asterisk (*) to "Name" and "Content Type" labels in Add/Edit Collection modals
    - Clearly indicates which fields are required
    - Files: `frontend/templates/settings.html`
  
  - **Task 3.2 (Inline required error messages)**:
    - Replaced toast notifications with inline error messages beneath form fields
    - Error messages display directly under the input field with red text
    - Form fields get Bootstrap `is-invalid` styling when errors occur
    - Client-side validation prevents form submission with empty required fields
    - Errors are cleared when modals are opened (fresh start)
    - Files: `frontend/templates/settings.html`, `frontend/static/js/collections_manager.js`
  
  - **Task 3.3 (Inline duplicate name/type errors)**:
    - API errors for duplicate collection name/type combinations now display inline
    - Duplicate errors show under the Name field instead of as toast notifications
    - Other API errors still use toast notifications for visibility
    - Improved error detection with keyword matching ("already exists", "duplicate")
    - Files: `frontend/static/js/collections_manager.js`
  
  - **Implementation details**:
    - Added `showCollectionError()` function to display inline errors
    - Added `clearCollectionErrors()` function to clear errors
    - Enhanced `saveCollection()` and `updateCollection()` functions with validation
    - Added error message containers in form HTML
    - Modal open events clear errors for fresh start

- **Collection Default Status Info Message**:
  - Added informative message under "Set as default collection" checkbox in Add Collection modal
  - Added same message to Edit Collection modal
  - Message informs users that setting a new default collection will remove default status from previous default
  - Improves UX by clarifying that only one collection can be default at a time
  - Files: `frontend/templates/settings.html`

- **Book Status Page (#187)** - Task 1.1:
  - Created dedicated "Reading Status" card on book detail pages
  - Added interactive 5-star rating system with visual feedback
  - Added reading progress tracking with 5 preset levels (0%, 25%, 50%, 75%, 100%)
  - Added "Your Notes" textarea for custom user descriptions
  - Implemented Save and Reset buttons for status management
  - Created database migration to add columns: `user_description`, `star_rating`, `reading_progress`
  - Created API endpoints: `PUT /api/books/<id>/status` and `GET /api/books/<id>/status`
  - Created JavaScript module for interactive star rating and form handling
  - Files: `backend/migrations/0021_add_book_status_tracking.py`, `frontend/templates/books/book.html`, `frontend/static/js/book-status.js`, `frontend/api.py`

- **Star Rating System Enhancements (#187)** - Task 1.2:
  - Added star rating display on book library cards (shows current rating or "Not rated yet")
  - Implemented rating filter dropdown in books library (All Ratings, 5 Stars, 4+ Stars, 3+ Stars, 2+ Stars, 1+ Stars, Unrated)
  - Added "Sort by Rating" option to library sorting dropdown
  - Created JavaScript module for dynamic filtering and sorting by rating
  - Books can be filtered by minimum rating threshold
  - Highest-rated books appear first when sorting by rating
  - Empty state message displays when no books match filter criteria
  - Files: `frontend/templates/books/home.html`, `frontend/static/js/book-library-filters.js`, `frontend/templates/books_layout.html`

- **Reading Status Tracking Enhancements (#187)** - Task 1.3:
  - Added reading progress bar overlay on book cover images (visual progress indicator at bottom of cover)
  - Progress bar appears as a thin colored bar at the bottom of each book cover
  - Implemented reading progress filter dropdown (All Progress, Completed 100%, In Progress 75%+, Half-way 50%+, Started 25%+, Not Started)
  - Added "Sort by Progress" option to library sorting dropdown
  - Books can be filtered by minimum progress threshold
  - Books with highest reading progress appear first when sorting by progress
  - Progress bar uses cyan/info color (#0dcaf0) with semi-transparent background
  - Files: `frontend/templates/books/home.html`, `frontend/static/js/book-library-filters.js`

- **UI Enhancement - Progress Bar Positioning**:
  - Moved reading progress bar from card body to book cover overlay
  - Progress bar now displays as a thin bar at the bottom of the book cover image
  - Cleaner card layout with progress indicator integrated into cover design
  - Better visual hierarchy - progress is immediately visible without scrolling card content

- **UI Enhancement - Progress Bar Floating Island Style**:
  - Redesigned progress bar as a floating island element with rounded corners
  - Progress bar now displays as a 28px tall rounded container at the bottom of book covers
  - Added gradient background (cyan to bright blue) for better visibility
  - Displays percentage text inside the progress bar with text shadow for readability
  - Added semi-transparent dark background (75% opacity) with blur effect for depth
  - Added box shadow for floating effect and visual separation from cover
  - Much more visible and prominent than the previous thin bar design
  - Updated JavaScript filters to work with new progress bar structure

- **Book Recommendations System (#186)** - Task 2.1 & 2.2:
  - **Task 2.1 (Category-only)**: Implemented category-based recommendations
    - Created API endpoint: `GET /api/books/<id>/recommendations/category`
    - Finds books with matching genres/categories
    - Returns up to 10 unique recommendations (excluding current book)
  
  - **Task 2.2 (AI-powered)**: Implemented AI-powered recommendations with fallback
    - Created API endpoint: `GET /api/books/<id>/recommendations/ai`
    - Uses AI provider to generate book recommendations based on:
      - Book title, author, genres/subjects
      - User's star rating of the book
    - AI generates list of recommended book titles and authors
    - Searches metadata providers for those books
    - Tries original book's metadata provider first, then falls back to others
    - Returns up to 10 recommendations from metadata providers
    - Falls back to category-only recommendations if AI fails
    - Supports all AI providers (Groq, Gemini, DeepSeek, Ollama)
  
  - **UI & Display**:
    - Added "Recommended for You" card on book detail pages
    - Displays recommendation cards with cover image, title, author, and rating
    - Each recommendation links to the book detail page
    - Shows different empty state messages based on recommendation method
    - Created JavaScript module for loading and displaying recommendations
    - Files: `frontend/api/series/routes.py`, `frontend/templates/books/book.html`, `frontend/static/js/book-recommendations.js`

### Fixed
- **Dropdown Arrow Display Issue**:
  - Fixed duplicate dropdown arrows appearing in all select elements (browser native + Bootstrap custom)
  - Modified CSS `appearance` property from `auto` to `none` for `select.form-select` elements
  - All dropdowns now display only the larger Bootstrap arrow for consistent styling
  - Files: `frontend/templates/base.html`

- **Book Status API Endpoints**:
  - Moved book status endpoints from old monolithic `api.py` to modular `frontend/api/series/routes.py`
  - Endpoints now properly registered in the series API blueprint
  - Fixed 404 errors when saving/retrieving book status
  - Endpoints: `PUT /api/books/<id>/status`, `GET /api/books/<id>/status`

- **Book Status Database Columns**:
  - Created migration `0021_add_book_status_tracking.py` to add columns to series table
  - Migration adds `user_description` (TEXT), `star_rating` (REAL), `reading_progress` (INTEGER) columns
  - Migration runs automatically at app startup via the migration system
  - Follows the same pattern as all other database migrations
  - Fixed database errors when trying to save book status

- **Book Status API - Removed is_book Constraint**:
  - Removed `is_book = 1` constraint from book status endpoints
  - Endpoints now work with any series record, not just those marked as books
  - Ensures compatibility with databases that may not have the `is_book` column yet
  - Allows book status tracking to work independently of content_type classification

- **Book Recommendations - Fixed Genre/Subject Column**:
  - Fixed API endpoint to use `subjects` column instead of non-existent `genres` column
  - Genres are stored in the `subjects` column as comma-separated strings
  - Updated recommendation queries to search the correct column
  - Recommendations now properly match books by shared subjects/genres

- **AI Recommendations - Fixed Provider API Calls**:
  - Updated AI recommendation generation to use correct provider APIs
  - Groq: Uses `client.chat.completions.create()`
  - Gemini: Uses `client.generate_content()`
  - DeepSeek: Uses `client.chat.completions.create()`
  - Ollama: Uses `client.generate()`
  - Added proper error handling for each provider type
  - AI recommendations now work correctly with all supported providers

- **Recommendations UI - Modal Display for Book Details**:
  - Changed "View Details" button to "Book Details"
  - Clicking "Book Details" now opens a modal instead of navigating away
  - Modal displays comprehensive book information matching search results:
    - Cover image with fallback placeholder
    - Author name
    - Star rating with visual stars
    - Publisher information
    - Publication date
    - ISBN number
    - Subjects/genres as badges
    - Full book description
    - Metadata source
  - Consistent with search results modal behavior
  - Prevents 404 errors from trying to navigate to metadata provider IDs
  - Fixed button click handlers using proper event delegation
  - Enhanced metadata extraction to handle various provider formats

- **Recommendations Caching System**:
  - Implemented recommendation caching to prevent redundant AI calls
  - Recommendations are cached with a hash of book details (subjects, rating, notes, progress)
  - Cache is automatically invalidated when book details change
  - AI is only called when book details are modified (rating, notes, progress, etc.)
  - Reduces API calls and provides consistent results across page refreshes
  - Created `recommendation_cache` table to store cached results
  - Returns `cached: true/false` flag in API response to indicate cache status

- **AI Prompt Enhancement**:
  - Updated AI prompt to consider user's notes/description
  - AI now factors in: genres, star rating, reading progress, and user notes
  - More personalized recommendations based on user's own thoughts about the book
  - Helps AI understand user preferences beyond just metadata

- **Recommendation Modal - Metadata API Integration**:
  - Recommendation modal now fetches full book details from metadata API
  - Uses same `/api/metadata/manga/{provider}/{id}` endpoint as search results
  - Displays complete book information: publisher, date, ISBN, genres, description
  - Handles both `genres` (array) and `subjects` (string) formats
  - Fallback to cached data if metadata API call fails
  - Consistent user experience between search and recommendations

- **Recommendation Cards - Layout Improvements**:
  - Recommendations now display as proper cards matching the Books tab layout
  - Fixed cover image display: uses 2:3 aspect ratio (proper book proportions, not square)
  - Cover images use `object-fit: cover` for proper scaling without stretching
  - Book titles truncated with "..." if they exceed 30 characters
  - Responsive grid layout: 1 col (mobile), 2 cols (tablet), 3 cols (desktop), 5 cols (large), 6 cols (extra-large)
  - Compact card design: minimal padding and spacing to reduce wasted space
  - Description in modal now has scrollable container with max-height of 200px
  - Consistent card styling with Books library for better UX
  - Smaller button text ("Details" instead of "Book Details") to fit compact design

## [0.2.6] - 2025-11-15

### Added
- **Book & Manga Card UX Improvements**:
  - Book and Manga library cards now treat the cover area as a clickable link
  - Clicking the cover (or placeholder) and the existing "View" button both navigate to the detail page
  - Title/author text remains non-clickable so text is still selectable
  - Applied to both initial page load and dynamically rendered filtered grids

- **Root-Level Tools Cleanup**:
  - Moved maintenance/diagnostic scripts out of the project root into a dedicated `tools/` folder
  - Scripts moved: `check_manga_route.py`, `check_scan_results.py`, `check_tables.py`, `clean_database.py`,
    `cleanup_authors.py`, `create_authors_tables.py`, `enrich_descriptions.py`, `query_trending.py`
  - Moved `DATABASE_AND_README_STRUCTURE.md` into `docs/technical/` for better documentation organization
  - Keeps repository root clean without impacting runtime behavior

### Fixed
- **Author README & Folder Path Sync (Fresh Start Safe)**:
  - `sync_author_readme()` now always resolves the author directory correctly when starting from a fresh database
  - If a series folder path exists, the author folder is derived from the parent of the series folder
    (e.g., `C:\Data\Author Name\Book Name` → author folder `C:\Data\Author Name`)
  - If no series path is available or extended schema columns are missing, falls back to the configured BOOK root
    and creates `{BookRoot}/{AuthorName}`
  - On successful sync, `authors.folder_path` is updated in the database, ensuring README sync no longer writes to
    the internal default ebook storage path
  - Guarded against older schemas where `series.folder_path` / `series.custom_path` may not exist
  - Files: `backend/features/author_readme_sync.py`

- **Author Creation/Re‑use Ensures README & Folder Path**:
  - Central `get_or_create_author()` helper now triggers `sync_author_readme()` for both existing and newly-created authors
    when `create_readme=True`
  - Guarantees that importing books via the Books tab (search/import flow) will also:
    - Create or update the author folder under the correct BOOK root
    - Write or refresh the author `README.md`
    - Persist `authors.folder_path` in the database
  - Aligns author folder creation with the book import folder structure (`{BookRoot}/{Author}/{BookTitle}`)
  - Files: `backend/features/authors_sync.py`, `backend/features/author_readme_sync.py`

- **Author README Sync Import Issues**:
  - Fixed incorrect imports introduced during earlier iterations (`get_root_folders` from `backend.base.helpers`)
    that caused the Author README sync API to fail entirely
  - Switched to the proper `get_root_folder_path()` helper in `backend.base.helpers_content_service`
  - Simplified `sync_all_author_readmes()` to rely on the improved `sync_author_readme()` logic and default
    folder resolution instead of trying to manually walk root folders with a non-existent helper
  - Files: `backend/features/author_readme_sync.py`, `backend/base/helpers_content_service.py`

### Changed
- **Consistent Author Folder Semantics**:
  - Documented and enforced that author folders represent the parent of book folders:
    - Books: `{BookRoot}/{AuthorName}/{BookTitle}`
    - Authors: `{BookRoot}/{AuthorName}`
  - All new logic for resolving author directories and updating `authors.folder_path` follows this convention,
    making fresh setups and re‑imports consistent across platforms (Windows/macOS/Linux)

## [0.2.5] - 2025-11-14

### Added
- **Manga Authors Exclusion**:
  - Manga/Manhwa/Manhua/Comic authors are NO LONGER added to the Authors table
  - Only BOOK and NOVEL content types sync authors to the Authors library
  - Prevents cluttering the Authors library with manga creators

- **Filter & Sort for Manga Library**:
  - Filter by manga name (partial match, case-insensitive)
  - Sort options: By Name (A-Z) or By Release Date (newest first)
  - Real-time filtering with Enter key support
  - Dynamic grid rendering with filtered results

- **Filter & Sort for Books Library**:
  - Filter by Author (partial match, case-insensitive)
  - Filter by Title (partial match, case-insensitive)
  - Filter by Release Year (YYYY format)
  - Sort options: By Author (A-Z), By Title (A-Z), or By Release Date (newest first)
  - Multiple simultaneous filters for advanced searching
  - Real-time filtering with Enter key support
  - Dynamic grid rendering with filtered results

- **Folder Renaming on Title/Name Update**:
  - Series folders automatically rename when manga/book title changes
  - Author folders automatically rename when author name changes
  - Handles special characters by converting to safe folder names
  - Gracefully merges folder contents if target folder already exists
  - Respects custom paths (skips rename for user-managed folders)
  - Non-blocking operation (rename failures don't prevent database updates)

<!-- ### Fixed
- Modal backdrop issue when editing series multiple times (backdrop now properly closes)
- Dropdown jitter and dark filter issues in "Link Root Folder to Collection" modal
- Mouse hover state causing modal flickering and unresponsive UI
- Dropdown interaction issues when modal is active -->

## [0.2.4] - 2025-11-13

### Added
- **Dynamic Book Library Display**:
  - "My Books" section now displays ALL books in the library (no hard limit)
  - Responsive grid layout that auto-wraps into multiple rows
  - Shows 6 books per row on desktop, responsive on smaller screens
  - Book count badge displays total number of books

- **Author README.md System**:
  - Each author now has a README.md file in their folder with complete metadata
  - README.md format matches book README.txt structure for consistency
  - Stores author metadata: ID, Name, Biography, Birth Date, Photo URL, Provider info
  - Includes top 5 notable works (books by the author)
  - Includes OpenLibrary URL for reference
  - Automatic creation when books are imported via search or file system
  - Portable README files (can be manually edited and reorganized)
  - Folder path tracked in database for internal use only (not in README)
  - UTF-8 encoding for international characters

- **Author Cards Split Buttons and Author Books Page Redesign**:
  - Split "View Details" button on author cards into two buttons: "View Details" and "View Books"
  - "View Details" opens author modal
  - "View Books" navigates to author's books page
  - Redesigned `/authors/{id}/books` page to match `/books` layout
  - Added book cover images with 320px height
  - Changed layout to responsive grid (1-6 columns based on screen size)
  - Split book action buttons into two: "View Book" (primary) and "Read" (outline)
  - Added book count badge in page header
  - Improved empty state with icon and search option
  - Added consistent styling with min-height for cards

- **Edit Author Modal in Authors Library**:
  - Added Edit Author modal with form for updating author details
  - Edit button in author details modal now opens modal instead of redirecting
  - Form includes: Name, Biography, Description, Birth Date, Death Date, Photo URL
  - Save button updates author in database and reloads page
  - Validation ensures author name is required
  - Loading state during save operation

- **Book and Manga README Sync Utilities**:
  - Added Book README Sync button to sync all book data to README.txt files
  - Added Manga README Sync button to sync all manga data to README.txt files
  - Both support merge mode to preserve existing README data
  - Shows sync statistics (total, synced, failed, errors)
  - API endpoints: `/api/series/sync-readme?merge=true/false` (books), `/api/series/sync-readme-manga?merge=true/false` (manga)
  - Files: `frontend/api/series/routes.py`, `frontend/templates/settings.html`

- **Basic E-Book Reader Implementation**:
  - Added `/books/{id}/read` route with basic reader UI
  - Features: Font size adjustment (12-24px), line height control (1-2x), theme selection (Light/Dark/Sepia)
  - Keyboard navigation: Arrow keys for scrolling
  - Settings persist in browser localStorage
  - Responsive design with sidebar for table of contents
  - Support for multiple file formats (PDF, EPUB, CBZ, CBR)
  - Files: `frontend/templates/books/reader.html`

- **Kavita E-Book Server Integration**:
  - Added Kavita integration in Settings → Integrations
  - Configure Kavita server URL, username, and password
  - Test connection button to verify Kavita server connectivity
  - Enable/disable integration toggle
  - Secure password handling (not returned in API responses)
  - API endpoints for settings management and library retrieval
  - Support for syncing libraries and series from Kavita
  - Files: `frontend/api/integrations/kavita.py`, `frontend/api/integrations/routes.py`, `frontend/templates/settings.html`

- **Author README Sync Improvements**:
  - Enhanced logging for debugging sync operations
  - Better error tracking and reporting
  - Detailed sync statistics with error messages
  - Improved folder creation and path handling

- **Author Books List Display in Modal**:
  - Changed author books display from grid to list format in author details modal
  - Each book shows: thumbnail photo, title, content type, volumes/chapters
  - Added "View" button to redirect to individual book details page
  - Improved readability and mobile responsiveness

- **Author README Sync Utility**:
  - Added Data Sync tab in Settings page
  - New "Sync Author READMEs" button to sync all author data from database to README files
  - Merge mode option: preserves existing README data while updating database values
  - All database fields written to README (including empty fields like BirthDate, DeathDate)
  - Non-database values in README are preserved when merge mode is enabled
  - Shows sync statistics: total authors, synced count, failed count, errors
  - API endpoint: `/api/authors/sync-readme?merge=true/false`
  - Files: `backend/features/author_readme_sync.py`, `frontend/api/authors/routes.py`, `frontend/templates/settings.html`

- **Manga Library Layout Improvements**:
  - Updated "Recent Series" header to show "My Manga" with series count badge
  - Matches book library layout for consistency
  - Responsive grid layout already in place (1-6 columns based on screen size)
  - Files: `frontend/templates/manga/home.html`

- **Author Edit and Delete Buttons in Modals**:
  - Added Edit and Delete buttons to author details modal in book search
  - Added Edit and Delete buttons to Author Details modal in Authors Library page
  - Buttons positioned in modal header (top right) next to close button
  - Edit button (blue pencil icon) redirects to author detail page for editing
  - Delete button (red trash icon) removes author and all associated books (README files preserved)
  - Buttons only appear when viewing authors from library (not from search results)
  - Confirmation dialog before deleting author
  - Loading state during deletion with spinner
  - Success/error notifications after action
  - Author details modal shows biography, photo, and book count
  - Click author name or view button to open details modal

### Fixed
- **Fixed Author folder_path Not Being Set During Book Import**:
  - Critical fix: Author's `folder_path` is now updated in database when book is imported
  - Previously, author was created without folder_path, causing README sync to use default location
  - Now updates author's folder_path to the correct root folder location (e.g., Y:\eBooks\Test_Data\Books\Navessa Allen)
  - Ensures subsequent README syncs use the correct folder path from database
  - Files: `frontend/api_enhanced_book_import.py`

- **Fixed Author README Sync Using Wrong Root Folder**:
  - Critical fix: `sync_all_author_readmes()` now uses the correct `folder_path` from database
  - Previously was creating READMEs in default ebook storage directory instead of actual book location
  - Now correctly passes `author_folder_path` from database to sync function
  - README files are now created in the correct location (e.g., Y:\eBooks\Test_Data\Books\Navessa Allen\README.md)
  - Added logging to show which folder_path is being used from database
  - Files: `backend/features/author_readme_sync.py`

- **Enhanced Author README Sync Diagnostics**:
  - Added comprehensive logging with [README SYNC] prefix for easy filtering
  - Logs directory existence, creation attempts, and write permissions
  - Logs file path and size after creation
  - Added permission check before writing (os.access)
  - Better error messages with traceback information
  - Helps diagnose why README files aren't being created
  - Files: `backend/features/author_readme_sync.py`

- **Missing sync_all_series_readmes Function**:
  - Added `sync_all_series_readmes()` function to `backend/features/readme_sync.py`
  - Syncs README.txt files for all series filtered by content type (BOOK, MANGA, COMIC)
  - Returns statistics: total, synced, failed, errors
  - Supports optional merge mode parameter (for future use)
  - Fixes import error in series API endpoints

- **Book Import Error When Adding Books with Authors**:
  - Fixed "'bool' object does not support item assignment" error when importing books
  - Issue was caused by overwriting `result` variable with boolean from `sync_author_readme()`
  - Changed to use separate `readme_result` variable for author README sync
  - Books and authors are now properly added to collection without errors
  - Files: `frontend/api_enhanced_book_import.py` (line 217)

- **Author Deletion Now Cascades to Books**:
  - Fixed issue where deleting an author left orphaned books in the app
  - When an author is deleted, all associated books/series are now deleted as well
  - Deletes author_books associations before deleting the author
  - README files are preserved (not deleted) as per requirements
  - Provides success message after deletion
  - Files: `frontend/api/authors/crud.py` (updated `delete_author()` function)

- **Unicode Encoding in README Files**:
  - Fixed `UnicodeEncodeError` when updating book metadata with special Unicode characters
  - README.txt files now use UTF-8 encoding for both read and write operations
  - Supports em-dashes, special characters, and international characters
  - Resolves Windows cp1252 encoding limitations
  - Files: `backend/base/helpers.py` (`ensure_readme_file()` and `read_metadata_from_readme()`)

- **Authors Auto-Creation from File System Import**:
  - Fixed issue where authors were not created when books were imported from file system
  - Authors are now automatically created for all books during discovery
  - Works for both flat book structure and author-based folder structure
  - Author-book relationships are created automatically
  - Authors appear in Authors Library immediately after import
  - Files: `backend/features/ebook_files.py` (added author sync to discovery functions)

### Changed
- **Book Search UI Simplification**:
  - Hidden the Title/Author search type dropdown in book search
  - Title search is now the only option (default and fixed)
  - Updated placeholder text to "Enter book title..."
  - Adjusted column widths for better layout without dropdown
  - Removed search type change listener from JavaScript

## [0.2.3] - 2025-11-13

### Added
- **README.txt Update Utility** (Maintenance Tool):
  - Created `update_readme_files.py` script to update all existing README.txt files
  - Added `/api/readme/update-all` endpoint for updating README files via web interface
  - Automatically finds all README.txt files in root folders
  - Fetches ALL metadata from series database and writes to README files
  - Updates README files with comprehensive fields:
    - **Core**: Series, ID, Type, Provider, MetadataID
    - **Metadata**: Author, Publisher, ISBN, PublishedDate, CoverURL, Subjects
    - **Status**: Status, Description
    - **System**: CustomPath, Created, Updated
  - Preserves existing Created timestamps during update
  - Truncates long descriptions (>500 chars) with ellipsis
  - Provides detailed statistics about update operation
  - Can be run from command line or triggered via API endpoint

- **Extended Series Metadata Storage** (Database Enhancement):
  - Added three new columns to series table: `isbn`, `published_date`, `subjects`
  - ISBN: Stores ISBN number for books (TEXT field)
  - PublishedDate: Stores publication date (TEXT field, flexible format)
  - Subjects: Stores comma-separated list of subjects/tags (TEXT field)
  - Created migration `0018_add_extended_series_metadata.py` for proper schema management
  - All new fields are optional and automatically added via migration system
  - README.txt files now include these fields when updated
  - Metadata parsing reads and parses these fields from README files
  - Subjects are stored as comma-separated values and parsed into lists

### Changed
- **Enhanced README.txt Structure** (Metadata Organization):
  - Standardized README.txt format for all series (Manga, Books, Comics)
  - New README.txt structure includes:
    - **Core Fields**: Series, ID, Type, Provider, MetadataID
    - **Metadata Fields**: Author, Publisher, ISBN, Genres, CoverURL
    - **Timestamp**: Created date in YYYY-MM-DD HH:MM:SS format
  - Updated `ensure_readme_file()` to accept and write author, publisher, ISBN, genres, and cover URL
  - Updated `read_metadata_from_readme()` to parse all new fields including cover URL
  - Genres are stored as comma-separated values and parsed back into lists
  - ISBN field supports empty values for non-book content
  - Cover URL stored for reference and re-import scenarios
  - Enables better metadata organization and future filtering/searching capabilities

- **Book Import Metadata Provider** (Enhancement):
  - Changed default metadata provider for book imports to use provider specified in README.txt
  - When importing a book, the system now checks for existing README.txt files in book folders
  - If README.txt contains "Provider: <ProviderName>", that provider is used instead of the UI-selected provider
  - This allows books to be re-imported with their original metadata provider (e.g., OpenLibrary, GoogleBooks)
  - Enables consistent metadata retrieval for books already in the collection

- **Series Metadata Population from README.txt** (Bug Fix):
  - Fixed issue where imported books/manga showed no cover, author description, or other metadata
  - When a series is imported, the system now reads the README.txt file and updates series with stored metadata
  - Cover URL from README.txt is now properly applied to the series record
  - Enables recovery of metadata for self-edited or previously imported content
  - Metadata from README.txt takes precedence over provider defaults for cover images

- **Auto-Update README.txt on Series Modification** (Enhancement):
  - Created new `readme_sync.py` module for automatic README synchronization
  - When series metadata is updated, README.txt is automatically synced with new values
  - Works for all metadata fields: cover_url, description, author, publisher, ISBN, genres, etc.
  - Integrated into series update endpoints in both `api.py` and `crud.py`
  - Fetches and properly converts genres and subjects strings to lists
  - Improved folder finding logic to handle both direct and author/series folder structures
  - Added debug logging to help troubleshoot folder discovery issues
  - Ensures README.txt always reflects current database state
  - No manual update needed - changes propagate automatically
  - Graceful error handling - sync failures don't block series updates

- **Import README Metadata When Scanning Folders** (Enhancement):
  - When scanning folders for series, README.txt metadata is now imported into the database
  - All metadata fields are extracted: description, author, publisher, ISBN, cover_url, published_date, subjects
  - Both `discover_and_create_series()` and `_process_series_directory()` now populate full metadata
  - Prevents "no description" and "no cover" issues when importing from existing folder structures
  - Metadata from README takes precedence over defaults during import
  - Imported series now have complete metadata without requiring enrichment

- **Extended Metadata Storage During Import** (Enhancement):
  - When importing series, now stores all available metadata from provider:
    - ISBN (from GoogleBooks, OpenLibrary, etc.)
    - Published Date (publication date from provider)
    - Subjects/Genres (categories/tags from provider)
  - Metadata providers (GoogleBooks, OpenLibrary) already fetch these fields
  - Genres/categories converted to comma-separated subjects for storage
  - All metadata automatically written to README.txt files
  - Enables complete metadata preservation for re-import scenarios

- **Comprehensive README.txt Creation for Search Results** (Enhancement):
  - When adding books/manga from search results, now creates comprehensive README.txt with all metadata
  - README.txt includes: ISBN, Published Date, Subjects, Cover URL, Author, Publisher, etc.
  - Same metadata model used for both import and search-based additions
  - Metadata passed directly to folder creation to ensure all fields are written
  - Folder structure creation now accepts optional metadata parameter
  - Ensures consistent metadata storage regardless of import method
  - Enables complete metadata recovery for re-import scenarios

- **AI-Generated Descriptions for Series** (Enhancement):
  - When importing series without descriptions, system now uses AI provider to generate descriptions
  - Automatically generates 2-3 sentence descriptions based on title and author
  - Requires configured AI provider (Groq, Google Generative AI, or OpenAI)
  - Eliminates "No description available" messages on series cards
  - Created `enrich_descriptions.py` utility to add descriptions to existing series
  - Descriptions are non-blocking - import completes even if AI enrichment fails

### Fixed
- **Fix: Convert Subjects List to String for Database Storage** (Bug Fix):
  - Fixed error "type 'list' is not supported" when inserting subjects metadata
  - Subjects are parsed as a list from README but SQLite requires a string
  - Now converts list to comma-separated string before database insertion
  - Applied to both `_process_series_directory()` and `discover_and_create_series()` functions
  - Allows subjects metadata to be properly stored and retrieved from database

- **Ensure Extended Metadata Columns Exist on Startup** (Enhancement):
  - Extended metadata columns (isbn, published_date, subjects) are now created in `db.py` during setup
  - Runs on every app startup to ensure database schema is up-to-date
  - Handles both fresh database creation and existing databases
  - Uses same pattern as other column additions (content_type, custom_path)
  - No need for defensive code in import functions - schema is guaranteed to exist
  - Columns are added with proper error handling for duplicate column scenarios

- **Fix: Author Folders Not Being Processed During Discovery** (Bug Fix):
  - Fixed issue where author folders were being skipped before checking for book subdirectories
  - Now checks for author folder structure FIRST before skipping
  - Author folders with book subdirectories are now properly detected and processed
  - Each book in the author folder is imported with its README metadata
  - Fixes imports for folder structures like: `Y:\eBooks\Books\Ana Huang\Twisted Hate\README.txt`

- **Enhanced Logging for Series Discovery** (Enhancement):
  - Added detailed logging to track series discovery process
  - Logs show which root folders are being scanned
  - Logs show why series are being skipped (missing README or metadata)
  - Helps troubleshoot import issues by showing metadata parsing results
  - Improved visibility into the series discovery workflow

- **Skip Books Without README.txt During Import** (Enhancement):
  - Books/series folders without README.txt files are now skipped during import
  - Only series with valid README.txt containing metadata_id and metadata_source are imported
  - Prevents orphaned folders from being added to the database
  - Ensures all imported series have proper metadata
  - Applied to all three import paths:
    - `_process_series_directory()` - direct series creation
    - `discover_and_create_series()` - folder discovery
    - Main scan loop - book root folder processing
  - Improves data quality by requiring README files for import

- **Skip Provider Enrichment When README Has Complete Metadata** (Enhancement):
  - When importing series from folders with README.txt files, metadata is now imported directly into database
  - If README contains description, author, and cover_url, provider enrichment is skipped
  - Eliminates unnecessary API calls to external metadata providers (GoogleBooks, OpenLibrary, etc.)
  - Faster import process - no waiting for provider responses
  - README metadata takes priority over provider defaults
  - All three import paths now check for complete README metadata before enriching:
    - `_process_series_directory()` - direct series creation
    - `discover_and_create_series()` - folder discovery
    - Main scan loop - e-book file processing

- **Fix: E-book Files Not Being Added After Fresh Scan** (Bug Fix):
  - Fixed issue where newly discovered series were not being processed for e-book files
  - After `discover_and_create_series()` creates new series, they are now properly added to processing queue
  - Added proper handling for books in direct book root folders (not just author/series structures)
  - Added fallback logic to find series by metadata_id, title, and case-insensitive title match
  - Improved logging to track series discovery and file processing
  - Ensures all newly created series are scanned for e-book files in the same operation

- **Preserve README.txt Files When Deleting Series** (Enhancement):
  - When a series is deleted from the app, the folder and README.txt file are now preserved
  - Only the database entry is deleted, not the physical files
  - Allows manual recovery of series data if accidentally deleted
  - Prevents accidental loss of metadata and e-book files
  - Useful for keeping historical records and backup data
  - Updated both delete endpoints to preserve files and log the action

- **README.txt Not Being Updated with New Metadata** (Bug Fix):
  - Fixed issue where existing README.txt files were not being updated with new metadata
  - `ensure_readme_file()` was returning early if README existed instead of updating it
  - Now always creates or updates README.txt with current metadata
  - Ensures comprehensive metadata is written to all README files
  - Fixed `api.py` in multiple places to fetch and pass all metadata when creating folder structure
  - Updated `add_series()` endpoint to store ISBN, published_date, subjects in database
  - Updated both `add_series()` and collection add endpoints to pass metadata to folder creation
  - Fixed `api_enhanced_book_import.py` to use `ensure_readme_file()` instead of manual README creation
  - Replaced hardcoded README creation with comprehensive metadata function call
  - Added description field to README.txt metadata
  - Added 2 blank paragraphs between metadata and footer for better formatting
  - Moved "This folder is managed by Readloom" message to after metadata section
  - Metadata now properly passed through entire chain: database → folder creation → README.txt
  - Fixes issue where old README format persisted after adding series from search or library

- **Orphaned Authors Not Being Deleted** (Bug Fix):
  - Fixed issue where authors remained in database after all their books/manga were removed
  - Added automatic author cleanup when removing collection items
  - Authors with no associated books/manga are now automatically deleted
  - Cleanup triggered when:
    - A collection item (book/manga) is removed from collection
    - A series is deleted from the app
  - Uses existing `cleanup_author_if_orphaned()` function for consistency
  - Prevents accumulation of orphaned author entries in the database

- **Minor bugs in various UI components**
- **Calendar functionality issues**
- **Dashboard infinite loading with recent series**

## [0.2.2] - 2025-11-12

### Added

- **Authors Tab Enhancements**:
  - Added edit author button in author details
  - Added author photos to author details modal (same as in search)
  - Added manga author search functionality
  - **Auto-creation of authors from book imports**: Authors are now automatically created in Authors Library when books are imported
  - **Author enrichment from imports**: Authors created from book imports are automatically enriched with:
    - Biography from OpenLibrary (priority 1) or Groq AI (priority 2)
    - Photo from OpenLibrary
    - Released books count from OpenLibrary
  - **Released count display on author cards**: Shows total published works by author from OpenLibrary
  - **Asynchronous released count fetching**: Author cards load instantly, released count populates in background

- **Collections Manager in Settings Tab**:
  - Moved Collections Manager from standalone page to Settings tab
  - Integrated as "Collections" tab alongside General, Calendar, Logging, and Integrations
  - Maintains full functionality for managing collections and root folders
  - Removed Collections Manager from sidebar navigation
  - Cleaner UI with all management tools in one place

- **Library Items Table**:
  - Created unified Library Items view displaying both books and manga volumes
  - Implemented table layout with columns: Title, Author, Description, Tags, Volumes, Value, Owned, Action
  - Added filtering by content type, ownership status, and format
  - Implemented resizable columns for Title and Author
  - Added responsive design with dark mode support
  - Integrated statistics cards (Total Series, Volumes, Owned, Value)
  - Optimized column widths for better visual balance

### Fixed

- **Author Details Display**:
  - Fixed author detail template to use dictionary-style access instead of index-based access
  - Fixed JavaScript in author detail template to properly reference author.id
  - Fixed book display in author detail template to use correct field names
  - Author modal now opens correctly when clicking "View Details" button

- **Author Duplicate Prevention**:
  - Implemented centralized `get_or_create_author()` function for case-insensitive duplicate checking
  - Authors are now deduplicated across all import methods (book import, author search, series import)
  - Prevents duplicate author entries when same author is added via different methods

- **Author Enrichment**:
  - Fixed author enrichment to trigger automatically when new authors are created
  - Enhanced enrichment to fetch released books count from OpenLibrary as fallback
  - Authors created from book imports now have biography, photo, and released count

- **Authors API Endpoints**:
  - Fixed `/api/authors` endpoint to include `book_count` for each author
  - Fixed `/api/authors/<id>` endpoint to return books, book_count, and released_books_count
  - Added pagination support to authors list endpoint
  - Added search functionality to authors list endpoint

- **Settings Loading Error**:
  - Fixed "Settings object has no attribute __dict__" error
  - Changed from `__dict__` to `_asdict()` for NamedTuple serialization
  - Settings now load correctly from API

- **Notification System Improvements** (UX):
  - Fixed missing timers on info/success/warning notifications
  - Added `showTimer` parameter to NotificationManager.show() method
  - Timers now display on all non-confirmation notifications (success, error, warning, info)
  - Confirmation dialogs remain without timers (manual dismiss only)
  - Added new `showPopup()` helper function for notifications without timers
  - Updated all collection and root folder notifications to use proper notification functions
  - Replaced all `alert()` calls in collections_manager.js with notification functions
  - Success notifications display with 3-second timer
  - Error notifications display with 5-second timer
  - Info notifications display with 4-second timer

- **UI Layout Issues**:
  - Fixed card layout affecting all divs/containers app-wide
  - Scoped card height styling to only author, book, and manga cards
  - Removed generic `.card` and `.card-img-top` selectors from extended height CSS rules
  - Dashboard, library, notifications, and settings sections now display with correct heights

- **Series Details Route (404 Error)**:
  - Fixed missing `/series/<id>` route that was causing 404 errors when accessing series details from Library Items
  - Added backward compatibility route that redirects to appropriate book or manga detail page
  - Implemented `series_detail()` route to handle generic series lookups
  - Implemented `manga_series_view()` route for manga/comic series display

- **Book Library Empty State**:
  - Fixed Book Library page showing empty state when books existed in database
  - Ensured `recent_books` variable is properly passed to template
  - Verified book collections and popular authors data loading

- **Imported Manga Metadata Enrichment**:
  - Fixed imported manga showing "Unknown" status instead of fetching from AniList
  - Updated `enrich_series_metadata()` to extract and save status from AniList metadata
  - Imported manga now display proper status (ONGOING, COMPLETED, ANNOUNCED, CANCELLED) from AniList
  - Prevents duplicate manga from appearing in search results by having proper metadata

- **Duplicate Series Prevention**:
  - Added duplicate detection in `discover_and_create_series()` to prevent creating duplicate series during import
  - Improved case-insensitive series matching when checking for existing entries
  - Added duplicate check in `create_series()` API endpoint to prevent adding same series twice from search
  - Returns existing series instead of creating duplicate when attempting to add same title

- **Metadata ID Integration for Duplicate Detection**:
  - Added `metadata_source` and `metadata_id` fields to README.txt files when creating series folders
  - Implemented `read_metadata_from_readme()` function to extract metadata from README files during import
  - Updated duplicate detection to check by `metadata_id` first (most reliable method)
  - Manually imported manga now store AniList metadata_id in README for future duplicate detection
  - When adding series from search, metadata_id is stored in database and README
  - Updated `create_series_folder_structure()` to fetch and write metadata to README files
  - Added metadata enrichment during file scan for existing series without metadata
  - Updated series lookup during scan to check README metadata first before title matching
  - Fixed metadata enrichment to detect incomplete metadata (has ID but missing author/cover)
  - Extended metadata enrichment to support both MANGA (via AniList) and BOOK (via OpenLibrary) content types
  - Updated book import to include metadata_id and Type: BOOK in README files
  - Enhanced `read_metadata_from_readme()` to support both manga and book README formats
  - Fixed book scan to properly handle author folder structure (Author/Book hierarchy)
  - Book discovery now recursively processes book subdirectories within author folders
  - Separated manga and book scanning to use content-type-specific root folders
  - Fixed content type detection to prioritize README Type field over parent folder name
  - Books are now correctly added to Books collection instead of Manga collection
  - Prevents duplicate entries even when same manga/book is added via different methods (import vs search)

## [0.2.1] - 2025-11-11

### Added
- **E-book Scan & Import Feature** (Major Feature):
  - Automatic series discovery and creation from folder structures
  - Metadata enrichment from AniList for newly imported manga
  - Support for folder-based volume/chapter organization with individual images
  - Automatic volume detection from folder names (Volume 1, Vol 1, v1, etc.)
  - Automatic chapter detection from folder names
  - Support for both file-based (PDF, EPUB, CBZ, etc.) and folder-based (Individual Images) formats
  - Statistics tracking: scanned, added, skipped, errors, series_processed
  - Non-blocking metadata enrichment (scan completes even if AniList lookup fails)

- **Folder-Based Volume Support**:
  - New `scan_folder_structure()` function for detecting Volume folders
  - Automatic creation of volumes with "Digital" format and "Individual Images" digital format
  - Support for hierarchical folder structures: `Series/Volume/Chapter/Images`
  - Volumes marked as `has_file = 1` for proper UI display
  - No file download/delete buttons for folder-based volumes (read-only display)

- **Digital Format Dropdown Enhancement**:
  - Added "Individual Images" option to Digital Format dropdown
  - Available in both manga and series detail views
  - Allows manual selection and automatic assignment during scan

- **In-App Notification System** (Major UX Improvement):
  - Replaced all browser alerts, confirms, and popups with elegant in-app toast notifications
  - Created centralized notification manager in `static/js/notifications.js`
  - Support for success, error, warning, and info notifications
  - Modal-based confirmation dialogs with overlay and Promise support
  - Auto-dismiss with 5-second countdown timer
  - Countdown timer displayed on each notification
  - Confirmation dialogs centered on screen with semi-transparent overlay
  - Click outside confirmation to cancel (auto-cancels)
  - Prevents interaction with page while confirmation is active
  - Smooth slide-in animations and scale transitions
  - XSS protection with HTML escaping
  - Full dark mode support
  - Responsive design (works on mobile and desktop)
  - Easy API: `showSuccess()`, `showError()`, `showWarning()`, `showInfo()`, `showConfirm()`
  - Global notification container in top-right corner
  - Close button on each notification for manual dismissal

- **UI/UX Redesign** (Major Enhancement):
  - Redesigned Books tab to match Manga tab layout with card-based grid
  - Redesigned Authors tab to match Manga tab layout with card-based grid
  - Added "Popular Books This Week" placeholder section in Books tab
  - Added "Popular Authors" placeholder section in Authors tab
  - Updated all grids to display 5-6 items per row with responsive zoom:
    - Recent Series/Books/Authors tabs: 4 → 5 columns (XL) → 6 columns (XXL)
    - Search results (Books, Manga, Authors): 4 → 5 columns (XL) → 6 columns (XXL)
    - Dashboard recent series: Dynamic responsive grid with 5-6 columns
    - Grid adapts when zooming out: items move to previous rows instead of stretching
  - Increased card heights for better cover display:
    - Manga/Books/Search covers: 200px → 280px → **320px**
    - Card minimum height: 400px → **450px**
    - Dashboard series covers: 150px → 280px → **320px**
    - Author cards: 280px → **350px**
  - Consistent responsive design across all tabs (1, 2, 3, 5 columns)
  - Improved search result display with better spacing

- **Performance Optimizations** (Critical):
  - Removed blocking OpenLibrary API calls from authors list endpoint
  - Removed blocking OpenLibrary API calls from author details endpoint
  - Authors tab now loads instantly (no external API calls on initial load)
  - Author details now load instantly (database queries only)
  - Books and Authors search now as fast as Manga search
  - Eliminated sequential HTTP requests to external APIs
  - Reduced server load significantly
  - Better scalability with large author/book collections

### Fixed
- **Series Details Loading Loop** (Critical):
  - Fixed infinite loading spinner on series detail page
  - Root cause: API endpoint `/api/series/{id}` was returning incomplete data structure
  - Fixed `read_series()` function to return complete data with volumes, chapters, and upcoming_events
  - Added error handling for optional tables (releases table may not exist)
  - Series details now load correctly with all related data

- **Series Route Redirect Loop** (Critical):
  - Fixed infinite redirect loop when viewing series details
  - Root cause: Multiple conflicting route definitions for `/series/<id>` across different files
  - Fixed endpoint name in redirect: changed `ui.series_view` to `manga_routes.series_view`
  - Commented out duplicate routes in `ui_complete.py` and `ui_content_specific.py`
  - Series detail page now loads without infinite redirects

- **Unicode Encoding Errors in Logging**:
  - Fixed UnicodeEncodeError when logging file paths with special characters
  - Added UTF-8 encoding with error replacement to both console and file handlers
  - Changed logging to use only filenames instead of full paths to avoid encoding issues
  - Updated `backend/base/logging.py` to force UTF-8 encoding on RotatingFileHandler
  - File paths with Japanese, Chinese, and other Unicode characters now log correctly

- **Collection Items Query Error**:
  - Fixed "type 'dict' is not supported" error in collection queries
  - Root cause: Dictionary was being passed directly instead of unpacked into parameters
  - Fixed `get_items()` function to properly extract filter parameters from dictionary
  - Collection queries now work correctly with proper parameter binding

- **Volume Format Update Queries**:
  - Fixed database queries in `frontend/api/volumes/formats.py`
  - Changed `item_id` to `volume_id` in WHERE clauses
  - Both `update_volume_format()` and `update_volume_digital_format()` now work correctly

- **Book Import to Wrong Root Folder** (Critical):
  - Fixed books being added to manga root folder instead of book root folder
  - Root cause #1: `api_enhanced_book_import.py` was selecting first root folder without filtering by content_type
  - Root cause #2: `import_manga_to_collection()` was creating duplicate book folders in root
  - Fixed `get_root_folder_path()` to filter by content_type when no collection specified
  - Added skip flag in `import_manga_to_collection()` to prevent folder creation for BOOK content type
  - Books now correctly created in: `BookRoot/Author/BookTitle/` structure
  - No more duplicate book folders in root directory

- **Author Import to Wrong Root Folder** (Critical):
  - Fixed authors being added to manga root folder instead of book root folder
  - Root cause: `api_author_import.py` was selecting first root folder without filtering by content_type
  - Updated author import to use `get_root_folder_path()` helper with BOOK content type
  - Authors now correctly created in: `BookRoot/AuthorName/` structure
  - Author subfolders and README.md created in correct location

- **Confirmation Dialogs Executing Before User Confirms** (Critical):
  - Fixed issue where delete/remove actions were executing before user confirmed
  - Updated all confirmation functions to use async/await with showConfirm()
  - Confirmation now properly blocks action until user confirms or cancels
  - Applied fix to: deleteCollection, deleteRootFolder, removeRootFolderFromCollection, removeSeriesFromCollection
  - Replaced browser alert() calls with showSuccess() and showError() notifications

- **Card Stretching in Responsive Grid** (UX):
  - Fixed cards stretching when zoomed out or on wider screens
  - Added CSS to prevent flex-grow on row-cols columns
  - Cards now maintain fixed width and don't expand to fill row
  - Items properly move to previous rows instead of stretching

- **Description Text Visibility in Dark Mode** (UX):
  - Fixed white text on white background in description boxes during dark mode
  - Added dark mode styling for textarea and description boxes
  - Description boxes now have dark background (#2c3034) with light text in dark mode
  - Improved contrast and readability in all modals and detail views

- **Book Folder Creation in Wrong Location** (Critical):
  - Fixed books being added to manga root folder instead of book root folder
  - Fixed duplicate book folder creation (one inside author folder, one in root)
  - Implemented `skip_folder_creation` flag for BOOK content type in `import_manga_to_collection()`
  - Books now correctly created in: `BookRoot/Author/BookTitle/` structure
  - No more duplicate book folders in root directory

- **Author Folder Creation in Wrong Location** (Critical):
  - Fixed authors being added to manga root folder instead of book root folder
  - Updated author import to use `get_root_folder_path()` helper with BOOK content type
  - Authors now correctly created in: `BookRoot/AuthorName/` structure
  - Author subfolders and README.md created in correct location

- **Authors Tab Performance** (Critical):
  - Fixed slow loading caused by blocking OpenLibrary API calls
  - Removed sequential HTTP requests to external APIs
  - Authors list now loads instantly from database
  - Author details now load instantly (database queries only)

### Changed
- Enhanced `scan_for_ebooks()` to support both file-based and folder-based scanning
- Improved logging verbosity: file-level logs now use DEBUG level, reduced noise
- Series creation now includes automatic metadata enrichment attempt
- Collection items now properly support "Individual Images" digital format
- Updated README file creation to log only directory names (not full paths)
- Updated 8 JavaScript files to use new notification system
- Updated 4 HTML templates to use new notification system
- Improved user experience with non-blocking notifications
- **Dashboard UI Redesign**:
  - Renamed "Series" to "Manga Series" with separate manga count
  - Added "Books" stat card showing total books in library
  - Added "Authors" stat card showing total authors in library
  - Hidden Volumes and Chapters stat cards (code commented, not removed)
  - Updated backend API to provide separate manga_series_count, books_count, and authors_count
  - All stat cards now display more relevant library statistics
- **Authors Tab Improvements**:
  - Enhanced error handling and logging in API endpoints
  - Improved error messages for better debugging
  - Better frontend error handling with detailed messages
  - Changed "Books" to "Works" to include both books and manga
  - Added fallback handling for missing data
  - Improved image URL handling with processImageUrl()
- **Author Sync Fix**:
  - Fixed author auto-creation when importing books/manga
  - Removed reference to non-existent `photo_url` column in author queries
  - Authors are now properly created and linked to series during import
  - Author enrichment (photo, biography) now works correctly
- **Author Biography Fetching**:
  - Enhanced logging for biography fetching process
  - Added detailed error messages when Groq API key is not configured
  - Biography fetching is automatic when authors are created
  - Uses Groq AI (Llama 3.3 70B) to generate author biographies
  - Requires GROQ_API_KEY environment variable or database setting
- **AI Provider Configuration - No Restart Required**:
  - Test endpoint now reinitializes AI providers without server restart
  - API keys can be configured and tested without downtime
  - Automatic configuration reload from database and environment variables
  - Enhanced logging for AI provider initialization and testing
  - Better error messages for API key configuration issues

### Technical Details
- **Files Modified**:
  - `backend/features/ebook_files.py` - Added folder structure scanning, metadata enrichment
  - `backend/base/logging.py` - Fixed Unicode encoding in file handler
  - `backend/base/helpers.py` - Fixed logging to use directory names only
  - `backend/base/helpers_content_service.py` - Fixed root folder selection to filter by content_type
  - `backend/features/metadata_service/facade.py` - Added skip flag for BOOK folder creation
  - `frontend/api/series/crud.py` - Fixed read_series() to return complete data structure
  - `frontend/api/collection/items.py` - Fixed filter parameter unpacking
  - `frontend/api/volumes/formats.py` - Fixed database query WHERE clauses
  - `frontend/api_enhanced_book_import.py` - Fixed root folder selection for book import
  - `frontend/api_author_import.py` - Fixed root folder selection for author import
  - `frontend/ui/manga.py` - Fixed series_detail redirect endpoint name
  - `frontend/ui_complete.py` - Commented out duplicate series_detail route
  - `frontend/ui_content_specific.py` - Commented out duplicate series_detail route
  - `frontend/templates/manga/series.html` - Added "Individual Images" to dropdown
  - `frontend/templates/series_detail.html` - Added "Individual Images" to dropdown
  - `frontend/templates/books/search.html` - Uses enhanced book import API

- **New Functions**:
  - `discover_and_create_series()` - Discovers new series folders and creates them in database
  - `enrich_series_metadata()` - Fetches metadata from AniList and updates series
  - `scan_folder_structure()` - Scans for folder-based volume/chapter structures

- **Database Updates**:
  - Volumes created from folder structures have `format = 'DIGITAL'` and `digital_format = 'Individual Images'`
  - Collection items properly track `has_file = 1` for folder-based volumes
  - Series created during scan include metadata from AniList (cover_url, description, author)

### Root Cause Analysis
- **Series Details Loading**: API was returning only series object instead of complete structure with volumes/chapters
- **Series Route Redirect**: Wrong endpoint name in url_for() caused redirect to non-existent route
- **Unicode Errors**: Windows console uses cp1252 encoding by default, incompatible with Unicode file paths
- **Collection Query**: Function signature mismatch between caller and implementation
- **Volume Format Queries**: Incorrect column name in WHERE clause (item_id vs volume_id)
- **Book Import Wrong Folder**: Two issues combined:
  1. `api_enhanced_book_import.py` selected first root folder without content_type filtering
  2. `import_manga_to_collection()` created duplicate folders for all content types
- **Author Import Wrong Folder**: `api_author_import.py` selected first root folder without content_type filtering
- **Solution**: Use `get_root_folder_path()` helper that respects content_type, collection_id, and root_folder_id priority

## [0.2.0] - 2025-11-11

### Added
- **Enhanced Authors Tab** (Major Feature):
  - Added "Released Books" count from OpenLibrary for each author
  - Added "Owned" count showing books from that author in your library
  - Display both counts on author cards and in author details modal
  - New "Books on OpenLibrary" section showing all published works by author
  - Book covers, titles, and publication years displayed for provider books
  - Metadata provider tracking (OpenLibrary, GoogleBooks, etc.)
  - Automatic detection of which provider was used to add books
  - Seamless integration with OpenLibrary search API

- **Author Enrichment Improvements**:
  - Hybrid enrichment strategy: OpenLibrary first, then Groq AI fallback
  - Automatic enrichment when books are added (if AI is configured)
  - Graceful handling of missing `photo_url` column in older databases
  - Migration script to add `photo_url` column to existing databases
  - Robust error handling for database schema variations

- **UI/UX Improvements**:
  - Removed birth date from author cards and details (not relevant)
  - Changed statistics display from "Total Volumes" to "Owned"
  - Added two-column statistics layout (Released vs Owned)
  - Improved book thumbnail grid layout in author details
  - Better visual distinction between library books and provider books
  - Faded appearance for provider books to distinguish from owned books

- **Logging & Debugging**:
  - Fixed Unicode encoding errors in logging (Windows compatibility)
  - Replaced Unicode checkmarks (✓✗) with ASCII alternatives ([OK], [FAIL])
  - Enhanced logging for author enrichment process
  - Detailed logging for OpenLibrary API calls
  - Console logging for debugging API responses

### Fixed
- **Unicode Encoding Issues**:
  - Fixed `UnicodeEncodeError` in logging on Windows systems
  - Replaced Unicode characters with ASCII-safe alternatives
  - Proper encoding handling for log file output

- **Author Enrichment Logic**:
  - Fixed enrichment skipping Groq fallback when OpenLibrary found author but no biography
  - Fixed wrong priority order (was Groq first, now OpenLibrary first)
  - Properly checks if biography was actually added before skipping fallback
  - Gracefully handles missing `photo_url` column in older databases

- **OpenLibrary API Integration**:
  - Fixed URL construction for OpenLibrary works endpoint
  - Fixed API endpoint from `/works.json` to `/search.json` with author parameter
  - Proper extraction of author ID from various key formats
  - Correct cover URL generation using `cover_i` field from search results
  - Fallback handling for books without cover images

### Changed
- **Author Details Display**:
  - Removed birth date field from author cards and modal
  - Changed "Total Works" to "Released" (from OpenLibrary)
  - Changed "Total Volumes" to "Owned" (from library)
  - Updated statistics layout to show both counts side-by-side

- **API Endpoints**:
  - Enhanced `/api/authors/` endpoint to fetch OpenLibrary stats for all authors
  - Enhanced `/api/authors/<id>` endpoint to return provider books and metadata
  - Added `released_books_count` and `provider_books` to response

- **Database**:
  - Added migration support for `photo_url` column
  - Robust handling of schema variations across database versions

### Technical Details
- **Files Modified**:
  - `frontend/api_authors.py` - Enhanced with OpenLibrary integration and metadata provider detection
  - `frontend/templates/authors/authors.html` - Updated UI with new statistics and provider books section
  - `backend/features/author_openlibrary_fetcher.py` - Added work_count extraction
  - `backend/features/author_photo_fetcher.py` - Graceful handling of missing photo_url column
  - `backend/features/authors_sync.py` - Fixed enrichment priority and fallback logic
  - `backend/features/ai_providers/manager.py` - Fixed Unicode encoding in logging
  - `backend/features/ai_providers/config.py` - Fixed Unicode encoding in logging
  - `frontend/api.py` - Fixed Unicode encoding in logging

### Backward Compatibility
- ✅ Fully backward compatible
- ✅ Gracefully handles databases without `photo_url` column
- ✅ No breaking changes to existing APIs
- ✅ Optional migration for adding `photo_url` column

## [0.1.9] - 2025-11-08

### Added
- **Authors Feature** (Major Feature):
    - Complete Authors management system with automatic synchronization
    - Beautiful card-based UI with author information display
    - AI-powered author biographies using Groq
    - Automatic author cleanup when books are deleted
    - Rich author detail modal with book gallery
- **AI Providers System** (Major Feature):
  - Implemented comprehensive AI provider system for accurate manga metadata extraction
  - Added support for 4 AI providers:
    - **Groq**: Fastest, free, recommended (1 minute setup)
    - **Google Gemini**: Powerful, free tier (2 minutes setup)
    - **DeepSeek**: Good reasoning, free tier (2 minutes setup)
    - **Ollama**: Self-hosted, private, free (5 minutes setup)
  - Intelligent fallback chain: Groq → Gemini → DeepSeek → Ollama → Web Scraping
  - Parallel extraction capability for best result selection
  - Confidence scoring for result quality assessment
  - Seamless integration with existing MangaInfoProvider
  - Automatic caching of AI results in `manga_volume_cache`

### Features
- **AIProvider Base Class**: Abstract interface for all providers
- **AIProviderManager**: Manages providers with fallback and parallel logic
- **MangaMetadata**: Structured output with volumes, chapters, status, dates, confidence
- **Configuration System**: Environment variable-based configuration
- **Integration Layer**: Easy integration with existing metadata system
- **Comprehensive Logging**: Debug and info logging for troubleshooting
- **Automatic Author Sync**: Authors created/linked automatically when books are added
- **Author Biography Fetcher**: Groq AI generates 2-3 sentence author summaries
- **Author Cleanup**: Orphaned authors removed automatically when all books deleted
- **Enhanced Authors API**: Accurate book count per author with search and pagination
- **Beautiful UI**:
    - Centered, enlarged author names
    - Expanded biography preview (180 characters)
    - Accurate book count display
    - Responsive card layout (1-3 cards per row)
    - Smooth hover effects and transitions

### Database
- Added `photo_url` column to authors table
- Added `biography` column to authors table
- Automatic migration on startup

### Documentation
- **AI_PROVIDERS_QUICKSTART.md**: 5-minute quick start guide
- **AI_PROVIDERS.md**: Complete reference documentation (400+ lines)
- **AI_PROVIDERS_IMPLEMENTATION.md**: Architecture and design details
- **MIGRATING_TO_AI_PROVIDERS.md**: Upgrade guide for existing users
- **backend/features/ai_providers/README.md**: Package documentation
- `docs/AUTOMATIC_AUTHOR_CLEANUP.md` - Cleanup feature documentation
- `docs/SETUP_GROQ_FOR_AUTHOR_BIOGRAPHIES.md` - Groq setup guide
- `docs/SESSION_COMPLETE_AUTHORS_FEATURE.md` - Complete session summary

### Testing
- **test_ai_providers.py**: Comprehensive test script
  - Configuration testing
  - Provider availability checking
  - Metadata extraction testing
  - Parallel extraction testing
  - Integration testing

### Configuration
- Updated requirements.txt with AI provider dependency notes
- Environment variable support for all providers
- Docker Compose examples
- Kubernetes examples

### Files Created
- `backend/features/authors_sync.py` - Author synchronization module
- `backend/features/author_cleanup.py` - Orphaned author removal
- `backend/features/author_biography_fetcher.py` - Groq AI biography generation
- `backend/features/author_photo_fetcher.py` - OpenLibrary photo fetching
- `tests/fetch_author_biographies.py` - Manual biography fetch script
- `tests/fetch_author_photos.py` - Manual photo fetch script
- `backend/migrations/0016_add_author_photo_url.py` - Database migration

### Files Modified
- `backend/internals/server.py` - Added database column check on startup
- `frontend/api_authors_complete.py` - Enhanced with accurate book count
- `frontend/api.py` - Added author cleanup to delete_series
- `frontend/templates/authors/authors.html` - Redesigned UI with better layout
- `backend/features/metadata_service/facade.py` - Added auto-sync integration

### Benefits
- ✅ Accurate metadata extraction for any manga title
- ✅ Free - all providers have free tiers, no credit card required
- ✅ Reliable - automatic fallback ensures extraction always works
- ✅ Flexible - multiple providers to choose from
- ✅ Private - Ollama option for self-hosted, offline capability
- ✅ Easy setup - 1-5 minutes to get started
- ✅ Well integrated - seamless integration with existing system
- ✅ Extensible - easy to add new providers

### Backward Compatibility
- ✅ Completely backward compatible
- ✅ No breaking changes
- ✅ Existing code continues to work without modifications
- ✅ Optional feature - can be enabled or disabled

### Setup Required
```bash
export GROQ_API_KEY=your_groq_api_key_here
python tests/fetch_author_biographies.py
```

## [0.1.8] - 2025-10-26

### Changed
- **Authors Tab Temporarily Disabled**:
  - Replaced Authors tab with a "Coming Soon" placeholder page
  - Reason: Complex JavaScript event loop blocking issue discovered during debugging
  - The Authors feature will be reimplemented in a future version with a more robust architecture
  - Users can still browse authors through the Books Search page

### Fixed
- **Development Mode Performance**:
  - Disabled periodic task manager during development to prevent Flask server blocking
  - Delayed notifications loading in base template to prevent JavaScript event loop blocking

### Known Issues
- Authors tab is temporarily unavailable (placeholder page shown instead)
- See KNOWN_ISSUES.md for detailed analysis of the root cause

## [0.1.7] - 2025-10-25

### Known Issues
- None at this time. Authors tab has been fixed and re-enabled.

### Added
- **Navigation Reorganization**:
  - Moved Books, Manga, and Authors from dashboard tabs to sidebar navigation
  - Books and Manga now appear as separate menu items under Series
  - Dashboard now displays only series statistics and recent activity
  - Cleaner, more intuitive navigation structure

- **Books and Manga Pages Redesign**:
  - Removed content type selector tabs from both Books and Manga pages
  - Removed "Search Books" menu from Books page
  - Removed "Manga Collections" and "Series" sidebars from Manga page
  - Books library now spans full width of the page
  - Manga library now spans full width of the page
  - Cleaner, more spacious layout for browsing content

- **Authors Tab Fixed and Re-enabled**:
  - Re-enabled Authors tab in sidebar navigation
  - Updated author detail page to use existing backend routes
  - Added card header with Edit, View Books, and Delete buttons (round icon-only style)
  - Added Books by Author collapsible section (collapsed by default)
  - Added Quick Actions footer with View All button
  - Improved author information display with biography and metadata
  - Fixed the previous hanging issue by using server-rendered data instead of API calls
  - Books section displays all author's books with cover images and links

- **Book Details Page Redesign**:
  - Changed layout from `books_layout.html` to `base.html` (full-width like manga)
  - Added "Edit Book" and "Move Book" buttons in card header
  - Added "Delete" button in card header
  - Redesigned buttons as round icon-only style matching manga tabs
  - Added E-book Management collapsible section (collapsed by default)
  - Added Quick Actions footer with Move and Scan buttons
  - Added file management with download and delete buttons
  - Added Scan for E-books functionality
  - Added Edit Book modal for editing series details
  - Added Move Book modal for moving books to different collections
  - Updated terminology: "Edit Series" → "Edit Book", "Move Series" → "Move Book"

- **Manga Series Page Consistency Updates**:
  - Moved buttons from series details area to card header
  - Updated button styling to match book details page
  - Added Delete button to header (Edit, Move, Delete)
  - Updated E-book Management section to collapse by default
  - Added Quick Actions footer with Move and Scan buttons
  - Improved button spacing with `gap-3` for better visual hierarchy

### Changed
- **Button Design**: All action buttons now use round icon-only style (`rounded-circle`) with proper spacing
- **Header Layout**: Both book and manga detail pages now have consistent card headers with buttons
- **E-book Management**: Now collapsed by default on both pages for cleaner interface
- **Button Terminology**: Books page uses "Book" terminology, manga page uses "Series" terminology
- **Button Positioning**: Buttons moved from floating/absolute positioning to card header for consistency

### Fixed
- Fixed database schema inconsistencies in BookService methods
- Fixed migration execution order
- Fixed file permission issues in ebook scanning
- Fixed Authors page blank display (BookService methods updated)
- Fixed Authors tab hanging issue (tab hidden from navigation)
- Fixed button styling inconsistencies between book and manga pages
- Fixed E-book Management section visibility (now collapsed by default)

## Previous Changes

### Manga Volume Detection Fix
- Fixed automatic volume identification with three-tier detection system
- Added `manga_volume_cache` table for caching volume data
- Implemented proper migration execution on app startup
- Added volume detection from static database, web scraping, and estimation

### Enhanced Ebook File Recognition
- Added `fix_file_permissions()` function for automatic permission fixing
- Integrated permission fixing into ebook scanner
- Support for files with restrictive permissions (700 mode)
- Graceful error handling for permission-denied scenarios

### Redesigned Volumes UI
- Completely redesigned volumes table matching v0.1.2-2 design
- Added Format selector (Physical, Digital, Both, None)
- Added Digital Format selector (PDF, EPUB, CBZ, CBR, MOBI, AZW)
- Added file management with download and delete buttons
- Integrated upload button for adding ebook files
- **Automatic Format Detection**:
  - Formats automatically detected from uploaded files
  - File extension mapping to digital formats
  - Auto-update of collection items in background
  - No manual format configuration needed
- **Database Schema Updates**:
  - Added `has_file` column to collection_items
  - Added `ebook_file_id` column to collection_items
  - Added `digital_format` column to collection_items
  - Created migration 0015 for schema updates
- **Improved File Scanning**:
  - Enhanced ebook scanner with permission handling
  - Better volume number extraction from filenames
  - Automatic volume creation during scanning
  - Collection item updates with file information
- **Migration System Improvements**:
  - Fixed duplicate migration version numbers
  - Corrected migration ordering and execution
  - Added proper error handling for already-applied migrations
  - Created `__init__.py` for migrations package

### Fixed
- Fixed 404 errors on format update endpoints (added `/api` prefix)
- Fixed database schema inconsistencies
- Fixed migration execution order
- Fixed file permission issues in ebook scanning
- Fixed volume detection for various manga titles

### Changed
- Updated volumes display to match old design with new features
- Improved API endpoint naming consistency
- Enhanced error messages and logging
- Optimized file scanning performance

### Technical Details
- See [LATEST_UPDATES.md](LATEST_UPDATES_v0.1.6.md) for comprehensive documentation

## [0.1.6] - 2025-10-19

### Added
- **JavaScript Files for Collections**:
  - Added missing `collection.js` for collection view functionality
  - Added missing `collections.js` for collections list functionality
  - Fixed 404 errors when accessing collection pages
- **Enhanced Author Search**:
  - Added author metadata API endpoint for detailed author information
  - Implemented specialized author cards in search results
  - Added comprehensive author details modal with biography, birth/death dates, and external links
  - Added support for OpenLibrary author photos and metadata
- **Enhanced Author Details**:
  - Improved author details modal with loading indicators
  - Added subject categorization for authors
  - Added notable works listing with direct links
  - Added external resource links (Goodreads, Wikipedia, etc.)
  - Implemented proper image display in both search results and author details
  - Added comprehensive biographical information from OpenLibrary
  - Added places associated with authors when available
- **Author Collection Management**:
  - Added ability to add authors to collections with proper folder structure
  - Created author folders with subfolders for notable works
  - Implemented README.md generation with author information
  - Added support for adding more books to existing author folders
  - Created database tables for authors, collection_authors, and author_books
  - Added API endpoints for author import and enhanced book import
  - Improved author details modal with "Add to Collection" button
  - Added workflow to search for and add books by an existing author

### Fixed
- **Root Folders Detection**:
  - Added API endpoint `/api/rootfolders/check-configured` to check if root folders are configured
  - Implemented JavaScript-based root folders detection in dashboard and series pages
  - Fixed issue where root folders warning was showing even when root folders were configured
  - Added localStorage flag to communicate root folder updates between pages
- **Search Functionality**:
  - Fixed provider/indexer dropdown in search forms
  - Implemented proper filtering of providers based on content type (books vs. manga)
  - Fixed search type selection to properly handle title and author searches
  - Corrected content type selector links in search templates
  - Fixed author image display in search results
  - Improved author details loading time with visual feedback
  - Fixed missing subjects and metadata in author details
- **Database Issues**:
  - Fixed database error related to missing `has_file` column in ebook_files table
  - Added fallback method to get inserted file ID when `RETURNING id` clause doesn't work
  - Fixed error handling in `add_ebook_file` function to prevent database errors
- **API Endpoints**:
  - Added missing `/api/series/{series_id}/scan` endpoint for scanning e-books
  - Improved error handling in scan endpoint with better logging
  - Fixed content-type handling in API requests
- **UI Improvements**:
  - Fixed folder path display in series details page
  - Removed duplicate folder path display
  - Fixed "Loading..." text that never updated in folder path elements
  - Improved error handling in scan for e-books functionality
- **Folder Creation**:
  - Fixed issue where series folders were created in the wrong root folder
  - Added proper association between collections and root folders
  - Improved logging for folder creation process


### Changed
- **Search Functionality**:
  - Removed Book Collections and Authors sections from search
  - Redesigned search page to match original clean layout
  - Kept content type selector while removing sidebar
  - Created unified search template for both Books and Manga
  - Enhanced author search to display proper author information instead of book covers
  - Improved search results presentation with better visual distinction between books and authors
- **Books Tab UI**:
  - Removed Book Collections and Authors sections from the Books tab sidebar
  - Added Search Box and Quick Actions to the sidebar instead
  - Streamlined the Books tab interface for better user experience

## [0.1.5] - 2025-10-18

### Added
- **Content Type System**:
  - Added comprehensive content type system with service factory pattern
  - Implemented `ContentType` enum for better type safety
  - Created `BookService` and `MangaService` classes for content-specific operations
  - Added helper functions to determine content type from metadata

### Changed
- **UI Blueprint Structure**:
  - Reorganized UI routes into content-specific and shared blueprints
  - Created comprehensive UI blueprint (`ui_complete.py`) that includes all routes
  - Updated route handlers to pass necessary context variables to templates

## [0.1.4] - 2025-10-15

### Added
- **Book-specific Features**:
  - Added author-based organization for books
  - Implemented book search by author name
  - Created author detail pages with book listings
  - Added book-specific templates and routes

### Changed
- **Database Schema**:
  - Added `is_book` column to series table
  - Created authors table and book_authors relationship table
  - Updated migration system to handle schema changes
  - Added content type detection from metadata

## [0.1.3] - 2025-10-10

### Added
- **Hybrid UI Implementation**:
  - Added content type tabs to dashboard
  - Implemented dynamic content loading based on selected tab
  - Created separate book and manga home pages
  - Added API endpoints for content-specific operations

### Changed
- **Series API**:
  - Updated series API to support filtering by content type
  - Added content type parameter to search endpoints
  - Modified series list to show appropriate content based on type

## [0.1.2] - 2025-10-04

### Added
- **Collections Manager**:
  - Link Root Folder button and modal in `Collections Manager` collection details
  - Modal lists only unlinked root folders for the selected collection
  - Frontend wiring to `POST /api/collections/{id}/root-folders/{root_folder_id}` and auto-refresh of the table
- **API Documentation**:
  - Documented `GET /api/collections/default` endpoint usage across the app
- **Expanded Content Types in UI**:
  - `frontend/templates/search.html` (Import modal) and `frontend/templates/series_list.html` (Add Series) now support: Manga, Manhwa, Manhua, Comics, Novel, Book, Other.
  - Implemented subtype-to-bucket mapping function to group these under collection buckets: `MANGA` (Manga/Manhwa/Manhua), `COMIC` (Comics), `BOOK` (Book/Novel/Other).
- **Root Folder Selection**:
  - Visible Root Folder selector added to both flows, populated from the auto-selected default collection for the chosen bucket.
  - Users can optionally choose a specific root folder when a collection has multiple.
 - **Series Move API**:
  - Added `POST /api/series/{id}/move` to move a series between collections within the same bucket (DB-only, no file moves yet).
  - Returns a summary of before/after collection memberships and whether a change occurred.
  - **Series Move Feature**:
  - Backend:
    - Added [move_service.py](cci:7://file:///c:/Users/dariu/Documents/GitHub/Readloom/backend/features/move_service.py:0:0-0:0) with full move operation support (DB + filesystem)
    - Dry-run mode to preview moves before executing
    - Bucket compatibility validation (MANGA/COMIC/BOOK)
  - API:
    - Extended `POST /api/series/{id}/move` endpoint with:
      - `target_collection_id` (required)
      - `target_root_folder_id` (optional)
      - `move_files` flag for physical moves
      - `clear_custom_path` option
      - `dry_run` mode
  - UI:
    - Added Move button in series header and Quick Actions
    - Interactive Move dialog with collection/folder selectors
    - Dry-run preview panel showing paths and conflicts
    - Safety checks to prevent destructive overwrites

### Fixed
- **Default Collection Handling**:
  - Ensured only one default collection is treated as active throughout UI flows
  - Consistent Default badge display in Collections Manager
  - Safer delete behavior for default collection and clearer UX around default selection
- **UnboundLocalError in folder path endpoint**:
  - `frontend/api.py`: removed inner import shadowing of `execute_query` and moved `Path` import to top-level to fix "cannot access local variable 'execute_query'" error in `get_series_folder_path()`.

### Changed
- **Docs**:
  - Updated `docs/COLLECTIONS.md` with the new Link Root Folder workflow and troubleshooting
  - Added `docs/LINK_ROOT_FOLDER.md` guide
- **Simplified Collection Selection UX**:
  - Collection selector is now hidden in both Import and Add Series flows and auto-selected to the single default collection per bucket.
  - Import/Add requests now include `content_type` (the selected subtype), resolved `collection_id` (default per bucket), and optional `root_folder_id`.
- **Type Inference on Details Modal**:
  - Light heuristics added in `search.html` to pre-select a sensible content subtype based on title/genres/description.

## [0.1.1-1] - 2025-10-02

### Added
- **Legal Documentation**:
  - Added comprehensive LEGAL.md file with copyright policy and terms of use
  - Added copyright notice section to README.md
  - Added copyright notice card to About page in UI
  - Clarified that Readloom is a management tool, not a content distribution platform
  - Outlined legitimate use cases and user responsibilities
  
### Fixed
- **Docker Volume Mounting**:
  - Fixed docker-compose.yml to mount data folder to `/config` instead of `/data`
  - Database and logs now properly persist in the mounted volume
  - Previously data was written to `/config/data` inside container (not persisted)

## [0.1.1] - 2025-10-01

### Added
- Helper scripts for volume management:
  - `add_manga_to_database.py` - Interactive tool to add manga to static database
  - `refresh_series_volumes.py` - Update existing series with correct volume counts
  - `test_volume_fix.py` - Test volume detection accuracy
  - `test_problematic_titles.py` - Test specific problematic titles
  - `debug_specific_titles.py` - Debug volume detection for any title
- Comprehensive documentation:
  - `VOLUME_FIX_FINAL_SUMMARY.md` - Complete overview of the fix
  - `ADDING_MANGA_TO_DATABASE.md` - Guide for adding manga to static database
  - `VOLUME_FIX_SUMMARY.md` - Initial fix documentation
  - `VOLUME_FIX_UPDATE.md` - Alias support documentation
- **Smart Caching System** - Implemented comprehensive volume detection caching:
  - Database cache table (`manga_volume_cache`) for persistent storage
  - Dynamic static database (auto-populating JSON file)
  - Memory cache for session-based performance
  - Automatic cache refresh (30 days for ongoing, 90 days for completed manga)
  - Migration system integration for automatic table creation
- **Improved MangaDex API Integration**:
  - Better search matching (top 5 results, prefer manga over doujinshi)
  - Uses `lastVolume` and `lastChapter` attributes when available
  - Removes language filter for complete volume data
  - Filters out 'none' volumes for accurate counts
- **Fixed MangaFire Scraper**:
  - Changed from broken `/search?q=` to working `/filter?keyword=` endpoint
  - Updated selector from `.manga-card` to `.unit` (correct class)
  - Added language dropdown parsing for volume counts (e.g., "English (32 Volumes)")
  - Now correctly detects volumes for most manga on MangaFire

### Fixed
- **Critical: Volume Detection System Overhaul**:
  - Fixed scraper not being called during volume creation in `get_manga_details()`
  - Resolved duplicate `"volumes"` key conflict in AniList provider
  - Fixed MangaFire scraper failing due to outdated search endpoint
  - Fixed MangaDex returning incomplete data for some manga
  - Added migration call to `Readloom_direct.py` for automatic table creation
  - Volume counts now accurate for most manga:
    - Blue Exorcist: 32 volumes ✓
    - D.Gray-man: 30 volumes ✓
    - Fire Force: 34 volumes ✓
    - One Piece: 115 volumes ✓
    - One Punch Man: 29 volumes ✓
    - Attack on Titan: 34 volumes ✓
- **Volume Format Update API**:
  - Fixed `digital_format` parameter being passed to functions that don't accept it
  - Removed invalid parameter from `add_to_collection()` call
  - Removed invalid parameter from `update_collection_item()` call
  - Volume format changes (Physical ↔ Digital) now work correctly
- **Migration System**:
  - Fixed migration 0004 to use `migrate()` instead of `run_migration()`
  - Docker containers now start correctly without migration errors

### Changed
- AniList provider now calls scraper in `get_manga_details()` for accurate volume counts
- Renamed duplicate `"volumes"` key to `"volume_count"` (integer) and `"volumes"` (list)
- Updated `get_chapter_list()` to use `volume_count` from manga details
- Expanded static database from 25 to 27 manga entries with aliases
- Enhanced scraper matching logic to support alternative titles
- Updated volume format API to only use valid parameters (`format` only, removed `digital_format`)

## [0.1.0] - 2025-09-27

### Added
- Enhanced Docker support:
  - Added comprehensive Docker Hub publishing documentation
  - Created optimized .dockerignore file for smaller image sizes
  - Added Docker Hub README template for repository description
  - Updated Docker documentation with Docker Hub usage instructions

## [0.0.9] - 2025-08-15

### Added
- Generalized application terminology:
  - Added support for more book-related metadata providers (Google Books, Open Library, ISBNdb, WorldCat)
- Added comprehensive UI documentation:
  - Created new UI_STRUCTURE.md documentation file
  - Updated codebase structure documentation to include frontend
  - Added detailed descriptions of UI components and patterns

### Changed
- Generalized application terminology:
  - Updated UI references from "manga" to "e-book" throughout the application
  - Enabled Google Books by default as the recommended provider for books due to its more accurate metadata
  - Made the application more suitable for all types of e-books, not just manga/comics
- Improved UI organization and navigation:
  - Moved Root Folders management into Collections Manager for unified experience
  - Relocated Integrations into Settings page as a new tab
  - Streamlined sidebar navigation by removing redundant tabs
  - Enhanced Settings page with better tab organization
  - Made E-book Management section collapsible with quick actions
  - Repositioned Edit Series button to top-right corner as icon-only button
- Modified default metadata provider settings:
  - Only AniList provider enabled by default
  - Disabled MyAnimeList, MangaDex, MangaFire, Jikan, and MangaAPI by default
  - Improved initial performance by reducing API calls
- Enhanced Series Detail page:
  - Moved Custom Path import functionality to Edit Series modal
  - Made E-book Management section collapsible to reduce visual clutter
  - Added quick action for scanning e-books without expanding details
  - Improved overall page layout and information hierarchy


### Fixed
- Critical issues in Readloom_direct.py:
  - Added metadata service initialization to ensure database tables are created
  - Added setup check to ensure the application is properly initialized
  - Fixed Flask app creation with correct static folder path configuration
  - Properly registered all required blueprints
  - Fixed missing OS imports
  - Ensured proper static file serving for JavaScript and CSS files
  - Fixed Setup Wizard functionality when running in direct mode
- Docker container issues:
  - Added missing iproute2 package for the ip command
  - Added net-tools package for netstat command
  - Removed deprecated version attribute from docker-compose.yml
  - Added comprehensive Docker documentation

## [0.0.8] - 2025-07-02
### Added
- Folder validation functionality across the application:
  - Added validation to check if folders exist and are writable
  - Added ability to create folders directly from the UI
  - Implemented in Root Folders tab, Collection Manager, and Setup Wizard
  - Reusable JavaScript component for consistent behavior
- New API endpoints for folder validation and creation
- Backend utilities for folder validation with proper error handling
- Implemented custom path feature for series:
  - Added ability to set a custom folder path for each series
  - Files are used directly from custom path without copying
  - Custom path validation with folder creation option
  - Integrated into the Edit Series form
- Implemented robust database migration system:
  - Added framework for tracking and applying migrations
  - Created migration scripts for schema changes
  - Automatic migration application during startup
  - Improved database versioning and upgrade path
- Enhanced folder validation system:
  - Added centralized folder validation utilities
  - Improved error handling for file system operations
  - Added ability to create folders with proper permissions
  - Consistent validation across all parts of the application

### Changed
- Completely redesigned collections management approach:
  - Removed automatic creation of "Default Collection"
  - Now users create their own collections from scratch
  - Any collection can be marked as default by the user
  - Improved setup wizard to guide users through collection creation
- Improved project organization and structure:
  - Moved utility and debug scripts to 'fix and test' folder
  - Cleaned up root directory for better maintainability
  - Updated documentation to reflect new script locations
- Improved API organization and structure:
  - Added dedicated API endpoints for folder operations
  - Better separation of concerns between API modules
  - Enhanced error handling and response formatting
  - More consistent API naming conventions

### Fixed
- Fixed collections management issues:
  - Resolved issue with duplicate Default Collections being created on restart
  - Added database constraint to prevent multiple default collections
  - Added proper migration system to handle database schema updates
  - Improved collection initialization logic
- Fixed API request issues:
  - Added proper Content-Type header to AJAX requests
  - Fixed 415 Unsupported Media Type errors when importing manga
  - Ensured consistent JSON data handling across all API endpoints
- Fixed static file serving configuration:
  - Corrected static folder paths in Flask application
  - Ensured consistent static URL paths across blueprints
  - Fixed 404 errors for JavaScript files


## [0.0.7] - 2025-05-18

### Fixed
- Fixed collections management issues:
  - Improved error handling in collections management
  - Added cleanup script to fix collection database issues
  - Enhanced collection-root folder relationship management
  - Fixed delete functionality for collections and root folders
- UI improvements:
  - Renamed "Collection" tab to "Library" for clarity
  - Added Collections Manager for managing multiple collections
  - Improved UI feedback when performing collection operations
  - Enhanced error handling and debugging in JavaScript functions

## [0.0.6] - 2025-03-25

### Fixed
- Fixed folder structure creation issues:
  - Corrected LOGGER import in the `import_manga_to_collection` function
  - Fixed LOGGER import in the `api_import_manga` function
  - Ensured proper folder name sanitization while preserving spaces
  - Fixed README file creation in series folders
  - Improved error handling during folder creation
- Enhanced folder name sanitization:
  - Only replaces characters that are invalid in file names
  - Preserves spaces and most special characters for better readability
  - Properly handles question marks and other problematic characters
- Fixed metadata provider search issues with special characters

### Added
- Collection-based organization system:
  - Added collections to organize manga/comics into groups
  - Collections can be linked to multiple root folders
  - Series can belong to multiple collections
  - Setup wizard for first-time users to create collections and root folders
  - Required setup check on application startup
- Improved e-book scanning:
  - Automatic scanning of existing folders when importing series
  - Better detection of CBZ files in existing folders
  - Enhanced logging for troubleshooting scanning issues

### Changed
- Application now requires at least one collection and one root folder before use
- Updated API endpoints to enforce setup requirements
- Import process now includes information about existing folders and e-books

## [0.0.5] - 2025-01-30

### Added
- Comprehensive e-book management system
  - Organized folder structure by content type and series name
  - Automatic volume number detection from filenames
  - Support for multiple e-book formats (PDF, EPUB, CBZ, CBR, MOBI, AZW)
  - Periodic scanning for new files
  - Manual scan button in the UI
  - Collection integration with digital format tracking
  - Detailed documentation for e-book management
- Enhanced file organization
  - Content type categorization (MANGA, MANHWA, MANHUA, COMICS, NOVEL, BOOK, OTHER)
  - Human-readable folder names based on series titles
  - Automatic folder creation when adding new series
  - README files in each series folder with metadata
- Database schema updates
  - Added `content_type` field to series table
  - Created `ebook_files` table for tracking e-book files
  - Extended `collection_items` table with digital format tracking
  - Added foreign key constraints for e-book files
- Utility scripts for e-book management
  - `create_content_type_dirs.py` - Create content type directories
  - `create_missing_folders.py` - Create folders for all series
  - `create_series_folder.py` - Create folder for a specific series
  - `test_folder_scan.py` - Test e-book scanning functionality
- Periodic task system for background operations
  - Configurable scan interval for e-book files
  - Automatic collection updates when new files are found

## [0.0.4] - 2024-12-12

### Added
- Improved metadata provider support
  - Better handling of null chapter numbers
  - Enhanced release date extraction from providers
  - Fixed caching issues with metadata providers
  - Added image proxy for external images to handle CORS issues
- Foreign key constraints for better data integrity
  - Calendar events now automatically deleted when series are removed
  - Volume events deleted when volumes are removed
  - Chapter events deleted when chapters are removed
- SQLite foreign key support enabled by default
- Improved database schema documentation
- Enhanced calendar functionality
  - Removed date range restrictions to show all release dates
  - Improved handling of historical release dates
  - Fixed chapter release date display in calendar
- Major performance improvements for manga imports
  - Series-specific calendar updates instead of full collection scans
  - Enhanced MangaFire scraper with improved volume detection
  - Added multiple fallback methods for manga search
  - Implemented better error handling for API failures
- Added robust volume detection system
  - Multiple scraping sources for accurate volume data
  - Enhanced pattern matching to find volume information
  - Automatic volume generation when provider data is missing
- Improved distribution of volume release dates
  - Intelligent spacing based on publication schedule
  - More realistic release patterns
- Utility scripts for bulk operations
  - `refresh_all_volumes.py` - Batch update volumes for all manga
  - `update_manga_volumes.py` - Update volumes for specific manga
  - `test_volume_scraper.py` - Test volume scraping functionality
- Added AniList API integration as a new metadata provider
  - Complete manga search functionality
  - Detailed manga information retrieval
  - Chapter list generation with release dates
  - Support for manga recommendations
- Implemented intelligent publication schedule detection
  - Different manga types follow their actual publication patterns
  - Weekly Shonen Jump titles release on Mondays
  - Monthly seinen magazines release on Thursdays
  - Korean manhwa release on Wednesdays
- Multi-source accurate chapter counting system
  - Web scraping for hard-to-find chapter counts
  - Static database of popular manga series with accurate counts
  - Smart chapter count estimation for unknown series
  - Adaptive release date generation based on publication schedules
- Added confirmed release flags for Sonarr/Radarr-like calendar
  - Calendar now only shows upcoming releases within 7 days
  - Past chapters marked as confirmed historical data
  - Future predicted chapters marked as unconfirmed
  - Better display of release patterns

### Changed
- Updated metadata service to handle different provider return formats
- Improved error handling for manga imports
- Modified calendar event cleanup to preserve historical events
- Updated database initialization to include foreign key constraints
- Modified calendar event cleanup to use cascading deletes

### Fixed
- Fixed metadata cache type parameter issue
- Fixed database constraints for chapter numbers
- Improved handling of 'already exists' cases during manga import
- Fixed issue with release dates not appearing in calendar
- Fixed issue with orphaned calendar events after series deletion
- Improved error handling for database constraints
- Fixed MangaDex cover images not displaying properly due to incorrect URL construction
- Fixed missing fallback image for manga covers
- Added image proxy to handle CORS issues with external images
- Updated all templates (search, series list, series details, collection, dashboard) to use image proxy
- Embedded image proxy utility function directly in base template for global availability
- Fixed fallback image paths to work correctly with Flask blueprint system

## [0.0.3] - 2024-10-28

### Added
- Improved documentation structure
- API documentation with endpoint descriptions and examples
- Installation guide with Docker and manual options
- Contributor guidelines and code of conduct
- External manga source integration:
  - MangaFire integration for searching and importing manga
  - MyAnimeList (MAL) integration for metadata and searching
  - Manga-API integration for additional manga sources
  - Search interface for finding manga across multiple sources
  - Import functionality to add manga from external sources to collection
  - Metadata caching system for improved performance
  - Provider configuration UI for customizing API keys and settings

### Changed
- Updated development workflow for better compatibility
- Simplified package requirements for easier installation

### Improved
- Enhanced search capabilities across the application
- Better metadata handling with external providers
- More comprehensive manga details from multiple sources
- Fixed logging to properly write to data/logs folder
- Improved settings persistence between application restarts
- Updated MangaAPI provider to use correct API endpoints
- Added fallback to latest updates when search returns no results

## [0.0.2] - 2024-09-15

### Added
- Enhanced interactive release calendar
  - Filter options for manga/comics by type and series
  - Different view modes (month, week, day)
  - Color coding for different types of releases
  - Improved event details modal
  - Add releases to collection directly from calendar
- Comprehensive manga/comic collection tracking
  - Track ownership status, read status, and purchase details
  - Collection statistics and visualizations
  - Import/export functionality
- Monitoring system for upcoming releases
  - Notification system for upcoming releases
  - Subscription functionality for specific series
  - Multiple notification channels (browser, email, Discord, Telegram)
  - Real-time notification updates
- Home Assistant integration
  - API endpoint for Home Assistant
  - Sensor data for dashboards
  - Setup instructions and configuration examples
- Homarr integration
  - API endpoint for Homarr
  - Status information for dashboards
  - Setup instructions and configuration examples
- Modern, responsive web interface
  - Redesigned base template
  - Collapsible sidebar for desktop and mobile
  - Notification system in navigation bar
  - Modern dashboard with statistics and visualizations
  - Dark/light theme toggle with persistent settings

### Changed
- Complete UI overhaul with responsive design
- Improved database schema for better data organization
- Enhanced API endpoints with better error handling
- Optimized performance for large collections

## [0.0.1] - 2024-07-27

### Added
- Initial project structure and architecture
- Database schema for manga/comic tracking
- Basic API endpoints structure
- Simple web interface with "Coming Soon" page
- Test data generator for development
- Development environment setup script
- Docker configuration for containerization
- Basic documentation framework
- Home Assistant and Homarr integration templates

### Changed
- N/A (Initial release)

### Deprecated
- N/A (Initial release)

### Removed
- N/A (Initial release)

### Fixed
- N/A (Initial release)

### Security
- N/A (Initial release)

## How to Use This Changelog

Each version should:

- List its release date in YYYY-MM-DD format.
- Group changes to describe their impact on the project, as follows:
  - **Added** for new features.
  - **Changed** for changes in existing functionality.
  - **Deprecated** for soon-to-be removed features.
  - **Removed** for now removed features.
  - **Fixed** for any bug fixes.
  - **Security** in case of vulnerabilities.

## Release Process

1. Update the changelog with all relevant changes under the "Unreleased" section.
2. When ready to release, move the "Unreleased" changes to a new version section.
3. Tag the release in Git:
   ```bash
   git tag -a v1.2.3 -m "Release v1.2.3"
   git push origin v1.2.3
   ```
4. Create a new GitHub release with the same version number.
5. Include the changelog entries in the release notes.

## Contact

If you have questions about the changelog or release process, please contact the project maintainers.
