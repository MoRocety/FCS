# Quick Start Guide - FCS Active Term System

## 🚀 5-Minute Setup

### Step 1: Configure .env File
```bash
# Generate a secure token
openssl rand -hex 32

# Edit .env file and set:
# WEBHOOK_SECRET=(paste the generated token)
# ACTIVE_TERM=2025FA
```

Save this token - you'll need it in two places (`.env` and PythonAnywhere)!

### Step 3: Test Scraper
```bash
cd scraper
python scrape.py
```

Expected output:
```
✓ Extracted tokens successfully
✓ Found selected term: 2025FA
✓ Saved active term to: /path/to/ACTIVE_TERM
✓ Successfully scraped 2025FA
```

### Step 4: Deploy to PythonAnywhere

1. Upload all files to PythonAnywhere
2. Go to **Web** tab → **Environment variables**
3. Add: `WEBHOOK_SECRET` = (your token from Step 1)
4. Click **Reload** button

### Step 5: Set up GitHub Actions

1. Create file: `.github/workflows/update-courses.yml`
2. Copy workflow from `WEBHOOK_INTEGRATION.md`
3. Go to GitHub → **Settings** → **Secrets** → **Actions**
4. Add two secrets:
   - `WEBHOOK_URL`: `https://yourusername.pythonanywhere.com/webhook/update-courses`
   - `WEBHOOK_SECRET`: (same token from Step 1)

### Step 6: Test It!

**Manual trigger:**
- Go to GitHub → **Actions** tab
- Click "Update Course Data"
- Click "Run workflow"

**Verify:**
```bash
curl https://yourusername.pythonanywhere.com/api/active-term
```

---

## 📝 That's It!

Your app will now:
- ✅ Scrape course data daily at 2 AM UTC
- ✅ Auto-detect the active term
- ✅ Push updates to your server
- ✅ Show current courses automatically

## 🆘 Troubleshooting

**"401 Unauthorized"**
→ Check WEBHOOK_SECRET matches in both places

**"No data showing"**
→ Check if ACTIVE_TERM file exists
→ Verify {TERM}data.txt file was created

**"Scraper fails"**
→ FCC website might be down
→ Check GitHub Actions logs

## 📚 More Info

- Full details: `SETUP_INSTRUCTIONS.md`
- Technical docs: `WEBHOOK_INTEGRATION.md`
- All changes: `CHANGES_SUMMARY.md`
- Test locally: `python test_integration.py`

