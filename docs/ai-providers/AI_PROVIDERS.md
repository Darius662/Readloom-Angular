# AI Providers for Manga Metadata Extraction

Readloom now includes support for multiple AI providers to extract accurate manga metadata including volumes, chapters, and release dates. This document explains how to set up and use these providers.

## Overview

The AI provider system uses an intelligent fallback chain to ensure metadata extraction always works:

1. **Groq** (Primary) - Fastest, free, generous limits
2. **Gemini** (Secondary) - Powerful, free tier
3. **DeepSeek** (Tertiary) - Good reasoning, free tier
4. **Ollama** (Fallback) - Self-hosted, no external dependencies

## Supported Providers

### 1. Groq (Recommended)

**Why Groq?**
- ✅ Fastest inference speed
- ✅ Completely free
- ✅ No rate limits (for practical purposes)
- ✅ No credit card required
- ✅ Generous free tier

**Setup:**

1. Get a free API key: https://groq.com/
2. Set environment variable:
   ```bash
   export GROQ_API_KEY=your_api_key_here
   ```

3. Or in Docker:
   ```yaml
   environment:
     - GROQ_API_KEY=your_api_key_here
   ```

**Configuration:**
- Model: `mixtral-8x7b-32768` (can be changed)
- Temperature: 0.3 (for consistent results)
- Max tokens: 500

---

### 2. Google Gemini

**Why Gemini?**
- ✅ Powerful reasoning capabilities
- ✅ 1M token context window
- ✅ Free tier available
- ✅ No credit card required
- ✅ Good for complex queries

**Setup:**

1. Get a free API key: https://aistudio.google.com/apikey
2. Set environment variable:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```

3. Or in Docker:
   ```yaml
   environment:
     - GEMINI_API_KEY=your_api_key_here
   ```

**Installation:**
```bash
pip install google-generativeai
```

**Configuration:**
- Model: `gemini-2.5-pro`
- Temperature: 0.3
- Max tokens: 500

---

### 3. DeepSeek

**Why DeepSeek?**
- ✅ Excellent reasoning models
- ✅ Free tier available
- ✅ No credit card required
- ✅ Good for structured data extraction

**Setup:**

1. Get a free API key: https://platform.deepseek.com/
2. Set environment variable:
   ```bash
   export DEEPSEEK_API_KEY=your_api_key_here
   ```

3. Or in Docker:
   ```yaml
   environment:
     - DEEPSEEK_API_KEY=your_api_key_here
   ```

**Installation:**
```bash
pip install openai
```

**Configuration:**
- Model: `deepseek-chat`
- Temperature: 0.3
- Max tokens: 500

---

### 4. Ollama (Self-Hosted)

**Why Ollama?**
- ✅ Completely free
- ✅ No external API dependencies
- ✅ Privacy-focused (runs locally)
- ✅ No rate limits
- ✅ Works offline

**Setup:**

1. Install Ollama: https://ollama.ai/
2. Pull a model:
   ```bash
   ollama pull llama2
   # or
   ollama pull mistral
   ```

3. Start Ollama server:
   ```bash
   ollama serve
   ```

4. Set environment variables (optional):
   ```bash
   export OLLAMA_BASE_URL=http://localhost:11434
   export OLLAMA_MODEL=llama2
   ```

5. Or in Docker (requires Docker network):
   ```yaml
   environment:
     - OLLAMA_BASE_URL=http://ollama:11434
     - OLLAMA_MODEL=llama2
   ```

**Available Models:**
- `llama2` - Fast, good for general tasks
- `mistral` - Faster, smaller
- `neural-chat` - Optimized for chat
- `dolphin-mixtral` - Powerful reasoning

**Configuration:**
- Base URL: `http://localhost:11434`
- Model: `llama2` (default)
- Timeout: 60 seconds (Ollama can be slow on first run)

---

## Configuration

### Environment Variables

```bash
# Groq
export GROQ_API_KEY=gsk_...

# Gemini
export GEMINI_API_KEY=AIzaSy...

# DeepSeek
export DEEPSEEK_API_KEY=sk-...

# Ollama (optional)
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama2
```

### Docker Compose

```yaml
version: '3.8'
services:
  readloom:
    build: .
    container_name: readloom
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - OLLAMA_BASE_URL=http://ollama:11434
    ports:
      - "7227:7227"
    volumes:
      - ./data:/config
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_MODELS=/root/.ollama/models

volumes:
  ollama_data:
```

### .env File

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIzaSy...
DEEPSEEK_API_KEY=sk-...
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

Then load it:
```bash
source .env
python Readloom.py
```

---

## Usage

### In Python Code

