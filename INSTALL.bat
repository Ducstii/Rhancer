@echo off
REM Main installer - uses PowerShell for reliable Python installation
REM This is the one to run!

echo ========================================
echo Rhancer - Complete Auto Installer
echo ========================================
echo.
echo This will install:
echo   - Python 3.12 (if not installed)
echo   - Visual C++ Redistributables
echo   - All Python dependencies
echo   - Real-ESRGAN (optional)
echo.
echo Press any key to start, or Ctrl+C to cancel...
pause >nul

REM Check if PowerShell is available
powershell -Command "exit 0" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PowerShell is required but not found!
    echo Please use Windows 7 or later.
    pause
    exit /b 1
)

REM Run PowerShell installer
echo.
echo Starting PowerShell installer...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0install_python.ps1"

if errorlevel 1 (
    echo.
    echo Installation failed!
    echo.
    echo Try manual installation:
    echo   1. Install Python 3.12 from https://www.python.org/downloads/
    echo   2. Install Visual C++ Redistributables from https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo   3. Run: python -m pip install numpy==1.26.4 PyQt6==6.6.1 Pillow==10.2.0 opencv-python==4.9.0.80
    echo.
    pause
    exit /b 1
)

echo.
echo Done! You can now run the application.
pause

