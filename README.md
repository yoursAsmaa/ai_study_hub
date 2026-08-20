# 🎓 AI Study Hub

**AI Study Hub** is a comprehensive, intelligent study management platform built with Django MVT architecture. It helps students organize their academic life with AI-powered features including personalized study coaching, smart note-taking, interactive quizzes, flashcards, task planning, and progress analytics.

---

## 🌟 Features

### 📝 **Smart Notes Management**
- Create, edit, and organize notes by subject
- Rich text formatting with markdown support
- AI-powered note summarization and key points extraction
- Tag-based organization and search
- Export notes to PDF with professional formatting

### 🎯 **Interactive Quiz System**
- Create custom quizzes with multiple-choice questions
- AI-generated quizzes from your notes
- Timed quiz sessions with auto-submission
- Instant grading and detailed result analytics
- Quiz history tracking and performance insights
- Export quiz results to PDF

### 🗂️ **Flashcards**
- Digital flashcard creation for active recall
- Organize flashcards by deck/subject
- Spaced repetition tracking
- Flip animation for interactive learning
- Export flashcards for offline study

### 📅 **Study Planner**
- Task management with priorities and due dates
- Calendar view for deadlines
- Task completion tracking
- Daily/weekly study goals
- Progress analytics and streaks

### 🤖 **AI Study Coach**
- Personalized study recommendations based on performance
- AI-powered Q&A assistant for quick help
- Study session analysis and feedback
- Motivational tips and study strategies
- Context-aware responses using your notes and quiz history

### 📚 **Resource Library**
- Upload and manage study materials (PDFs, images, documents)
- Categorize resources by subject/topic
- Quick search and filtering
- Secure file storage and access control

### 📊 **Analytics Dashboard**
- Study time tracking and visualization
- Quiz performance trends
- Task completion rates
- Subject-wise progress breakdown
- Weekly/monthly activity reports
- Streak tracking and achievements

### 🎨 **Modern UI/UX**
- Fully responsive design (desktop, tablet, mobile)
- Dark mode with seamless theme switching
- Accessible ARIA-compliant components
- Smooth animations and transitions
- Mobile-optimized navigation

### 🔒 **Security & User Management**
- Secure user authentication and authorization
- Profile management with avatar uploads
- Email verification support
- Password reset functionality
- Per-user data isolation

---

## 🛠️ Tech Stack

### **Backend**
- **Framework:** Django 6.1 (MVT Architecture)
- **Database:** PostgreSQL
- **ORM:** Django ORM
- **Authentication:** Django Auth System
- **PDF Generation:** ReportLab

### **Frontend**
- **HTML5** with Django Templates
- **CSS3** with CSS Variables (Light/Dark themes)
- **Vanilla JavaScript** (ES6+)
- **No frameworks** — pure MVT pattern

### **AI Integration**
- **Google Gemini API** (models/gemini-2.5-flash)
- Server-side AI processing
- Contextual prompt engineering
- Rate limiting and error handling

### **Development Tools**
- Python 3.12+
- PostgreSQL 15+
- Git version control
- Environment-based configuration (.env)

---

## 📦 Installation

### **Prerequisites**
- Python 3.12 or higher
- PostgreSQL 15 or higher
- Git
- pip (Python package manager)

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/yoursAsmaa/ai_study_hub.git
cd AI_STUDY_HUB
```

### **Step 2: Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### **Step 3: Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Required packages:**
```
Django>=6.1
psycopg2-binary
python-dotenv
google-genai
Pillow
reportlab
```

### **Step 4: Database Setup**

#### **Create PostgreSQL Database**
```bash
# Access PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ai_study_hub;
CREATE USER ai_study_user WITH PASSWORD 'your_secure_password';
ALTER ROLE ai_study_user SET client_encoding TO 'utf8';
ALTER ROLE ai_study_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ai_study_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ai_study_hub TO ai_study_user;
\q
```

### **Step 5: Environment Configuration**

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

**Edit `.env` with your settings:**

```env
# Django Settings
SECRET_KEY=your-super-secret-django-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ai_study_hub
DB_USER=ai_study_user
DB_PASSWORD=your_secure_password
DB_HOST=127.0.0.1
DB_PORT=5432

# Email Configuration (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=AI Study Hub <your-email@gmail.com>

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

### **Step 6: Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **Step 7: Create Superuser**
```bash
python manage.py createsuperuser
```

