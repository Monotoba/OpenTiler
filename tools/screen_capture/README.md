# Cross-Platform Screen Capture Tool

A professional, cross-platform screen capture utility that supports capturing active windows and full screen across Windows, macOS, and Linux.

## 🚀 Features

- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Window Capture**: Capture active window or find by title
- **Full Screen**: Capture entire screen or specific monitor
- **Multiple Formats**: PNG, JPEG, WebP, BMP, TIFF support
- **Flexible Output**: Custom resolution, quality, and file naming
- **CLI Interface**: Easy command-line usage with comprehensive flags
- **Professional Quality**: High-quality captures with optimization

## 📦 Installation

### From Source
```bash
# Clone or copy the screen_capture directory
cd screen_capture
pip install -r requirements.txt
```

### As Package (when standalone)
```bash
pip install screen-capture-tool
```

## 🔧 Dependencies

- **pywinctl**: Cross-platform window management
- **mss**: Fast screen capture
- **Pillow**: Image processing and format support

## 🎯 Quick Start

### Capture Active Window
```bash
python screen_capture.py --window --output-file window.png
```

### Capture Full Screen
```bash
python screen_capture.py --fullscreen --output-file desktop.jpg --format jpeg
```

### Capture Specific Window
```bash
python screen_capture.py --window-title "OpenTiler" --output-file app.png
```

### List Available Windows
```bash
python screen_capture.py --list-windows
```

## 📋 Command Line Options

### Capture Modes
- `--window, -w`: Capture active window
- `--fullscreen, -f`: Capture full screen
- `--window-title TITLE, -t TITLE`: Capture window by title
- `--list-windows, -l`: List all visible windows

### Output Options
- `--output-file PATH, -o PATH`: Output file path (required)
- `--format FORMAT`: Output format (png, jpg, jpeg, webp, bmp, tiff)
- `--quality QUALITY, -q QUALITY`: JPEG/WebP quality 1-100 (default: 95)

### Size Options
- `--width WIDTH`: Target width in pixels
- `--height HEIGHT`: Target height in pixels
- `--monitor NUMBER`: Monitor number for fullscreen (default: 1)

### Other Options
- `--verbose, -v`: Verbose output
- `--help, -h`: Show help message

## 💡 Usage Examples

### Basic Window Capture
```bash
# Capture active window as PNG
python screen_capture.py -w -o screenshot.png

# Capture with specific size
python screen_capture.py -w -o window.png --width 1920 --height 1080
```

### Application-Specific Capture
```bash
# Capture OpenTiler window
python screen_capture.py -t "OpenTiler" -o opentiler.png

# Capture browser window
python screen_capture.py -t "Firefox" -o browser.jpg --format jpeg --quality 85
```

### Full Screen Capture
```bash
# Capture primary monitor
python screen_capture.py -f -o desktop.png

# Capture secondary monitor
python screen_capture.py -f -o monitor2.png --monitor 2

# Capture with compression
python screen_capture.py -f -o desktop.webp --format webp --quality 80
```

### Documentation Workflow
```bash
# List windows to find target
python screen_capture.py --list-windows

# Capture specific application
python screen_capture.py -t "MyApp" -o docs/images/main-interface.png

# Capture with consistent sizing
python screen_capture.py -w -o docs/images/dialog.png --width 800 --height 600
```

## 🔍 Advanced Features

### Window Detection
- Partial title matching for flexible window finding
- Automatic window activation and restoration
- Support for minimized window capture

### Image Processing
- Automatic format detection from file extension
- Quality optimization for different formats
- Aspect ratio preservation during resizing

### Cross-Platform Compatibility
- Native window management on each platform
- Consistent behavior across operating systems
- Platform-specific optimizations

## 🧪 Testing

```bash
# Run tests (when available)
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=screen_capture
```

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- [API Reference](docs/api.md)
- [Platform Notes](docs/platforms.md)
- [Integration Guide](docs/integration.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Integration

### Python Integration
```python
from screen_capture import ScreenCapture

capture = ScreenCapture()

# Capture active window
success = capture.capture_active_window("output.png")

# Capture by title
window = capture.find_window_by_title("MyApp")
if window:
    capture.capture_window(window, "app.png")
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Capture Screenshots
  run: |
    python screen_capture.py -t "MyApp" -o screenshots/app.png
    python screen_capture.py -f -o screenshots/desktop.png
```

## 🐛 Troubleshooting

### Common Issues
- **No active window**: Ensure a window is focused before capture
- **Permission denied**: Run with appropriate permissions on Linux/macOS
- **Window not found**: Use `--list-windows` to see available windows

### Platform-Specific Notes
- **Windows**: Requires no additional setup
- **macOS**: May require screen recording permissions
- **Linux**: Requires X11 or Wayland support

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **pywinctl**: Cross-platform window management
- **mss**: Fast screen capture library
- **Pillow**: Python Imaging Library

## 🔗 Related Projects

- [OpenTiler](../../../README.md): Professional document scaling and tiling application
- Part of the OpenTiler project ecosystem
