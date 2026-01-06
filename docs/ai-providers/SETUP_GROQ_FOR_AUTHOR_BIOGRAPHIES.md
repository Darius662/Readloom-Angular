# Setup Groq for Author Biographies

## ⚠️ Current Status

Author biographies are **not showing** because the Groq API key is not configured.

---

## 🔑 Step 1: Get Your Groq API Key

1. **Go to Groq Console**: https://console.groq.com
2. **Sign up** (free account)
3. **Create API key** in the API keys section
4. **Copy the key** (looks like: `gsk_...`)

---

## 🔧 Step 2: Set the API Key

### Option A: Terminal (Recommended)

```bash
export GROQ_API_KEY=gsk_your_key_here
```

Then restart the server:
```bash
Ctrl+C
python run_dev.py
```

### Option B: Permanent (Linux/Mac)

Add to `~/.bashrc` or `~/.zshrc`:
```bash
export GROQ_API_KEY=gsk_your_key_here
```

Then reload:
```bash
source ~/.bashrc
# or
source ~/.zshrc
```

### Option C: Windows

```cmd
set GROQ_API_KEY=gsk_your_key_here
python run_dev.py
```

---

## ✅ Step 3: Verify Setup

After setting the key and restarting the server, run:

```bash
python tests/fetch_author_biographies.py
```

You should see:
```
Found X authors without biographies
Fetching author biographies from Groq AI...

✓ Author biography fetch completed!
  Authors checked: X
  Biographies added: X
  Errors: 0
```

---

## 🚀 Step 4: See the Results

1. **Refresh Authors page**: http://127.0.0.1:7227/authors
2. **Click on an author** to see their biography
3. **Add new books** - authors will get biographies automatically

---

## 📝 What Happens After Setup

### Automatic (on book add)
1. Book is added with author name
2. Author is created
3. **Photo fetched** from OpenLibrary ✅
4. **Biography generated** by Groq AI ✅
5. Author appears in Authors page with full details

### Manual (if needed)
```bash
# Fetch biographies for existing authors
python tests/fetch_author_biographies.py
```

---

## 🎯 Expected Result

**Before Setup:**
```
Author Details
- Navessa Allen
- Born: Unknown
- Biography: No biography available
```

**After Setup:**
```
Author Details
- Navessa Allen
- Born: Unknown
- Biography: Navessa Allen is an American author known for her 
  psychological thrillers and dark fiction. Her debut novel "Lights 
  Out" explores themes of trauma and survival...
```

---

## ❓ Troubleshooting

### "GROQ_API_KEY not set" error
- Make sure you set the environment variable
- Restart the server after setting it
- Check: `echo $GROQ_API_KEY` (should show your key)

### "Invalid API key" error
- Double-check your key from console.groq.com
- Make sure there are no extra spaces
- Try generating a new key

### "No biographies added" 
- Check if Groq API is working: `python tests/fetch_author_biographies.py`
- Check server logs for errors
- Verify internet connection

### Biographies not showing in UI
- Refresh the page (Ctrl+F5)
- Check database: `python tests/fetch_author_biographies.py`
- Restart server

---

## 💡 Tips

- **Free tier** - Groq offers free API access with generous limits
- **Fast** - Groq is one of the fastest LLM APIs available
- **Quality** - Generates accurate, relevant author biographies
- **Automatic** - Once set up, everything works automatically

---

## 📞 Need Help?

1. Check Groq status: https://status.groq.com
2. Verify API key: https://console.groq.com
3. Check logs: `tail -f data/logs/readloom.log | grep -i groq`

---

## ✨ Summary

1. **Get API key** from https://console.groq.com
2. **Set environment variable**: `export GROQ_API_KEY=your_key`
3. **Restart server**: `Ctrl+C` then `python run_dev.py`
4. **Fetch biographies**: `python tests/fetch_author_biographies.py`
5. **Refresh page** - See author biographies! ✅

---

**Once set up, author biographies will be generated automatically for all new books!** 🎉
