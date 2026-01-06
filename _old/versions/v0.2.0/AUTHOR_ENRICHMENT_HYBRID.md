# Author Enrichment: Hybrid Approach

## Overview
Readloom now uses a hybrid approach to populate author metadata with three sources in priority order:

1. **OpenLibrary** (Primary) - Most accurate, verified data
2. **Groq AI** (Fallback) - For missing data
3. **Manual Edits** (Override) - User corrections

## How It Works

### Enrichment Priority Flow

```
User clicks "Enrich Authors"
    ↓
For each author without complete data:
    ↓
Try OpenLibrary API
    ├─ Found? → Update author, continue to next
    └─ Not found? → Try Groq AI
    ↓
Try Groq AI for biography
    ├─ Success? → Add biography
    └─ Failed? → Try photo fetcher
    ↓
Try OpenLibrary for photo
    ├─ Success? → Add photo
    └─ Failed? → Move to next author
    ↓
User can manually edit any field
```

## Data Sources

### 1. OpenLibrary (Primary)

**What it provides:**
- Author biography
- Birth date
- Death date (if applicable)
- Author photo
- OpenLibrary key for reference

**Advantages:**
- ✅ Most accurate data
- ✅ Verified and curated
- ✅ Free, no API key needed
- ✅ Comprehensive coverage
- ✅ Well-maintained

**Limitations:**
- ❌ May not have all authors
- ❌ Occasionally incomplete data

**API:** https://openlibrary.org/api/

### 2. Groq AI (Fallback)

**What it provides:**
- Author biography (generated)
- Contextual information

**Advantages:**
- ✅ Works for any author
- ✅ Generates custom content
- ✅ Fast responses
- ✅ Free tier available

**Limitations:**
- ❌ Can hallucinate or be inaccurate
- ❌ Generated, not verified
- ❌ Requires API key

**API:** https://console.groq.com/

### 3. Manual Edits (Override)

**What you can edit:**
- Author name
- Biography
- Birth date
- Description

**Advantages:**
- ✅ Full user control
- ✅ Can correct AI/OpenLibrary data
- ✅ Add custom information
- ✅ No external dependencies

**How to use:**
- Click "Edit" button on author card
- Modify any field
- Click "Save"

## API Endpoints

### Enrich All Authors
```
POST /api/authors/enrich-all

Response:
{
  "success": true,
  "message": "Author enrichment completed",
  "stats": {
    "authors_checked": 45,
    "openlibrary_updated": 30,
    "biographies_added": 10,
    "photos_added": 5,
    "errors": 0
  }
}
```

### Enrich Single Author
```
POST /api/authors/{author_id}/enrich

Response:
{
  "success": true,
  "message": "Author enriched",
  "stats": {
    "biography_added": true,
    "photo_added": true
  }
}
```

### Edit Author Manually
```
PUT /api/authors/{author_id}/edit

Request body:
{
  "name": "Stephen King",
  "biography": "American author of horror and suspense...",
  "birth_date": "1947-09-21",
  "description": "Master of horror fiction"
}

Response:
{
  "success": true,
  "message": "Author updated successfully",
  "author": {
    "id": 1,
    "name": "Stephen King",
    "biography": "American author...",
    "birth_date": "1947-09-21",
    "description": "Master of horror fiction",
    "photo_url": "https://..."
  }
}
```

### Check Incomplete Authors
```
GET /api/authors/check-incomplete

Response:
{
  "total_authors": 50,
  "authors_without_biography": 10,
  "authors_without_photo": 15,
  "incomplete_authors": 20
}
```

## Usage Guide

### Automatic Enrichment (Recommended)

1. **Go to Authors Tab**
   - Click "Enrich Authors" button
   - System automatically enriches all authors

2. **What Happens:**
   - OpenLibrary data is fetched first (most accurate)
   - For missing data, Groq AI fills gaps
   - Photos are fetched from OpenLibrary
   - All data is stored in database

3. **Results:**
   - Authors now have biographies
   - Authors have photos
   - Birth dates are populated
   - All information is searchable

### Manual Edits

1. **Click Edit on Author Card**
   - Edit form appears
   - Modify any field
   - Click "Save"

2. **What You Can Edit:**
   - Author name
   - Biography
   - Birth date
   - Description

3. **Changes Are Saved:**
   - Immediately stored in database
   - Visible in author details
   - Not overwritten by enrichment

## Configuration

### OpenLibrary
- No configuration needed
- Free, no API key required
- Always available

### Groq AI
- Requires API key
- Set in Settings → AI Providers
- Free tier available

### Manual Edits
- No configuration needed
- Available anytime

## Data Quality

### Accuracy Levels

| Source | Accuracy | Coverage | Speed |
|--------|----------|----------|-------|
| OpenLibrary | High ✅ | 70-80% | Fast |
| Groq AI | Medium ⚠️ | 100% | Fast |
| Manual | Perfect ✅ | User-defined | Manual |

### Best Practices

1. **Trust OpenLibrary First**
   - Most accurate source
   - Use as primary data

2. **Use Groq as Fallback**
   - For authors not in OpenLibrary
   - Better than nothing
   - Can be corrected manually

3. **Manual Override**
   - Correct any inaccuracies
   - Add custom information
   - Improve data quality

## Enrichment Statistics

After enrichment, you'll see:
- ✅ Authors checked
- ✅ Authors updated from OpenLibrary
- ✅ Biographies added from Groq
- ✅ Photos added
- ✅ Errors encountered

Example:
```
Authors checked: 45
OpenLibrary updated: 30 (67%)
Biographies added: 10 (22%)
Photos added: 5 (11%)
Errors: 0
```

## Troubleshooting

### "No authors found on OpenLibrary"
- Author name might be spelled differently
- Author might not be in OpenLibrary
- Try manual edit to add data

### "Groq API key not configured"
- Go to Settings → AI Providers
- Enter Groq API key
- Click Save
- Try enrichment again

### "Biography looks incorrect"
- Click Edit on author card
- Correct the biography
- Click Save
- Your correction is preserved

### "Photo didn't load"
- Photos come from OpenLibrary
- If not available, manual edit can add URL
- Or leave blank

## Performance

### Enrichment Speed
- OpenLibrary: ~500ms per author
- Groq AI: ~1-2 seconds per author
- Manual edit: Instant

### Batch Enrichment
- 50 authors: ~2-5 minutes
- 100 authors: ~5-10 minutes
- Depends on OpenLibrary availability

## Related Documentation

- [Author Data Sources](AUTHOR_DATA_SOURCES.md) - Comparison of approaches
- [API Key Storage](API_KEY_STORAGE.md) - Managing API keys
- [Author Biography Setup](AUTHOR_BIOGRAPHY_SETUP.md) - Groq AI setup
- [Installation Requirements](INSTALLATION_REQUIREMENTS.md) - Dependencies

## Files Involved

| File | Purpose |
|------|---------|
| `backend/features/author_openlibrary_fetcher.py` | OpenLibrary API integration |
| `backend/features/author_biography_fetcher.py` | Groq AI biography fetching |
| `backend/features/author_photo_fetcher.py` | Photo fetching |
| `frontend/api_author_enrichment.py` | Enrichment endpoints |
| `frontend/templates/authors/authors.html` | Authors tab UI |

## Future Enhancements

- ⏳ Wikipedia integration
- ⏳ Google Books integration
- ⏳ Author verification system
- ⏳ Data quality scoring
- ⏳ Batch import from CSV
- ⏳ Author relationship mapping
