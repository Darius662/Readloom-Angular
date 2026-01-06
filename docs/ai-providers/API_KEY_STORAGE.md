# API Key Storage

## Overview
Readloom stores API keys in multiple locations for flexibility and security. API keys are never hardcoded and can be configured through the UI or environment variables.

## Storage Locations

### 1. Persistent File Storage (Primary)
**Location:** `data/ai_providers_config.json`

This is the main storage location for API keys. The file is created automatically when you configure providers.

**Example structure:**
```json
{
  "groq_api_key": "gsk_your_key_here",
  "gemini_api_key": "AIzaSy_your_key_here",
  "deepseek_api_key": "sk_your_key_here",
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "llama2"
}
```

**Security Notes:**
- File is stored locally in the `data/` directory
- Not included in version control (in .gitignore)
- Readable by the application process
- Should be protected with appropriate file permissions

### 2. Environment Variables (Runtime)
**Variables:**
- `GROQ_API_KEY` - Groq API key
- `GEMINI_API_KEY` - Google Gemini API key
- `DEEPSEEK_API_KEY` - DeepSeek API key
- `OLLAMA_BASE_URL` - Ollama server URL (optional)
- `OLLAMA_MODEL` - Ollama model name (optional)

**How it works:**
1. Application loads config from `data/ai_providers_config.json`
2. Config is applied to environment variables
3. Providers read from environment variables at runtime

### 3. Database Settings Table (Legacy)
**Table:** `settings`
**Key:** `groq_api_key`

This is used for backward compatibility and can store Groq API key in the database.

**Query:**
```sql
SELECT value FROM settings WHERE key = 'groq_api_key'
```

## How API Keys Flow

```
┌─────────────────────────────────────────┐
│  User enters API key in Settings UI     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  API endpoint saves to:                 │
│  1. data/ai_providers_config.json       │
│  2. Environment variables               │
│  3. Database settings (optional)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  On application restart:                │
│  1. Load from ai_providers_config.json  │
│  2. Apply to environment variables      │
│  3. Initialize AI providers             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Providers use env vars to connect      │
│  to AI services                         │
└─────────────────────────────────────────┘
```

## Configuration Methods

### Method 1: Web UI (Recommended)
1. Go to **Settings** → **AI Providers**
2. Enter your API key
3. Click **Save**
4. Click **Test** to verify
5. Configuration is automatically saved to `data/ai_providers_config.json`

### Method 2: Environment Variables
Set before starting the application:

**Windows:**
```bash
set GROQ_API_KEY=gsk_your_key_here
set GEMINI_API_KEY=AIzaSy_your_key_here
set DEEPSEEK_API_KEY=sk_your_key_here
python run_dev.py
```

**macOS/Linux:**
```bash
export GROQ_API_KEY=gsk_your_key_here
export GEMINI_API_KEY=AIzaSy_your_key_here
export DEEPSEEK_API_KEY=sk_your_key_here
python run_dev.py
```

### Method 3: Docker Environment
In `docker-compose.yml`:
```yaml
environment:
  - GROQ_API_KEY=gsk_your_key_here
  - GEMINI_API_KEY=AIzaSy_your_key_here
  - DEEPSEEK_API_KEY=sk_your_key_here
```

## File Locations

### Configuration File
```
Readloom/
├── data/
│   └── ai_providers_config.json    ← API keys stored here
├── data/
│   └── db/
│       └── readloom.db             ← Database (legacy storage)
└── ...
```

### Database Schema
```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Security Considerations

### Best Practices

1. **Never commit API keys to version control**
   - `data/ai_providers_config.json` is in `.gitignore`
   - Environment variables are not committed

2. **Protect file permissions**
   ```bash
   # On Linux/macOS, restrict access
   chmod 600 data/ai_providers_config.json
   ```

3. **Use environment variables in production**
   - More secure than file storage
   - Can be managed by deployment system
   - Easier to rotate keys

4. **Mask sensitive data**
   - API keys are masked in logs (first 10 + last 4 chars)
   - UI shows masked keys for verification
   - Full keys never logged

5. **Rotate keys regularly**
   - Delete old keys from provider dashboard
   - Update in Readloom settings
   - Test to verify new key works

### What NOT to Do

❌ Don't hardcode API keys in source code
❌ Don't commit `data/ai_providers_config.json` to git
❌ Don't share API keys in logs or error messages
❌ Don't use weak or shared API keys
❌ Don't expose the `data/` directory publicly

## Accessing API Keys Programmatically

### From Environment Variables
```python
import os

