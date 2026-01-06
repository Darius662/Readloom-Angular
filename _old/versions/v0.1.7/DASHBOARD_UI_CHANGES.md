# Dashboard UI Changes

## Overview
The Dashboard has been redesigned to show more relevant statistics with separate counts for Manga Series, Books, and Authors.

## Changes Made

### Updated Components
The following stat cards are now visible on the Dashboard:

1. **Manga Series Card** (Blue)
   - Shows count of all manga series in the library
   - Status: Visible and active
   - Icon: Book icon

2. **Books Card** (Green)
   - Shows count of all books in the library
   - Status: Visible and active
   - Icon: Book-open icon

3. **Authors Card** (Cyan/Info)
   - Shows count of all authors currently in the library
   - Status: Visible and active
   - Icon: User-edit icon

4. **Today's Releases Card** (Yellow/Warning)
   - Shows releases scheduled for today
   - Status: Visible and active
   - Icon: Calendar-day icon

### Hidden Components
The following stat cards have been hidden from the Dashboard:

1. **Volumes Card** (Green)
   - Shows total volume count
   - Status: Hidden (code commented)
   - Location: `frontend/templates/dashboard.html` lines 148-163

2. **Chapters Card** (Blue)
   - Shows total chapter count
   - Status: Hidden (code commented)
   - Location: `frontend/templates/dashboard.html` lines 165-180

## Current Dashboard Layout

### Before
```
[Series] [Volumes] [Chapters] [Today's Releases]
```

### After
```
[Manga Series] [Books] [Authors] [Today's Releases]
```

## Implementation Details

### HTML Changes
- Renamed "Series" label to "Manga Series"
- Updated series-count ID to manga-series-count
- Added new Books card with books-count ID
- Added new Authors card with authors-count ID
- Volumes and Chapters cards wrapped in HTML comment blocks
- All original code preserved for easy restoration

### JavaScript Changes
- Updated `loadDashboardData()` function to populate new fields:
  ```javascript
  document.getElementById('manga-series-count').textContent = data.stats.manga_series_count || 0;
  document.getElementById('books-count').textContent = data.stats.books_count || 0;
  document.getElementById('authors-count').textContent = data.stats.authors_count || 0;
  document.getElementById('releases-today').textContent = data.stats.releases_today || 0;
  ```

### Backend API Changes
- Updated `/api/dashboard` endpoint in `frontend/api.py`
- Added separate queries for:
  - `manga_series_count`: Count of series with content_type = 'manga'
  - `books_count`: Count of series with content_type = 'book'
  - `authors_count`: Count of all authors
- Response now includes these new fields in stats object

## How to Re-enable Volumes and Chapters

To restore the Volumes and Chapters cards:

1. **Uncomment HTML in `frontend/templates/dashboard.html`**:
   - Remove comment markers from lines 148-163 (Volumes card)
   - Remove comment markers from lines 165-180 (Chapters card)

2. **Uncomment JavaScript in `frontend/templates/dashboard.html`**:
   - Uncomment lines that populate volumes-count and chapters-count in `loadDashboardData()`

3. **Refresh the browser** to see the changes

## Files Modified

| File | Changes | Type |
|------|---------|------|
| `frontend/templates/dashboard.html` | Renamed Series to Manga Series, added Books and Authors cards | UI/JS |
| `frontend/api.py` | Updated dashboard API to return new stat fields | Backend |

## Testing

After making changes, verify:
- [ ] Dashboard loads without errors
- [ ] Manga Series card displays correct manga count
- [ ] Books card displays correct books count
- [ ] Authors card displays correct authors count
- [ ] Today's Releases card displays correct count
- [ ] No console errors in browser developer tools
- [ ] Responsive design works on mobile devices
- [ ] All stat cards align properly in a row

## Future Considerations

- Consider making dashboard card visibility configurable via settings
- Add user preferences for which stats to display
- Create dashboard customization panel
- Add ability to reorder stat cards
