# Readloom Changelog - December 15, 2025

## Summary
Fixed critical bugs in book import logic, implemented folder picker functionality, and resolved book deletion redirect issues.

---

## Features Implemented

### 1. Folder Picker Implementation
**Status:** ✅ Completed

Added a user-friendly folder picker modal with browse buttons throughout the application:

- **Added browse buttons to all folder path input locations:**
  - `setup_wizard.html` - Setup Wizard Step 2
  - `settings.html` - Add and Edit Root Folder modals
  - `collections_manager.html` - Add and Edit Root Folder modals
  - `collections_modals.html` - Add and Edit Root Folder modals
  - `series_detail.html` - Edit Series custom path input
  - `books/book.html` - Edit Book custom path input
  - `root_folders.html` - Add/Browse Root Folder modal

- **Created shared folder browser module:**
  - `/frontend/static/js/folder-browser.js` - Reusable FolderBrowser class
  - Manages modal interactions and folder navigation
  - Supports Windows drive listing and navigation

- **Backend API for folder browsing:**
  - `/frontend/api_folder_browser.py` - New API endpoints
  - `/api/folders/browse` - List directories and drives
  - `/api/folders/validate` - Validate folder paths
  - Registered with Flask app in `backend/internals/server.py`

---

## Bug Fixes

### 2. Book Import Title Bug
**Status:** ✅ Completed
**File:** `/backend/features/ebook_files.py`

**Issue:** Books were being imported with folder names instead of series titles from README metadata.
- Example: "Game On" by Navessa Allen was imported as "Game On Lincoln Pierce" (the folder name)

**Root Cause:** Import logic was using `series_dir_name` (folder name) instead of `readme_metadata.get('title')` (series name from README)

**Solution:** Updated both series creation locations in `ebook_files.py`:
- Line 631: Added `series_title = readme_metadata.get('title') or series_dir_name`
- Line 797: Added same logic in `scan_for_ebooks` function
- Updated all INSERT and SELECT queries to use `series_title` instead of `series_dir_name`

**Impact:** Books now import with correct series titles from README metadata

---

### 3. Book Import Author Bug
**Status:** ✅ Completed
**File:** `/backend/features/ebook_files.py`

**Issue:** Author information from README was being overwritten by external provider data (OpenLibrary).
- Example: "Game On" by Navessa Allen was being imported as "Game On" by Lincoln Pierce

**Root Cause:** `enrich_series_metadata()` function was fetching metadata from external providers and overwriting README data without checking if README data already existed

**Solution:** Modified `enrich_series_metadata()` to preserve README metadata:
- Lines 456-464: Retrieve current series data (author, description, cover_url) from database
- Lines 494-500: For MANGA - preserve README author, description, and cover_url if they exist
- Lines 539-545: For BOOK - preserve README author, description, and cover_url if they exist

**Impact:** README metadata is now prioritized over external provider data. Only status is fetched from providers if not already set.

---

### 4. Book Deletion Redirect Issue
**Status:** ✅ Completed
**File:** `/frontend/templates/books/book.html`

**Issue:** When deleting a book, the modal wouldn't close and user wouldn't be redirected to Books tab. Button stayed in "Deleting" state.

**Root Causes:**
1. API response check was looking for `response.success` field that doesn't exist (API returns `{"message": "..."}`)
2. `showToast()` function was not defined in proper scope, causing ReferenceError
3. Modal closing logic used `getInstance()` which could return null

**Solutions:**

**Step 1 - Fixed API response handling:**
- Removed the `if (response.success)` check
- Now success callback executes directly on successful API response

**Step 2 - Fixed showToast scope issue:**
- Moved `showToast()` function definition outside of `$(document).ready()` block
- Changed from `window.showToast = function()` to standard `function showToast()` declaration
- Function is now properly hoisted and accessible throughout the page

**Step 3 - Improved modal closing:**
- Changed from `bootstrap.Modal.getInstance()` to `bootstrap.Modal.getOrCreateInstance()`
- More reliable modal closing mechanism

**Step 4 - Simplified redirect logic:**
- Removed referrer checking (was causing issues)
- Now always redirects to Books home page after deletion
- Increased redirect delay to 1500ms to allow toast to display

**Implementation Details:**
- Added inline toast creation in delete success callback
- Added console logging for debugging
- Added timeout to AJAX request (10 seconds)
- Proper error handling with toast display on failure

**Impact:** Book deletion now works smoothly:
1. Click delete → button shows "Deleting..." state
2. Success toast appears
3. Modal closes
4. After 1.5 seconds, user is redirected to Books tab

---

## Technical Details

### Modified Files
1. `/backend/features/ebook_files.py`
   - Lines 456-464: Added retrieval of current series metadata
   - Lines 494-500: Added README metadata preservation for MANGA
   - Lines 539-545: Added README metadata preservation for BOOK
   - Lines 631: Added series_title from README
   - Lines 797: Added series_title from README in scan_for_ebooks

2. `/frontend/templates/books/book.html`
   - Lines 535-559: Defined `showToast()` function in global scope
   - Lines 893-972: Rewrote delete book handler with inline toast creation
   - Removed dependency on undefined function references

3. `/frontend/api_folder_browser.py`
   - Created new file with folder browsing API endpoints

4. `/backend/internals/server.py`
   - Registered folder_browser_api_bp blueprint

5. Multiple template files (added browse buttons):
   - `setup_wizard.html`
   - `settings.html`
   - `collections_manager.html`
   - `collections_modals.html`
   - `series_detail.html`
   - `books/book.html`
   - `root_folders.html`

### Testing Recommendations
1. Test book deletion flow end-to-end
2. Test folder picker in all locations
3. Test book import with README metadata
4. Verify author information is preserved from README
5. Test redirect after book deletion

---

## Known Issues / Notes
- Pre-existing JavaScript lint errors in book.html related to Jinja2 template syntax (do not affect functionality)
- Folder picker uses HTML5 `webkitdirectory` attribute (works in modern browsers)

---

## Completion Status
✅ All tasks completed successfully

- ✅ Folder Picker Implementation
- ✅ Book Import Title Bug Fix
- ✅ Book Import Author Bug Fix
- ✅ Book Deletion Redirect Fix
