# AI Providers - Quick Start Guide

Get up and running with AI-powered manga metadata extraction in 5 minutes.

## 30-Second Setup

### Option 1: Groq (Recommended - Fastest)

1. Get free API key: https://groq.com/
2. Set environment variable:
   ```bash
   export GROQ_API_KEY=your_key_here
   ```
3. Done! Groq is now your primary metadata source.

### Option 2: Google Gemini (Powerful Alternative)

1. Get free API key: https://aistudio.google.com/apikey
2. Install package:
   ```bash
   pip install google-generativeai
   ```
3. Set environment variable:
   ```bash
   export GEMINI_API_KEY=your_key_here
   ```

### Option 3: Ollama (Self-Hosted, No API Key)

1. Install Ollama: https://ollama.ai/
2. Pull a model:
   ```bash
   ollama pull llama2
   ```
3. Start server:
   ```bash
   ollama serve
   ```
4. Done! Ollama is now available at `http://localhost:11434`

## Docker Setup

### With Groq

```yaml
version: '3.8'
services:
  readloom:
    build: .
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    ports:
      - "7227:7227"
    volumes:
      - ./data:/config
```

Run with:
```bash
GROQ_API_KEY=your_key docker-compose up
```

### With Ollama

```yaml
version: '3.8'
services:
  readloom:
    build: .
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    ports:
      - "7227:7227"
    volumes:
      - ./data:/config
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

Run with:
```bash
docker-compose up
```

## Using AI Providers

### In Your Code

```python
from backend.features.ai_providers import get_ai_provider_manager

# Get the manager
manager = get_ai_provider_manager()

# Extract metadata (automatic fallback)
metadata = manager.extract_metadata_with_fallback(
    manga_title="Attack on Titan",
    known_chapters=139
)

if metadata:
    print(f"Volumes: {metadata.volumes}")
    print(f"Chapters: {metadata.chapters}")
    print(f"Status: {metadata.status}")
    print(f"Source: {metadata.source}")
```

### Check Configuration

```python
from backend.features.ai_providers.config import AIProviderConfig

# Print current setup
AIProviderConfig.print_configuration()
```

## Fallback Chain

The system automatically tries providers in this order:

1. ✅ **Groq** (if API key set)
2. ✅ **Gemini** (if API key set)
3. ✅ **DeepSeek** (if API key set)
4. ✅ **Ollama** (if server running)

If one fails, the next one is automatically tried.

## Troubleshooting

### "No providers available"

Make sure at least one provider is configured:

```bash
# Check Groq
echo $GROQ_API_KEY

# Check Gemini
echo $GEMINI_API_KEY

# Check Ollama
curl http://localhost:11434/api/tags
```

### "Groq API error"

- Check your API key is correct
- Visit https://groq.com/ to verify your account
- Check rate limits at https://console.groq.com/

### "Ollama connection refused"

- Make sure Ollama is running: `ollama serve`
- Check it's accessible: `curl http://localhost:11434/api/tags`
- Verify model is installed: `ollama list`

### "No JSON found in response"

- The AI model didn't return valid JSON
- Try a different provider
- Check logs for the raw response

## Performance Tips

1. **Use Groq for speed** - Fastest inference
2. **Use Gemini for accuracy** - Most powerful models
3. **Use Ollama for privacy** - Runs locally, no external calls
4. **Set up multiple providers** - Automatic fallback if one fails
5. **Cache results** - Readloom automatically caches in `manga_volume_cache`

## Next Steps

- Read full documentation: [AI_PROVIDERS.md](AI_PROVIDERS.md)
- Check provider-specific setup: [AI_PROVIDERS.md#supported-providers](AI_PROVIDERS.md#supported-providers)
- Integrate with your workflow: [AI_PROVIDERS.md#integration-with-metadata-system](AI_PROVIDERS.md#integration-with-metadata-system)

## Support

For issues:

1. Check logs: `docker logs readloom`
2. Print configuration: `AIProviderConfig.print_configuration()`
3. Test provider directly: `curl http://localhost:11434/api/tags`
4. See full docs: [AI_PROVIDERS.md](AI_PROVIDERS.md)

---

**That's it!** Your manga metadata is now AI-powered. 🚀
