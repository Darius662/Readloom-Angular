# Quick Guide: Identify Data Source

## 🎯 Fastest Way to Check

### In Calendar View

```
Hover over calendar entry
                ↓
Tooltip shows:
  Source: Groq ← This tells you!
  Confidence: 0.9
```

**Source Values:**
- **Groq** = AI Provider ✅
- **Gemini** = AI Provider ✅
- **DeepSeek** = AI Provider ✅
- **Ollama** = AI Provider ✅
- **MangaDex** = Web Scraper
- **MangaFire** = Web Scraper
- **AniList** = Metadata Provider
- **Estimated** = Fallback

---

### In Series Details Page

```
Series: Attack on Titan
  Volumes: 34
  Chapters: 139
  Source: Groq ← Shows provider!
  Confidence: 0.9
```

---

### In Database

```bash
sqlite3 data/db/readloom.db
SELECT manga_title, source FROM manga_volume_cache LIMIT 5;
```

Output:
```
Attack on Titan | Groq
Demon Slayer    | MangaDex
One Piece       | AniList
```

---

## ✅ That's It!

**Just look for the "Source" field** - it tells you exactly which provider supplied the data!

- **Groq, Gemini, DeepSeek, Ollama** = AI Provider
- **MangaDex, MangaFire, etc.** = Web Scraper
- **AniList, Google Books, etc.** = Metadata Provider
- **Estimated** = Fallback calculation

🎉 Done!
