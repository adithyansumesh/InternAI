@echo off
cd /d "%~dp0"
echo ===================================================
echo   Starting InternAI FastAPI Backend Server
echo ===================================================
echo.
echo Activating virtual environment...
if exist ..\venv\Scripts\activate.bat (
    call ..\venv\Scripts\activate.bat
) else if exist ..\.venv\Scripts\activate.bat (
    call ..\.venv\Scripts\activate.bat
) else (
    echo WARNING: Cannot find venv or .venv folder in parent directory. Relying on global Python.
)

echo.
echo Starting Uvicorn on http://localhost:8000...
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
