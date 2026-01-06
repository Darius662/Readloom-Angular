# Migrating to AI Providers

This guide helps you upgrade Readloom to use AI providers for better manga metadata extraction.

## What's New

Readloom now supports AI-powered metadata extraction with:
- **Groq** (fastest, recommended)
- **Google Gemini** (powerful, accurate)
- **DeepSeek** (good reasoning)
- **Ollama** (self-hosted, private)

All completely **free** with no credit card required.

## Why Upgrade

### Before (Web Scraping Only)
- ❌ Limited to web scraper availability
- ❌ Slow for large collections
- ❌ Inaccurate volume counts for lesser-known manga
- ❌ No release date predictions

### After (AI-Powered)
- ✅ Accurate metadata from AI
- ✅ Automatic fallback if one provider fails
- ✅ Works for any manga title
- ✅ Release date predictions
- ✅ Confidence scoring

## Upgrade Steps

### Step 1: No Code Changes Required

The AI provider system is **backward compatible**. Your existing code continues to work without changes.

### Step 2: Optional - Enable AI Providers

To use AI providers, set environment variables:

```bash
# Option A: Groq (recommended - 1 minute setup)
export GROQ_API_KEY=your_key_here

# Option B: Gemini (2 minutes setup)
export GEMINI_API_KEY=your_key_here

# Option C: DeepSeek (2 minutes setup)
export DEEPSEEK_API_KEY=your_key_here

# Option D: Ollama (5 minutes setup - self-hosted)
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama2
```

### Step 3: Restart Readloom

```bash
# Docker
docker-compose restart

# Or manually
python Readloom.py
```

### Step 4: Verify Setup

```bash
# Run test script
python test_ai_providers.py
```

## Migration Paths

### Path 1: Groq (Recommended)

**Time**: 5 minutes  
**Cost**: Free  
**Difficulty**: Easy

1. Visit https://groq.com/
2. Sign up (free, no credit card)
3. Get API key from console
4. Set environment variable:
   ```bash
   export GROQ_API_KEY=your_key
   ```
5. Done!

### Path 2: Groq + Gemini (Best Reliability)

**Time**: 10 minutes  
**Cost**: Free  
**Difficulty**: Easy

1. Follow Path 1 for Groq
2. Visit https://aistudio.google.com/apikey
3. Get API key (free, no credit card)
4. Install package:
   ```bash
   pip install google-generativeai
   ```
5. Set environment variable:
   ```bash
   export GEMINI_API_KEY=your_key
   ```
6. Done! Gemini is now backup provider

### Path 3: Ollama (Self-Hosted, Private)

**Time**: 15 minutes  
**Cost**: Free  
**Difficulty**: Medium

1. Install Ollama: https://ollama.ai/
2. Pull a model:
   ```bash
   ollama pull llama2
   ```
3. Start server:
   ```bash
   ollama serve
   ```
4. Readloom automatically detects it
5. Done!

### Path 4: All Providers (Maximum Reliability)

**Time**: 30 minutes  
**Cost**: Free  
**Difficulty**: Medium

1. Follow Path 1 (Groq)
2. Follow Path 2 (Gemini)
3. Follow Path 3 (Ollama)
4. All providers now available with automatic fallback

## Docker Migration

### Before

```yaml
version: '3.8'
services:
  readloom:
    build: .
    ports:
      - "7227:7227"
    volumes:
      - ./data:/config
```

### After (with Groq)

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

### After (with Ollama)

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

## Kubernetes Migration

### ConfigMap for API Keys

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: readloom-ai-config
data:
  GROQ_API_KEY: "your_key_here"
  GEMINI_API_KEY: "your_key_here"
  DEEPSEEK_API_KEY: "your_key_here"
```

### Pod Spec

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: readloom
spec:
  containers:
  - name: readloom
    image: readloom:latest
    envFrom:
    - configMapRef:
        name: readloom-ai-config
    ports:
    - containerPort: 7227
    volumeMounts:
    - name: data
      mountPath: /config
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: readloom-data
```

## Verification

### Check Configuration

```python
from backend.features.ai_providers.config import AIProviderConfig

AIProviderConfig.print_configuration()
```

### Run Tests

```bash
python test_ai_providers.py
```

### Check Logs

```bash
# Docker
docker logs readloom

# Or check log file
tail -f data/logs/readloom.log
```

## Rollback

If you need to disable AI providers:

1. **Remove environment variables**:
   ```bash
   unset GROQ_API_KEY
   unset GEMINI_API_KEY
   unset DEEPSEEK_API_KEY
   ```

2. **Restart Readloom**:
   ```bash
   docker-compose restart
   ```

3. **Verify**:
   ```bash
   python test_ai_providers.py
   ```

The system will fall back to web scraping automatically.

## Performance Impact

### Metadata Extraction Time

| Source | Time | Accuracy |
|--------|------|----------|
| Web Scraping | 2-5s | Medium |
| AI (Groq) | 1-2s | High |
| AI (Gemini) | 2-3s | Very High |
| AI (Ollama) | 5-10s | Good |

### First Run

- **Groq/Gemini/DeepSeek**: Fast (1-3 seconds)
- **Ollama**: Slow on first request (model loading), then fast

### Caching

All results are cached in `manga_volume_cache` table, so subsequent requests are instant.

## Troubleshooting

### "No providers available"

Check environment variables:
```bash
echo $GROQ_API_KEY
echo $GEMINI_API_KEY
echo $DEEPSEEK_API_KEY
```

### "Groq API error"

1. Verify API key is correct
2. Check rate limits at https://console.groq.com/
3. Try different provider

### "Ollama connection refused"

1. Check Ollama is running: `ollama serve`
2. Verify it's accessible: `curl http://localhost:11434/api/tags`
3. Check model is installed: `ollama list`

### "No JSON found in response"

- AI model didn't return valid JSON
- Try a different provider
- Check logs for raw response

## FAQ

**Q: Do I need to set up all providers?**  
A: No, just one is enough. The system works with any provider.

**Q: Which provider should I use?**  
A: Groq is recommended - it's fastest and most reliable.

**Q: Is there a cost?**  
A: No, all providers have free tiers with no credit card required.

**Q: Can I use multiple providers?**  
A: Yes! Set multiple API keys and they'll all be available with automatic fallback.

**Q: Does this break existing functionality?**  
A: No, it's completely backward compatible.

**Q: Can I use Ollama instead of cloud providers?**  
A: Yes! Ollama is self-hosted and completely private.

**Q: What if all providers fail?**  
A: The system falls back to web scraping (existing behavior).

**Q: How do I disable AI providers?**  
A: Remove environment variables and restart.

**Q: Can I use this in Docker?**  
A: Yes, just add environment variables to docker-compose.yml

**Q: Can I use this in Kubernetes?**  
A: Yes, use ConfigMaps for API keys.

## Support

- **Quick Start**: [AI_PROVIDERS_QUICKSTART.md](AI_PROVIDERS_QUICKSTART.md)
- **Full Docs**: [AI_PROVIDERS.md](AI_PROVIDERS.md)
- **Implementation Details**: [AI_PROVIDERS_IMPLEMENTATION.md](AI_PROVIDERS_IMPLEMENTATION.md)

## Next Steps

1. Choose a provider (Groq recommended)
2. Follow setup steps above
3. Run `python test_ai_providers.py`
4. Enjoy accurate manga metadata! 🎉

---

**Migration Guide Version**: 1.0  
**Last Updated**: November 8, 2025
