@echo off
REM AI Review Tool Startup Script
REM Ensures the application runs from the correct directory

echo Starting AI Review Tool...
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Navigate to the AIReview subdirectory
cd /d "%SCRIPT_DIR%AIReview"

REM Check if AIReview.py exists
if not exist "AIReview.py" (
    echo ERROR: AIReview.py not found in %CD%
    echo Please ensure this script is in the correct directory.
    echo Expected file: %CD%\AIReview.py
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

REM Display current directory and file info
echo Current directory: %CD%
echo Starting AIReview.py...
echo.

REM Start the application
python AIReview.py

REM If there's an error, show it and pause
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Application failed to start (Exit code: %errorlevel%)
    echo Check the error messages above for details.
    pause
)