### **Step 8: Collect Static Files (Production)**
```bash
python manage.py collectstatic --noinput
```

### **Step 9: Run Development Server**
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## ⚙️ Configuration Guide

### **Environment Variables Explained**

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key for cryptographic signing | `django-insecure-...` |
| `DEBUG` | Enable/disable debug mode | `True` / `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `127.0.0.1,localhost,example.com` |
| `DB_NAME` | PostgreSQL database name | `ai_study_hub` |
| `DB_USER` | PostgreSQL username | `ai_study_user` |
| `DB_PASSWORD` | PostgreSQL password | `your_password` |
| `DB_HOST` | Database host | `127.0.0.1` |
| `DB_PORT` | Database port | `5432` |
| `EMAIL_HOST_USER` | SMTP email address | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | SMTP password (app-specific) | `xxxx xxxx xxxx xxxx` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |

### **AI Setup (Google Gemini - Free Tier)**

1. **Get API Key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy and add to `.env` as `GEMINI_API_KEY`

2. **Free Tier Benefits:**
   - 60 requests per minute
   - 1,500 requests per day
   - No credit card required
   - Model: models/gemini-2.5-flash (current recommended model)

3. **Rate Limits:**
   - Free tier: 60 RPM, 1500 RPD
   - Automatic retry on rate limit errors
   - No additional configuration needed

### **Email Setup (Gmail)**

1. **Enable 2-Step Verification:**
   - Google Account → Security → 2-Step Verification

2. **Generate App Password:**
   - Google Account → Security → App passwords
   - Select "Mail" and your device
   - Copy 16-character password to `EMAIL_HOST_PASSWORD`

3. **Test Email:**
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```

### **PDF Export Configuration**

- **Library:** ReportLab (server-side generation)
- **Supported Exports:**
  - Individual notes → `/notes/<id>/pdf/`
  - Quiz results → `/quizzes/<id>/result/pdf/`
  - Study sessions → `/quizzes/sessions/export/pdf/`
- **Security:** Ownership validation before PDF generation
- **Styling:** Professional formatting with headers, footers, tables

---

## 🧪 Testing

### **Run All Tests**
```bash
python manage.py test
```

### **Run Specific App Tests**
```bash
python manage.py test accounts
python manage.py test notes
python manage.py test quizzes
python manage.py test ai_assistant
```

### **Check for Issues**
```bash
# Development checks
python manage.py check

# Production deployment checks
python manage.py check --deploy

# Migration consistency check
python manage.py makemigrations --check --dry-run
```

### **Test Coverage (Optional)**
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # generates htmlcov/index.html
```

---

## 📁 Project Structure

```
AI_STUDY_HUB/
│
├── accounts/              # User authentication & profiles
│   ├── models.py         # UserProfile model
│   ├── views.py          # Login, register, profile views
│   ├── forms.py          # User registration, profile forms
│   └── urls.py
│
├── dashboard/            # Main dashboard & analytics
│   ├── views.py         # Dashboard overview, stats
│   └── urls.py
│
├── notes/               # Smart notes management
│   ├── models.py        # Note model
│   ├── views.py         # CRUD operations
│   ├── pdf_views.py     # PDF export functionality
│   └── urls.py
│
├── quizzes/             # Interactive quiz system
│   ├── models.py        # Quiz, Question, QuizAttempt models
│   ├── views.py         # Quiz CRUD, take quiz, results
│   ├── pdf_views.py     # Quiz result PDF export
│   └── urls.py
│
├── planner/             # Task & study planner
│   ├── models.py        # Task, StudySession models
│   ├── views.py         # Task management, calendar
│   └── urls.py
│
├── resources/           # Study materials library
│   ├── models.py        # Resource model
│   ├── views.py         # Upload, manage resources
│   └── urls.py
│
├── ai_assistant/        # AI Study Coach
│   ├── models.py        # ChatMessage, CoachingSession
│   ├── views.py         # AI chat, recommendations
│   ├── services/
│   │   └── ai_service.py  # Gemini integration
│   └── urls.py
│
├── config/              # Project configuration
│   ├── settings.py      # Django settings
│   ├── urls.py          # Root URL configuration
│   └── wsgi.py
│
├── static/              # Static assets
│   ├── css/
│   │   └── main.css    # Responsive + dark mode styles
│   ├── js/
│   │   └── main.js     # Theme toggle, sidebar, interactions
│   └── images/
│
├── templates/           # Global templates
│   ├── base.html       # Base template with navigation
│   ├── 400.html        # Bad Request error page
│   ├── 403.html        # Forbidden error page
│   ├── 404.html        # Page Not Found error page
│   └── 500.html        # Server Error error page
│
├── media/               # User uploads (profiles, resources)
├── logs/                # Application logs
├── .env                 # Environment variables (DO NOT COMMIT)
├── .env.example         # Environment template
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🚀 Deployment

