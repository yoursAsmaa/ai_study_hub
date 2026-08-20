# 📊 ERD Generation Guide - AI Study Hub

## Quick Summary

Your project has **13 entities** with **19 one-to-many** and **1 many-to-many** relationships.

---

## ✅ RECOMMENDED METHOD: dbdiagram.io (Professional & Free)

### Why This Method?
- ✅ Professional, publication-ready output
- ✅ Free, no installation required
- ✅ Export as PNG or PDF
- ✅ Fully customizable colors and layout
- ✅ Perfect for graduation project submission

### Steps:

1. **Open the generated DBML file:**
   - File: `erd_dbml_code.txt` (already created)

2. **Visit dbdiagram.io:**
   - Go to: https://dbdiagram.io/
   - Click "Go to App" (no signup required)

3. **Import the diagram:**
   - Delete default content in editor
   - Copy ALL content from `erd_dbml_code.txt`
   - Paste into the left editor panel
   - Diagram auto-generates on the right

4. **Customize (Optional):**
   - Click "Settings" (gear icon)
   - Choose colors and theme
   - Adjust layout by dragging tables

5. **Export:**
   - Click "Export" (top right)
   - Choose "Export to PNG" or "Export to PDF"
   - High resolution, professional quality

### What You'll Get:
- ✅ All 13 models (User + 12 custom)
- ✅ All ForeignKey relationships shown with arrows
- ✅ OneToOne relationship (User-Profile) clearly marked
- ✅ ManyToMany relationship (Note-Tag) with junction table
- ✅ Primary keys marked
- ✅ Foreign keys highlighted
- ✅ Professional diagram suitable for graduation project

---

## 🔧 ALTERNATIVE METHOD 1: django-extensions (Automated)

### Installation:

```bash
# Install django-extensions and pydot
pip install django-extensions pydot

# Or try pygraphviz (requires Graphviz installed on system)
pip install django-extensions pygraphviz
```

### Configuration:

Add to `config/settings.py` INSTALLED_APPS:
```python
INSTALLED_APPS = [
    # ... existing apps
    'django_extensions',
]
```

### Generate ERD:

```bash
# All apps including Django built-in
python manage.py graph_models -a -g -o erd_full.png

# Custom apps only (recommended)
python manage.py graph_models accounts planner notes resources quizzes ai_assistant dashboard -g -o erd_custom.png

# With more details
python manage.py graph_models accounts planner notes resources quizzes ai_assistant dashboard --arrow-shape normal -g -o erd_detailed.png
```

### Options:
- `-a` : All apps
- `-g` : Group models by app
- `-o` : Output file
- `--arrow-shape normal` : Better arrow style
- `--hide-relations-from-fields` : Cleaner diagram

### Pros:
- ✅ Fully automated
- ✅ Always up-to-date with models
- ✅ Direct from Django code

### Cons:
- ❌ Requires Graphviz installation (can be tricky on Windows)
- ❌ Less customizable appearance
- ❌ May be cluttered with all Django built-in tables

---

## 🔧 ALTERNATIVE METHOD 2: ERDAlchemy (Database-Based)

### Installation:

```bash
pip install eralchemy
```

### Generate:

```bash
# From database connection
eralchemy -i 'postgresql://postgres:password@localhost/ai_study_hub' -o erd.png

# Or from Django models
python -c "from eralchemy import render_er; from django.db import connection; render_er(connection, 'erd.pdf')"
```

### Pros:
- ✅ Reads from actual database
- ✅ Shows real structure

### Cons:
- ❌ Requires database credentials
- ❌ Less customizable
- ❌ May show Django internal tables

---

## 🎨 ALTERNATIVE METHOD 3: Draw.io / Lucidchart (Manual)

### Tools:
- **Draw.io** (Free): https://app.diagrams.net/
- **Lucidchart** (Free tier): https://www.lucidchart.com/

### Steps:
1. Create new diagram
2. Use ERD shapes
3. Add tables based on models (see table structure below)
4. Draw relationships
5. Export as PNG/PDF

### Pros:
- ✅ Complete control over appearance
- ✅ Professional quality

### Cons:
- ❌ Manual work required
- ❌ Must update manually when models change

---

## 📋 TABLE STRUCTURE REFERENCE

For manual ERD creation, here's the structure:

### User (Django Built-in)
- **PK**: id
- username
- email
- password
- first_name, last_name
- is_active, date_joined

### Profile
- **PK**: id
- **FK**: user_id → User.id (OneToOne)
- profile_image, bio
- university, major, phone
- is_email_verified
- created_at, updated_at

