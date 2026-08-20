# 🚀 Quick Start Guide — AI Study Hub

## ⚡ Fast Setup (5 minutes)

### 1️⃣ Prerequisites Check
```bash
python --version   # Should be 3.12+
psql --version     # Should be PostgreSQL 15+
```

### 2️⃣ Database Setup
```bash
psql -U postgres
```
```sql
CREATE DATABASE ai_study_hub;
CREATE USER ai_study_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_study_hub TO ai_study_user;
\q
```

### 3️⃣ Environment Setup
```bash
# Copy example env
cp .env.example .env

# Edit .env and update these:
# - SECRET_KEY (generate new: https://djecrety.ir/)
# - DB_PASSWORD (your database password)
# - AI_API_KEY (from https://platform.openai.com/api-keys)
# - EMAIL_HOST_USER + EMAIL_HOST_PASSWORD (Gmail app password)
```

### 4️⃣ Install & Run
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### 5️⃣ Access Application
- **Homepage:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

## 🧪 Quick Test

```bash
# Run system checks
python manage.py check

# Run tests
python manage.py test --no-input

# Check deployment readiness
python manage.py check --deploy
```

---

## 🎨 Features to Test

1. **Dark Mode Toggle** — Click moon icon in navbar
2. **Mobile Navigation** — Resize browser or use mobile device
3. **Create Note** — Dashboard → Notes → New Note
4. **AI Assistant** — Dashboard → AI Coach → Ask a question
5. **Take Quiz** — Dashboard → Quizzes → Take Quiz
6. **Export PDF** — View any note → Click "Export to PDF"
7. **Error Pages** — Visit `/test-404/` to see custom 404 page

---

## 🔧 Common Commands

```bash
# Create new superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Make migrations (after model changes)
python manage.py makemigrations
python manage.py migrate

# Collect static files (for production)
python manage.py collectstatic

# Open Django shell
python manage.py shell

# Run specific app tests
python manage.py test notes
python manage.py test quizzes
```

---

## 📧 Gmail Setup (Email Verification)

1. **Enable 2-Step Verification:**
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy 16-character password

3. **Update .env:**
   ```env
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
   ```

---

## 🤖 OpenAI API Setup

1. **Get API Key:**
   - Visit: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy key (starts with `sk-`)

2. **Update .env:**
   ```env
   AI_API_KEY=sk-your-key-here
   ```

3. **Check Balance:**
   - Visit: https://platform.openai.com/usage
   - Ensure you have credits

---

## 🐛 Troubleshooting

### Database Connection Failed
```bash
# Check PostgreSQL is running
# Windows: Services → PostgreSQL
# macOS: brew services list
# Linux: sudo systemctl status postgresql
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Migration Errors
```bash
# Reset migrations (CAUTION: Development only!)
python manage.py migrate --fake <app_name> zero
python manage.py makemigrations
python manage.py migrate
```

### AI API Not Working
- Check API key is correct in `.env`
- Verify OpenAI account has credits
- Check `ai_assistant/services/ai_service.py` model name

---

## 📚 Additional Resources

- **Full Documentation:** See `README.md`
- **Phase 9 Checklist:** See `PHASE_9_CHECKLIST.md`
- **Django Docs:** https://docs.djangoproject.com/
- **OpenAI Docs:** https://platform.openai.com/docs/

---

## 🎯 Project Structure Quick Reference

```
AI_STUDY_HUB/
├── accounts/         # User auth & profiles
├── dashboard/        # Analytics & overview
├── notes/           # Smart notes + PDF export
├── quizzes/         # Quizzes + results + PDF export
├── planner/         # Tasks & study sessions
├── resources/       # Study materials library
├── ai_assistant/    # AI Study Coach
├── config/          # Django settings
├── static/          # CSS, JS, images
├── templates/       # HTML templates
├── media/           # User uploads
└── logs/            # Application logs
```

---

## ✅ You're Ready!

Everything is set up. Now you can:
- ✨ Create notes and organize your study materials
- 🎯 Take quizzes and track your performance
- 🤖 Chat with your AI Study Coach
- 📅 Plan your study schedule
- 📊 View your progress analytics
- 🌙 Toggle dark mode anytime
- 📱 Use on any device (fully responsive)
- 📄 Export notes and results to PDF

**Happy studying! 🎓**
