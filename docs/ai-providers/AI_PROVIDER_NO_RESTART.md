# AI Provider Configuration - No Restart Required

## Overview
You can now configure AI provider API keys and test them **without restarting the server**!

## How It Works

When you test an AI provider via the Settings page:

1. **Save API Key** - The key is saved to the database settings
2. **Click Test** - The test endpoint reinitializes the AI providers
3. **Providers Reload** - New configuration is picked up automatically
4. **Test Runs** - The provider is tested with sample data
5. **Result Shown** - Success or error message displayed

## Testing AI Providers

### Via Web UI
1. Go to **Settings** → **AI Providers**
2. Enter your API key (e.g., Groq API key)
3. Click **Test** button
4. Result appears in modal dialog

### Via API
```bash
curl -X POST http://localhost:7227/api/test-ai-providers \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq"}'
```

## Supported Providers

- **Groq** - Fastest, free, recommended
- **Gemini** - Powerful, free tier
- **DeepSeek** - Good reasoning, free tier
- **Ollama** - Self-hosted, no external API

## Configuration Methods

### Method 1: Database Settings (Recommended)
The system automatically saves API keys to the database settings table.

### Method 2: Environment Variables
Set environment variables before starting the server:
```bash
export GROQ_API_KEY="gsk_your_key_here"
export GEMINI_API_KEY="your_key_here"
export DEEPSEEK_API_KEY="your_key_here"
```

## How Reinitialization Works

The test endpoint:
1. Calls `initialize_ai_providers()` to reload all providers
2. Loads saved configuration from database
3. Loads environment variables
4. Reinitializes each provider with new credentials
5. Tests the specified provider
6. Returns result without requiring server restart

## Key Features

✅ **No Server Restart** - Test and configure without downtime
✅ **Automatic Reload** - New API keys picked up immediately
✅ **Fallback Chain** - Multiple providers with automatic fallback
✅ **Detailed Logging** - Server logs show all configuration steps
✅ **Error Messages** - Clear feedback on what's wrong

## Troubleshooting

### "API endpoint not found"
**Cause:** The test endpoint wasn't found (404 error)
**Solution:** Make sure the server is running and the endpoint is registered

### "Provider not found"
**Cause:** The provider name is incorrect or not supported
**Solution:** Use one of: groq, gemini, deepseek, ollama

### "Provider is not available"
**Cause:** API key is not configured or invalid
**Solution:** 
1. Check the API key is correct
2. Ensure it's saved to database or environment
3. Check server logs for details

### "Test failed: [error message]"
**Cause:** The provider failed to extract metadata
**Solution:**
1. Check API key validity
2. Check API quota/rate limits
3. Check server logs for detailed error
4. Try with a different provider

## Server Logs

When testing, check the server logs for:

**Successful Test:**
```
INFO - Reinitializing AI providers to pick up new configuration...
INFO - Testing groq provider with 'Attack on Titan'...
INFO - ✓ groq provider test successful!
```

**Failed Test:**
```
WARNING - GROQ_API_KEY not set in database settings or environment - cannot fetch biography for [Author Name]
ERROR - Error testing AI provider: [error details]
```

## API Endpoint

**POST** `/api/test-ai-providers`

**Request:**
```json
{
  "provider": "groq"
}
```

**Response (Success):**
```json
{
  "message": "✓ Groq provider is working!",
  "metadata": {
    "title": "Attack on Titan",
    "volumes": 34,
    "chapters": 139,
    "status": "COMPLETED",
    "confidence": 0.95
  }
}
```

**Response (Error):**
```json
{
  "error": "Provider groq is not available. Please configure API key or check server status."
}
```

## Files Modified

- `frontend/api.py` - Updated test endpoint to reinitialize providers

## Related Documentation

- [Author Biography Setup](AUTHOR_BIOGRAPHY_SETUP.md) - How biographies are fetched
- [AI Provider Configuration](../backend/features/ai_providers/README.md) - Provider details

## Future Enhancements

1. Add UI to reload all providers without test
2. Add provider status indicator in UI
3. Add API quota monitoring
4. Add provider performance metrics
5. Add ability to enable/disable providers per user
