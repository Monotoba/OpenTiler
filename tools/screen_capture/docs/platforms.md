# Platform-Specific Notes

This document covers platform-specific considerations, requirements, and behaviors for the Screen Capture Tool.

## 🪟 Windows

### Requirements
- **Python**: 3.8+
- **Dependencies**: pywinctl, mss, Pillow
- **Permissions**: No special permissions required

### Features
- ✅ Full window management support
- ✅ All capture modes supported
- ✅ All image formats supported
- ✅ Multi-monitor support
- ✅ Window activation and restoration

### Platform-Specific Behavior
- **Window Detection**: Uses Windows API through pywinctl
- **Screen Capture**: Direct access via mss
- **Window Activation**: Immediate activation support
- **Minimized Windows**: Can restore and capture

### Installation
```bash
# Standard installation
pip install pywinctl mss Pillow

# Or from requirements
pip install -r requirements.txt
```

### Known Issues
- **DPI Scaling**: High DPI displays may affect coordinates
- **Protected Windows**: Some system windows cannot be captured
- **UAC Dialogs**: Elevated windows may not be accessible

### Troubleshooting
```bash
# Test window detection
python screen_capture.py --list-windows

# Test with verbose output
python screen_capture.py -w -o test.png --verbose
```

## 🍎 macOS

### Requirements
- **Python**: 3.8+
- **macOS**: 10.14+ (Mojave or later)
- **Dependencies**: pywinctl, mss, Pillow
- **Permissions**: Screen Recording permission may be required

### Features
- ✅ Window management support
- ✅ All capture modes supported
- ✅ All image formats supported
- ✅ Multi-monitor support
- ⚠️ Window activation with delays

### Platform-Specific Behavior
- **Window Detection**: Uses Quartz/Cocoa APIs
- **Screen Capture**: Core Graphics framework
- **Window Activation**: May have 0.2s delay for proper activation
- **Permissions**: May prompt for Screen Recording access

### Installation
```bash
# Standard installation
pip install pywinctl mss Pillow

# macOS may require additional setup for some features
```

### Permissions Setup
1. **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Screen Recording** from the left panel
3. Add Terminal or your Python application
4. Restart the application

### Known Issues
- **Permission Dialogs**: First run may require permission grant
- **Window Activation**: Some windows may not activate immediately
- **System Windows**: Some macOS system windows are protected
- **Retina Displays**: Coordinates may need scaling adjustment

### Troubleshooting
```bash
# Check permissions
python screen_capture.py --list-windows

# Test with delays
python screen_capture.py -w -o test.png --verbose

# Manual permission check
# System Preferences → Security & Privacy → Screen Recording
```

### macOS-Specific Tips
```python
# Add delays for window activation
import time
window = capture.find_window_by_title("MyApp")
if window:
    window.activate()
    time.sleep(0.5)  # Wait for activation
    capture.capture_window(window, "output.png")
```

## 🐧 Linux

### Requirements
- **Python**: 3.8+
- **Display Server**: X11 or Wayland
- **Dependencies**: pywinctl, mss, Pillow
- **System Packages**: May require additional packages

### Features
- ✅ Window management support (X11)
- ✅ All capture modes supported
- ✅ All image formats supported
- ✅ Multi-monitor support
- ⚠️ Display server dependent behavior

### Platform-Specific Behavior
- **Window Detection**: X11 or Wayland APIs
- **Screen Capture**: X11/Wayland specific methods
- **Window Activation**: Window manager dependent
- **Permissions**: May require user session access

### Installation

#### Ubuntu/Debian
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev python3-pip

# Install Python packages
pip install pywinctl mss Pillow

# Additional packages for X11 support
sudo apt-get install python3-xlib
```

#### CentOS/RHEL/Fedora
```bash
# Install system dependencies
sudo dnf install python3-devel python3-pip

# Install Python packages
pip install pywinctl mss Pillow
```

#### Arch Linux
```bash
# Install system dependencies
sudo pacman -S python python-pip

