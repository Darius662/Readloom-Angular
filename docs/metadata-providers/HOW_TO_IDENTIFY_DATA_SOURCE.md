# How to Identify Which Provider Supplied the Data

## 🔍 Multiple Ways to Check the Source

### Method 1: Check the Database (MOST RELIABLE)

```bash
# Open database
sqlite3 data/db/readloom.db

# Query the cache table
SELECT manga_title, volumes, chapters, source FROM manga_volume_cache 
WHERE manga_title LIKE '%Attack%';
```

**Output:**
```
manga_title         | volumes | chapters | source
Attack on Titan     | 34      | 139      | Groq
Demon Slayer        | 16      | 205      | MangaDex
My Hero Academia    | 42      | 426      | MangaFire
```

**What This Tells You:**
- **source = "Groq"** → AI provider supplied the data
- **source = "MangaDex"** → Web scraper supplied the data
- **source = "MangaFire"** → Web scraper supplied the data
- **source = "AniList"** → Metadata provider supplied the data

---

### Method 2: Check the Server Logs

**Watch the logs while searching:**

```bash
tail -f data/logs/readloom.log
```

**Look for these messages:**

```
# AI Provider (Groq)
Groq extraction successful for Attack on Titan
Extracted metadata: volumes=34, chapters=139, status=COMPLETED

# Web Scraper (MangaDex)
MangaDex scraper found: volumes=34, chapters=139

# Metadata Provider (AniList)
AniList provider returned: volumes=34, chapters=139

# Fallback (Estimation)
Estimated volumes from chapter count: 34
```

**What This Tells You:**
- Message contains "Groq extraction" → AI provider
- Message contains "scraper" → Web scraper
- Message contains "provider" → Metadata provider
- Message contains "Estimated" → Fallback estimation

---

### Method 3: Check the Calendar Page

