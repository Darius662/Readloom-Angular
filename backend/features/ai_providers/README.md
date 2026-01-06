# AI Providers Package

This package provides AI-powered metadata extraction for manga, with support for multiple free AI services.

## Features

- **Multiple AI Providers**: Groq, Gemini, DeepSeek, Ollama
- **Intelligent Fallback**: Automatically tries next provider if one fails
- **Parallel Extraction**: Get results from all providers and select the best
- **Flexible Configuration**: Environment variables or code configuration
- **Self-Hosted Option**: Ollama for privacy and offline capability
- **Seamless Integration**: Works with existing Readloom metadata system

## Quick Start

### 1. Set API Key (Groq recommended)

```bash
export GROQ_API_KEY=your_key_here
```

### 2. Use in Code

```python
from backend.features.ai_providers import get_ai_provider_manager

manager = get_ai_provider_manager()
metadata = manager.extract_metadata_with_fallback(
    manga_title="Attack on Titan",
    known_chapters=139
)

print(f"Volumes: {metadata.volumes}")
print(f"Chapters: {metadata.chapters}")
```

### 3. Test It

```bash
python test_ai_providers.py
```

## Providers

### Groq (Recommended)
- **Speed**: ⚡⚡⚡ Fastest
- **Cost**: Free
- **Setup**: 1 minute
- **API Key**: https://groq.com/

### Google Gemini
- **Speed**: ⚡⚡ Fast
- **Cost**: Free
- **Setup**: 2 minutes
- **API Key**: https://aistudio.google.com/apikey

### DeepSeek
- **Speed**: ⚡⚡ Fast
- **Cost**: Free
- **Setup**: 2 minutes
- **API Key**: https://platform.deepseek.com/

### Ollama (Self-Hosted)
- **Speed**: ⚡ Slower (but local)
- **Cost**: Free
- **Setup**: 5 minutes
- **Installation**: https://ollama.ai/

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

### In Code

```python
from backend.features.ai_providers import GroqProvider, GeminiProvider

# Create provider with API key
groq = GroqProvider(api_key="your_key")

# Or load from environment
groq = GroqProvider()  # Loads from GROQ_API_KEY
```

## Usage Examples

### Basic Extraction

```python
from backend.features.ai_providers import extract_metadata_with_ai

metadata = extract_metadata_with_ai(
    manga_title="One Piece",
    known_chapters=1000
)

if metadata:
    print(f"Volumes: {metadata.volumes}")
    print(f"Status: {metadata.status}")
```

### Fallback Chain

```python
manager = get_ai_provider_manager()

# Tries Groq → Gemini → DeepSeek → Ollama
metadata = manager.extract_metadata_with_fallback(
    manga_title="Demon Slayer"
)
```

### Parallel Extraction

```python
# Get results from all providers, select best
metadata = manager.extract_metadata_parallel(
    manga_title="Jujutsu Kaisen"
)

print(f"Best source: {metadata.source}")
print(f"Confidence: {metadata.confidence:.1%}")
```

### Check Provider Status

```python
from backend.features.ai_providers.config import AIProviderConfig

# Print configuration
AIProviderConfig.print_configuration()

# Get specific config
groq_config = AIProviderConfig.get_groq_config()
print(f"Groq enabled: {groq_config['enabled']}")
```

## Integration with MangaInfoProvider

The AI providers integrate with the existing metadata system:

```python
from backend.features.ai_providers.integration import add_ai_to_mangainfo_provider

# Add AI as fallback to MangaInfoProvider
add_ai_to_mangainfo_provider()

# Now MangaInfoProvider will use AI if web scraping fails
from backend.features.scrapers.mangainfo.provider import MangaInfoProvider
provider = MangaInfoProvider()
chapters, volumes, source = provider.get_chapter_count("Attack on Titan")
```

## File Structure

```
ai_providers/
├── __init__.py              # Package exports
├── README.md                # This file
├── base.py                  # Base classes (AIProvider, AIProviderManager)
├── config.py                # Configuration management
├── manager.py               # Provider manager and initialization
├── integration.py           # Integration with existing system
├── groq_provider.py         # Groq implementation
├── gemini_provider.py       # Gemini implementation
├── deepseek_provider.py     # DeepSeek implementation
└── ollama_provider.py       # Ollama implementation
```

## API Reference

### MangaMetadata

```python
@dataclass
class MangaMetadata:
    title: str                          # Manga title
    volumes: int                        # Number of volumes
    chapters: int                       # Total chapters
    status: str                         # ONGOING, COMPLETED, HIATUS, CANCELLED
    release_dates: Dict[int, str]      # Volume -> Release date
    next_release_date: Optional[str]   # Next release (YYYY-MM-DD)
    confidence: float                   # 0.0-1.0 confidence score
    source: str                         # Provider name
    raw_response: Optional[str]        # Raw AI response
```

### AIProvider

```python
class AIProvider(ABC):
    def extract_manga_metadata(
        self,
        manga_title: str,
        known_chapters: Optional[int] = None
    ) -> Optional[MangaMetadata]:
        """Extract metadata using AI."""
        pass
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass
```

### AIProviderManager

```python
class AIProviderManager:
    def extract_metadata_with_fallback(
        self,
        manga_title: str,
        known_chapters: Optional[int] = None
    ) -> Optional[MangaMetadata]:
        """Extract with automatic fallback."""
        pass
    
    def extract_metadata_parallel(
        self,
        manga_title: str,
        known_chapters: Optional[int] = None
    ) -> Optional[MangaMetadata]:
        """Extract from all providers, return best."""
        pass
```

## Troubleshooting

### Provider Not Available

```python
from backend.features.ai_providers.config import AIProviderConfig

# Check configuration
AIProviderConfig.print_configuration()

# Check specific provider
config = AIProviderConfig.get_groq_config()
print(f"Groq enabled: {config['enabled']}")
print(f"API key set: {config['api_key'] is not None}")
```

### No JSON in Response

The AI model didn't return valid JSON. Try:
1. Different provider
2. Different model
3. Check logs for raw response

### Ollama Connection Error

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve

# Check model is installed
ollama list

# Pull model if needed
ollama pull llama2
```

## Performance

| Provider | Speed | Accuracy | Cost | Setup |
|----------|-------|----------|------|-------|
| Groq | ⚡⚡⚡ | High | Free | 1 min |
| Gemini | ⚡⚡ | Very High | Free | 2 min |
| DeepSeek | ⚡⚡ | High | Free | 2 min |
| Ollama | ⚡ | Good | Free | 5 min |

## Best Practices

1. **Use Groq as primary** - Fastest and most reliable
2. **Set up Gemini as backup** - For when Groq is down
3. **Optional: Use Ollama locally** - For privacy
4. **Monitor confidence scores** - Lower = less reliable
5. **Cache results** - Use `manga_volume_cache` table

## Contributing

To add a new provider:

1. Create `your_provider.py` extending `AIProvider`
2. Implement `extract_manga_metadata()` and `is_available()`
3. Register in `manager.py`
4. Add config to `config.py`
5. Update documentation

## License

Part of Readloom, licensed under MIT License.

## Support

- **Quick Start**: [AI_PROVIDERS_QUICKSTART.md](../../docs/AI_PROVIDERS_QUICKSTART.md)
- **Full Docs**: [AI_PROVIDERS.md](../../docs/AI_PROVIDERS.md)
- **Test Script**: [test_ai_providers.py](../../../test_ai_providers.py)
