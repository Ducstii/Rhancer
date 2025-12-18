@echo off
REM Quick launcher for Rhancer Image Enhancer on Windows

echo Starting Rhancer Image Enhancer...
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application!
    echo.
    echo Make sure you have:
    echo   1. Python 3.8+ installed
    echo   2. Dependencies installed (run install.bat)
    echo.
    pause
)

