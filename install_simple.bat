@echo off
REM Simple installer - just installs dependencies
REM Assumes Python is already installed

echo Installing Rhancer dependencies...
echo.

python -m pip install --upgrade pip
python -m pip install numpy==1.26.4 PyQt6==6.6.1 Pillow==10.2.0 opencv-python==4.9.0.80

if errorlevel 1 (
    echo.
    echo Installation failed!
    echo.
    echo Try manually:
    echo   python -m pip install --upgrade pip
    echo   python -m pip install numpy PyQt6 Pillow opencv-python
    echo.
    pause
    exit /b 1
)

echo.
echo Done! Run: python main.py
pause

