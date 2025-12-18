@echo off
REM Complete installer - installs Python 3.12 and all dependencies
REM Run as Administrator for best results

echo ========================================
echo Rhancer - Complete Auto Installer
echo Installs Python 3.12 + All Dependencies
echo ========================================
echo.

REM Check if running as admin (optional but helpful)
net session >nul 2>&1
if errorlevel 1 (
    echo NOTE: Not running as Administrator.
    echo Some steps may require admin rights.
    echo.
)

REM Step 1: Check/Install Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
set PYTHON_EXISTS=%ERRORLEVEL%
if %PYTHON_EXISTS% neq 0 (
    echo Python not found. Installing Python 3.12...
    echo.
    
    REM Create temp directory
    set TEMP_DIR=%TEMP%\rhancer_install
    if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
    
    REM Download Python 3.12 installer
    echo Downloading Python 3.12 installer...
    echo This may take a few minutes...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile '%TEMP_DIR%\python-installer.exe'}"
    
    if not exist "%TEMP_DIR%\python-installer.exe" (
        echo ERROR: Failed to download Python installer!
        echo.
        echo Please download manually from:
        echo https://www.python.org/downloads/release/python-3120/
        echo.
        echo Make sure to check "Add Python to PATH" during installation!
        pause
        exit /b 1
    )
    
    echo Installing Python 3.12...
    echo This will run silently. Please wait...
    echo.
    "%TEMP_DIR%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_launcher=1
    
    REM Clean up
    del "%TEMP_DIR%\python-installer.exe" >nul 2>&1
    rmdir "%TEMP_DIR%" >nul 2>&1
    
    REM Add Python to PATH for this session
    set PATH=%PATH%;C:\Program Files\Python312;C:\Program Files\Python312\Scripts
    set PATH=%PATH%;C:\Program Files (x86)\Python312;C:\Program Files (x86)\Python312\Scripts
    set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312
    set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\Scripts
    
    REM Try to find Python in common locations
    if exist "C:\Program Files\Python312\python.exe" (
        set "PYTHON_EXE=C:\Program Files\Python312\python.exe"
    ) else if exist "C:\Program Files (x86)\Python312\python.exe" (
        set "PYTHON_EXE=C:\Program Files (x86)\Python312\python.exe"
    ) else if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
        set "PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    ) else (
        echo.
        echo Python installed but not found in standard locations.
        echo Please restart your terminal and run this installer again,
        echo or manually add Python to PATH.
        pause
        exit /b 1
    )
    
    REM Use the found Python executable
    set "PYTHON_CMD=%PYTHON_EXE%"
    
    REM Verify installation
    "%PYTHON_EXE%" --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo WARNING: Python installed but verification failed.
        echo Please restart your terminal/command prompt and run this installer again.
        pause
        exit /b 1
    )
    
    echo Python 3.12 installed and verified!
    echo.
    echo NOTE: You may need to restart your terminal for Python to be in PATH.
    echo Continuing with installation using found Python executable...
    echo.
) else (
    REM Check if it's Python 3.12 or compatible
    python -c "import sys; v = sys.version_info; print(f'Python {v.major}.{v.minor}.{v.micro} found'); exit(0 if v.major == 3 and 8 <= v.minor <= 12 else 1)" 2>nul
    if errorlevel 1 (
        echo WARNING: Python found but version may not be optimal.
        echo Recommended: Python 3.8-3.12
        echo.
    ) else (
        python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} found')"
    )
    echo.
)
echo.

REM Step 2: Install Visual C++ Redistributables
echo [2/5] Checking Visual C++ Redistributables...
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" >nul 2>&1
if errorlevel 1 (
    echo Visual C++ Redistributables not found.
    echo Downloading and installing...
    echo.
    
    set TEMP_DIR=%TEMP%\rhancer_install
    if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"
    
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile '%TEMP_DIR%\vc_redist.x64.exe'}"
    
    if exist "%TEMP_DIR%\vc_redist.x64.exe" (
        echo Installing Visual C++ Redistributables...
        start /wait "" "%TEMP_DIR%\vc_redist.x64.exe" /quiet /norestart
        del "%TEMP_DIR%\vc_redist.x64.exe" >nul 2>&1
        echo Visual C++ Redistributables installed!
    ) else (
        echo WARNING: Failed to download Visual C++ Redistributables.
        echo Please install manually from:
        echo https://aka.ms/vs/17/release/vc_redist.x64.exe
        echo.
        pause
    )
    rmdir "%TEMP_DIR%" >nul 2>&1
) else (
    echo Visual C++ Redistributables already installed.
)
echo.