# Install Python packages
pip install pywinctl mss Pillow
```

### Display Server Support

#### X11 (Traditional)
- ✅ Full window management
- ✅ All capture features
- ✅ Multi-monitor support

#### Wayland (Modern)
- ⚠️ Limited window management
- ✅ Screen capture support
- ⚠️ Some features may be restricted

### Known Issues
- **Wayland Limitations**: Some window operations restricted
- **Permission Issues**: May need user session access
- **Window Manager**: Behavior varies by window manager
- **Compositor Effects**: May affect capture quality

### Troubleshooting

#### Check Display Server
```bash
echo $XDG_SESSION_TYPE
# Output: x11 or wayland
```

#### Test Window Detection
```bash
# List available windows
python screen_capture.py --list-windows

# Test with verbose output
python screen_capture.py -w -o test.png --verbose
```

#### Permission Issues
```bash
# Run with user session
python screen_capture.py --list-windows

# Check X11 access
xwininfo -root -tree
```

### Linux Distribution Notes

#### Ubuntu/Debian
- Default X11 or Wayland depending on version
- GNOME desktop may have additional restrictions
- Works well with most window managers

#### CentOS/RHEL/Fedora
- Usually X11 by default
- SELinux may affect permissions
- Works with GNOME and KDE

#### Arch Linux
- Flexible display server choice
- May require manual configuration
- Works with various window managers

## 🔧 Cross-Platform Development

### Consistent Behavior
```python
import time
import platform

def capture_with_platform_delays(capture, window, output_path):
    """Capture with platform-appropriate delays."""
    
    if platform.system() == "Darwin":  # macOS
        window.activate()
        time.sleep(0.5)  # macOS needs more time
    elif platform.system() == "Linux":
        window.activate()
        time.sleep(0.2)  # Linux may need brief delay
    else:  # Windows
        window.activate()
        time.sleep(0.1)  # Windows is usually fast
    
    return capture.capture_window(window, output_path)
```

### Platform Detection
```python
import platform

def get_platform_info():
    """Get platform-specific information."""
    system = platform.system()
    
    if system == "Windows":
        return {
            "name": "Windows",
            "activation_delay": 0.1,
            "permissions_required": False
        }
    elif system == "Darwin":
        return {
            "name": "macOS", 
            "activation_delay": 0.5,
            "permissions_required": True
        }
    elif system == "Linux":
        return {
            "name": "Linux",
            "activation_delay": 0.2,
            "permissions_required": False
        }
```

### Testing Across Platforms
```bash
# Test script for all platforms
python screen_capture.py --list-windows
python screen_capture.py -w -o test-window.png
python screen_capture.py -f -o test-fullscreen.png
python screen_capture.py -t "Terminal" -o test-terminal.png
```

## 📊 Platform Comparison

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| Window Detection | ✅ Full | ✅ Full | ✅ Full* |
| Window Activation | ✅ Fast | ⚠️ Delayed | ⚠️ Variable |
| Screen Capture | ✅ Full | ✅ Full | ✅ Full* |
| Multi-Monitor | ✅ Yes | ✅ Yes | ✅ Yes |
| Permissions | ✅ None | ⚠️ Required | ✅ None** |
| Protected Windows | ⚠️ Some | ⚠️ Some | ⚠️ Some |

*Depends on display server (X11/Wayland)
**May require user session access

## 🚀 Best Practices

### Cross-Platform Code
```python
def robust_window_capture(title, output_path):
    """Robust cross-platform window capture."""
    capture = ScreenCapture()
    
    # Find window
    window = capture.find_window_by_title(title)
    if not window:
        return False
    
    # Platform-specific activation
    window.activate()
    
    # Platform-appropriate delay
    delay = 0.5 if platform.system() == "Darwin" else 0.2
    time.sleep(delay)
    
    # Capture with error handling
    try:
        return capture.capture_window(window, output_path)
    except Exception as e:
        logging.error(f"Capture failed: {e}")
        return False
```

### Error Handling
```python
def safe_capture(capture_func, *args, **kwargs):
    """Safe capture with platform-specific error handling."""
    try:
        return capture_func(*args, **kwargs)
    except PermissionError:
        if platform.system() == "Darwin":
            print("❌ Screen Recording permission required on macOS")
            print("   Go to System Preferences → Security & Privacy → Screen Recording")
        else:
            print("❌ Permission denied")
        return False
    except Exception as e:
        print(f"❌ Capture failed: {e}")
        return False
```
