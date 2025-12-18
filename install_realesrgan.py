"""
Auto-installer for Real-ESRGAN (realesrgan-ncnn-vulkan).
Downloads and installs the binary to a local bin directory.
"""

import os
import sys
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, Callable


def get_realesrgan_url() -> Optional[str]:
    """Get the download URL for Real-ESRGAN based on the system."""
    # Real-ESRGAN ncnn-vulkan releases
    base_url = "https://github.com/xinntao/Real-ESRGAN/releases/download"
    
    import platform
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # Latest version
    version = "v0.2.5.0"
    
    # Windows
    if system == "windows":
        if machine in ('x86_64', 'amd64'):
            return f"{base_url}/{version}/realesrgan-ncnn-vulkan-{version}-windows.zip"
        elif machine in ('x86', 'i386', 'i686'):
            return f"{base_url}/{version}/realesrgan-ncnn-vulkan-{version}-windows-x86.zip"
    
    # Linux
    elif system == "linux":
        if machine in ('x86_64', 'amd64'):
            return f"{base_url}/{version}/realesrgan-ncnn-vulkan-20220424-ubuntu.zip"
    
    # macOS
    elif system == "darwin":
        if machine in ('x86_64', 'amd64'):
            return f"{base_url}/{version}/realesrgan-ncnn-vulkan-{version}-macos.zip"
        elif machine == "arm64":
            return f"{base_url}/{version}/realesrgan-ncnn-vulkan-{version}-macos-arm64.zip"
    
    # For other architectures, return None (user needs manual install)
    return None


def download_file(url: str, dest_path: Path, progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
    """Download a file with progress reporting."""
    try:
        if progress_callback:
            progress_callback(0, f"Downloading from {url}...")
        
        def report_progress(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, int((block_num * block_size * 100) / total_size))
                if progress_callback:
                    progress_callback(percent, f"Downloading... {percent}%")
        
        urllib.request.urlretrieve(url, dest_path, report_progress)
        
        if progress_callback:
            progress_callback(100, "Download complete")
        
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False


def extract_archive(archive_path: Path, extract_to: Path, progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
    """Extract zip or tar archive."""
    try:
        if progress_callback:
            progress_callback(0, "Extracting archive...")
        
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_path.suffix in ('.tar', '.gz', '.bz2', '.xz'):
            mode = 'r'
            if archive_path.suffix == '.gz':
                mode = 'r:gz'
            elif archive_path.suffix == '.bz2':
                mode = 'r:bz2'
            elif archive_path.suffix == '.xz':
                mode = 'r:xz'
            
            with tarfile.open(archive_path, mode) as tar_ref:
                tar_ref.extractall(extract_to)
        else:
            return False
        
        if progress_callback:
            progress_callback(100, "Extraction complete")
        
        return True
    except Exception as e:
        print(f"Extraction error: {e}")
        return False


def find_realesrgan_binary(extract_dir: Path) -> Optional[Path]:
    """Find the realesrgan-ncnn-vulkan binary in extracted directory."""
    import platform
    system = platform.system().lower()
    
    # Windows uses .exe extension
    if system == "windows":
        binary_name = "realesrgan-ncnn-vulkan.exe"
    else:
        binary_name = "realesrgan-ncnn-vulkan"
    
    # Walk through the extracted directory to find the binary
    for root, dirs, files in os.walk(extract_dir):
        for name in files:
            # Look for the binary (exact name or starts with it)
            if name == binary_name or (name.startswith("realesrgan-ncnn-vulkan") and 
                                      not name.endswith('.zip') and 
                                      not name.endswith('.tar.gz') and
                                      not name.endswith('.tar')):
                binary_path = Path(root) / name
                # Check if it's a file (not a directory)
                if binary_path.is_file():
                    return binary_path
    
    # Try common direct paths
    possible_paths = [
        extract_dir / binary_name,
        extract_dir / "realesrgan-ncnn-vulkan" / binary_name,
        extract_dir / "realesrgan-ncnn-vulkan-20220424-ubuntu" / binary_name,
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_file():
            return path
    
    return None


def install_realesrgan(progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
    """Download and install Real-ESRGAN to local bin directory.
    
    Args:
        progress_callback: Optional callback(percent, message) for progress updates
    
    Returns:
        True if installation successful, False otherwise
    """
    try:
        # Get project directory
        project_dir = Path(__file__).parent
        bin_dir = project_dir / "bin"
        bin_dir.mkdir(exist_ok=True)
        
        # Check if already installed
        import platform
        system = platform.system().lower()
        binary_name = "realesrgan-ncnn-vulkan.exe" if system == "windows" else "realesrgan-ncnn-vulkan"
        binary_path = bin_dir / binary_name
        
        # On Windows, just check if file exists. On Unix, check if executable
        if binary_path.exists():
            if system != "windows":
                if os.access(binary_path, os.X_OK):
                    if progress_callback:
                        progress_callback(100, "Already installed")
                    return True
            else:
                if progress_callback:
                    progress_callback(100, "Already installed")
                return True
        
        # Get download URL
        url = get_realesrgan_url()
        if not url:
            if progress_callback:
                progress_callback(0, "Unsupported architecture - manual install required")
            return False
        
        # Download to temp file
        if progress_callback:
            progress_callback(10, "Preparing download...")
        
        temp_dir = project_dir / ".temp_install"
        temp_dir.mkdir(exist_ok=True)
        archive_path = temp_dir / "realesrgan.zip"
        
        # Download
        if not download_file(url, archive_path, progress_callback):
            return False
        
        # Extract
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        if not extract_archive(archive_path, extract_dir, progress_callback):
            return False
        
        # Find binary
        if progress_callback:
            progress_callback(90, "Locating binary...")
        
        found_binary = find_realesrgan_binary(extract_dir)
        if not found_binary:
            if progress_callback:
                progress_callback(0, "Binary not found in archive")
            return False
        
        # Copy to bin directory
        if progress_callback:
            progress_callback(95, "Installing binary...")
        
        # Determine correct binary name for target platform
        import platform
        system = platform.system().lower()
        target_binary_name = "realesrgan-ncnn-vulkan.exe" if system == "windows" else "realesrgan-ncnn-vulkan"
        binary_path = bin_dir / target_binary_name
        
        shutil.copy2(found_binary, binary_path)
        
        # Make executable (Unix only)
        if system != "windows":
            os.chmod(binary_path, 0o755)
        
        # Clean up
        if progress_callback:
            progress_callback(98, "Cleaning up...")
        
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        if progress_callback:
            progress_callback(100, "Installation complete!")
        
        return True
        
    except Exception as e:
        print(f"Installation error: {e}")
        if progress_callback:
            progress_callback(0, f"Error: {str(e)}")
        return False


if __name__ == "__main__":
    # Test installation
    def test_progress(percent, message):
        print(f"[{percent}%] {message}")
    
    print("Testing Real-ESRGAN installation...")
    success = install_realesrgan(test_progress)
    if success:
        print("Installation successful!")
    else:
        print("Installation failed!")

