#!/usr/bin/env python
"""
Django Project Check Script
Runs all pre-deployment checks and reports results
"""
import subprocess
import sys

def run_command(description, command):
    """Run a command and return exit code"""
    print(f"\n{'='*60}")
    print(f"[CHECK] {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=False,
        text=True
    )
    
    return result.returncode

def main():
    print("\n🔍 DJANGO PROJECT VALIDATION")
    print("="*60)
    
    checks = [
        ("Django System Check", "python manage.py check"),
        ("Django Deployment Check", "python manage.py check --deploy"),
        ("Migration Consistency Check", "python manage.py makemigrations --check --dry-run"),
        ("Test Suite", "python manage.py test --no-input"),
    ]
    
    results = {}
    
    for desc, cmd in checks:
        exit_code = run_command(desc, cmd)
        results[desc] = exit_code == 0
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    for desc, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {desc}")
    
    all_passed = all(results.values())
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("="*60)
        print("\n✨ Your Django project is ready for deployment!")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("="*60)
        print("\n⚠️  Please review the output above and fix any issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
