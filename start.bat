@echo off
echo ===================================================
echo   Assam Farm Analyzer - Web Dashboard
echo ===================================================
echo.

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe server.py
) else (
    python server.py
)

pause
