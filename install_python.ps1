# PowerShell script to install Python 3.12 and all dependencies
# Run: powershell -ExecutionPolicy Bypass -File install_python.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Rhancer - Complete Auto Installer" -ForegroundColor Cyan
Write-Host "Installs Python 3.12 + All Dependencies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "NOTE: Not running as Administrator. Some steps may require elevation." -ForegroundColor Yellow
    Write-Host ""
}

# Step 1: Check/Install Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Green
$pythonFound = $false
$pythonPath = $null

# Check if python is in PATH
try {
    $version = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python found: $version" -ForegroundColor Green
        $pythonFound = $true
        $pythonPath = "python"
    }
} catch {
    # Python not in PATH, check common locations
    $commonPaths = @(
        "C:\Program Files\Python312\python.exe",
        "C:\Program Files (x86)\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:ProgramFiles\Python312\python.exe"
    )
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            Write-Host "Python found at: $path" -ForegroundColor Green
            $pythonFound = $true
            $pythonPath = $path
            break
        }
    }
}

if (-not $pythonFound) {
    Write-Host "Python not found. Installing Python 3.12..." -ForegroundColor Yellow
    Write-Host ""
    
    # Create temp directory
    $tempDir = Join-Path $env:TEMP "rhancer_install"
    if (-not (Test-Path $tempDir)) {
        New-Item -ItemType Directory -Path $tempDir | Out-Null
    }
    
    $installerPath = Join-Path $tempDir "python-installer.exe"
    
    # Download Python 3.12
    Write-Host "Downloading Python 3.12 installer..." -ForegroundColor Yellow
    Write-Host "This may take a few minutes..." -ForegroundColor Yellow
    
    try {
        $url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $installerPath -UseBasicParsing
        
        Write-Host "Installing Python 3.12 (silent install)..." -ForegroundColor Yellow
        Write-Host "Please wait, this may take a minute..." -ForegroundColor Yellow
        
        # Install Python silently with PATH
        $process = Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0", "Include_launcher=1" -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Host "Python 3.12 installed successfully!" -ForegroundColor Green
            
            # Refresh PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            
            # Wait a moment for PATH to update
            Start-Sleep -Seconds 2
            
            # Try to find Python
            $commonPaths = @(
                "C:\Program Files\Python312\python.exe",
                "C:\Program Files (x86)\Python312\python.exe",
                "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
            )
            
            foreach ($path in $commonPaths) {
                if (Test-Path $path) {
                    $pythonPath = $path
                    Write-Host "Python found at: $path" -ForegroundColor Green
                    break
                }
            }
            
            # Try python command
            try {
                $version = & python --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $pythonPath = "python"
                    Write-Host "Python is now in PATH: $version" -ForegroundColor Green
                }
            } catch {
                Write-Host "Python installed but not in PATH yet." -ForegroundColor Yellow
                Write-Host "You may need to restart your terminal." -ForegroundColor Yellow
            }
        } else {
            Write-Host "Python installation may have failed. Exit code: $($process.ExitCode)" -ForegroundColor Red
            Write-Host "Please install Python manually from https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }
        
        # Clean up
        Remove-Item $installerPath -ErrorAction SilentlyContinue
        Remove-Item $tempDir -ErrorAction SilentlyContinue
        
    } catch {
        Write-Host "ERROR: Failed to download/install Python: $_" -ForegroundColor Red
        Write-Host "Please install Python manually from https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
}

