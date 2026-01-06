# Author Enrichment Debugging Guide

## Overview
This guide helps you troubleshoot why author details (biography, birth date, photos) are not appearing in the Authors tab.

## Checklist: Why Authors Don't Have Details

### 1. Check if Groq API Key is Configured

**Step 1: Verify API Key is Set**
```bash
# Check environment variable
echo $GROQ_API_KEY

# Or check database
sqlite3 data/db/readloom.db "SELECT value FROM settings WHERE key = 'groq_api_key';"
```

**Step 2: Verify in Settings UI**
- Go to Settings → AI Providers
- Check if Groq API Key field shows masked key (e.g., `gsk_...here`)
- If empty, enter your Groq API key and click Save

**Step 3: Test the API Key**
- Go to Settings → AI Providers
- Click "Test" button next to Groq
- Should see "✓ Groq provider is working!"

### 2. Check Server Logs for Enrichment Errors

**Look for these log messages:**

**Success:**
```
INFO - Starting enrichment for author: Stephen King (ID: 1)
INFO - Attempting to fetch biography for Stephen King from Groq...
✓ Successfully added biography for author Stephen King
```

**Failure - API Key Not Configured:**
```
WARNING - ✗ Could not fetch biography for Stephen King - Groq API key may not be configured
```

**Failure - API Error:**
```
ERROR - ✗ Error fetching biography for Stephen King: [error details]
```

### 3. Check Database for Author Data

**Check if biography is in database:**
```bash
sqlite3 data/db/readloom.db "SELECT id, name, biography, birth_date FROM authors LIMIT 5;"
```

**Expected output:**
```
1|Stephen King|American author of horror and suspense...|1947-09-21
2|J.K. Rowling|British author best known for Harry Potter...|1965-07-31
```

**If biography is NULL:**
```
1|Stephen King||
2|J.K. Rowling||
```

### 4. Check if Authors Tab is Displaying Data

**Open Browser Developer Tools (F12)**

**Check Network Tab:**
- Go to Authors tab
- Look for `/api/authors/` request
- Check Response tab
- Should see biography and birth_date fields

**Example Response:**
```json
{
  "authors": [
    {
      "id": 1,
      "name": "Stephen King",
      "biography": "American author of horror...",
      "birth_date": "1947-09-21",
      "book_count": 5
    }
  ]
}
```

**Check Console Tab:**
- Look for any JavaScript errors
- Should see author data being displayed

## Common Issues and Solutions

### Issue 1: "Groq API key not configured"

**Symptoms:**
- Authors have no biography
- Server logs show: "Could not fetch biography - Groq API key may not be configured"

**Solutions:**

1. **Get a Groq API Key:**
   - Visit https://console.groq.com/
   - Sign up (free)
   - Create API key
   - Copy the key

2. **Set the API Key:**
   - Option A: Environment Variable
     ```bash
     export GROQ_API_KEY=gsk_your_key_here
     python run_dev.py
     ```
   - Option B: Settings UI
     - Go to Settings → AI Providers
     - Enter key in Groq field
     - Click Save

3. **Restart Server:**
   - Stop: Ctrl+C
   - Start: `python run_dev.py`

4. **Test:**
   - Go to Settings → AI Providers
   - Click "Test" button
   - Should see success message

### Issue 2: Authors Created Before API Key Configuration

**Symptoms:**
- Old authors have no biography
- New authors added after API key configuration have biography

**Solution:**

1. **Enrich Existing Authors:**
   - Go to Authors tab
   - Click "Enrich Authors" button
   - System will fetch data for all authors without biography

2. **Or Manually:**
   - Click "Edit" on author card
   - Add biography manually
   - Click "Save"

### Issue 3: Biography Shows "No biography available"

**Symptoms:**
- Authors tab shows "No biography available" text
- Database has NULL for biography

**Causes:**
- Groq API key not configured
- Groq API rate limit exceeded
- Author name not found in Groq

**Solutions:**

1. **Check Groq Configuration:**
   ```bash
   # Check if API key is set
   echo $GROQ_API_KEY
   
   # Check if it's in database
   sqlite3 data/db/readloom.db "SELECT value FROM settings WHERE key = 'groq_api_key';"
   ```

2. **Check Server Logs:**
   - Look for Groq error messages
   - Check if API key is valid

3. **Test Groq:**
   - Go to Settings → AI Providers
   - Click "Test" button
   - If it fails, API key is invalid

4. **Manual Fix:**
   - Click "Edit" on author
   - Add biography manually
   - Click "Save"

### Issue 4: Birth Date Shows "Unknown"

**Symptoms:**
- Birth date column shows "Unknown"
- Database has NULL for birth_date

