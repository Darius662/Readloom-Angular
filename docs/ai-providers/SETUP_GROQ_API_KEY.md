# Setup Groq API Key - Quick Guide

## Step 1: Get Free Groq API Key

1. Visit: https://groq.com/
2. Sign up (free, no credit card required)
3. Go to console/dashboard
4. Create API key
5. Copy the key (starts with `gsk_`)

## Step 2: Set Environment Variable

### On Linux/Mac (in terminal):
```bash
export GROQ_API_KEY=gsk_your_key_here
```

### On Windows (Command Prompt):
```cmd
set GROQ_API_KEY=gsk_your_key_here
```

### On Windows (PowerShell):
```powershell
$env:GROQ_API_KEY="gsk_your_key_here"
```

## Step 3: Start Server with API Key Set

Make sure you set the environment variable BEFORE starting the server:

```bash
# Linux/Mac
export GROQ_API_KEY=gsk_your_key_here
python run_dev.py

# Windows (Command Prompt)
set GROQ_API_KEY=gsk_your_key_here
python run_dev.py

# Windows (PowerShell)
$env:GROQ_API_KEY="gsk_your_key_here"
python run_dev.py
```

## Step 4: Verify Setup

Check the logs when server starts. You should see:

```
2025-11-08 23:XX:XX,XXX - Readloom - INFO - Initializing AI providers...
2025-11-08 23:XX:XX,XXX - Readloom - INFO - Registered AI provider: Groq
2025-11-08 23:XX:XX,XXX - Readloom - INFO - AI providers initialized: 1 providers available
  ✓ Groq
```

NOT this:
```
2025-11-08 23:XX:XX,XXX - Readloom - WARNING - AI provider Groq is not available (missing config)
```

## Step 5: Test in Browser

1. Refresh browser: http://127.0.0.1:7227/
2. Settings → Integrations → Configure (AI Providers)
3. You should see Groq status as "Available" (green)
4. Click Test
5. Should work now!

## Troubleshooting

### Still showing "not available"?
- Check you set the environment variable BEFORE starting the server
- Restart the server after setting the variable
- Check the variable is set: `echo $GROQ_API_KEY` (Linux/Mac) or `echo %GROQ_API_KEY%` (Windows)

### Still getting 404?
- The Flask app needs to fully reload
- Stop server (`Ctrl+C`)
- Start server again
- Refresh browser

### API key is invalid?
- Double-check you copied the key correctly
- Make sure it starts with `gsk_`
- Try generating a new key from Groq console

---

**Important**: The API key must be set as an environment variable BEFORE the server starts.
