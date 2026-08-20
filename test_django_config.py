"""
Test Django settings loading (safe - no key exposure)
"""
import os
import sys
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings

print("=" * 70)
print("🔍 Django Settings Test")
print("=" * 70)
print()

print("1. Django successfully loaded: ✓")
print()

# Check AI_API_KEY from Django settings
api_key = getattr(settings, 'AI_API_KEY', '').strip()

print("2. AI Configuration from Django settings:")
print(f"   - AI_API_KEY configured: {bool(api_key)}")
print(f"   - AI_API_KEY length: {len(api_key)} characters")

if api_key:
    prefix = api_key[:7] if len(api_key) >= 7 else api_key[:3]
    suffix = api_key[-4:] if len(api_key) >= 4 else ""
    print(f"   - Prefix: {prefix}...")
    print(f"   - Suffix: ...{suffix}")
    print(f"   - Starts with 'sk-': {api_key.startswith('sk-')}")
    
    # Validate length
    if len(api_key) < 40:
        print(f"   ⚠️  WARNING: Key is too short!")
        print(f"      Expected: 51+ characters")
        print(f"      Actual: {len(api_key)} characters")
        print(f"      This is NOT a valid OpenAI API key format")
    else:
        print(f"   - Length validation: ✓ OK")
else:
    print(f"   ✗ ERROR: API key not loaded")

print()

# Check OpenAI package
try:
    import openai
    print(f"3. OpenAI SDK:")
    print(f"   - Installed: ✓")
    print(f"   - Version: {openai.__version__}")
    print(f"   - Expected: >=1.30.0,<2.0.0")
except ImportError:
    print(f"3. OpenAI SDK:")
    print(f"   - Installed: ✗")

print()
print("=" * 70)
print("✓ Diagnostic complete")
print("=" * 70)
