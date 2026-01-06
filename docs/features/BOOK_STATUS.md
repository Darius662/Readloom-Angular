# Book Status & Reading Tracking

Track your reading progress, rate books, and add personal notes for each book in your collection.

## Overview

The Book Status feature allows you to:
- **Rate books** with a 5-star rating system
- **Track reading progress** with 5 preset levels (0%, 25%, 50%, 75%, 100%)
- **Add personal notes** about each book
- **Filter and sort** your library by rating and progress
- **Visualize progress** with progress bars on book covers

## Features

### Star Rating System

Rate each book on a scale of 1-5 stars:
- Click on any star to set your rating
- Visual feedback shows your current rating
- Filter library by rating threshold (5 stars, 4+ stars, 3+ stars, etc.)
- Sort library by rating (highest-rated first)
- Display on library cards shows your rating or "Not rated yet"

### Reading Progress Tracking

Track your reading progress with 5 preset levels:
- **0%** - Not started
- **25%** - Started
- **50%** - Half-way
- **75%** - In progress
- **100%** - Completed

Features:
- Visual progress bar overlay on book covers
- Floating island style with rounded corners and gradient
- Displays percentage text inside the progress bar
- Filter library by progress level
- Sort library by progress (highest progress first)

### Personal Notes

Add custom notes or descriptions for each book:
- Textarea for writing your thoughts about the book
- Save notes along with rating and progress
- Notes are displayed on the book detail page

## How to Use

### Rating a Book

1. Navigate to a book's detail page
2. Find the "Reading Status" card
3. Click on the stars to set your rating (1-5)
4. Click "Save Status" to save your rating

### Tracking Progress

1. On the book detail page, find the "Reading Status" card
2. Click on the progress level buttons (0%, 25%, 50%, 75%, 100%)
3. The selected progress level will be highlighted
4. Click "Save Status" to save your progress

### Adding Notes

1. On the book detail page, find the "Reading Status" card
2. Click in the "Your Notes" textarea
3. Type your thoughts, impressions, or reminders about the book
4. Click "Save Status" to save your notes

### Filtering by Rating

1. Go to the Book Library
2. Use the "All Ratings" dropdown to filter by rating:
   - **All Ratings** - Show all books
   - **5 Stars** - Show only 5-star books
   - **4+ Stars** - Show books rated 4 or higher
   - **3+ Stars** - Show books rated 3 or higher
   - **2+ Stars** - Show books rated 2 or higher
   - **1+ Stars** - Show books rated 1 or higher
   - **Unrated** - Show books with no rating

### Filtering by Progress

1. Go to the Book Library
2. Use the "All Progress" dropdown to filter by progress:
   - **All Progress** - Show all books
   - **Completed (100%)** - Show only completed books
   - **In Progress (75%+)** - Show books 75% or more read
   - **Half-way (50%+)** - Show books 50% or more read
   - **Started (25%+)** - Show books 25% or more read
   - **Not Started** - Show books with 0% progress

### Sorting by Rating or Progress

1. Go to the Book Library
2. Use the "Sort by" dropdown to choose:
   - **Sort by Rating** - Highest-rated books first
   - **Sort by Progress** - Most-read books first

## Database

The Book Status feature uses the following database columns in the `series` table:
- `star_rating` (REAL) - Rating from 0-5
- `reading_progress` (INTEGER) - Progress percentage (0, 25, 50, 75, 100)
- `user_description` (TEXT) - Custom user notes

These columns are created automatically via database migration `0021_add_book_status_tracking.py`.

## API Endpoints

### Get Book Status
```
GET /api/books/<id>/status
```

Returns the current status of a book:
```json
{
  "id": 1,
  "star_rating": 4.5,
  "reading_progress": 75,
  "user_description": "Great book! Really enjoyed the plot."
}
```

### Update Book Status
```
PUT /api/books/<id>/status
```

Request body:
```json
{
  "star_rating": 4.5,
  "reading_progress": 75,
  "user_description": "Great book! Really enjoyed the plot."
}
```

Response:
```json
{
  "success": true,
  "message": "Book status updated successfully"
}
```

## Files

- **Backend**: `frontend/api/series/routes.py` - API endpoints
- **Frontend**: `frontend/templates/books/book.html` - UI template
- **JavaScript**: `frontend/static/js/book-status.js` - Interactive functionality
- **Database**: `backend/migrations/0021_add_book_status_tracking.py` - Schema migration

## Related Features

- **[Book Recommendations](RECOMMENDATIONS.md)** - Get personalized book recommendations based on your ratings
- **[Collections](COLLECTIONS.md)** - Organize books into collections
