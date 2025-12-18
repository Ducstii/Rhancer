# Windows Installation Guide

## Quick Start

1. **Double-click `INSTALL.bat`** - This is the main installer!
   - Automatically installs Python 3.12 if needed
   - Installs Visual C++ Redistributables
   - Installs all dependencies
   - Installs Real-ESRGAN (optional)
   - **No manual steps required - just run it!**

**Other Options** (if main installer doesn't work):
- `install_simple.bat` - Simple installer (assumes Python is already installed)
- `run.bat` - Quick launcher for the application

## Manual Installation

### Step 1: Install Python

**IMPORTANT**: Use Python 3.8-3.12 for best compatibility!

1. Download Python 3.12 (recommended) from https://www.python.org/downloads/release/python-3120/
   - Or Python 3.8-3.11 from https://www.python.org/downloads/
2. **IMPORTANT**: During installation, check "Add Python to PATH"
3. Verify installation: Open Command Prompt and type `python --version`

**Why not Python 3.13+?**
- Python 3.13 and 3.14 are very new
- Many packages don't have pre-built wheels yet
- You'll need Visual Studio Build Tools (not just Redistributables) to compile from source
- Python 3.12 has full wheel support and is recommended

### Step 2: Install Visual C++ Redistributables

**Required for NumPy, OpenCV, and PyQt6 to run!**

Download and install:
- **Microsoft Visual C++ 2015-2022 Redistributable (x64)**
  - Direct link: https://aka.ms/vs/17/release/vc_redist.x64.exe
  - Or search for "Visual C++ Redistributable" on Microsoft's website

This is a runtime library - you don't need Visual Studio or build tools, just the redistributables.

**Note**: If you're using Python 3.13 or 3.14, you may also need Visual Studio Build Tools (see troubleshooting section).

### Step 3: Install Dependencies

**Option A: Simple Installer (If Python is already installed)**
Double-click `install_simple.bat`

**Option B: Manual Install - Single Command**
Open Command Prompt in the project folder and run:

```batch
python -m pip install --upgrade pip
python -m pip install numpy==1.26.4 PyQt6==6.6.1 Pillow==10.2.0 opencv-python==4.9.0.80
```

**Option C: Manual Install - One at a Time**
```batch
python -m pip install --upgrade pip
python -m pip install numpy==1.26.4
python -m pip install PyQt6==6.6.1
python -m pip install Pillow==10.2.0
python -m pip install opencv-python==4.9.0.80
```

### Step 4: Install Real-ESRGAN (Optional)

The application will offer to install Real-ESRGAN automatically on first run, or you can run:

```batch
python -c "from install_realesrgan import install_realesrgan; install_realesrgan(lambda p, m: print(f'[{p}%] {m}'))"
```

## Troubleshooting

### "Failed to install NumPy" or "Unknown compiler"

**If using Python 3.8-3.12:**
- Install Visual C++ Redistributables (see Step 2 above)
- Pre-built wheels should be available

**If using Python 3.13 or 3.14:**
- You need **Visual Studio Build Tools** (not just Redistributables)
- Download: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
- Run installer and select "C++ build tools" workload
- This includes the C++ compiler needed to build packages from source
- **OR** use Python 3.12 instead (recommended - has pre-built wheels)

### "Python is not recognized"

**Solution**: 
1. Reinstall Python and make sure to check "Add Python to PATH"
2. Or manually add Python to PATH:
   - Find Python installation (usually `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\`)
   - Add to System PATH in Environment Variables

### "Failed to install OpenCV"

**Solution**: 
1. Make sure Visual C++ Redistributables are installed
2. Try: `python -m pip install --upgrade pip` then retry
3. Try: `python -m pip install opencv-python-headless` (lighter version)

### Application won't start

**Solution**:
1. Check all dependencies are installed: `python -m pip list`
2. Make sure Visual C++ Redistributables are installed
3. Try running from command line: `python main.py` to see error messages

## What You Need

- **Python 3.8+** - Programming language runtime
- **Visual C++ Redistributables** - Runtime libraries for compiled packages
- **Internet connection** - To download packages

**You do NOT need:**
- Visual Studio
- C++ compiler
- Build tools
- Any development software

All packages are installed as pre-built wheels - no compilation required!

