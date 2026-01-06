# Author Biography Setup

## Overview
Author biographies are automatically fetched from Groq AI when you add books or manga to your library. The system will attempt to fetch a 2-3 sentence biography for each author.

## How It Works

When you import a book/manga:
1. Author is created/linked to the series
2. `update_author_biography()` is called automatically
3. Groq AI generates a biography based on the author name
4. Biography is stored in the database
5. Biography appears in the Authors tab

## Requirements

To enable automatic biography fetching, you need to configure a **Groq API key**.

### Getting a Groq API Key

1. **Visit Groq Console**: https://console.groq.com/
2. **Sign up** (free account)
3. **Create an API key** in your account settings
4. **Copy the API key**

### Configuring the API Key

You can set the Groq API key in two ways:

#### Option 1: Environment Variable (Recommended for Development)
```bash
export GROQ_API_KEY="your-api-key-here"
```

#### Option 2: Database Settings (Recommended for Production)
The system will automatically look for the API key in the database settings table under the key `groq_api_key`.

You can set this via:
- Settings page in the application (if available)
- Direct database query:
  ```sql
  INSERT INTO settings (key, value) VALUES ('groq_api_key', '"your-api-key-here"');
  ```

## Troubleshooting

### Biographies Not Appearing

Check the server logs for these messages:

**Missing API Key:**
```
GROQ_API_KEY not set in database settings or environment - cannot fetch biography for [Author Name]
```

**Solution:** Configure the Groq API key as described above.

**API Error:**
```
Error fetching author biography from Groq: [error message]
```

**Solution:** Check that your API key is valid and you have API quota remaining.

### Checking If Biography Fetch is Working

Look for these log messages when importing a book:

**Success:**
```
Attempting to fetch biography for author [Author Name] (ID: [ID])
Successfully updated author [Author Name] with biography: [First 50 chars]...
```

**Failure:**
```
Could not fetch biography for author [Author Name] - Groq API key may not be configured
```

## Manual Biography Update

To fetch biographies for all authors without biographies:

You can call the `fetch_and_update_all_author_biographies()` function from `backend/features/author_biography_fetcher.py`:

```python
from backend.features.author_biography_fetcher import fetch_and_update_all_author_biographies

stats = fetch_and_update_all_author_biographies()
print(stats)
# Output: {'authors_checked': 5, 'biographies_added': 4, 'errors': 0}
```

## Features

- **Automatic Fetching**: Biographies are fetched automatically when authors are created
- **AI-Powered**: Uses Groq's Llama 3.3 70B model for high-quality biographies
- **Concise**: Generates 2-3 sentence biographies focusing on notable works and literary significance
- **Fallback**: If Groq is unavailable, the system continues without biography (no errors)
- **Batch Update**: Can update all authors without biographies at once

## API Model

The system uses:
- **Model**: `llama-3.3-70b-versatile`
- **Max Tokens**: 200
- **Provider**: Groq (free tier available)

## Performance

- Biography fetching is **non-blocking** - it happens in the background
- Each biography takes ~1-2 seconds to fetch
- Failed fetches are logged but don't prevent author creation

## Future Enhancements

1. Add UI to manually edit author biographies
2. Add option to re-fetch biography for existing authors
3. Add support for multiple AI providers (OpenAI, Anthropic, etc.)
4. Add biography caching to avoid re-fetching
5. Add author photo fetching from OpenLibrary

## Files Involved

- `backend/features/author_biography_fetcher.py` - Main biography fetching logic
- `backend/features/authors_sync.py` - Calls biography fetcher during author sync
- `backend/features/author_photo_fetcher.py` - Fetches author photos (separate)

## Related Documentation

- [Author Sync Fix](AUTHOR_SYNC_FIX.md) - How authors are created and linked
- [Authors Tab Fix](AUTHORS_TAB_FIX.md) - Authors tab improvements