```python
from backend.features.ai_providers import get_ai_provider_manager

# Get the manager
manager = get_ai_provider_manager()

# Extract metadata with automatic fallback
metadata = manager.extract_metadata_with_fallback(
    manga_title="Attack on Titan",
    known_chapters=139
)

if metadata:
    print(f"Volumes: {metadata.volumes}")
    print(f"Chapters: {metadata.chapters}")
    print(f"Status: {metadata.status}")
    print(f"Source: {metadata.source}")
    print(f"Confidence: {metadata.confidence}")
```

### Fallback Chain

The system automatically tries providers in order:

1. **Groq** - If available and enabled
2. **Gemini** - If Groq fails
3. **DeepSeek** - If Gemini fails
4. **Ollama** - If all others fail

### Parallel Extraction

For better results, extract from all providers and use the best:

```python
metadata = manager.extract_metadata_parallel(
    manga_title="Attack on Titan",
    known_chapters=139
)
```

This returns the result with the highest confidence score.

---

## Integration with Metadata System

The AI providers integrate seamlessly with Readloom's existing metadata system:

```python
from backend.features.scrapers.mangainfo.provider import MangaInfoProvider

# The MangaInfoProvider now has access to AI providers
provider = MangaInfoProvider()

# When scraping fails, it can fall back to AI
chapters, volumes, source = provider.get_chapter_count("Attack on Titan")
```

---

## Troubleshooting

### Provider Not Available

If a provider shows as unavailable:

1. **Check API Key:**
   ```bash
   echo $GROQ_API_KEY
   ```

2. **Check Installation:**
   ```bash
   pip install groq google-generativeai openai
   ```

3. **Check Configuration:**
   ```python
   from backend.features.ai_providers.config import AIProviderConfig
   AIProviderConfig.print_configuration()
   ```

### Ollama Connection Issues

If Ollama provider fails:

1. **Check Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Check model is installed:**
   ```bash
   ollama list
   ```

3. **Pull a model if needed:**
   ```bash
   ollama pull llama2
   ```

### Slow Responses

- **Groq/Gemini/DeepSeek:** Check internet connection and API rate limits
- **Ollama:** First request is slow (model loading). Subsequent requests are faster.

### JSON Parsing Errors

If you see "No JSON found in response":

1. The AI model may not be returning valid JSON
2. Try a different model
3. Check the raw response in logs

---

## Performance Comparison

| Provider | Speed | Accuracy | Cost | Setup |
|----------|-------|----------|------|-------|
| Groq | ⚡⚡⚡ Fastest | High | Free | Easy |
| Gemini | ⚡⚡ Fast | Very High | Free | Easy |
| DeepSeek | ⚡⚡ Fast | High | Free | Easy |
| Ollama | ⚡ Slow | Good | Free | Medium |

---

## Best Practices

1. **Use Groq as primary** - It's the fastest and most reliable
2. **Set up Gemini as backup** - For when Groq is down
3. **Optional: Use Ollama locally** - For privacy and offline capability
4. **Monitor confidence scores** - Lower confidence means less reliable
5. **Cache results** - Use the existing `manga_volume_cache` table

---

## API Reference

### MangaMetadata

```python
@dataclass
class MangaMetadata:
    title: str                          # Manga title
    volumes: int                        # Number of volumes
    chapters: int                       # Total chapters
    status: str                         # ONGOING, COMPLETED, HIATUS, CANCELLED
    release_dates: Dict[int, str]      # Volume -> Release date mapping
    next_release_date: Optional[str]   # Next release date (YYYY-MM-DD)
    confidence: float                   # 0.0-1.0 confidence score
    source: str                         # Provider name (Groq, Gemini, etc.)
    raw_response: Optional[str]        # Raw AI response
```

### AIProviderManager Methods

```python
# Extract with fallback (tries each provider in order)
metadata = manager.extract_metadata_with_fallback(
    manga_title: str,
    known_chapters: Optional[int] = None
) -> Optional[MangaMetadata]

# Extract from all providers and return best result
metadata = manager.extract_metadata_parallel(
    manga_title: str,
    known_chapters: Optional[int] = None
) -> Optional[MangaMetadata]

# Get specific provider
provider = manager.get_provider(name: str) -> Optional[AIProvider]

# Get all providers
providers = manager.get_all_providers() -> List[AIProvider]
```

---

## Contributing

To add a new AI provider:

1. Create a new file: `backend/features/ai_providers/your_provider.py`
2. Extend `AIProvider` base class
3. Implement `extract_manga_metadata()` and `is_available()`
4. Register in `manager.py`
5. Add configuration to `config.py`
6. Update this documentation

---

## License

AI Providers are part of Readloom and are licensed under the MIT License.

---

**Last Updated:** November 8, 2025
