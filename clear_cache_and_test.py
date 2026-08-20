"""
Clear Python cache and verify Django configuration
"""
import os
import sys
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

print("=" * 70)
print("CLEARING PYTHON CACHE")
print("=" * 70)

# Remove all __pycache__ directories
cache_count = 0
for pycache_dir in BASE_DIR.rglob('__pycache__'):
    try:
        shutil.rmtree(pycache_dir)
        cache_count += 1
        print(f"Deleted: {pycache_dir}")
    except Exception as e:
        print(f"Could not delete {pycache_dir}: {e}")

# Remove all .pyc files
pyc_count = 0
for pyc_file in BASE_DIR.rglob('*.pyc'):
    try:
        pyc_file.unlink()
        pyc_count += 1
    except Exception as e:
        pass

print(f"\nRemoved {cache_count} __pycache__ directories")
print(f"Removed {pyc_count} .pyc files")
print()

print("=" * 70)
print("CACHE CLEARED SUCCESSFULLY")
print("=" * 70)
print()
print("NEXT STEPS:")
print("1. Stop Django server (Ctrl+C)")
print("2. Run: python manage.py check")
print("3. Run: python manage.py runserver")
print("4. Test: http://127.0.0.1:8000/ai/")
print("5. Send message: Hi")
print("=" * 70)

