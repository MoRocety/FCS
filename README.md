# FCS - Forman Course Scheduler

Automated course scheduling system for Forman Christian College with GitHub Actions integration.

## 🎯 What It Does

- **Scrapes** FCC course catalog daily
- **Detects** the active term automatically (2026 Spring, 2025 Fall, etc.)
- **Updates** your website with fresh course data
- **Generates** conflict-free course schedules
- **Filters** by department, course, instructor
- **Visualizes** weekly class schedules

## 🏗️ Architecture

```
GitHub Actions (Daily 2 AM UTC)
    ↓ Scrapes FCC website
    ↓ Detects latest FA/SP term
    ↓ Parses course data
    ↓ POSTs to webhook
PythonAnywhere Server
    ↓ Receives & saves data
    ↓ Updates ACTIVE_TERM
    ↓ Reloads course listings
Users Browse Website
    ✓ See current semester
    ✓ Generate schedules
    ✓ No conflicts!
```

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/yourusername/FCS.git
cd FCS
pip install -r requirements2.txt
```

### 2. Configure Environment
```bash
# Copy and edit .env file
# Set WEBHOOK_SECRET to a secure random token
openssl rand -hex 32  # Generate a token
# Edit .env and paste the token
```

### 3. Deploy to PythonAnywhere
- Upload all files (`.env` is gitignored, so upload separately)
- Go to Web tab → Environment variables section
- Set `WEBHOOK_SECRET` = (your token from .env)
- Click Reload

### 4. Configure GitHub Actions
- Go to repo Settings → Secrets and variables → Actions
- Add `WEBHOOK_URL`: `https://yourusername.pythonanywhere.com/webhook/update-courses`
- Add `WEBHOOK_SECRET`: (same token from .env)

### 5. Test
```bash
# From GitHub Actions tab
Click "Update Course Data" → "Run workflow"

# Or test locally first
cd scraper && python scrape.py
cat ../ACTIVE_TERM  # Should show term like 2026SP
```

**Done!** 🎉 The system now updates automatically every day at 2 AM UTC.

## 📁 Project Structure

```
FCS/
├── app.py                    # Flask application entry point
├── views.py                  # Routes & webhook endpoint
├── config.py                 # Configuration & term management
├── dataread.py               # Data loading from files
├── combcheck.py              # Schedule conflict checking
├── ACTIVE_TERM               # Current term code (auto-generated)
├── {TERM}data.txt            # Course data files
│
├── scraper/
│   ├── scrape.py             # Scrapes FCC website
│   └── parse.py              # Parses JSON to CSV
│
├── templates/
│   └── trying.html           # Main UI
│
├── .github/workflows/
│   └── update-courses.yml    # GitHub Actions workflow
│
└── docs/
    ├── GITHUB_ACTIONS_SETUP.md
    ├── DEPLOYMENT_CHECKLIST.md
    └── README.md (this file)
```

## 🔧 Configuration

### Environment Variables (.env file)

Create/edit `.env` in the project root:

```bash
# Active term (auto-updated by scraper)
ACTIVE_TERM=2025FA

# Webhook secret (REQUIRED for security)
# Generate with: openssl rand -hex 32
WEBHOOK_SECRET=your_random_32_char_token
```

**Note:** `.env` is gitignored for security. On PythonAnywhere, set these in the Web tab → Environment variables section.

### GitHub Secrets

In your repository Settings → Secrets → Actions:

```
WEBHOOK_URL=https://yourusername.pythonanywhere.com/webhook/update-courses
WEBHOOK_SECRET=same_token_as_in_env_file
```

## 📊 API Endpoints

### Get Active Term
```bash
GET /api/active-term

Response:
{
  "term_code": "2026SP",
  "term_name": "2026 Spring",
  "courses_count": 1234,
  "departments_count": 45
}
```

### Update Courses (Webhook)
```bash
POST /webhook/update-courses
Headers:
  Content-Type: application/json
  X-Webhook-Token: your_secret

Body:
{
  "term_code": "2026SP",
  "content": "DEPT!!CODE!!SECTION!!..."
}
```

## 🧪 Testing

```bash
# Test integration
python test_integration.py

# Test scraper locally
cd scraper && python scrape.py

# Test webhook
curl https://yourusername.pythonanywhere.com/api/active-term
```

## 📅 Schedule

- **Automatic:** Daily at 2 AM UTC (7 AM Pakistan Time)
- **Manual:** GitHub Actions tab → Run workflow

## 🛠️ Tech Stack

- **Backend:** Flask, Python 3.11+
- **Frontend:** HTML, CSS, JavaScript (jQuery)
- **Scraping:** BeautifulSoup4, Requests
- **Automation:** GitHub Actions
- **Hosting:** PythonAnywhere (free tier)

## 📖 Documentation

- [GitHub Actions Setup](GITHUB_ACTIONS_SETUP.md) - Complete guide
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) - Quick reference
- [Test Integration](test_integration.py) - Automated tests

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Error | Check WEBHOOK_SECRET matches |
| 500 Error | Check PythonAnywhere logs |
| No data | Verify ACTIVE_TERM file exists |
| Scraper fails | FCC website might be down |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push branch: `git push origin feature-name`
5. Submit pull request

## 📝 License

MIT License - Feel free to use for your institution!

## 🎓 Credits

Built for Forman Christian College students to easily plan their schedules.

## 📞 Support

- **Issues:** GitHub Issues tab
- **Logs:** PythonAnywhere → Web → Error log
- **Status:** GitHub Actions tab

---

**Happy Scheduling! 📚✨**

