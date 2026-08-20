@echo off
echo ======================================================================
echo AI STUDY HUB - CLEAR CACHE AND RESTART
echo ======================================================================
echo.

echo Clearing Python cache...
python clear_cache_and_test.py
echo.

echo ======================================================================
echo NOW RUN THESE COMMANDS:
echo ======================================================================
echo 1. python manage.py check
echo 2. python manage.py runserver
echo 3. Test at: http://127.0.0.1:8000/ai/
echo ======================================================================
echo.
pause
