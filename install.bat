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
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Detected Python version: %PYTHON_VERSION%
echo.

REM Check if Python version is too new (3.14+)
python -c "import sys; exit(0 if sys.version_info < (3, 14) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ========================================
    echo WARNING: Python 3.14+ Detected
    echo ========================================
    echo.
    echo Python 3.14 is very new and may not have pre-built wheels
    echo for all packages. This means packages will try to build from source,
    echo which requires Visual Studio Build Tools (not just Redistributables).
    echo.
    echo RECOMMENDED: Use Python 3.8-3.12 for best compatibility
    echo Download: https://www.python.org/downloads/
    echo.
    echo If you continue with Python 3.14, you will need:
    echo   1. Visual Studio Build Tools (not just Redistributables)
    echo      https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
    echo   2. Select "C++ build tools" workload during installation
    echo.
    echo Press any key to continue anyway, or Ctrl+C to cancel...
    pause >nul
    echo.
)

echo.
echo ========================================
echo IMPORTANT: Visual C++ Redistributables
echo ========================================
echo.
echo Python packages like NumPy and OpenCV require
echo Microsoft Visual C++ Redistributables to run.
echo.
echo If installation fails, install this first:
echo   Microsoft Visual C++ 2015-2022 Redistributable (x64)
echo   Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
echo.
echo Press any key to continue installation...
pause >nul
echo.

echo [1/4] Upgrading pip and installing build tools...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip!
    pause
    exit /b 1
)
echo.

echo [2/4] Installing Python dependencies (stable versions)...
echo.
echo Installing stable, tested versions with pre-built wheels...
echo These versions work on Python 3.8-3.12 (recommended: Python 3.12)
echo.

REM Check if Python 3.14+
python -c "import sys; exit(0 if sys.version_info < (3, 14) else 1)" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Python 3.14+ detected!
    echo.
    echo Python 3.14 may not have pre-built wheels for all packages.
    echo You may need Visual Studio Build Tools to compile from source.
    echo.
    echo RECOMMENDED: Use Python 3.12 instead
    echo Download: https://www.python.org/downloads/release/python-3120/
    echo.
    echo Press any key to continue anyway...
    pause >nul
    echo.
)

echo Installing all dependencies from requirements.txt...
python -m pip install --upgrade pip setuptools wheel
python -m pip install --only-binary :all: --no-cache-dir -r requirements.txt
if errorlevel 1 (
    echo.
    echo WARNING: --only-binary failed, trying with prefer-binary...
    python -m pip install --prefer-binary --no-cache-dir -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo.
        echo SOLUTIONS:
        echo   1. Install Visual C++ Redistributables (REQUIRED):
        echo      https://aka.ms/vs/17/release/vc_redist.x64.exe
        echo   2. Use Python 3.8-3.12 (recommended: 3.12)
        echo   3. Check your internet connection
        echo   4. Try: python -m pip install --upgrade pip
        echo.
        pause
        exit /b 1
    )
)
echo.
echo All dependencies installed successfully!
echo.

echo [3/4] Installing Real-ESRGAN...
python -c "from install_realesrgan import install_realesrgan; install_realesrgan(lambda p, m: print(f'[{p}%%] {m}'))"
if errorlevel 1 (
    echo WARNING: Real-ESRGAN installation failed, but you can still use basic upscaling.
    echo You can try installing it manually later.
) else (
    echo Real-ESRGAN installed successfully!
)
echo.

echo [4/4] Verification...
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

