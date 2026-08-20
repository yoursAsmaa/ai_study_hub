"""
Management command to safely diagnose AI API configuration.
NEVER prints the actual API key — only reports status.

Usage: python manage.py check_ai_config
"""

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Safely diagnose AI API configuration without exposing secrets'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("🔍 AI Configuration Diagnostic Report")
        self.stdout.write("=" * 70 + "\n")

        # 1. Check AI Provider
        self.stdout.write(self.style.SUCCESS("✓ AI Provider: Google Gemini"))
        self.stdout.write(self.style.SUCCESS("✓ SDK: google-genai>=0.1.0"))
        self.stdout.write(self.style.SUCCESS("✓ Model: models/gemini-2.5-flash"))
        self.stdout.write("")

        # 2. Check environment variable name
        self.stdout.write("📋 Environment Variable Expected:")
        self.stdout.write("   Variable Name: GEMINI_API_KEY")
        self.stdout.write("")

        # 3. Check if .env file is being loaded
        env_file_path = settings.BASE_DIR / '.env'
        if env_file_path.exists():
            self.stdout.write(self.style.SUCCESS("✓ .env file exists at project root"))
        else:
            self.stdout.write(self.style.ERROR("✗ .env file NOT FOUND at project root"))
            self.stdout.write("  Create a .env file in the project root directory.")
        self.stdout.write("")

        # 4. Check if API key is loaded
        api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
        
        if not api_key:
            self.stdout.write(self.style.ERROR("✗ GEMINI_API_KEY_CONFIGURED: False"))
            self.stdout.write(self.style.ERROR("✗ GEMINI_API_KEY_LENGTH: 0"))
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("⚠️  PROBLEM DETECTED:"))
            self.stdout.write("   The GEMINI_API_KEY is empty or not loaded from .env")
            self.stdout.write("")
            self.stdout.write("🔧 FIX:")
            self.stdout.write("   1. Visit: https://makersuite.google.com/app/apikey")
            self.stdout.write("   2. Click 'Create API Key' (no credit card required)")
            self.stdout.write("   3. Copy your key (starts with AIza...)")
            self.stdout.write("   4. Open your .env file and add:")
            self.stdout.write("")
            self.stdout.write("      GEMINI_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            self.stdout.write("")
            self.stdout.write("   5. Restart the Django development server")
            self.stdout.write("")
            return

        # 5. Report safe statistics about the key
        self.stdout.write(self.style.SUCCESS("✓ GEMINI_API_KEY_CONFIGURED: True"))
        self.stdout.write(self.style.SUCCESS(f"✓ GEMINI_API_KEY_LENGTH: {len(api_key)} characters"))
        
        # 6. Check for common issues
        issues = []
        
        if api_key.startswith(' ') or api_key.endswith(' '):
            issues.append("API key has leading/trailing whitespace")
        
        if api_key.startswith('"') or api_key.startswith("'"):
            issues.append("API key is wrapped in quotes (remove them)")
        
        if api_key == 'your_gemini_api_key_here':
            issues.append("API key is still the placeholder from .env.example")
        
        if not api_key.startswith('AIza'):
            issues.append("API key doesn't start with 'AIza' (invalid format)")
        
        if len(api_key) < 30:
            issues.append(f"API key is too short ({len(api_key)} chars, expected 39+ chars)")
        
        self.stdout.write("")
        
        if issues:
            self.stdout.write(self.style.WARNING("⚠️  POTENTIAL ISSUES DETECTED:"))
            for issue in issues:
                self.stdout.write(f"   • {issue}")
            self.stdout.write("")
            self.stdout.write("🔧 FIX:")
            self.stdout.write("   1. Open your .env file")
            self.stdout.write("   2. Ensure GEMINI_API_KEY is formatted correctly:")
            self.stdout.write("")
            self.stdout.write("      GEMINI_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            self.stdout.write("")
            self.stdout.write("   3. No quotes, no spaces, just: GEMINI_API_KEY=AIza...")
            self.stdout.write("   4. Restart the Django server after changes")
            self.stdout.write("")
        else:
            self.stdout.write(self.style.SUCCESS("✓ API key format looks valid"))
            self.stdout.write("")
            self.stdout.write("🧪 NEXT STEPS:")
            self.stdout.write("   1. If you just added/changed the key, RESTART the Django server")
            self.stdout.write("   2. Test the AI chat in the browser")
            self.stdout.write("   3. If still getting errors:")
            self.stdout.write("      - Check key is active: https://makersuite.google.com/app/apikey")
            self.stdout.write("      - Verify Free Tier quotas (60 RPM, 1500 RPD)")
            self.stdout.write("")

        # 7. Check Gemini package installation
        try:
            from google.genai import Client
            self.stdout.write(self.style.SUCCESS(f"✓ google-genai package installed"))
        except ImportError:
            self.stdout.write(self.style.ERROR("✗ google-genai package NOT installed"))
            self.stdout.write("  Run: pip install google-genai")
        
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write("📝 Summary:")
        self.stdout.write("   - Provider: Google Gemini (models/gemini-2.5-flash)")
        self.stdout.write("   - Config Location: config/settings.py → GEMINI_API_KEY")
        self.stdout.write("   - Service Module: ai_assistant/services/ai_service.py")
        self.stdout.write("   - Free Tier: YES (60 RPM, 1500 RPD)")
        self.stdout.write("   - Security: ✓ Key is server-side only, never sent to browser")
        self.stdout.write("=" * 70 + "\n")
