"""
Safe diagnostic script to check environment variable loading.
Run with: python test_env_loading.py
NEVER prints the actual API key.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'

print("=" * 70)
print("🔍 Environment Variable Loading Test")
print("=" * 70)
print()

# Check .env file exists
print(f"1. .env file path: {env_path}")
print(f"   .env exists: {env_path.exists()}")
print()

# Load the .env file
load_dotenv(env_path)
print("2. Loaded .env file using python-dotenv")
print()

# Get the API key
api_key = os.getenv('AI_API_KEY', '').strip()

# Safe reporting (NEVER print the actual key)
print("3. AI_API_KEY variable:")
print(f"   - Configured: {bool(api_key)}")
print(f"   - Length: {len(api_key)} characters")

if api_key:
    # Only show first 3 and last 4 characters
    prefix = api_key[:3] if len(api_key) >= 3 else "***"
    suffix = api_key[-4:] if len(api_key) >= 4 else "***"
    print(f"   - Prefix: {prefix}...")
    print(f"   - Suffix: ...{suffix}")
    print(f"   - Format valid: {api_key.startswith('sk-')}")
    
    # Check for common issues
    issues = []
    if api_key != api_key.strip():
        issues.append("Has whitespace at start/end")
    if '\n' in api_key or '\r' in api_key:
        issues.append("Contains newline characters")
    if api_key.startswith('"') or api_key.startswith("'"):
        issues.append("Starts with quote character")
    if api_key.endswith('"') or api_key.endswith("'"):
        issues.append("Ends with quote character")
    if '\\n' in api_key:
        issues.append("Contains escaped newline (\\n)")
    
    if issues:
        print(f"   - Issues detected: {', '.join(issues)}")
    else:
        print(f"   - Format check: ✓ No obvious issues")
else:
    print(f"   - ERROR: Variable is empty!")

print()
print("4. Raw value inspection (first 50 chars only):")
raw_value = os.getenv('AI_API_KEY', '')
if raw_value:
    # Show first 50 chars for debugging
    safe_sample = raw_value[:50] if len(raw_value) > 50 else raw_value
    # Mask most of it
    if len(safe_sample) > 10:
        display = safe_sample[:3] + "*" * (len(safe_sample) - 7) + safe_sample[-4:]
    else:
        display = "***"
    print(f"   Sample: {display}")
    print(f"   Has leading space: {raw_value.startswith(' ')}")
    print(f"   Has trailing space: {raw_value.endswith(' ')}")
    print(f"   Has newline: {'\\n' in repr(raw_value) or '\\r' in repr(raw_value)}")
else:
    print(f"   ERROR: No value found")

print()
print("=" * 70)
print("✓ Diagnostic complete - No secrets exposed")
print("=" * 70)