### Category
- **PK**: id
- **FK**: user_id → User.id
- name, color
- created_at

### Tag
- **PK**: id
- **FK**: user_id → User.id
- name

### Note
- **PK**: id
- **FK**: user_id → User.id
- **FK**: category_id → Category.id
- **M2M**: tags ↔ Tag
- title, content, summary
- created_at, updated_at

### Task
- **PK**: id
- **FK**: user_id → User.id
- **FK**: category_id → Category.id
- title, description
- due_date, priority, status
- is_completed
- created_at, updated_at

### Resource
- **PK**: id
- **FK**: user_id → User.id
- **FK**: category_id → Category.id
- title, description, link
- resource_type
- created_at, updated_at

### Quiz
- **PK**: id
- **FK**: user_id → User.id
- **FK**: source_note_id → Note.id
- title, score
- total_questions, correct_answers
- completed
- created_at, updated_at

### Question
- **PK**: id
- **FK**: quiz_id → Quiz.id
- question_text
- options (JSON)
- correct_answer, user_answer
- explanation, is_correct
- created_at

### Flashcard
- **PK**: id
- **FK**: user_id → User.id
- **FK**: quiz_id → Quiz.id
- **FK**: source_note_id → Note.id
- front, back
- known
- created_at

### StudySession
- **PK**: id
- **FK**: user_id → User.id
- **FK**: category_id → Category.id
- subject
- start_time, end_time
- duration_minutes, notes
- created_at

### ChatMessage
- **PK**: id
- **FK**: user_id → User.id
- role, content
- created_at

### Activity
- **PK**: id
- **FK**: user_id → User.id
- action_type, description
- created_at

---

## 🎯 RELATIONSHIP SUMMARY

### OneToOne (1:1)
- User ←→ Profile

### OneToMany (1:N)
- User → Category, Tag, Task, Note, Resource, Quiz, Flashcard, StudySession, ChatMessage, Activity
- Category → Note, Task, Resource, StudySession
- Note → Quiz, Flashcard
- Quiz → Question, Flashcard

### ManyToMany (N:M)
- Note ↔ Tag (via Note_Tags junction table)

---

## ✅ RECOMMENDED FOR GRADUATION PROJECT

**Use dbdiagram.io method** because:
1. Professional appearance
2. No installation required
3. Easy to customize
4. Perfect for documentation
5. High-quality PNG/PDF export
6. Free and fast

**File already created:** `erd_dbml_code.txt`

**Time to complete:** 2-3 minutes

---

## 📝 NOTES FOR GRADUATION SUBMISSION

When including ERD in your documentation:

1. **Title:** "AI Study Hub - Entity Relationship Diagram"

2. **Description:** Include text explaining:
   - 13 entities (User + 12 custom models)
   - 19 one-to-many relationships
   - 1 many-to-many relationship
   - PostgreSQL database

3. **Legend:** Explain symbols:
   - Solid lines = ForeignKey (one-to-many)
   - Dashed lines = ManyToMany
   - Diamond/special marker = OneToOne

4. **Export Quality:**
   - PNG: Use high DPI (300+)
   - PDF: Vector format (preferred)

---

## 🚀 QUICK START (1 MINUTE)

```bash
# Already done:
✓ erd_dbml_code.txt created

# Do now:
1. Open: https://dbdiagram.io/
2. Copy: erd_dbml_code.txt content
3. Paste: Into dbdiagram.io editor
4. Export: PNG or PDF

Done! ✓
```

---

## 📞 TROUBLESHOOTING

### If dbdiagram.io has issues:
- Try different browser
- Clear content and paste again
- Check DBML syntax (should be valid)

### If django-extensions fails:
- Install Graphviz system package first
- Use pydot instead of pygraphviz
- Check INSTALLED_APPS configuration

### If you need changes:
- Edit `erd_dbml_code.txt`
- Reload in dbdiagram.io
- All relationships are documented correctly

---

## ✅ VALIDATION CHECKLIST

Your ERD should show:

- [ ] 13 tables/entities
- [ ] User table with all models connected to it
- [ ] Profile with OneToOne to User
- [ ] Category shared by Task, Note, Resource, StudySession
- [ ] Note connected to Tag with M2M relationship
- [ ] Quiz connected to Note, Question, Flashcard
- [ ] All primary keys visible
- [ ] All foreign keys visible
- [ ] Clear relationship lines
- [ ] Professional appearance

---

Good luck with your graduation project! 🎓
