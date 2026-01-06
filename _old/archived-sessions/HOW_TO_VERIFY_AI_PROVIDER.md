# How to Verify AI Provider is Working

## 🔍 Multiple Ways to Verify

### Method 1: Check the Logs (BEST)

**Watch the server logs in real-time:**

```bash
# In one terminal, start the server
python run_dev.py

# In another terminal, watch the logs
tail -f data/logs/readloom.log
```

**Look for these log messages:**

```
Groq extraction successful for [manga_title]
Extracted metadata: volumes=34, chapters=139, status=COMPLETED
```

Or if it fails:

```
Groq extraction failed for [manga_title]: [error message]
Trying next provider...
```

---

### Method 2: Check Browser Console

1. **Open browser**: http://127.0.0.1:7227/
2. **Press F12** - Open Developer Tools
3. **Go to Console tab**
4. **Search for manga**
5. **Look for network requests** to `/api/ai-providers/test` or metadata endpoints

---

### Method 3: Check the Database

The extracted metadata is cached in the database:

```bash
# Open SQLite database
sqlite3 data/db/readloom.db

# Query the cache
SELECT * FROM manga_volume_cache WHERE manga_title LIKE '%Attack on Titan%';
```

You'll see:
```
manga_title | volumes | chapters | status | source
Attack on Titan | 34 | 139 | COMPLETED | Groq
```

---

### Method 4: Visual Indicators in GUI

**Settings → Integrations → Configure (AI Providers)**

Look for:
- ✅ **Status Badge** - "Available" (green) = Provider is working
- ✅ **Test Button** - Click to verify
- ✅ **Success Message** - Shows metadata extracted

---

### Method 5: Terminal Test

```bash
# Set API key
export GROQ_API_KEY=gsk_your_key_here

# Run test
python test_ai_integration.py
```

Output shows:
```
✓ Metadata extraction successful!
  - Title: Attack on Titan
  - Volumes: 34
  - Chapters: 139
  - Status: COMPLETED
  - Confidence: 0.9
  - Source: Groq
```

---

## 📊 Real-Time Verification Steps

### Step 1: Start Server with Logging

```bash
python run_dev.py
```

Watch for startup messages:
```
Initializing AI providers...
Registered AI provider: Groq
AI providers initialized: 1 providers available
  ✓ Groq
```

### Step 2: Open Browser Console

```
F12 → Console tab
```

### Step 3: Search for Manga

Go to: http://127.0.0.1:7227/search

Search for: "Attack on Titan"

### Step 4: Watch for Indicators

**In Server Terminal:**
```
Groq extraction successful for Attack on Titan
Extracted metadata: volumes=34, chapters=139
```

**In Browser Console:**
```
Network request to /api/ai-providers/...
Response: {metadata: {...}}
```

**In GUI:**
- Metadata appears with volumes, chapters, status
- Shows "Source: Groq" or similar

---

## 🎯 What to Look For

### Success Indicators ✅

- ✅ Logs show "extraction successful"
- ✅ Metadata appears in search results
- ✅ Database has cached data
- ✅ Status badge shows "Available"
- ✅ Test button shows success message

### Failure Indicators ❌

- ❌ Logs show "extraction failed"
- ❌ No metadata appears
- ❌ Status badge shows "Not Available"
- ❌ Test button shows error
- ❌ Database has no cached data

---

## 📝 Example Log Output

### Successful Extraction

```
2025-11-09 00:02:49,123 - Readloom - INFO - Initializing AI providers...
2025-11-09 00:02:49,124 - Readloom - INFO - Registered AI provider: Groq
2025-11-09 00:02:49,125 - Readloom - INFO - AI providers initialized: 1 providers available
2025-11-09 00:02:49,126 - Readloom - INFO - ✓ Groq

[User searches for "Attack on Titan"]

2025-11-09 00:03:15,456 - Readloom - INFO - Groq extraction successful for Attack on Titan
2025-11-09 00:03:15,457 - Readloom - INFO - Extracted metadata: volumes=34, chapters=139, status=COMPLETED, confidence=0.9
```

### Failed Extraction

```
2025-11-09 00:03:15,456 - Readloom - ERROR - Groq extraction failed for Attack on Titan: Invalid API key
2025-11-09 00:03:15,457 - Readloom - INFO - Trying next provider...
```

---

## 🔧 Debugging Commands

### Check if Provider is Available

```bash
python -c "
from backend.features.ai_providers import get_ai_provider_manager
manager = get_ai_provider_manager()
groq = manager.get_provider('groq')
print(f'Groq available: {groq.is_available()}')
"
```

### Check API Key

```bash
echo $GROQ_API_KEY
```

Should show your key (masked): `gsk_TPqL3y...w6Xq1`

### Check Cached Metadata

```bash
sqlite3 data/db/readloom.db "SELECT manga_title, volumes, chapters FROM manga_volume_cache LIMIT 5;"
```

### Check Configuration File

```bash
cat data/ai_providers_config.json
```

Should show:
```json
{
  "groq_api_key": "gsk_..."
}
```

---

## 🎯 Complete Verification Workflow

1. **Start server** with logging visible
2. **Open browser** with DevTools console
3. **Search for manga** in GUI
4. **Watch server logs** for extraction messages
5. **Check browser console** for network requests
6. **Verify metadata** appears in search results
7. **Query database** to confirm caching
8. **Test endpoint** via GUI test button

---

## ✅ Success Checklist

- [ ] Server logs show "Groq" provider initialized
- [ ] Search results show volumes and chapters
- [ ] Logs show "extraction successful"
- [ ] Database has cached metadata
- [ ] Test button shows success message
- [ ] Status badge shows "Available"
- [ ] Metadata appears consistently

---

## 🎉 You'll Know It's Working When:

1. **You search for a manga**
2. **Metadata appears instantly** (or within a few seconds)
3. **Volumes and chapters are shown** (not just chapter count)
4. **Status is displayed** (COMPLETED, ONGOING, etc.)
5. **Server logs confirm** "extraction successful"
6. **Same data appears on second search** (cached)

---

**That's how you know the AI provider is providing!** 😄
