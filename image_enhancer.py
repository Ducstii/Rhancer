"""
Image enhancement engine with various algorithms for improving picture quality.
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Tuple, Optional
import subprocess
import shutil
import tempfile
import os
from pathlib import Path


class ImageEnhancer:
    """Handles image enhancement operations."""
    
    def __init__(self):
        self.original_image: Optional[np.ndarray] = None
        self.current_image: Optional[np.ndarray] = None
        self._realesrgan_available = self._check_realesrgan()
        self._max_image_size = 50_000_000  # 50MP limit (roughly 8000x6000)
    
    def _check_realesrgan(self) -> bool:
        """Check if realesrgan-ncnn-vulkan is available in PATH or local bin."""
        import platform
        system = platform.system().lower()
        binary_name = "realesrgan-ncnn-vulkan.exe" if system == "windows" else "realesrgan-ncnn-vulkan"
        
        # Check PATH first
        if shutil.which(binary_name) is not None or shutil.which("realesrgan-ncnn-vulkan") is not None:
            return True
        
        # Check local bin directory
        local_bin = Path(__file__).parent / "bin" / binary_name
        if local_bin.exists():
            # On Windows, just check existence. On Unix, check if executable
            if system == "windows" or os.access(local_bin, os.X_OK):
                return True
        
        return False
    
    def _get_realesrgan_path(self) -> str:
        """Get the path to realesrgan-ncnn-vulkan binary."""
        import platform
        system = platform.system().lower()
        binary_name = "realesrgan-ncnn-vulkan.exe" if system == "windows" else "realesrgan-ncnn-vulkan"
        
        # Check PATH first
        path_bin = shutil.which(binary_name) or shutil.which("realesrgan-ncnn-vulkan")
        if path_bin:
            return path_bin
        
        # Check local bin directory
        local_bin = Path(__file__).parent / "bin" / binary_name
        if local_bin.exists():
            if system == "windows" or os.access(local_bin, os.X_OK):
                return str(local_bin)
        
        return binary_name  # Fallback to PATH (will fail if not found)
    
    def _validate_image_size(self, image: np.ndarray) -> Tuple[bool, str]:
        """Validate image size to prevent memory issues.
        
        Returns:
            (is_valid, error_message)
        """
        if image is None:
            return False, "No image loaded"
        
        height, width = image.shape[:2]
        pixel_count = height * width
        
        if pixel_count > self._max_image_size:
            return False, f"Image too large ({width}x{height}). Maximum size: ~8000x6000 pixels"
        
        # Warn for very large images (> 10MP)
        if pixel_count > 10_000_000:
            return True, f"Warning: Large image ({width}x{height}), processing may be slow"
        
        return True, ""
    
    def load_image(self, image_path: str) -> bool:
        """Load an image from file path."""
        try:
            if not os.path.exists(image_path):
                return False
            
            if not os.access(image_path, os.R_OK):
                return False
            
            self.original_image = cv2.imread(image_path)
            if self.original_image is None:
                return False
            
            # Validate size
            is_valid, error_msg = self._validate_image_size(self.original_image)
            if not is_valid:
                return False
            
            # Convert BGR to RGB for display
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.current_image = self.original_image.copy()
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def reset(self):
        """Reset to original image."""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
    
    def get_image(self) -> Optional[np.ndarray]:
        """Get current processed image."""
        return self.current_image
    
    def sharpen(self, strength: float = 1.0):
        """Apply sharpening filter.
        
        Args:
            strength: Sharpening strength (0.0 to 2.0)
        """
        if self.current_image is None:
            return
        
        try:
            # Create sharpening kernel
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]]) * strength
            
            # Apply convolution
            self.current_image = cv2.filter2D(self.current_image, -1, kernel)
            self.current_image = np.clip(self.current_image, 0, 255).astype(np.uint8)
        except Exception as e:
            print(f"Error in sharpening: {e}")
    
    def denoise(self, strength: float = 1.0):
        """Apply noise reduction using faster bilateral filter.
        
        Args:
            strength: Denoising strength (0.0 to 1.0)
        """
        if self.current_image is None:
            return
        
        try:
            # Use bilateral filter for edge-preserving denoising (much faster)
            # Map strength (0-1) to d parameter (5-15)
            d = int(5 + strength * 10)
            sigma_color = 50 + strength * 50
            sigma_space = 50 + strength * 50
            
            self.current_image = cv2.bilateralFilter(
                self.current_image,
                d,
                sigma_color,
                sigma_space
            )
        except Exception as e:
            print(f"Error in denoising: {e}")
    
    def upscale(self, scale_factor: int = 2):
        """Upscale image using interpolation.
        
        Args:
            scale_factor: Upscaling factor (2 or 4)
        """
        if self.current_image is None:
            return
        
        height, width = self.current_image.shape[:2]
        new_width = width * scale_factor
        new_height = height * scale_factor
        
        # Use Lanczos interpolation for better quality
        self.current_image = cv2.resize(
            self.current_image,
            (new_width, new_height),
            interpolation=cv2.INTER_LANCZOS4
        )
    
    def super_resolution_realesrgan(self, scale_factor: int = 2, progress_callback=None) -> bool:
        """Apply Real-ESRGAN super-resolution via command-line tool.
        
        Args:
            scale_factor: Upscaling factor (2, 3, or 4)
            progress_callback: Optional callback function(progress_percent, message)
        
        Returns:
            True if successful, False otherwise
        """
        if self.current_image is None:
            return False
        
        if not self._realesrgan_available:
            return False
        
        try:
            # Validate size before processing
            is_valid, error_msg = self._validate_image_size(self.current_image)
            if not is_valid:
                return False
            
            # Save current image to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_input:
                input_path = tmp_input.name
                # Convert RGB to BGR for saving
                bgr_image = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(input_path, bgr_image)
            
            # Create output temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_output:
                output_path = tmp_output.name
            
            try:
                if progress_callback:
                    progress_callback(10, "Starting Real-ESRGAN processing...")
                
                # Get the binary path
                realesrgan_bin = self._get_realesrgan_path()
                
                # For 4x, we need to do 2x twice
                if scale_factor == 4:
                    # First 2x upscale
                    intermediate_path = output_path.replace('.png', '_intermediate.png')
                    cmd1 = [
                        realesrgan_bin,
                        "-i", input_path,
                        "-o", intermediate_path,
                        "-s", "2",
                        "-f", "png"
                    ]
                    
                    if progress_callback:
                        progress_callback(30, "First 2x upscale...")
                    
                    result1 = subprocess.run(
                        cmd1,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result1.returncode != 0:
                        raise Exception(f"Real-ESRGAN error: {result1.stderr}")
                    
                    # Second 2x upscale
                    if progress_callback:
                        progress_callback(70, "Second 2x upscale...")
                    
                    cmd2 = [
                        realesrgan_bin,
                        "-i", intermediate_path,
                        "-o", output_path,
                        "-s", "2",
                        "-f", "png"
                    ]
                    
                    result2 = subprocess.run(
                        cmd2,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result2.returncode != 0:
                        raise Exception(f"Real-ESRGAN error: {result2.stderr}")
                    
                    # Clean up intermediate file
                    if os.path.exists(intermediate_path):
                        os.unlink(intermediate_path)
                else:
                    # Single upscale (2x or 3x)
                    cmd = [
                        realesrgan_bin,
                        "-i", input_path,
                        "-o", output_path,
                        "-s", str(scale_factor),
                        "-f", "png"
                    ]
                    
                    if progress_callback:
                        progress_callback(50, f"Upscaling {scale_factor}x...")
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode != 0:
                        raise Exception(f"Real-ESRGAN error: {result.stderr}")
                
                if progress_callback:
                    progress_callback(90, "Loading enhanced image...")
                
                # Load the enhanced image
                enhanced = cv2.imread(output_path)
                if enhanced is None:
                    raise Exception("Failed to load enhanced image")
                
                # Convert BGR to RGB
                self.current_image = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
                
                if progress_callback:
                    progress_callback(100, "Complete!")
                
                return True
                
            finally:
                # Clean up temporary files
                if os.path.exists(input_path):
                    os.unlink(input_path)
                if os.path.exists(output_path):
                    os.unlink(output_path)
                    
        except subprocess.TimeoutExpired:
            print("Real-ESRGAN processing timed out")
            return False
        except Exception as e:
            print(f"Error in Real-ESRGAN processing: {e}")
            return False
    
    def super_resolution(self, scale_factor: int = 2, strength: float = 1.0, progress_callback=None) -> bool:
        """Apply AI-based super-resolution enhancement.
        
        Tries Real-ESRGAN first, falls back to filter-based approach if unavailable.
        
        Args:
            scale_factor: Upscaling factor (2 or 4)
            strength: Enhancement strength (0.0 to 1.0) - only used for fallback
            progress_callback: Optional callback for progress updates
        
        Returns:
            True if successful, False otherwise
        """
        if self.current_image is None:
            return False
        
        # Try Real-ESRGAN first
        if self._realesrgan_available:
            return self.super_resolution_realesrgan(scale_factor, progress_callback)
        
        # Fallback to filter-based approach (removed slow denoising)
        try:
            height, width = self.current_image.shape[:2]
            new_width = width * scale_factor
            new_height = height * scale_factor
            
            # Use Lanczos interpolation for better quality
            upscaled = cv2.resize(
                self.current_image,
                (new_width, new_height),
                interpolation=cv2.INTER_LANCZOS4
            )
            
            # Apply edge-preserving filter
            upscaled = cv2.edgePreservingFilter(upscaled, flags=2, sigma_s=50, sigma_r=0.4)
            
            # Unsharp masking for detail enhancement
            blurred = cv2.GaussianBlur(upscaled, (0, 0), 2.0)
            unsharp_mask = cv2.addWeighted(upscaled, 1.0 + (strength * 0.5), blurred, -(strength * 0.5), 0)
            
            # Apply CLAHE for local contrast
            lab = cv2.cvtColor(unsharp_mask, cv2.COLOR_RGB2LAB)
            l_channel, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l_channel = clahe.apply(l_channel)
            lab = cv2.merge([l_channel, a, b])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            # Final sharpening
            kernel = np.array([[-0.5, -0.5, -0.5],
                              [-0.5,  5.0, -0.5],
                              [-0.5, -0.5, -0.5]]) * (0.3 + strength * 0.4)
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
            
            self.current_image = enhanced
            return True
            
        except Exception as e:
            print(f"Error in super-resolution: {e}")
            return False
    
    def enhance_details(self, strength: float = 1.0):
        """Enhance fine details in the image.
        
        Args:
            strength: Detail enhancement strength (0.0 to 1.0)
        """
        if self.current_image is None:
            return
        
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2LAB)
            l_channel, a, b = cv2.split(lab)
            
            # Apply unsharp masking to L channel
            blurred = cv2.GaussianBlur(l_channel, (0, 0), 1.5)
            sharpened = cv2.addWeighted(
                l_channel,
                1.0 + (strength * 0.8),
                blurred,
                -(strength * 0.8),
                0
            )
            sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
            
            # Apply CLAHE for local contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0 + strength, tileGridSize=(8, 8))
            enhanced_l = clahe.apply(sharpened)
            
            # Merge back
            lab = cv2.merge([enhanced_l, a, b])
            self.current_image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        except Exception as e:
            print(f"Error in detail enhancement: {e}")
    
    def adjust_contrast(self, factor: float):
        """Adjust image contrast.
        
        Args:
            factor: Contrast factor (0.5 to 2.0)
        """
        if self.current_image is None:
            return
        
        try:
            # Convert to PIL for easy enhancement
            pil_image = Image.fromarray(self.current_image)
            enhancer = ImageEnhance.Contrast(pil_image)
            enhanced = enhancer.enhance(factor)
            self.current_image = np.array(enhanced)
        except Exception as e:
            print(f"Error adjusting contrast: {e}")
    
    def adjust_brightness(self, factor: float):
        """Adjust image brightness.
        
        Args:
            factor: Brightness factor (0.5 to 2.0)
        """
        if self.current_image is None:
            return
        
        try:
            pil_image = Image.fromarray(self.current_image)
            enhancer = ImageEnhance.Brightness(pil_image)
            enhanced = enhancer.enhance(factor)
            self.current_image = np.array(enhanced)
        except Exception as e:
            print(f"Error adjusting brightness: {e}")
    
    def adjust_saturation(self, factor: float):
        """Adjust image saturation.
        
        Args:
            factor: Saturation factor (0.0 to 2.0)
        """
        if self.current_image is None:
            return
        
        try:
            pil_image = Image.fromarray(self.current_image)
            enhancer = ImageEnhance.Color(pil_image)
            enhanced = enhancer.enhance(factor)
            self.current_image = np.array(enhanced)
        except Exception as e:
            print(f"Error adjusting saturation: {e}")
    
    def save_image(self, file_path: str) -> bool:
        """Save current image to file.
        
        Args:
            file_path: Path to save the image
        """
        if self.current_image is None:
            return False
        
        try:
            # Check if directory exists and is writable
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            if dir_path and not os.access(dir_path, os.W_OK):
                return False
            
            # Convert RGB back to BGR for OpenCV
            bgr_image = cv2.cvtColor(self.current_image, cv2.COLOR_RGB2BGR)
            success = cv2.imwrite(file_path, bgr_image)
            return success
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