**Causes:**
- OpenLibrary doesn't have birth date
- Groq doesn't provide birth date
- Author data not enriched

**Solutions:**

1. **Enrich from OpenLibrary:**
   - Click "Enrich Authors" button
   - OpenLibrary might have birth date

2. **Manual Entry:**
   - Click "Edit" on author
   - Enter birth date (YYYY-MM-DD format)
   - Click "Save"

### Issue 5: Book Count Shows 0

**Symptoms:**
- "Books" count shows 0 for all authors
- But author has books in library

**Causes:**
- Author not linked to series in author_books table
- Series doesn't have author information

**Check:**
```bash
# Check if author_books links exist
sqlite3 data/db/readloom.db "SELECT * FROM author_books LIMIT 5;"

# Check if series have author names
sqlite3 data/db/readloom.db "SELECT id, title, author FROM series LIMIT 5;"
```

**Solution:**
- Re-import series to create author_books links
- Or manually add links to author_books table

## Debugging Steps

### Step 1: Check Groq Configuration
```bash
# Check environment
echo "GROQ_API_KEY=$GROQ_API_KEY"

# Check database
sqlite3 data/db/readloom.db "SELECT key, value FROM settings WHERE key LIKE '%groq%';"
```

### Step 2: Check Server Logs
```bash
# Look for enrichment logs
tail -f data/logs/readloom.log | grep -i "enrichment\|biography\|groq"
```

### Step 3: Check Database
```bash
# Check authors table
sqlite3 data/db/readloom.db ".headers on" ".mode column" "SELECT id, name, biography, birth_date FROM authors LIMIT 10;"

# Check author_books links
sqlite3 data/db/readloom.db "SELECT COUNT(*) as links FROM author_books;"
```

### Step 4: Check API Response
```bash
# Test API directly
curl "http://localhost:7227/api/authors/?page=1&per_page=5"
```

### Step 5: Check Browser Console
- Open Developer Tools (F12)
- Go to Console tab
- Look for JavaScript errors
- Check Network tab for API responses

## Manual Enrichment

### Enrich All Authors at Once
```bash
# Via API
curl -X POST "http://localhost:7227/api/authors/enrich-all"
```

### Enrich Single Author
```bash
# Via API
curl -X POST "http://localhost:7227/api/authors/1/enrich"
```

### Manually Edit Author
```bash
# Via API
curl -X PUT "http://localhost:7227/api/authors/1/edit" \
  -H "Content-Type: application/json" \
  -d '{
    "biography": "Stephen King is an American author...",
    "birth_date": "1947-09-21"
  }'
```

## Expected Behavior

### When Author is Created
1. Author record is created in database
2. Enrichment process starts automatically
3. Groq API is called to fetch biography
4. OpenLibrary API is called to fetch photo
5. Data is stored in database
6. Author appears in Authors tab with details

### When You Click "Enrich Authors"
1. System finds all authors without biography
2. For each author:
   - Tries OpenLibrary first
   - Falls back to Groq AI
   - Tries to fetch photos
3. Updates database with fetched data
4. Returns statistics

### When You Manually Edit
1. You enter data in edit form
2. Click "Save"
3. Data is immediately stored in database
4. Author card updates with new data

## Performance Notes

- **First enrichment:** 2-5 minutes for 50 authors
- **Subsequent enrichments:** Faster (only missing data)
- **Manual edits:** Instant
- **API calls:** ~500ms per author (OpenLibrary), ~1-2s per author (Groq)

## Related Documentation

- [Author Enrichment Hybrid](AUTHOR_ENRICHMENT_HYBRID.md) - How enrichment works
- [API Key Storage](API_KEY_STORAGE.md) - Where API keys are stored
- [Installation Requirements](INSTALLATION_REQUIREMENTS.md) - Getting Groq API key

## Getting Help

If authors still don't have details after following this guide:

1. **Check server logs** for specific error messages
2. **Verify Groq API key** is valid and has quota
3. **Try manual enrichment** via "Enrich Authors" button
4. **Manually edit** individual authors if needed
5. **Check database** directly to see if data is being stored

## Quick Test

Run this to verify everything is working:

```bash
# 1. Check Groq API key
echo "Groq API Key: $GROQ_API_KEY"

# 2. Check database
sqlite3 data/db/readloom.db "SELECT COUNT(*) FROM authors WHERE biography IS NOT NULL;"

# 3. Check API
curl "http://localhost:7227/api/authors/?page=1" | grep -i biography

# 4. Check logs
tail -20 data/logs/readloom.log | grep -i "enrichment\|biography"
```

If all checks pass, authors should have details in the Authors tab!
