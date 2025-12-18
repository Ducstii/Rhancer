# Windows Installation Guide

## Quick Start

1. **Double-click `install.bat`** - This will install everything automatically!

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

Open Command Prompt in the project folder and run:

```batch
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
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

