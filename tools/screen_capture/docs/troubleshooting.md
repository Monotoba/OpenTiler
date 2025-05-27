# Troubleshooting Guide

This guide helps resolve common issues with the Screen Capture Tool across different platforms.

## 🚨 Common Issues

### Installation Issues

#### Missing Dependencies
**Problem**: `ImportError: No module named 'pywinctl'` or similar

**Solution**:
```bash
# Install all required dependencies
pip install pywinctl mss Pillow

# Or install from requirements file
pip install -r requirements.txt

# Verify installation
python -c "import pywinctl, mss, PIL; print('All dependencies installed')"
```

#### Platform-Specific Installation Issues

**Windows**:
```bash
# If pip install fails, try:
pip install --upgrade pip
pip install pywinctl mss Pillow

# For Visual Studio Build Tools issues:
# Download and install Microsoft C++ Build Tools
```

**macOS**:
```bash
# If installation fails, ensure Xcode Command Line Tools:
xcode-select --install

# Then retry installation:
pip install pywinctl mss Pillow
```

**Linux**:
```bash
# Ubuntu/Debian - install system dependencies first:
sudo apt-get update
sudo apt-get install python3-dev python3-pip
pip install pywinctl mss Pillow

# CentOS/RHEL/Fedora:
sudo dnf install python3-devel python3-pip
pip install pywinctl mss Pillow
```

### Permission Issues

#### macOS Screen Recording Permission
**Problem**: `PermissionError` or blank screenshots on macOS

**Solution**:
1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Screen Recording** from the left panel
3. Click the lock icon and enter your password
4. Add your Terminal application or Python executable
5. Restart the application

**Verification**:
```bash
# Test if permissions are working
python screen_capture.py --list-windows
```

#### Linux Display Access
**Problem**: `Cannot connect to display` or permission errors

**Solution**:
```bash
# Check if running in user session
echo $DISPLAY

# If empty, set display:
export DISPLAY=:0

# For Wayland users:
echo $WAYLAND_DISPLAY

# Test X11 access:
xwininfo -root -tree
```

### Window Detection Issues

#### Window Not Found
**Problem**: `Window 'AppName' not found`

**Diagnosis**:
```bash
# List all available windows
python screen_capture.py --list-windows

# Check exact window title
python screen_capture.py --list-windows | grep -i "appname"
```

**Solutions**:
```bash
# Use partial matching (default)
python screen_capture.py -t "App" -o screenshot.png

# Try different parts of the title
python screen_capture.py -t "Main Window" -o screenshot.png

# Use exact title if needed
# (modify script to use partial_match=False)
```

#### Window Behind Other Windows
**Problem**: Captures wrong window or empty area

**Solution**:
```python
# Add window activation in your script
window = capture.find_window_by_title("MyApp")
if window:
    window.activate()  # Bring to front
    time.sleep(0.5)    # Wait for activation
    capture.capture_window(window, "output.png")
```

### Capture Quality Issues

#### Blank or Black Screenshots
**Problem**: Screenshots are blank or completely black

**Diagnosis**:
```bash
# Test with verbose output
python screen_capture.py -w -o test.png --verbose

# Check if file is created but empty
ls -la test.png
```

**Solutions**:

1. **Window Minimized**:
```python
# Ensure window is restored
if window.isMinimized:
    window.restore()
    time.sleep(1)
```

2. **Wrong Coordinates**:
```bash
# Check window position
python screen_capture.py --list-windows
```

3. **Permission Issues** (see Permission Issues section)

4. **Display Scaling** (Windows/macOS):
```python
# Account for DPI scaling
import platform
if platform.system() == "Windows":
    # May need to adjust coordinates for high DPI
    pass
```

#### Poor Image Quality
**Problem**: Screenshots are blurry or low quality

**Solutions**:
```bash
# Use PNG for lossless quality
python screen_capture.py -w -o high_quality.png --format png

# Increase JPEG quality
python screen_capture.py -w -o high_quality.jpg --format jpeg --quality 95

# Capture at higher resolution
python screen_capture.py -w -o large.png --width 1920 --height 1080
```

### Performance Issues

#### Slow Capture
**Problem**: Screenshots take a long time to capture

**Diagnosis**:
```bash
# Time the capture
time python screen_capture.py -w -o test.png
```

**Solutions**:
1. **Reduce Image Size**:
```bash
python screen_capture.py -w -o small.png --width 800 --height 600
```

2. **Use Faster Format**:
```bash
# JPEG is faster than PNG
python screen_capture.py -w -o fast.jpg --format jpeg --quality 80
```

3. **Optimize for Batch Captures**:
```python
# Reuse ScreenCapture instance
capture = ScreenCapture()
for i in range(10):
    capture.capture_active_window(f"screenshot_{i}.png")
```

#### Memory Issues
**Problem**: High memory usage or out of memory errors

**Solutions**:
```python
# Process images in smaller batches
def batch_capture(window_list, batch_size=5):
    for i in range(0, len(window_list), batch_size):
        batch = window_list[i:i+batch_size]
        # Process batch
        # Clear memory between batches
        import gc
        gc.collect()
```

## 🔧 Platform-Specific Issues

### Windows Issues

#### High DPI Display Problems
**Problem**: Screenshots have wrong size or coordinates

**Solution**:
```python
import ctypes

# Set DPI awareness
ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Then use screen capture normally
```