groq_key = os.environ.get('GROQ_API_KEY')
gemini_key = os.environ.get('GEMINI_API_KEY')
```

### From Configuration File
```python
from backend.features.ai_providers.persistence import AIProviderConfigPersistence

groq_key = AIProviderConfigPersistence.get_api_key('groq')
gemini_key = AIProviderConfigPersistence.get_api_key('gemini')
```

### From Database
```python
from backend.internals.db import execute_query
import json

result = execute_query("SELECT value FROM settings WHERE key = 'groq_api_key'")
if result:
    groq_key = json.loads(result[0]['value'])
```

## Troubleshooting

### "API key not found"
**Check:**
1. Is `data/ai_providers_config.json` present?
2. Is the environment variable set?
3. Is the database settings table populated?

**Solution:**
```bash
# Re-enter API key via Settings UI
# Or set environment variable and restart
export GROQ_API_KEY=your_key_here
python run_dev.py
```

### "API key not working"
**Check:**
1. Is the key valid?
2. Has the key expired?
3. Does the key have the right permissions?

**Solution:**
1. Verify key on provider's dashboard
2. Generate a new key if needed
3. Update in Readloom settings
4. Click Test to verify

### "Configuration not persisting"
**Check:**
1. Is `data/` directory writable?
2. Is `data/ai_providers_config.json` being created?

**Solution:**
```bash
# Check file exists
ls -la data/ai_providers_config.json

# Check permissions
chmod 600 data/ai_providers_config.json

# Restart application
```

## Migration Guide

### From Environment Variables to File Storage
1. Set environment variables
2. Start application
3. Go to Settings → AI Providers
4. Enter API keys via UI
5. Click Save
6. Configuration is now in `data/ai_providers_config.json`
7. Environment variables can be removed

### From Database to File Storage
1. API keys in database are automatically migrated
2. When you update via UI, they're saved to file
3. File storage takes priority over database

## Related Documentation

- [Installation Requirements](INSTALLATION_REQUIREMENTS.md) - How to get API keys
- [AI Provider Configuration](AI_PROVIDER_NO_RESTART.md) - Configuring providers
- [Author Biography Setup](AUTHOR_BIOGRAPHY_SETUP.md) - Using Groq for biographies
- [Security Best Practices](SECURITY.md) - General security guidelines

## Files Involved

| File | Purpose |
|------|---------|
| `data/ai_providers_config.json` | Persistent API key storage |
| `backend/features/ai_providers/persistence.py` | Handles file I/O |
| `backend/features/ai_providers/config.py` | Configuration management |
| `frontend/api.py` | API endpoints for saving keys |
| `backend/internals/settings.py` | Database settings management |

## API Endpoints

### Get API Key Status
```
GET /api/settings/groq-api-key
Response: { "configured": true, "masked_key": "gsk_...here" }
```

### Save API Key
```
PUT /api/settings/groq-api-key
Body: { "api_key": "gsk_your_key_here" }
Response: { "success": true, "masked_key": "gsk_...here" }
```

### Delete API Key
```
DELETE /api/settings/groq-api-key
Response: { "success": true, "message": "Groq API key deleted successfully" }
```

### Save Provider Config
```
POST /api/ai-providers/config
Body: { "provider": "groq", "api_key": "gsk_your_key_here" }
Response: { "message": "Configuration saved for groq" }
```

### Test Provider
```
POST /api/test-ai-providers
Body: { "provider": "groq" }
Response: { "message": "✓ Groq provider is working!", "metadata": {...} }
```
