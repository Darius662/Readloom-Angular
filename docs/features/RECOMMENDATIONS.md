# Book Recommendations

Get personalized book recommendations based on your ratings, reading progress, and notes.

## Overview

The Book Recommendations feature provides two types of recommendations:

1. **AI-Powered Recommendations** - Uses AI to generate personalized recommendations based on your thoughts about the book
2. **Category-Based Recommendations** - Falls back to showing books in the same category if AI is unavailable

## Features

### AI-Powered Recommendations

The AI recommendation system:
- Analyzes the book you're viewing
- Considers your star rating of the book
- Reads your personal notes about the book
- Tracks your reading progress
- Generates a list of similar books you might enjoy
- Searches metadata providers to find those books
- Returns up to 10 recommendations

**Supported AI Providers:**
- Groq (recommended for best performance)
- Google Gemini
- DeepSeek
- Ollama (local)

### Category-Based Recommendations

If AI is unavailable:
- Finds books with matching genres/categories
- Returns books in the same category as the current book
- Returns up to 10 recommendations
- Provides a fallback when AI is not configured

### Smart Caching

Recommendations are cached to:
- Reduce API calls to AI providers
- Provide consistent results across page refreshes
- Automatically invalidate when book details change (rating, notes, progress)
- Improve performance and reduce latency

### Recommendation Cards

Each recommendation displays:
- **Book Cover** - Full cover image with proper aspect ratio (2:3)
- **Title** - Truncated with "..." if too long
- **Author** - Author name
- **Book Details Button** - Opens a modal with full information

### Recommendation Modal

Click "Book Details" on any recommendation to see:
- **Cover Image** - Full book cover
- **Title & Author** - Complete information
- **Publisher** - Publishing company
- **Published Date** - Publication date
- **ISBN** - ISBN number
- **Subjects/Genres** - Category badges
- **Description** - Full book description
- **Metadata Source** - Where the data came from
- **Collection Dropdown** - Select which collection to add to
- **Root Folder Dropdown** - Optional folder selection
- **Add to Collection Button** - Add the recommended book to your library

## How to Use

### View Recommendations

1. Navigate to any book's detail page
2. Scroll down to the "Recommended for You" section
3. Browse the recommendation cards
4. Each card shows the cover, title, and author

### View Book Details

1. Click the "Book Details" button on any recommendation card
2. A modal opens showing complete book information
3. Review the description and metadata
4. Optionally add the book to your collection

### Add Recommended Book to Collection

1. Click "Book Details" on a recommendation
2. In the modal, select a collection from the "Collection" dropdown
3. Optionally select a root folder
4. Click "Add to Collection"
5. The book is added to your library

### Configure AI Provider

To use AI recommendations, configure an AI provider:

1. Go to Settings
2. Find the AI Providers section
3. Configure Groq, Gemini, DeepSeek, or Ollama
4. Save your configuration
5. AI recommendations will now be available

## How It Works

### AI Recommendation Process

1. **Fetch Book Data** - Get the current book's information
2. **Prepare Prompt** - Create an AI prompt including:
   - Book title, author, genres
   - Your star rating
   - Your reading progress
   - Your personal notes
3. **Generate Recommendations** - AI generates a list of similar books
4. **Search Metadata** - Search for those books in metadata providers
5. **Return Results** - Return up to 10 found books
6. **Cache Results** - Store results with a hash of book details

### Cache Invalidation

The cache is automatically invalidated when:
- Your star rating changes
- Your reading progress changes
- Your personal notes are updated
- The book's genres/subjects change

This ensures recommendations stay fresh and relevant to your current thoughts about the book.

## Database

Recommendations are cached in the `recommendation_cache` table:
- `book_id` - ID of the book being recommended
- `book_details_hash` - Hash of book details (for cache validation)
- `recommendations` - JSON array of recommended books
- `created_at` - When the cache was created
- `updated_at` - When the cache was last updated

## API Endpoints

### Get AI Recommendations
```
GET /api/books/<id>/recommendations/ai
```

Query Parameters:
- None (uses book ID from URL)

Response:
```json
{
  "success": true,
  "method": "ai",
  "cached": false,
  "recommendations": [
    {
      "id": "12345",
      "title": "Similar Book Title",
      "author": "Author Name",
      "cover_url": "https://...",
      "publisher": "Publisher Name",
      "published_date": "2023-01-15",
      "isbn": "978-1234567890",
      "subjects": "Fiction, Mystery, Thriller",
      "description": "Book description...",
      "metadata_source": "GoogleBooks",
      "metadata_id": "12345"
    }
  ]
}
```

### Get Category Recommendations
```
GET /api/books/<id>/recommendations/category
```

Returns books in the same category (fallback if AI fails).

## Files

- **Backend**: `frontend/api/series/routes.py` - API endpoints and AI integration
- **Frontend**: `frontend/templates/books/book.html` - UI template
- **JavaScript**: `frontend/static/js/book-recommendations.js` - Interactive functionality
- **Database**: `backend/migrations/0022_add_recommendation_cache.py` - Cache table schema

## Configuration

### AI Provider Configuration

Edit `data/ai_providers_config.json`:

```json
{
  "groq": {
    "enabled": true,
    "api_key": "your-groq-api-key"
  },
  "gemini": {
    "enabled": false,
    "api_key": "your-gemini-api-key"
  },
  "deepseek": {
    "enabled": false,
    "api_key": "your-deepseek-api-key"
  },
  "ollama": {
    "enabled": false,
    "base_url": "http://localhost:11434"
  }
}
```

## Troubleshooting

### No Recommendations Appearing

1. Check that at least one AI provider is configured
2. Verify the book has genres/subjects
3. Check the server logs for errors
4. Try refreshing the page

### AI Recommendations Not Working

1. Verify your AI provider API key is valid
2. Check that the provider is enabled in settings
3. Ensure you have internet connectivity
4. Check server logs for API errors

### Recommendations Are Stale

1. Update the book's rating or notes
2. This will invalidate the cache and generate new recommendations
3. Or wait for the cache to expire (if configured)

## Related Features

- **[Book Status](BOOK_STATUS.md)** - Rate books and track reading progress
- **[Collections](COLLECTIONS.md)** - Organize recommended books into collections
- **[Metadata Providers](../metadata-providers/)** - Learn about book data sources
