# Installation Requirements

## Overview
This document outlines all the dependencies required to run Readloom with full functionality.

## Quick Install

To install all dependencies at once:

```bash
pip install -r requirements.txt
```

## Core Dependencies

These are required for basic Readloom functionality:

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.0 | Web framework |
| waitress | 3.0.0 | WSGI application server |
| requests | 2.31.0 | HTTP library |
| beautifulsoup4 | 4.12.2 | HTML parsing |
| flask-socketio | 5.3.6 | WebSocket support |
| websocket-client | 1.3.3 | WebSocket client |
| python-dateutil | 2.8.2 | Date/time utilities |
| cryptography | 44.0.1 | Encryption support |
| flask_cors | 6.0.1 | CORS support |
| simple-websocket | 1.0.0 | WebSocket implementation |
| bidict | 0.23.1 | Bidirectional dictionary |

## AI Provider Dependencies

These packages enable AI-powered features:

### Groq (Recommended - Free, Fast)
```bash
pip install groq==0.4.2
```
- Used for author biographies
- Used for manga metadata extraction
- Free tier with generous rate limits
- Get API key: https://console.groq.com/

### Google Gemini
```bash
pip install google-generativeai==0.3.0
```
- Alternative AI provider
- Free tier available
- Get API key: https://aistudio.google.com/apikey

### OpenAI/DeepSeek
```bash
pip install openai==1.3.0
```
- For DeepSeek API access
- Requires API key

### Ollama (Self-Hosted)
No additional dependencies needed - uses `requests` which is already installed.
Just run Ollama locally: https://ollama.ai/

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Readloom.git
cd Readloom
```

### 2. Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure AI Providers (Optional)
To use AI features, set your API keys:

**Option A: Environment Variables**
```bash
# On Windows
set GROQ_API_KEY=your_key_here
set GEMINI_API_KEY=your_key_here
set DEEPSEEK_API_KEY=your_key_here

# On macOS/Linux
export GROQ_API_KEY=your_key_here
export GEMINI_API_KEY=your_key_here
export DEEPSEEK_API_KEY=your_key_here
```

**Option B: Via Settings UI**
1. Start Readloom
2. Go to Settings → AI Providers
3. Enter your API keys
4. Click Test to verify

### 5. Run Readloom
```bash
python run_dev.py
```

Then open your browser to: http://127.0.0.1:7227/

## Platform-Specific Notes

### Windows
- Python 3.8+ required
- Optional: `pip install pywin32` for Windows-specific features

### macOS
- Python 3.8+ required
- May need to use `python3` instead of `python`

### Linux
- Python 3.8+ required
- May need to use `python3` instead of `python`

### Docker
- All dependencies are included in the Docker image
- No additional installation needed

## Troubleshooting

### "groq package not installed"
```bash
pip install groq
```

### "google-generativeai not found"
```bash
pip install google-generativeai
```

### "openai not found"
```bash
pip install openai
```

### Module import errors
Try reinstalling all dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## Updating Dependencies

To update all packages to their latest versions:
```bash
pip install --upgrade -r requirements.txt
```

To update a specific package:
```bash
pip install --upgrade groq
```

## Checking Installed Packages

To see all installed packages and versions:
```bash
pip list
```

To check if a specific package is installed:
```bash
pip show groq
```

## AI Provider Setup Guide

### Groq (Recommended)
1. Visit https://console.groq.com/
2. Sign up (free)
3. Create API key
4. Set `GROQ_API_KEY` environment variable or via Settings UI
5. Test in Settings → AI Providers

### Google Gemini
1. Visit https://aistudio.google.com/apikey
2. Create API key
3. Set `GEMINI_API_KEY` environment variable or via Settings UI
4. Test in Settings → AI Providers

### DeepSeek
1. Visit https://platform.deepseek.com/
2. Create API key
3. Set `DEEPSEEK_API_KEY` environment variable or via Settings UI
4. Test in Settings → AI Providers

### Ollama (Self-Hosted)
1. Download from https://ollama.ai/
2. Install and run locally
3. No API key needed
4. Test in Settings → AI Providers

## Development Dependencies

For development and testing, you may also want:

```bash
# Testing
pip install pytest==7.4.0
pip install pytest-cov==4.1.0

# Code quality
pip install black==23.9.0
pip install flake8==6.0.0
pip install pylint==2.17.5

# Documentation
pip install sphinx==7.2.0
pip install sphinx-rtd-theme==1.3.0
```

## Docker Installation

If using Docker, all dependencies are pre-installed:

```bash
docker build -t readloom .
docker run -p 7227:7227 readloom
```

See [Docker Guide](DOCKER.md) for more details.

## Support

If you encounter any issues:
1. Check the [Troubleshooting](TROUBLESHOOTING.md) guide
2. Review server logs in `data/logs/`
3. Check [Known Issues](KNOWN_ISSUES.md)
4. Open an issue on GitHub

## Related Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Docker Guide](DOCKER.md) - Running with Docker
- [AI Provider Configuration](AI_PROVIDER_NO_RESTART.md) - Setting up AI providers
- [Author Biography Setup](AUTHOR_BIOGRAPHY_SETUP.md) - Biography fetching setup
