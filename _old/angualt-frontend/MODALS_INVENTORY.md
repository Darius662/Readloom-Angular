# Readloom Modals and Popups Inventory

## Complete Modal List from Old Frontend

### 1. Collections Management Modals
**File**: `collections_modals.html`

#### 1.1 Add Root Folder Modal
- **ID**: `addRootFolderModal`
- **Purpose**: Add a new root folder for content storage
- **Fields**: Name, Path (with browse button), Content Type dropdown
- **Actions**: Save, Cancel
- **API**: POST `/api/folders/add`

#### 1.2 Edit Root Folder Modal
- **ID**: `editRootFolderModal`
- **Purpose**: Edit existing root folder
- **Fields**: Name, Path (with browse button), Content Type dropdown
- **Actions**: Update, Cancel
- **API**: PUT `/api/folders/{id}`

#### 1.3 Add Root Folder to Collection Modal
- **ID**: `addRootFolderToCollectionModal`
- **Purpose**: Link a root folder to a collection
- **Fields**: Select Root Folder dropdown
- **Actions**: Add, Cancel
- **API**: POST `/api/collections/{id}/add-root-folder`

#### 1.4 Delete Confirmation Modal
- **ID**: `deleteConfirmationModal`
- **Purpose**: Confirm deletion of items
- **Fields**: Dynamic confirmation text, warning alert
- **Actions**: Delete, Cancel
- **API**: DELETE (varies by context)

#### 1.5 Setup Wizard Modal
- **ID**: `setupWizardModal`
- **Purpose**: Initial setup for first-time users
- **Steps**: 
  - Step 1: Create first collection
  - Step 2: Add root folder
  - Step 3: Finish setup
- **Actions**: Next, Previous, Finish Setup
- **API**: POST `/api/collections`, POST `/api/folders/add`

#### 1.6 Folder Browser Modal
- **ID**: `folderBrowserModal`
- **Purpose**: Browse file system for folder selection
- **Features**: 
  - Current path display
  - Folder navigation (Up, Home buttons)
  - Drive selection (Windows)
  - Folder list with scrolling
  - Selected path display
- **Actions**: Select, Cancel
- **API**: POST `/api/folders/browse`

---

### 2. Search Modals
**Files**: `books/search.html`, `manga/search.html`

#### 2.1 Book Details Modal
- **ID**: `bookDetailsModal`
- **Purpose**: Display detailed book information from search results
- **Sections**:
  - Cover image (left column)
  - Collection selector
  - Root folder selector
  - Add to Collection button
  - Want to Read button
  - Book details (right column): Title, Alt titles, Author, Publisher, Published date, ISBN, Subjects, Description
- **Actions**: Add to Collection, Want to Read, Close
- **API**: GET `/api/metadata/book/{id}`, POST `/api/series/add`

#### 2.2 Manga Details Modal
- **ID**: `mangaDetailsModal`
- **Purpose**: Display detailed manga information from search results
- **Sections**:
  - Cover image (left column)
  - Content Type selector (Manga/Manhwa/Manhua/Comics)
  - Collection selector
  - Root folder selector
  - Add to Collection button
  - Want to Read button
  - View Chapters button
  - Manga details (right column): Title, Alt titles, Status badge, Source badge, Rating badge, Author, Genres, Description
  - Chapters section (collapsible): List of chapters with loading indicator
- **Actions**: Add to Collection, Want to Read, View Chapters, Close
- **API**: GET `/api/metadata/manga/{id}`, POST `/api/series/add`, GET `/api/metadata/manga/{id}/chapters`

#### 2.3 Import Success Modal
- **ID**: `importSuccessModal`
- **Purpose**: Confirm successful import of book/manga
- **Content**: Success icon, success message, View Book/Series link
- **Actions**: Close, View Book/Series
- **API**: None (display only)

---

### 3. Series Detail Modals
**File**: `series_detail.html`

#### 3.1 Move Series Modal
- **ID**: `moveSeriesModal`
- **Purpose**: Move series to different collection/root folder
- **Fields**:
  - Target Collection dropdown
  - Target Root Folder dropdown
  - Physically move files toggle
  - Clear custom path after move toggle
  - Dry run preview (pre element)
- **Actions**: Preview (Dry Run), Execute Move
- **API**: POST `/api/series/{id}/move` (with dry_run parameter)

