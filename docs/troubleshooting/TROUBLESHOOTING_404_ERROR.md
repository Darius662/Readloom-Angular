# Troubleshooting 404 Error

## The Problem

The test endpoint returns "API endpoint not found" (404 error).

## Root Cause

Flask's development server's auto-reload isn't properly reloading the `api.py` file with the new endpoints.

## Solution

### Step 1: Verify Server is Running Latest Code

Add this to your browser console or make a request to:
```
http://127.0.0.1:7227/api/ai-providers/health
```

If you get:
```json
{"status": "ok", "version": "1.0"}
```

Then the server HAS reloaded and the endpoints should work.

If you get 404, the server hasn't reloaded yet.

### Step 2: Force Complete Server Restart

1. **Stop the server** - Press `Ctrl+C` in terminal
2. **Wait 5 seconds** - Make sure it's completely stopped
3. **Clear Python cache**:
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
   ```
4. **Start fresh**:
   ```bash
   python run_dev.py
   ```
5. **Wait for startup** - Watch for "Application initialized successfully"

### Step 3: Hard Refresh Browser

- **Windows/Linux**: `Ctrl+Shift+Delete` (clear cache) or `Ctrl+F5`
- **Mac**: `Cmd+Shift+Delete` or `Cmd+Shift+R`

### Step 4: Test Health Endpoint

In browser, go to:
```
http://127.0.0.1:7227/api/ai-providers/health
```

Should show: `{"status": "ok", "version": "1.0"}`

### Step 5: Try Test Again

Now go back to Settings → Integrations → Configure and click Test.

## If Still Not Working

### Check Server Logs

Look for these messages when server starts:
```
Initializing AI providers...
Registered AI provider: Groq
AI providers initialized: 1 providers available
```

If you see "0 providers available", the API key wasn't set.

### Verify API Key is Set

In the GUI:
1. Go to Settings → Integrations → Configure
2. Enter your Groq API key
3. Click **Save** (not Test yet)
4. Check if status changes to "Available"

### Check Browser Console

Press `F12` to open developer tools, go to Console tab, and look for errors.

## Alternative: Use curl to Test

In terminal:
```bash
curl -X POST http://127.0.0.1:7227/api/ai-providers/test \
  -H "Content-Type: application/json" \
  -d '{"provider": "groq"}'
```

This will show the exact error from the server.

## Common Issues

| Issue | Solution |
|-------|----------|
| 404 error | Server hasn't reloaded - restart completely |
| "Not available" status | API key not saved - click Save button |
| "Provider not found" | API key is invalid - check it's correct |
| No response | Server crashed - check logs |

## Nuclear Option

If nothing works:

1. Stop server (`Ctrl+C`)
2. Delete all `__pycache__` directories:
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
   ```
3. Delete `.pyc` files:
   ```bash
   find . -name "*.pyc" -delete 2>/dev/null || true
   ```
4. Start fresh:
   ```bash
   python run_dev.py
   ```

---

**The endpoints ARE there - Flask just needs to reload them properly!**
