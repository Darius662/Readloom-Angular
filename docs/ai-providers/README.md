# AI Providers

Readloom uses AI providers to enhance metadata, particularly for author biographies and enrichment.

## Available AI Providers

- **[Groq](GROQ.md)** - Fast AI with Llama 3.3 70B (recommended)
- **[Google Generative AI](GOOGLE_GENERATIVE_AI.md)** - Google's AI models
- **[OpenAI](OPENAI.md)** - GPT models

## Getting Started

1. **[Setup Guide](SETUP.md)** - Configure your AI provider
2. **[API Key Storage](API_KEY_STORAGE.md)** - Secure key management
3. **[Configuration](AI_PROVIDER_NO_RESTART.md)** - Test without restarting

## Features

- **Author Biography Generation** - Automatic biography fetching
- **Metadata Enrichment** - Enhance author information
- **No Restart Required** - Configure and test on the fly

## Recommended Setup

1. **Groq** (free tier available)
   - Fast and reliable
   - No credit card required for free tier
   - Llama 3.3 70B model

2. **Google Generative AI** (free tier available)
   - Generous free tier
   - Good for testing

3. **OpenAI** (paid)
   - Most powerful models
   - Requires API key and credits

## Configuration

- **Environment Variables** - Set `GROQ_API_KEY`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`
- **Web Interface** - Configure in Settings → AI Providers
- **File-based** - Stored in `data/ai_providers_config.json`

For metadata provider integration, see [Metadata Providers](../metadata-providers/).