REM Step 3: Upgrade pip
echo [3/5] Upgrading pip and build tools...
if defined PYTHON_CMD (
    "%PYTHON_CMD%" -m pip install --upgrade pip setuptools wheel
) else (
    python -m pip install --upgrade pip setuptools wheel
)
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip!
    pause
    exit /b 1
)
echo.

REM Step 4: Install Python dependencies
echo [4/5] Installing Python dependencies (stable versions)...
echo.
if defined PYTHON_CMD (
    "%PYTHON_CMD%" -m pip install --only-binary :all: --no-cache-dir numpy==1.26.4 PyQt6==6.6.1 Pillow==10.2.0 opencv-python==4.9.0.80
    if errorlevel 1 (
        echo.
        echo WARNING: --only-binary failed, trying with prefer-binary...
        "%PYTHON_CMD%" -m pip install --prefer-binary --no-cache-dir numpy==1.26.4 PyQt6==6.6.1 Pillow==10.2.0 opencv-python==4.9.0.80
    )
) else (
    python -m pip install --only-binary :all: --no-cache-dir numpy==1.26.4 PyQt6==6.6.1 Pillow==10.2.0 opencv-python==4.9.0.80
    if errorlevel 1 (
        echo.
        echo WARNING: --only-binary failed, trying with prefer-binary...
        python -m pip install --prefer-binary --no-cache-dir numpy==1.26.4 PyQt6==6.6.1 Pillow==10.2.0 opencv-python==4.9.0.80
    )
)
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo.
        echo Make sure Visual C++ Redistributables are installed:
        echo https://aka.ms/vs/17/release/vc_redist.x64.exe
        echo.
        pause
        exit /b 1
    )
)
echo.
echo All dependencies installed successfully!
echo.

REM Step 5: Install Real-ESRGAN
echo [5/5] Installing Real-ESRGAN (optional but recommended)...
if defined PYTHON_CMD (
    "%PYTHON_CMD%" -c "from install_realesrgan import install_realesrgan; install_realesrgan(lambda p, m: print(f'[{p}%%] {m}'))" 2>nul
) else (
    python -c "from install_realesrgan import install_realesrgan; install_realesrgan(lambda p, m: print(f'[{p}%%] {m}'))" 2>nul
)
if errorlevel 1 (
    echo WARNING: Real-ESRGAN installation failed or skipped.
    echo You can still use basic upscaling features.
) else (
    echo Real-ESRGAN installed successfully!
)
echo.

REM Verification
echo ========================================
echo Verification
echo ========================================
if defined PYTHON_CMD (
    "%PYTHON_CMD%" -c "import sys; print(f'Python: {sys.version}')"
    "%PYTHON_CMD%" -c "import numpy; print(f'NumPy: {numpy.__version__}')" 2>nul || echo NumPy: Not installed
    "%PYTHON_CMD%" -c "import PyQt6; print(f'PyQt6: {PyQt6.__version__}')" 2>nul || echo PyQt6: Not installed
    "%PYTHON_CMD%" -c "import PIL; print(f'Pillow: {PIL.__version__}')" 2>nul || echo Pillow: Not installed
    "%PYTHON_CMD%" -c "import cv2; print(f'OpenCV: {cv2.__version__}')" 2>nul || echo OpenCV: Not installed
    "%PYTHON_CMD%" -c "from image_enhancer import ImageEnhancer; e = ImageEnhancer(); print('Real-ESRGAN: Available' if e._realesrgan_available else 'Real-ESRGAN: Not available')" 2>nul || echo Real-ESRGAN: Check failed
) else (
    python -c "import sys; print(f'Python: {sys.version}')"
    python -c "import numpy; print(f'NumPy: {numpy.__version__}')" 2>nul || echo NumPy: Not installed
    python -c "import PyQt6; print(f'PyQt6: {PyQt6.__version__}')" 2>nul || echo PyQt6: Not installed
    python -c "import PIL; print(f'Pillow: {PIL.__version__}')" 2>nul || echo Pillow: Not installed
    python -c "import cv2; print(f'OpenCV: {cv2.__version__}')" 2>nul || echo OpenCV: Not installed
    python -c "from image_enhancer import ImageEnhancer; e = ImageEnhancer(); print('Real-ESRGAN: Available' if e._realesrgan_available else 'Real-ESRGAN: Not available')" 2>nul || echo Real-ESRGAN: Check failed
)
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run the application with:
echo   python main.py
echo.
echo Or double-click: run.bat
echo.
pause

