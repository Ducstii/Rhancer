# Rhancer - Image Enhancer for Linux

A modern, user-friendly image enhancement application for Linux that improves picture quality through various enhancement algorithms.

## Features

- **Multiple Enhancement Options:**
  - **AI Super-Resolution** - Advanced upscaling with detail recovery (2x, 4x)
  - Image sharpening
  - Detail enhancement
  - Noise reduction
  - Basic upscaling (2x, 4x)
  - Contrast adjustment
  - Brightness adjustment
  - Saturation enhancement

- **User-Friendly Interface:**
  - Drag-and-drop image loading
  - Real-time preview with before/after comparison
  - Adjustable enhancement parameters with debounced updates
  - Background processing to keep UI responsive
  - Progress indicators for long operations
  - Save enhanced images

## Installation

1. Install Python 3.8 or higher
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. **Automatic Real-ESRGAN Installation** (Recommended):
   - The application will automatically detect if Real-ESRGAN is missing
   - On first launch, you'll be prompted to install it automatically
   - Click "Yes" to download and install (~45MB download)
   - Installation happens automatically - no manual steps required!
   
   **Manual Installation** (if auto-install fails):
   - Download `realesrgan-ncnn-vulkan` from [Real-ESRGAN releases](https://github.com/xinntao/Real-ESRGAN/releases)
   - Extract the archive
   - Add the extracted directory to your PATH, or place the binary in a directory that's already in PATH
   - Verify installation: `realesrgan-ncnn-vulkan -h` should show help text
   
   **Note**: Real-ESRGAN requires a Vulkan-compatible GPU for optimal performance. The application will work without it but will use a fallback method with lower quality.

## Usage

Run the application:
```bash
python main.py
```

1. Load an image by clicking "Load Image" or dragging a file into the window
2. Use **Super Resolution** buttons for AI-powered upscaling (recommended for higher quality)
3. Adjust enhancement parameters using the sliders for fine-tuning
4. Preview the enhanced image in real-time
5. Save the result using "Save Enhanced Image"

## Super Resolution

The **Super Resolution** feature provides AI-powered upscaling with two modes:

### Real-ESRGAN Mode (Recommended)
When `realesrgan-ncnn-vulkan` is installed, the application uses Real-ESRGAN for maximum quality:
- **AI-based detail recovery** - Uses deep learning to reconstruct high-resolution details
- **GPU acceleration** - Leverages Vulkan for fast processing
- **Superior quality** - Produces significantly better results than traditional methods
- Supports 2x, 3x, and 4x upscaling

### Fallback Mode
If Real-ESRGAN is not available, the application uses optimized filter-based techniques:
- Edge-preserving upscaling
- Unsharp masking for detail recovery
- Adaptive contrast enhancement (CLAHE)
- Intelligent sharpening

**Performance**: Real-ESRGAN is 10-100x faster than the filter-based approach on GPU and produces much better quality results.

## Requirements

- Python 3.8+
- PyQt6
- Pillow
- OpenCV 4.8+
- NumPy

### Optional (for best quality):
- Real-ESRGAN (realesrgan-ncnn-vulkan) - See Installation section
- Vulkan-compatible GPU (for Real-ESRGAN acceleration)

## Performance Notes

- **Large Images**: Images larger than 10MP may process slowly. Maximum supported size is ~50MP (8000x6000).
- **Processing Time**: Super-resolution processing time depends on image size and hardware:
  - With GPU: Typically 5-30 seconds for 2x upscale
  - Without GPU: May take several minutes for large images
- **Memory**: The application validates image sizes to prevent memory issues

## Troubleshooting

- **"Real-ESRGAN Not Found"**: Install Real-ESRGAN as described in Installation section, or use basic upscaling
- **Slow Processing**: Ensure you have a Vulkan-compatible GPU and Real-ESRGAN installed
- **Crashes**: Check that images are not too large (>8000x6000) and you have sufficient RAM
- **Display Issues**: Very large images are automatically downscaled for preview to prevent display errors