### **Pre-Deployment Checklist**

1. **Security:**
   ```bash
   python manage.py check --deploy
   ```

2. **Environment:**
   - Set `DEBUG=False` in production `.env`
   - Set `ALLOWED_HOSTS` to your domain
   - Generate new `SECRET_KEY`
   - Use strong database password

3. **Static Files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Database:**
   - Backup production database regularly
   - Run migrations before deployment
   - Set up database connection pooling

5. **Security Headers:**
   - All set automatically when `DEBUG=False`
   - SSL/HTTPS enforced
   - Secure cookies enabled
   - HSTS configured

### **Deployment Platforms**

#### **Option 1: Railway.app**
```bash
# Install Railway CLI
npm install -g railway

# Login and deploy
railway login
railway init
railway up
```

#### **Option 2: Render.com**
- Create new Web Service
- Connect GitHub repo
- Add environment variables
- Deploy automatically

#### **Option 3: DigitalOcean App Platform**
- Create new app
- Link repository
- Configure environment
- Deploy with one click

#### **Option 4: Traditional VPS (Ubuntu)**
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx

# Set up Gunicorn
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Configure Nginx reverse proxy
# Set up SSL with Let's Encrypt
```

---

## 🔐 Security Notes

- **Never commit `.env` file** — it contains secrets
- **Use app-specific passwords** for email (not your main Gmail password)
- **Rotate API keys** regularly
- **Enable HTTPS** in production (enforced when `DEBUG=False`)
- **Validate user input** on all forms (CSRF protection enabled)
- **Ownership checks** on all CRUD operations
- **SQL injection protection** via Django ORM parameterized queries
- **XSS protection** via Django template auto-escaping

---

## 🐛 Troubleshooting

### **Database Connection Error**
```
django.db.utils.OperationalError: FATAL: password authentication failed
```
**Solution:** Check `.env` database credentials and ensure PostgreSQL is running.

### **AI API Error**
```
Invalid Gemini API key. Please check your configuration.
```
**Solution:** 
1. Run the diagnostic command to check configuration:
   ```bash
   python manage.py check_ai_config
   ```
2. Verify `GEMINI_API_KEY` in `.env` is formatted correctly (no quotes, no spaces)
3. Get your key at: https://makersuite.google.com/app/apikey
4. **IMPORTANT:** Restart Django server after changing `.env` file
5. Free tier available - no credit card required

For detailed debugging, see: `AI_CONFIG_DEBUG.md`

### **Email Not Sending**
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```
**Solution:** Use app-specific password, not your Gmail password. Enable 2FA first.

### **Static Files Not Loading**
```
GET /static/css/main.css 404
```
**Solution:** Run `python manage.py collectstatic` and check `STATIC_ROOT` configuration.

### **Migration Conflicts**
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```
**Solution:** 
```bash
python manage.py migrate --fake <app_name> <migration_name>
python manage.py migrate
```

---

## 📄 License

This project is a graduation project for educational purposes. All rights reserved.

---

## 👨‍💻 Author

**AI Study Hub Team**  
Summer Training 2025  
Django Full-Stack Development

---

## 🤝 Contributing

This is a graduation project and not open for external contributions. However, feedback and suggestions are welcome!

---

## 📧 Support

For issues or questions:
- Check the troubleshooting section above
- Review Django documentation: https://docs.djangoproject.com/
- Check OpenAI API docs: https://platform.openai.com/docs/

---

## 🎯 Future Enhancements

- [ ] Mobile app (React Native / Flutter)
- [ ] Real-time collaboration on notes
- [ ] Voice-to-text note recording
- [ ] Integration with Google Calendar
- [ ] Gamification with badges and leaderboards
- [ ] Social features (study groups, peer reviews)
- [ ] Offline mode with PWA
- [ ] Advanced analytics with ML predictions
- [ ] Multi-language support (i18n)
- [ ] API for third-party integrations

---

**Built with ❤️ using Django MVT Architecture**