#### UAC/Elevated Windows
**Problem**: Cannot capture elevated windows

**Solution**:
- Run Python script as administrator
- Or capture non-elevated windows only

### macOS Issues

#### Retina Display Scaling
**Problem**: Screenshots are double the expected size

**Solution**:
```python
# Account for Retina scaling
import platform
if platform.system() == "Darwin":
    # Coordinates may need scaling
    scale_factor = 2  # For Retina displays
```

#### System Window Protection
**Problem**: Some system windows cannot be captured

**Solution**:
- This is a macOS security feature
- Focus on application windows instead
- Use fullscreen capture for system elements

### Linux Issues

#### Wayland Limitations
**Problem**: Limited window management on Wayland

**Diagnosis**:
```bash
echo $XDG_SESSION_TYPE
# If output is "wayland", some features may be limited
```

**Solutions**:
- Use X11 session if possible
- Focus on fullscreen captures
- Use application-specific capture methods

#### Window Manager Differences
**Problem**: Different behavior across window managers

**Solution**:
```bash
# Test with different window managers
echo $XDG_CURRENT_DESKTOP

# Adjust delays based on window manager
if [ "$XDG_CURRENT_DESKTOP" = "GNOME" ]; then
    # GNOME may need longer delays
    sleep 1
fi
```

## 🧪 Debugging Tools

### Verbose Logging
```bash
# Enable verbose output
python screen_capture.py -w -o test.png --verbose

# Or set logging level in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Window Information
```python
def debug_window_info(title):
    """Print detailed window information for debugging."""
    capture = ScreenCapture()
    
    print(f"Searching for window: '{title}'")
    
    # List all windows
    windows = capture.list_windows()
    print(f"Found {len(windows)} total windows:")
    
    for i, window in enumerate(windows):
        print(f"  {i+1}. Title: '{window.title}'")
        print(f"      Position: ({window.left}, {window.top})")
        print(f"      Size: {window.width}x{window.height}")
        print(f"      Visible: {window.visible}")
        print(f"      Minimized: {window.isMinimized}")
        print()
    
    # Try to find specific window
    target_window = capture.find_window_by_title(title)
    if target_window:
        print(f"✅ Found target window: '{target_window.title}'")
    else:
        print(f"❌ Target window '{title}' not found")

# Usage
debug_window_info("OpenTiler")
```

### Test Script
```python
#!/usr/bin/env python3
"""
Screen Capture Tool Test Script
"""

import sys
import tempfile
import os
from screen_capture import ScreenCapture

def run_tests():
    """Run comprehensive tests."""
    
    print("🧪 Running Screen Capture Tool Tests")
    print("=" * 40)
    
    capture = ScreenCapture()
    
    # Test 1: List windows
    print("Test 1: List Windows")
    try:
        windows = capture.list_windows()
        print(f"  ✅ Found {len(windows)} windows")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    # Test 2: Get active window
    print("\nTest 2: Get Active Window")
    try:
        active = capture.get_active_window()
        if active:
            print(f"  ✅ Active window: {active.title}")
        else:
            print("  ⚠️  No active window found")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    # Test 3: Capture active window
    print("\nTest 3: Capture Active Window")
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            temp_path = tmp.name
        
        success = capture.capture_active_window(temp_path)
        if success and os.path.exists(temp_path):
            size = os.path.getsize(temp_path)
            print(f"  ✅ Captured active window ({size} bytes)")
            os.unlink(temp_path)
        else:
            print("  ❌ Failed to capture active window")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    # Test 4: Capture fullscreen
    print("\nTest 4: Capture Fullscreen")
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            temp_path = tmp.name
        
        success = capture.capture_fullscreen(temp_path)
        if success and os.path.exists(temp_path):
            size = os.path.getsize(temp_path)
            print(f"  ✅ Captured fullscreen ({size} bytes)")
            os.unlink(temp_path)
        else:
            print("  ❌ Failed to capture fullscreen")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    print("\n🎉 Tests completed!")

if __name__ == "__main__":
    run_tests()
```

## 📞 Getting Help

### Information to Provide
When reporting issues, please include:

1. **Platform Information**:
```bash
python -c "import platform; print(f'OS: {platform.system()} {platform.release()}')"
python --version
```

2. **Dependency Versions**:
```bash
pip list | grep -E "(pywinctl|mss|Pillow)"
```

3. **Error Messages**:
```bash
# Run with verbose output
python screen_capture.py -w -o test.png --verbose
```

4. **Window Information**:
```bash
# List available windows
python screen_capture.py --list-windows
```

### Common Solutions Summary

| Issue | Quick Fix |
|-------|-----------|
| Import Error | `pip install pywinctl mss Pillow` |
| Permission Denied (macOS) | Enable Screen Recording permission |
| Window Not Found | Use `--list-windows` to check titles |
| Blank Screenshot | Check window is visible and not minimized |
| Poor Quality | Use PNG format and higher resolution |
| Slow Performance | Reduce image size or use JPEG |

### Support Resources

- **Documentation**: Check `docs/` directory for detailed guides
- **Examples**: See `examples/` directory for usage patterns
- **Tests**: Run test script to verify functionality
- **Issues**: Report bugs with detailed information

Remember: Most issues are platform or environment specific. The verbose output and test script are your best tools for diagnosis!
