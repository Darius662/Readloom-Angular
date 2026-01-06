# Troubleshooting: Authors Tab Crash

## Step 1: Check Browser Console

1. **Open browser**: http://127.0.0.1:7227/
2. **Press F12** - Open Developer Tools
3. **Go to Console tab**
4. **Click Authors** in sidebar
5. **Look for error messages**

**Common errors:**
- `Uncaught SyntaxError` - JavaScript error
- `404 Not Found` - Missing resource
- `500 Internal Server Error` - Server error

---

## Step 2: Check Server Logs

1. **Look at terminal** where you ran `python run_dev.py`
2. **Search for error messages** when you click Authors
3. **Look for these patterns:**

```
ERROR - ...
Traceback - ...
Exception - ...
```

---

## Step 3: Check Network Tab

1. **Open DevTools** (F12)
2. **Go to Network tab**
3. **Click Authors**
4. **Look for failed requests**
   - Red status codes (4xx, 5xx)
   - Failed resource loads

---

## Step 4: Test Route Directly

In browser, go to:
```
http://127.0.0.1:7227/authors
```

**If it works:**
- Route is fine
- Problem is elsewhere

**If it fails:**
- Route has an issue
- Check server logs

---

## Step 5: Check Template

The template file is valid (syntax checked).

**But check if:**
- `authors/` directory exists
- `authors.html` file exists
- File has correct permissions

```bash
ls -la frontend/templates/authors/
```

---

## Common Fixes

### Fix 1: Clear Browser Cache
```
Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
Select "All time"
Click "Clear data"
```

### Fix 2: Restart Server
```bash
# Stop: Ctrl+C
# Start: python run_dev.py
```

### Fix 3: Check Database
```bash
sqlite3 data/db/readloom.db
SELECT COUNT(*) FROM authors;
```

If table doesn't exist, that might be the issue.

---

## Report the Issue

When reporting, include:

1. **Browser console error** (screenshot or text)
2. **Server log output** (when clicking Authors)
3. **Network tab failures** (if any)
4. **What you see** (blank page, error message, etc.)

---

**Let me know what you find and I'll help fix it!**
