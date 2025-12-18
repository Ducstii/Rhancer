@echo off
REM Quick launcher for Rhancer Image Enhancer on Windows

echo Starting Rhancer Image Enhancer...
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application!
    echo.
    echo Make sure you have:
    echo   1. Python 3.8-3.12 installed and in PATH
    echo   2. Dependencies installed
    echo.
    echo To install dependencies, run:
    echo   python -m pip install numpy==1.26.4 PyQt6==6.6.1 Pillow==10.2.0 opencv-python==4.9.0.80
    echo.
    echo Or see INSTALL_SIMPLE.md for step-by-step instructions.
    echo.
    pause
)


