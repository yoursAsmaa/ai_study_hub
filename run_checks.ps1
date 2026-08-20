Write-Host "=== Django Check Script ===" -ForegroundColor Cyan

Write-Host "[1/4] Running: python manage.py check"
python manage.py check

Write-Host "[2/4] Running: python manage.py check --deploy"
python manage.py check --deploy

Write-Host "[3/4] Running: python manage.py makemigrations --check --dry-run"
python manage.py makemigrations --check --dry-run

Write-Host "[4/4] Running: python manage.py test --no-input"
python manage.py test --no-input

Write-Host "=== All checks complete ===" -ForegroundColor Green
