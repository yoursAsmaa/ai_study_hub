# 🔍 AI API Configuration Debug Guide

## Problem
You're getting: **"Invalid AI API key. Please check your configuration."**

## What I Found

### ✅ Code Configuration (CORRECT)
1. **AI Provider:** OpenAI
2. **SDK:** `openai>=1.30.0,<2.0.0` (installed via requirements.txt)
3. **Model:** `gpt-4o-mini`
4. **Environment Variable:** `AI_API_KEY`
5. **Configuration Location:** `config/settings.py` line 160
6. **Service Module:** `ai_assistant/services/ai_service.py`
7. **Security:** ✅ API key is server-side only, never exposed to browser

### 📋 Configuration Details

**settings.py (line 160):**
```python
AI_API_KEY = os.getenv('AI_API_KEY', '')
```

**ai_service.py (_get_client function):**
```python
api_key = getattr(settings, "AI_API_KEY", "").strip()
if not api_key:
    raise AIServiceError(
        "AI_API_KEY is not configured. "
        "Add AI_API_KEY=your_key to your .env file."
    )
return OpenAI(api_key=api_key)
```

The code strips whitespace and validates the key before making API calls.

---

## 🔧 How to Fix

### Step 1: Check Your .env File

Open your `.env` file in the **project root directory** (same folder as manage.py).

### Step 2: Add Your OpenAI API Key

The line should look EXACTLY like this (no quotes, no spaces):

```plaintext
AI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**IMPORTANT:**
- ❌ NO quotes: `AI_API_KEY="sk-proj-xxx"` (WRONG)
- ❌ NO spaces: `AI_API_KEY = sk-proj-xxx` (WRONG)
- ❌ NO placeholder: `AI_API_KEY=sk-your-openai-api-key-here` (WRONG)
- ✅ YES correct: `AI_API_KEY=sk-proj-xxx` (CORRECT)

### Step 3: Get Your OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Click **"Create new secret key"**
3. Copy the key (starts with `sk-proj-` or `sk-`)
4. Paste it in your .env file

### Step 4: Restart Django Server

**CRITICAL:** You MUST restart the Django development server after changing .env

1. Stop the server: `Ctrl+C`
2. Start again: `python manage.py runserver`

The server only loads .env variables at startup, not during runtime.

---

## 🧪 Run Diagnostic Command

I've created a safe diagnostic tool that checks your configuration **without exposing the API key**:

```bash
python manage.py check_ai_config
```

This will report:
- ✓ AI_PROVIDER
- ✓ AI_API_KEY_CONFIGURED (true/false)
- ✓ AI_API_KEY_LENGTH (number of characters)
- ⚠️ Common issues detected (whitespace, quotes, placeholder, etc.)

**The actual API key is NEVER printed.**

---

## 📝 Your .env File Should Contain

```plaintext
# Django Core
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# PostgreSQL Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ai_study_hub
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=127.0.0.1
DB_PORT=5432

# Email (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
DEFAULT_FROM_EMAIL=AI Study Hub <your_gmail@gmail.com>

# AI Provider (OpenAI) — THIS IS WHAT YOU NEED TO FIX
AI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🚨 Common Mistakes

### Mistake 1: Placeholder Still There
```plaintext
AI_API_KEY=sk-your-openai-api-key-here  ❌ WRONG
```
**Fix:** Replace with your actual key from OpenAI

### Mistake 2: Quotes Around Key
```plaintext
AI_API_KEY="sk-proj-xxx"  ❌ WRONG
AI_API_KEY='sk-proj-xxx'  ❌ WRONG
```
**Fix:** Remove quotes

### Mistake 3: Spaces Around =
```plaintext
AI_API_KEY = sk-proj-xxx  ❌ WRONG (space before/after =)
```
**Fix:** No spaces around equals sign

### Mistake 4: Whitespace
```plaintext
AI_API_KEY= sk-proj-xxx   ❌ WRONG (space after =)
AI_API_KEY=sk-proj-xxx    ❌ WRONG (space at end)
```
**Fix:** Trim all whitespace

### Mistake 5: Didn't Restart Server
You changed .env but didn't restart Django → old empty value is still loaded

**Fix:** Always restart the server after .env changes

### Mistake 6: Wrong Key Type
Some keys start with `sk-` (older format) or `sk-proj-` (newer project keys). Both work.

If your key doesn't start with `sk-`, it's invalid.

---

## 🔍 How the Error Happens

**Flow:**
1. Browser sends chat message → Django view
2. View calls `ai_service.chat_with_ai()`
3. Service calls `_get_client()`
4. `_get_client()` reads `settings.AI_API_KEY`
5. If empty → raises AIServiceError("AI_API_KEY is not configured")
6. If present → OpenAI client attempts connection
7. If invalid key → OpenAI raises authentication error
8. Service catches error → raises AIServiceError("Invalid AI API key")

**Your Error:** Step 5 or Step 8
- **Step 5:** Key is empty/not loaded
- **Step 8:** Key is loaded but invalid (wrong key, expired, or no credits)

---

## 🧪 Test Your Configuration

### Test 1: Run Diagnostic
```bash
python manage.py check_ai_config
```

### Test 2: Django Check
```bash
python manage.py check
```

### Test 3: Python Shell Test (Safe)
```bash
python manage.py shell
```
```python
from django.conf import settings
key = settings.AI_API_KEY
print(f"Key configured: {bool(key)}")
print(f"Key length: {len(key)}")
print(f"Key starts with 'sk-': {key.startswith('sk-')}")
# DO NOT print the actual key
```

### Test 4: Test in Browser
1. Restart Django server
2. Go to: http://127.0.0.1:8000/ai/
3. Send a test message: "Hello"
4. If it works → ✅ Fixed!
5. If error → Check browser console (F12) for details

---

## 🔒 Security Notes

✅ **What I Did:**
- Created diagnostic command that NEVER prints the actual key
- Only reports: configured (yes/no), length, format validation
- All checks are safe and secure

✅ **What the Code Does:**
- Reads API key from environment variables (server-side only)
- Never sends the key to the browser
- Never logs the key value
- Strips whitespace automatically
- Validates before making API calls

❌ **What NOT to Do:**
- Don't commit .env to git (already in .gitignore)
- Don't share your API key publicly
- Don't paste your key in this chat
- Don't hardcode the key in Python files

---

## 📞 Need More Help?

**If diagnostic shows "Key configured: True" but still getting errors:**
1. Check OpenAI dashboard: https://platform.openai.com/account/usage
2. Verify you have API credits
3. Check if the key is active (not revoked)
4. Try regenerating a new key

**If diagnostic shows "Key configured: False":**
1. Verify .env file exists in project root
2. Verify the line is: `AI_API_KEY=sk-proj-xxx`
3. Restart Django server
4. Run diagnostic again

---

## ✅ Checklist

Before testing, verify:
- [ ] .env file exists in project root (same folder as manage.py)
- [ ] AI_API_KEY line exists in .env
- [ ] Value starts with `sk-` or `sk-proj-`
- [ ] No quotes around the value
- [ ] No spaces around the equals sign
- [ ] No whitespace at the end
- [ ] Not using the placeholder value from .env.example
- [ ] Django server was RESTARTED after .env changes
- [ ] OpenAI key is active and has credits

---

**Created:** August 15, 2026  
**Purpose:** Debug AI API configuration issue  
**Security:** Safe diagnostic - never exposes actual API key values