if (-not $pythonPath) {
    Write-Host "ERROR: Could not find or install Python!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Install Visual C++ Redistributables
Write-Host "[2/5] Checking Visual C++ Redistributables..." -ForegroundColor Green
$vcRedistInstalled = $false

# Check registry
$regPath = "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"
if (Test-Path $regPath) {
    $vcRedistInstalled = $true
    Write-Host "Visual C++ Redistributables already installed." -ForegroundColor Green
} else {
    Write-Host "Visual C++ Redistributables not found. Installing..." -ForegroundColor Yellow
    
    $tempDir = Join-Path $env:TEMP "rhancer_install"
    if (-not (Test-Path $tempDir)) {
        New-Item -ItemType Directory -Path $tempDir | Out-Null
    }
    
    $vcRedistPath = Join-Path $tempDir "vc_redist.x64.exe"
    
    try {
        Write-Host "Downloading Visual C++ Redistributables..." -ForegroundColor Yellow
        $url = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $url -OutFile $vcRedistPath -UseBasicParsing
        
        Write-Host "Installing Visual C++ Redistributables..." -ForegroundColor Yellow
        $process = Start-Process -FilePath $vcRedistPath -ArgumentList "/quiet", "/norestart" -Wait -PassThru
        
        if ($process.ExitCode -eq 0 -or $process.ExitCode -eq 3010) {
            Write-Host "Visual C++ Redistributables installed successfully!" -ForegroundColor Green
            $vcRedistInstalled = $true
        } else {
            Write-Host "Visual C++ Redistributables installation may have failed." -ForegroundColor Yellow
            Write-Host "You can install manually from: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
        }
        
        Remove-Item $vcRedistPath -ErrorAction SilentlyContinue
        Remove-Item $tempDir -ErrorAction SilentlyContinue
        
    } catch {
        Write-Host "WARNING: Failed to download/install Visual C++ Redistributables: $_" -ForegroundColor Yellow
        Write-Host "You can install manually from: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 3: Upgrade pip
Write-Host "[3/5] Upgrading pip and build tools..." -ForegroundColor Green
try {
    if ($pythonPath -ne "python") {
        & $pythonPath -m pip install --upgrade pip setuptools wheel
    } else {
        python -m pip install --upgrade pip setuptools wheel
    }
    Write-Host "pip upgraded successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to upgrade pip: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Install Python dependencies
Write-Host "[4/5] Installing Python dependencies (stable versions)..." -ForegroundColor Green
Write-Host ""

$packages = @("numpy==1.26.4", "PyQt6==6.6.1", "Pillow==10.2.0", "opencv-python==4.9.0.80")
$packageString = $packages -join " "

try {
    if ($pythonPath -ne "python") {
        & $pythonPath -m pip install --only-binary :all: --no-cache-dir $packageString
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Trying with prefer-binary..." -ForegroundColor Yellow
            & $pythonPath -m pip install --prefer-binary --no-cache-dir $packageString
        }
    } else {
        python -m pip install --only-binary :all: --no-cache-dir $packageString
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Trying with prefer-binary..." -ForegroundColor Yellow
            python -m pip install --prefer-binary --no-cache-dir $packageString
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "All dependencies installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
        Write-Host "Make sure Visual C++ Redistributables are installed." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ERROR: Failed to install dependencies: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 5: Install Real-ESRGAN (optional)
Write-Host "[5/5] Installing Real-ESRGAN (optional but recommended)..." -ForegroundColor Green
try {
    if ($pythonPath -ne "python") {
        & $pythonPath -c "from install_realesrgan import install_realesrgan; install_realesrgan(lambda p, m: print(f'[{p}%] {m}'))" 2>$null
    } else {
        python -c "from install_realesrgan import install_realesrgan; install_realesrgan(lambda p, m: print(f'[{p}%] {m}'))" 2>$null
    }
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Real-ESRGAN installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Real-ESRGAN installation skipped or failed (optional)." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Real-ESRGAN installation skipped (optional)." -ForegroundColor Yellow
}

Write-Host ""

# Verification
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

try {
    if ($pythonPath -ne "python") {
        $pyVersion = & $pythonPath -c "import sys; print(f'Python {sys.version}')" 2>&1
        Write-Host $pyVersion -ForegroundColor Green
        
        $numpyVersion = & $pythonPath -c "import numpy; print(f'NumPy: {numpy.__version__}')" 2>&1
        Write-Host $numpyVersion -ForegroundColor Green
        
        $pyqt6Version = & $pythonPath -c "import PyQt6; print(f'PyQt6: {PyQt6.__version__}')" 2>&1
        Write-Host $pyqt6Version -ForegroundColor Green
        
        $pillowVersion = & $pythonPath -c "import PIL; print(f'Pillow: {PIL.__version__}')" 2>&1
        Write-Host $pillowVersion -ForegroundColor Green
        
        $opencvVersion = & $pythonPath -c "import cv2; print(f'OpenCV: {cv2.__version__}')" 2>&1
        Write-Host $opencvVersion -ForegroundColor Green
        
        $realesrgan = & $pythonPath -c "from image_enhancer import ImageEnhancer; e = ImageEnhancer(); print('Real-ESRGAN: Available' if e._realesrgan_available else 'Real-ESRGAN: Not available')" 2>&1
        Write-Host $realesrgan -ForegroundColor $(if ($realesrgan -like "*Available*") { "Green" } else { "Yellow" })
    } else {
        python -c "import sys; print(f'Python {sys.version}')"
        python -c "import numpy; print(f'NumPy: {numpy.__version__}')" 2>$null
        python -c "import PyQt6; print(f'PyQt6: {PyQt6.__version__}')" 2>$null
        python -c "import PIL; print(f'Pillow: {PIL.__version__}')" 2>$null
        python -c "import cv2; print(f'OpenCV: {cv2.__version__}')" 2>$null
        python -c "from image_enhancer import ImageEnhancer; e = ImageEnhancer(); print('Real-ESRGAN: Available' if e._realesrgan_available else 'Real-ESRGAN: Not available')" 2>$null
    }
} catch {
    Write-Host "Some verification checks failed, but installation may still be successful." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now run the application with:" -ForegroundColor Green
if ($pythonPath -ne "python") {
    Write-Host "  $pythonPath main.py" -ForegroundColor White
} else {
    Write-Host "  python main.py" -ForegroundColor White
}
Write-Host ""
Write-Host "Or double-click: run.bat" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

