@echo off
REM Wellbeing Desktop Tracker - Startup Script
REM This script activates the virtual environment and runs the application

echo Starting Wellbeing Desktop Tracker...
echo.

REM Activate virtual environment and run application
call venv\Scripts\activate.bat
python src\main.py

REM If application exits, pause to see any errors
if errorlevel 1 (
    echo.
    echo Application exited with error code: %errorlevel%
    pause
)
