@echo off
REM Auto-installer for Rhancer Image Enhancer
REM Installs Python dependencies and Real-ESRGAN

echo ========================================
echo Rhancer Image Enhancer - Auto Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies!
    pause
    exit /b 1
)
echo.

echo [2/3] Installing Real-ESRGAN...
python -c "from install_realesrgan import install_realesrgan; install_realesrgan(lambda p, m: print(f'[{p}%%] {m}'))"
if errorlevel 1 (
    echo WARNING: Real-ESRGAN installation failed, but you can still use basic upscaling.
    echo You can try installing it manually later.
) else (
    echo Real-ESRGAN installed successfully!
)
echo.

echo [3/3] Verification...
python -c "from image_enhancer import ImageEnhancer; e = ImageEnhancer(); print('Real-ESRGAN available:' if e._realesrgan_available else 'Real-ESRGAN not available (will use fallback)')"
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run the application with:
echo   python main.py
echo.
pause

