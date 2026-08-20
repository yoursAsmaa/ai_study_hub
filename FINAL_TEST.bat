@echo off
echo ======================================================================
echo AI STUDY HUB - FINAL VERIFICATION
echo ======================================================================
echo.

echo Step 1: Checking Django configuration...
python manage.py check
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Django check failed!
    pause
    exit /b 1
)
echo.

echo ======================================================================
echo Django check PASSED
echo ======================================================================
echo.
echo MANUAL TESTING REQUIRED:
echo.
echo 1. Stop Django if running (Ctrl+C)
echo 2. Run: python manage.py runserver
echo 3. Open: http://127.0.0.1:8000/ai/
echo 4. Test AI Chat with message: Hi
echo 5. Expected: AI responds successfully
echo.
echo 6. Test another feature (choose one):
echo    - Visit: http://127.0.0.1:8000/notes/
echo    - Create/edit a note
echo    - Click "Summarize with AI" or "Explain with AI"
echo    - Expected: AI feature works
echo.
echo ======================================================================
pause
