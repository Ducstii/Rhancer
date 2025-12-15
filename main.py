#!/usr/bin/env python3
"""
Rhancer - Image Enhancer Application for Linux
Main application entry point with GUI.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFileDialog, QMessageBox, QGroupBox,
    QScrollArea, QSizePolicy, QProgressDialog
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal as Signal, QTimer
from PyQt6.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent
import numpy as np
import cv2

from image_enhancer import ImageEnhancer

# Try to import installer
try:
    from install_realesrgan import install_realesrgan
    INSTALLER_AVAILABLE = True
except ImportError:
    INSTALLER_AVAILABLE = False


class EnhancementWorker(QThread):
    """Worker thread for image processing to prevent UI freezing."""
    
    progress = Signal(int, str)  # progress_percent, message
    finished = Signal(bool, str)  # success, error_message
    image_ready = Signal()  # signal that image is ready
    
    def __init__(self, enhancer, operation, *args, **kwargs):
        super().__init__()
        self.enhancer = enhancer
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self._cancelled = False
    
    def cancel(self):
        """Cancel the processing operation."""
        self._cancelled = True
    
    def run(self):
        """Execute the enhancement operation in background thread."""
        try:
            if self.operation == "super_resolution":
                scale_factor = self.args[0]
                strength = self.kwargs.get('strength', 1.0)
                
                def progress_callback(percent, message):
                    if not self._cancelled:
                        self.progress.emit(percent, message)
                
                success = self.enhancer.super_resolution(
                    scale_factor,
                    strength,
                    progress_callback
                )
                
                if self._cancelled:
                    self.finished.emit(False, "Cancelled")
                    return
                
                if success:
                    self.image_ready.emit()
                    self.finished.emit(True, "")
                else:
                    self.finished.emit(False, "Super-resolution processing failed")
            
            elif self.operation == "enhancements":
                # Apply all enhancements
                self.progress.emit(10, "Applying enhancements...")
                
                if self._cancelled:
                    return
                
                sharpen_val = self.args[0]
                if sharpen_val > 0:
                    self.enhancer.sharpen(sharpen_val)
                
                if self._cancelled:
                    return
                
                self.progress.emit(30, "Denoising...")
                denoise_val = self.args[1]
                if denoise_val > 0:
                    self.enhancer.denoise(denoise_val)
                
                if self._cancelled:
                    return
                
                self.progress.emit(50, "Adjusting colors...")
                contrast_val = self.args[2]
                if contrast_val != 1.0:
                    self.enhancer.adjust_contrast(contrast_val)
                
                brightness_val = self.args[3]
                if brightness_val != 1.0:
                    self.enhancer.adjust_brightness(brightness_val)
                
                saturation_val = self.args[4]
                if saturation_val != 1.0:
                    self.enhancer.adjust_saturation(saturation_val)
                
                if self._cancelled:
                    return
                
                self.progress.emit(80, "Enhancing details...")
                detail_val = self.args[5]
                if detail_val > 0:
                    self.enhancer.enhance_details(detail_val)
                
                if self._cancelled:
                    self.finished.emit(False, "Cancelled")
                    return
                
                self.progress.emit(100, "Complete!")
                self.image_ready.emit()
                self.finished.emit(True, "")
            
            elif self.operation == "upscale":
                scale_factor = self.args[0]
                self.progress.emit(50, f"Upscaling {scale_factor}x...")
                self.enhancer.upscale(scale_factor)
                
                if self._cancelled:
                    self.finished.emit(False, "Cancelled")
                    return
                
                self.progress.emit(100, "Complete!")
                self.image_ready.emit()
                self.finished.emit(True, "")
                
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class ImageLabel(QLabel):
    """Custom label that supports drag and drop."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Drag and drop an image here\nor click 'Load Image'")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 10px;
                background-color: #f5f5f5;
                padding: 20px;
                color: #666;
            }
        """)
        self.setMinimumHeight(300)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            self.parent().load_image_file(files[0])


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.enhancer = ImageEnhancer()
        self.current_image_path = None
        self.worker = None
        self.progress_dialog = None
        self.enhance_timer = QTimer()
        self.enhance_timer.setSingleShot(True)
        self.enhance_timer.timeout.connect(self._apply_enhancements_debounced)
        self.init_ui()
        self._check_and_install_realesrgan()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Rhancer - Image Enhancer")
        self.setMinimumSize(1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Image display
        left_panel = QVBoxLayout()
        
        # Image display area
        self.image_label = ImageLabel(self)
        left_panel.addWidget(self.image_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)
        self.save_btn = QPushButton("Save Enhanced Image")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_image)
        self.reset_btn.setEnabled(False)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.save_btn)
        left_panel.addLayout(button_layout)
        
        # Right panel - Controls
        right_panel = QVBoxLayout()
        
        # Scroll area for controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        controls_layout.addWidget(self.status_label)
        
        # Enhancement controls
        self.create_control_group(
            controls_layout, "Sharpening", "sharpen", 0, 200, 0, self._on_slider_changed
        )
        self.create_control_group(
            controls_layout, "Denoising", "denoise", 0, 100, 0, self._on_slider_changed
        )
        self.create_control_group(
            controls_layout, "Contrast", "contrast", 50, 200, 100, self._on_slider_changed
        )
        self.create_control_group(
            controls_layout, "Brightness", "brightness", 50, 200, 100, self._on_slider_changed
        )
        self.create_control_group(
            controls_layout, "Saturation", "saturation", 0, 200, 100, self._on_slider_changed
        )
        
        # Super Resolution
        super_res_group = QGroupBox("Super Resolution (AI Enhancement)")
        super_res_layout = QVBoxLayout()
        
        self.super_res_2x_btn = QPushButton("2x Super Resolution")
        self.super_res_2x_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.super_res_2x_btn.clicked.connect(lambda: self.apply_super_resolution(2))
        
        self.super_res_4x_btn = QPushButton("4x Super Resolution")
        self.super_res_4x_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.super_res_4x_btn.clicked.connect(lambda: self.apply_super_resolution(4))
        
        self.create_control_group(
            super_res_layout, "Enhancement Strength", "super_res_strength", 
            50, 100, 100, None
        )
        
        super_res_layout.addWidget(self.super_res_2x_btn)
        super_res_layout.addWidget(self.super_res_4x_btn)
        super_res_group.setLayout(super_res_layout)
        controls_layout.addWidget(super_res_group)
        
        # Detail Enhancement
        self.create_control_group(
            controls_layout, "Detail Enhancement", "detail_enhance", 
            0, 100, 0, self._on_slider_changed
        )
        
        # Basic Upscaling (for comparison)
        upscale_group = QGroupBox("Basic Upscaling (Simple)")
        upscale_layout = QVBoxLayout()
        self.upscale_2x_btn = QPushButton("2x Basic Upscale")
        self.upscale_2x_btn.clicked.connect(lambda: self.apply_upscale(2))
        self.upscale_4x_btn = QPushButton("4x Basic Upscale")
        self.upscale_4x_btn.clicked.connect(lambda: self.apply_upscale(4))
        upscale_layout.addWidget(self.upscale_2x_btn)
        upscale_layout.addWidget(self.upscale_4x_btn)
        upscale_group.setLayout(upscale_layout)
        controls_layout.addWidget(upscale_group)
        
        controls_layout.addStretch()
        
        scroll.setWidget(controls_widget)
        right_panel.addWidget(scroll)
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)
        
        # Apply styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #ddd;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #45a049;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
    
    def create_control_group(self, parent_layout, title, name, min_val, max_val, default, callback):
        """Create a control group with slider."""
        group = QGroupBox(title)
        layout = QVBoxLayout()
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default)
        if callback is not None:
            slider.valueChanged.connect(callback)
        setattr(self, f"{name}_slider", slider)
        
        value_label = QLabel(f"{default}")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setattr(self, f"{name}_label", value_label)
        
        slider.valueChanged.connect(
            lambda v: value_label.setText(f"{v}")
        )
        
        layout.addWidget(slider)
        layout.addWidget(value_label)
        group.setLayout(layout)
        parent_layout.addWidget(group)
    
    def load_image_file(self, file_path: str):
        """Load image from file path."""
        try:
            if self.enhancer.load_image(file_path):
                self.current_image_path = file_path
                self.save_btn.setEnabled(True)
                self.reset_btn.setEnabled(True)
                self.status_label.setText("Image loaded")
                self.display_image()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to load image.\n\nPossible reasons:\n"
                    "- File format not supported\n"
                    "- File is corrupted\n"
                    "- File is too large (>8000x6000)\n"
                    "- Insufficient permissions"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Unexpected error loading image:\n{str(e)}"
            )
    
    def load_image(self):
        """Open file dialog to load image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
        )
        if file_path:
            self.load_image_file(file_path)
    
    def _check_and_install_realesrgan(self):
        """Check for Real-ESRGAN and offer auto-install on startup."""
        if self.enhancer._realesrgan_available:
            return  # Already installed
        
        if not INSTALLER_AVAILABLE:
            return  # Installer not available
        
        # Offer to install automatically
        reply = QMessageBox.question(
            self,
            "Install Real-ESRGAN?",
            "Real-ESRGAN is not installed.\n\n"
            "Real-ESRGAN provides AI-powered super-resolution with much better quality.\n\n"
            "Would you like to install it automatically now?\n"
            "(This will download ~45MB)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._install_realesrgan()
    
    def _offer_auto_install(self):
        """Offer to install Real-ESRGAN when user tries to use super-resolution."""
        if not INSTALLER_AVAILABLE:
            return
        
        reply = QMessageBox.question(
            self,
            "Install Real-ESRGAN?",
            "Real-ESRGAN is not installed.\n\n"
            "For best quality AI-powered super-resolution, install Real-ESRGAN now?\n"
            "(This will download ~45MB)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._install_realesrgan()
    
    def _install_realesrgan(self):
        """Install Real-ESRGAN with progress dialog."""
        if not INSTALLER_AVAILABLE:
            QMessageBox.warning(
                self,
                "Installer Unavailable",
                "Auto-installer is not available. Please install manually."
            )
            return
        
        # Show progress dialog
        progress = QProgressDialog("Installing Real-ESRGAN...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setCancelButton(None)  # Can't cancel download easily
        progress.show()
        QApplication.processEvents()
        
        def progress_callback(percent, message):
            progress.setValue(percent)
            progress.setLabelText(message)
            QApplication.processEvents()
        
        try:
            success = install_realesrgan(progress_callback=progress_callback)
            
            if success:
                # Re-initialize enhancer to detect new installation
                self.enhancer = ImageEnhancer()
                QMessageBox.information(
                    self,
                    "Installation Complete",
                    "Real-ESRGAN has been installed successfully!\n\n"
                    "You can now use AI-powered super-resolution for best quality."
                )
                self.status_label.setText("Real-ESRGAN installed and ready")
            else:
                QMessageBox.warning(
                    self,
                    "Installation Failed",
                    "Failed to install Real-ESRGAN automatically.\n\n"
                    "You can try installing manually or use basic upscaling."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Installation Error",
                f"Error during installation:\n{str(e)}"
            )
        finally:
            progress.close()
    
    def reset_image(self):
        """Reset image to original."""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Processing", "Please wait for current operation to complete.")
            return
        
        self.enhancer.reset()
        # Reset sliders to default
        self.sharpen_slider.setValue(0)
        self.denoise_slider.setValue(0)
        self.contrast_slider.setValue(100)
        self.brightness_slider.setValue(100)
        self.saturation_slider.setValue(100)
        self.detail_enhance_slider.setValue(0)
        self.super_res_strength_slider.setValue(100)
        self.status_label.setText("Reset to original")
        self.display_image()
    
    def _on_slider_changed(self):
        """Handle slider changes with debouncing."""
        if self.enhancer.original_image is None:
            return
        
        # Debounce: wait 300ms before processing
        self.enhance_timer.stop()
        self.enhance_timer.start(300)
    
    def _apply_enhancements_debounced(self):
        """Apply enhancements after debounce delay."""
        self.apply_enhancements()
    
    def apply_upscale(self, factor: int):
        """Apply basic upscaling."""
        if self.enhancer.original_image is None:
            return
        
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Processing", "Please wait for current operation to complete.")
            return
        
        self.enhancer.reset()
        self._start_worker("upscale", factor)
    
    def apply_super_resolution(self, factor: int):
        """Apply AI-based super-resolution."""
        if self.enhancer.original_image is None:
            return
        
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Processing", "Please wait for current operation to complete.")
            return
        
        # Check if Real-ESRGAN is available
        if not self.enhancer._realesrgan_available:
            self._offer_auto_install()
            # Re-check after potential installation
            if not self.enhancer._realesrgan_available:
                reply = QMessageBox.question(
                    self,
                    "Real-ESRGAN Not Found",
                    "Real-ESRGAN (realesrgan-ncnn-vulkan) is not installed.\n\n"
                    "Continue with basic upscaling?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
        
        self.enhancer.reset()
        strength = self.super_res_strength_slider.value() / 100.0
        self._start_worker("super_resolution", factor, strength=strength)
    
    def _start_worker(self, operation, *args, **kwargs):
        """Start a worker thread for processing."""
        if self.worker and self.worker.isRunning():
            return
        
        # Reset to original
        self.enhancer.reset()
        
        # Create and start worker
        self.worker = EnhancementWorker(self.enhancer, operation, *args, **kwargs)
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.image_ready.connect(self._on_image_ready)
        
        # Show progress dialog
        self.progress_dialog = QProgressDialog("Processing...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.canceled.connect(self._cancel_worker)
        self.progress_dialog.show()
        
        self.status_label.setText("Processing...")
        self.worker.start()
    
    def _cancel_worker(self):
        """Cancel the current worker operation."""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.status_label.setText("Cancelling...")
    
    def _on_worker_progress(self, percent: int, message: str):
        """Handle progress updates from worker."""
        if self.progress_dialog:
            self.progress_dialog.setValue(percent)
            self.progress_dialog.setLabelText(message)
        self.status_label.setText(message)
    
    def _on_worker_finished(self, success: bool, error_message: str):
        """Handle worker completion."""
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        if not success:
            if error_message and error_message != "Cancelled":
                QMessageBox.warning(self, "Processing Error", error_message)
            self.status_label.setText("Error occurred" if error_message != "Cancelled" else "Cancelled")
        else:
            self.status_label.setText("Ready")
    
    def _on_image_ready(self):
        """Handle processed image ready signal from worker."""
        self.display_image()
    
    def apply_enhancements(self):
        """Apply all enhancement settings."""
        if self.enhancer.original_image is None:
            return
        
        if self.worker and self.worker.isRunning():
            return
        
        # Get slider values
        sharpen_val = self.sharpen_slider.value() / 100.0
        denoise_val = self.denoise_slider.value() / 100.0
        contrast_val = self.contrast_slider.value() / 100.0
        brightness_val = self.brightness_slider.value() / 100.0
        saturation_val = self.saturation_slider.value() / 100.0
        detail_val = self.detail_enhance_slider.value() / 100.0
        
        # Start worker for enhancements
        self._start_worker(
            "enhancements",
            sharpen_val,
            denoise_val,
            contrast_val,
            brightness_val,
            saturation_val,
            detail_val
        )
    
    def display_image(self):
        """Display current image in the label."""
        try:
            image = self.enhancer.get_image()
            if image is None:
                return
            
            height, width = image.shape[:2]
            
            # For very large images, create a thumbnail for display
            max_display_size = 3840  # 4K width
            if width > max_display_size or height > max_display_size:
                scale = min(max_display_size / width, max_display_size / height)
                display_width = int(width * scale)
                display_height = int(height * scale)
                display_image = cv2.resize(image, (display_width, display_height), interpolation=cv2.INTER_AREA)
            else:
                display_image = image
            
            display_height, display_width = display_image.shape[:2]
            bytes_per_line = 3 * display_width
            
            # Create QImage
            q_image = QImage(
                display_image.data,
                display_width,
                display_height,
                bytes_per_line,
                QImage.Format.Format_RGB888
            )
            
            if q_image.isNull():
                raise Exception("Failed to create QImage")
            
            # Scale to fit label while maintaining aspect ratio
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setText("")
            
        except Exception as e:
            print(f"Error displaying image: {e}")
            QMessageBox.warning(
                self,
                "Display Error",
                f"Failed to display image:\n{str(e)}\n\nImage may be too large."
            )
    
    def save_image(self):
        """Save enhanced image to file."""
        if self.enhancer.get_image() is None:
            QMessageBox.warning(self, "No Image", "No image to save.")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Enhanced Image",
                "",
                "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
            )
            
            if file_path:
                if self.enhancer.save_image(file_path):
                    QMessageBox.information(self, "Success", f"Image saved successfully!\n{file_path}")
                    self.status_label.setText(f"Saved: {Path(file_path).name}")
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Failed to save image.\n\nPossible reasons:\n"
                        "- Invalid file path\n"
                        "- Insufficient permissions\n"
                        "- Disk full"
                    )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Unexpected error saving image:\n{str(e)}"
            )


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