**Path**: Calendar (http://127.0.0.1:7227/calendar)

**Look for:**
```
Calendar Entry:
┌─────────────────────────────────────────┐
│ Attack on Titan - Volume 35             │
│ Release Date: 2025-12-15                │
│ Source: Groq                            │ ← Shows provider!
│ Confidence: 0.9                         │
└─────────────────────────────────────────┘
```

**What This Tells You:**
- **Source: Groq** → AI provider
- **Source: MangaDex** → Web scraper
- **Source: AniList** → Metadata provider
- **Confidence: 0.9** → How reliable the data is (AI shows confidence)

---

### Method 4: Hover Over Calendar Entry

**In Calendar View:**

```
Hover over an entry:
                ↓
Tooltip appears:
┌─────────────────────────────────────────┐
│ Attack on Titan Vol 35                  │
│ Release: 2025-12-15                     │
│ Source: Groq (Confidence: 0.9)          │
│ Volumes: 34 | Chapters: 139             │
└─────────────────────────────────────────┘
```

**What This Tells You:**
- **Source: Groq** → AI provider supplied this
- **Confidence: 0.9** → 90% confidence (higher = more reliable)

---

### Method 5: Check Series Details Page

**Path**: Click on a series → Details page

**Look for:**

```
Series: Attack on Titan
┌─────────────────────────────────────────┐
│ Volumes: 34                             │
│ Chapters: 139                           │
│ Status: COMPLETED                       │
│ Last Updated: 2025-11-09 00:05:09       │
│ Source: Groq                            │ ← Shows provider!
│ Confidence: 0.9                         │
└─────────────────────────────────────────┘
```

**What This Tells You:**
- **Source: Groq** → AI provider
- **Confidence: 0.9** → Reliability score
- **Last Updated** → When data was fetched

---

## 📊 Data Source Hierarchy

```
Priority Order (what gets used first):

1. AI Providers (if configured)
   ├─ Groq (fastest)
   ├─ Gemini (powerful)
   ├─ DeepSeek (reasoning)
   └─ Ollama (self-hosted)
        ↓ (if all fail)

2. Web Scrapers
   ├─ MangaFire
   ├─ MangaDex
   ├─ MangaPark
   └─ Other scrapers
        ↓ (if all fail)

3. Metadata Providers
   ├─ AniList
   ├─ Google Books
   ├─ OpenLibrary
   └─ Other providers
        ↓ (if all fail)

4. Estimation
   └─ Calculated from chapter count
```

---

## 🎯 Quick Identification Guide

| Source | Indicator | Confidence | Speed |
|--------|-----------|-----------|-------|
| **Groq** | "Groq" in source | 0.8-0.95 | Fast |
| **Gemini** | "Gemini" in source | 0.85-0.95 | Fast |
| **DeepSeek** | "DeepSeek" in source | 0.8-0.9 | Fast |
| **Ollama** | "Ollama" in source | 0.7-0.85 | Slow |
| **MangaDex** | "MangaDex" in source | 0.7-0.9 | Medium |
| **MangaFire** | "MangaFire" in source | 0.6-0.8 | Medium |
| **AniList** | "AniList" in source | 0.75-0.9 | Fast |
| **Estimated** | "Estimated" in source | 0.5-0.7 | Instant |

---

## 📋 Complete Verification Workflow

### For Calendar Entries:

1. **Open Calendar** → http://127.0.0.1:7227/calendar
2. **Find an entry** (e.g., "Attack on Titan Vol 35")
3. **Hover over it** → Tooltip shows source
4. **Check the source**:
   - ✅ "Groq" = AI provider
   - ✅ "MangaDex" = Web scraper
   - ✅ "AniList" = Metadata provider

### For Series Details:

1. **Go to Series** → Search for manga
2. **Click on series** → Details page
3. **Look for "Source" field** → Shows provider name
4. **Check confidence** → Higher = more reliable

### For Database Verification:

1. **Open terminal**
2. **Query database**:
   ```bash
   sqlite3 data/db/readloom.db
   SELECT manga_title, source, volumes FROM manga_volume_cache LIMIT 10;
   ```
3. **Check the "source" column** → Shows which provider supplied data

---

## 🔍 Example Scenarios

### Scenario 1: AI Provider Supplied Data

```
Calendar Entry: "Attack on Titan Vol 35"
Hover tooltip shows:
  Source: Groq
  Confidence: 0.9
  Volumes: 34

What happened:
1. User searched for "Attack on Titan"
2. Web scrapers tried but failed or incomplete
3. Groq AI extracted: volumes=34, chapters=139
4. Data cached with source="Groq"
5. Calendar entry created from AI data
```

### Scenario 2: Web Scraper Supplied Data

```
Calendar Entry: "Demon Slayer Vol 16"
Hover tooltip shows:
  Source: MangaDex
  Confidence: 0.8
  Volumes: 16

What happened:
1. User searched for "Demon Slayer"
2. MangaDex scraper found the data
3. Data cached with source="MangaDex"
4. Calendar entry created from scraper data
5. AI provider not used (scraper succeeded)
```

### Scenario 3: Metadata Provider Supplied Data

```
Calendar Entry: "One Piece Vol 105"
Hover tooltip shows:
  Source: AniList
  Confidence: 0.85
  Volumes: 105

What happened:
1. User searched for "One Piece"
2. Web scrapers failed
3. AI providers failed or not configured
4. AniList metadata provider returned data
5. Calendar entry created from AniList data
```

---

## ✅ Summary

**To know which provider supplied the data:**

1. **Check the "Source" field** in:
   - Calendar entry tooltip
   - Series details page
   - Database query

2. **Look for these values:**
   - "Groq" = AI provider ✅
   - "MangaDex" = Web scraper
   - "AniList" = Metadata provider
   - "Estimated" = Fallback

3. **Check confidence score:**
   - 0.8-0.95 = High confidence (AI or good scraper)
   - 0.7-0.8 = Medium confidence (web scraper)
   - 0.5-0.7 = Low confidence (estimation)

---

**That's how you know which provider supplied the data!** 🎯
