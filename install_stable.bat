@echo off
REM Quick install script using stable, tested versions
REM Works on Python 3.8-3.12 (recommended: Python 3.12)

echo ========================================
echo Rhancer - Stable Installation
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install Python 3.8-3.12 from https://www.python.org/
    pause
    exit /b 1
)

echo Installing stable versions (tested and working)...
echo.

REM Full install command - all stable versions
python -m pip install --upgrade pip setuptools wheel
python -m pip install --only-binary :all: --no-cache-dir numpy==1.26.4 PyQt6==6.6.1 Pillow==10.2.0 opencv-python==4.9.0.80

if errorlevel 1 (
    echo.
    echo Installation failed. Trying with prefer-binary...
    python -m pip install --prefer-binary --no-cache-dir numpy==1.26.4 PyQt6==6.6.1 Pillow==10.2.0 opencv-python==4.9.0.80
    if errorlevel 1 (
        echo.
        echo ERROR: Installation failed!
        echo.
        echo Make sure you have:
        echo   1. Python 3.8-3.12 installed
        echo   2. Visual C++ Redistributables installed:
        echo      https://aka.ms/vs/17/release/vc_redist.x64.exe
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Run the application with: python main.py
echo.
pause