#### 3.2 Add/Edit Volume Modal
- **ID**: `volumeModal`
- **Purpose**: Add or edit volume information
- **Fields**: Volume Number, Title, Description, Release Date, Cover URL
- **Actions**: Save Volume, Cancel
- **API**: POST `/api/series/{id}/volumes`, PUT `/api/series/{id}/volumes/{volume_id}`

#### 3.3 Add/Edit Chapter Modal
- **ID**: `chapterModal`
- **Purpose**: Add or edit chapter information
- **Fields**: Chapter Number, Title, Volume (dropdown), Description, Release Date, Status (dropdown), Read Status (dropdown)
- **Actions**: Save Chapter, Cancel
- **API**: POST `/api/series/{id}/chapters`, PUT `/api/series/{id}/chapters/{chapter_id}`

#### 3.4 Edit Series Modal
- **ID**: `seriesModal`
- **Purpose**: Edit series metadata
- **Fields**:
  - Title (required)
  - Author
  - Publisher
  - Content Type (dropdown)
  - Status (dropdown)
  - Description
  - Cover URL
  - Custom Path (with browse and validate buttons)
  - Import from custom path toggle
- **Actions**: Save Series, Cancel
- **API**: PUT `/api/series/{id}`

#### 3.5 Delete Confirmation Modal
- **ID**: `deleteModal`
- **Purpose**: Confirm deletion of series/volume/chapter
- **Content**: Dynamic delete message
- **Actions**: Delete, Cancel
- **API**: DELETE (varies by context)

---

### 4. Settings Modals
**File**: `settings.html`

#### 4.1 Link Root Folder to Collection Modal
- **ID**: `linkRootFolderModal`
- **Purpose**: Link root folder to collection from settings
- **Fields**: Root Folder dropdown (only shows unlinked folders)
- **Actions**: Link, Cancel
- **API**: POST `/api/collections/{id}/add-root-folder`

---

## Implementation Priority

### Phase 1: Critical Modals (Week 1)
1. **Delete Confirmation Modal** - Generic, reusable
2. **Book Details Modal** - Essential for search functionality
3. **Manga Details Modal** - Essential for search functionality
4. **Import Success Modal** - Feedback for user actions

### Phase 2: Collections Management (Week 2)
5. **Add Root Folder Modal**
6. **Edit Root Folder Modal**
7. **Add Root Folder to Collection Modal**
8. **Folder Browser Modal** - Complex, requires file system API

### Phase 3: Series Management (Week 3)
9. **Move Series Modal**
10. **Add/Edit Volume Modal**
11. **Add/Edit Chapter Modal**
12. **Edit Series Modal**

### Phase 4: Setup & Advanced (Week 4)
13. **Setup Wizard Modal** - For first-time users
14. **Link Root Folder to Collection Modal** - Settings-specific

---

## Technical Implementation Notes

### Modal Service Architecture
- Create `ModalService` in Angular for centralized modal management
- Use Angular Material Dialog or Bootstrap modals
- Implement reusable modal components
- Handle modal state management

### API Integration
- All modals will use existing Flask backend APIs
- Maintain CORS configuration for API calls
- Implement proper error handling and validation

### Styling
- Use old UI color scheme: #212529, #2c3034, #373b3e, #0d6efd, #f8f9fa
- Bootstrap modal styling with custom CSS overrides
- Responsive design for mobile/tablet

### State Management
- Use Angular services for modal data
- Implement proper cleanup on modal close
- Handle form validation before submission

---

## File Structure for Angular Implementation

```
frontend-angular/src/app/
├── components/
│   └── modals/
│       ├── delete-confirmation/
│       ├── book-details/
│       ├── manga-details/
│       ├── import-success/
│       ├── add-root-folder/
│       ├── edit-root-folder/
│       ├── add-root-folder-collection/
│       ├── folder-browser/
│       ├── move-series/
│       ├── volume-form/
│       ├── chapter-form/
│       ├── edit-series/
│       ├── setup-wizard/
│       └── link-root-folder/
├── services/
│   └── modal.service.ts
└── ...
```

---

## Next Steps
1. Create ModalService for centralized management
2. Implement Phase 1 modals
3. Test with Flask backend APIs
4. Gradually add remaining modals
5. Implement form validation and error handling
