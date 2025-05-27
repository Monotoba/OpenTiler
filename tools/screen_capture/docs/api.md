# Screen Capture Tool API Reference

This document provides detailed API reference for the Screen Capture Tool classes and methods.

## ScreenCapture Class

The main class providing screen capture functionality.

### Constructor

```python
ScreenCapture()
```

Creates a new ScreenCapture instance with logging and MSS screen capture initialized.

### Methods

#### get_active_window()

```python
def get_active_window() -> Optional[pywinctl.Window]
```

**Description**: Gets the currently active (focused) window.

**Returns**: 
- `pywinctl.Window`: The active window object
- `None`: If no active window found

**Example**:
```python
capture = ScreenCapture()
window = capture.get_active_window()
if window:
    print(f"Active window: {window.title}")
```

#### list_windows()

```python
def list_windows() -> List[pywinctl.Window]
```

**Description**: Returns a list of all visible windows with titles.

**Returns**: List of visible window objects

**Example**:
```python
capture = ScreenCapture()
windows = capture.list_windows()
for window in windows:
    print(f"Window: {window.title} at ({window.left}, {window.top})")
```

#### find_window_by_title()

```python
def find_window_by_title(title: str, partial_match: bool = True) -> Optional[pywinctl.Window]
```

**Description**: Finds a window by its title.

**Parameters**:
- `title` (str): Window title to search for
- `partial_match` (bool): If True, performs partial matching (default: True)

**Returns**:
- `pywinctl.Window`: Found window object
- `None`: If window not found

**Example**:
```python
capture = ScreenCapture()
window = capture.find_window_by_title("OpenTiler")
if window:
    print(f"Found: {window.title}")
```

#### capture_window()

```python
def capture_window(
    window: pywinctl.Window, 
    output_path: str,
    target_size: Optional[Tuple[int, int]] = None,
    format_type: str = "png", 
    quality: int = 95
) -> bool
```

**Description**: Captures a specific window.

**Parameters**:
- `window` (pywinctl.Window): Window object to capture
- `output_path` (str): Path where to save the screenshot
- `target_size` (Optional[Tuple[int, int]]): Target size (width, height) for resizing
- `format_type` (str): Output format ('png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff')
- `quality` (int): Quality for JPEG/WebP (1-100)

**Returns**: 
- `True`: If capture successful
- `False`: If capture failed

**Example**:
```python
capture = ScreenCapture()
window = capture.find_window_by_title("MyApp")
if window:
    success = capture.capture_window(
        window, 
        "app_screenshot.png",
        target_size=(1920, 1080),
        format_type="png"
    )
```

#### capture_active_window()

```python
def capture_active_window(
    output_path: str,
    target_size: Optional[Tuple[int, int]] = None,
    format_type: str = "png", 
    quality: int = 95
) -> bool
```

**Description**: Captures the currently active window.

**Parameters**: Same as `capture_window()` except no window parameter needed.

**Returns**: 
- `True`: If capture successful
- `False`: If capture failed

**Example**:
```python
capture = ScreenCapture()
success = capture.capture_active_window(
    "active_window.png",
    target_size=(800, 600)
)
```

#### capture_fullscreen()

```python
def capture_fullscreen(
    output_path: str,
    target_size: Optional[Tuple[int, int]] = None,
    format_type: str = "png", 
    quality: int = 95,
    monitor_number: int = 1
) -> bool
```

**Description**: Captures full screen or specific monitor.

**Parameters**:
- `output_path` (str): Path where to save the screenshot
- `target_size` (Optional[Tuple[int, int]]): Target size for resizing
- `format_type` (str): Output format
- `quality` (int): Quality for JPEG/WebP (1-100)
- `monitor_number` (int): Monitor to capture (1-based index)

**Returns**: 
- `True`: If capture successful
- `False`: If capture failed

**Example**:
```python
capture = ScreenCapture()
success = capture.capture_fullscreen(
    "desktop.jpg",
    format_type="jpeg",
    quality=85,
    monitor_number=2
)
```

## Command Line Interface

### Main Function

```python
def main() -> int
```

**Description**: Main entry point for command-line usage.

**Returns**: Exit code (0 for success, 1 for failure)

### Argument Parser

The tool uses `argparse` for command-line argument parsing with the following structure:

#### Capture Mode Arguments (Mutually Exclusive)
- `--window, -w`: Capture active window
- `--fullscreen, -f`: Capture full screen  
- `--window-title TITLE, -t TITLE`: Capture window by title
- `--list-windows, -l`: List all windows

#### Output Arguments
- `--output-file PATH, -o PATH`: Output file path
- `--format FORMAT`: Output format
- `--quality QUALITY, -q QUALITY`: Image quality

#### Size Arguments
- `--width WIDTH`: Target width
- `--height HEIGHT`: Target height
- `--monitor NUMBER`: Monitor number

#### Utility Arguments
- `--verbose, -v`: Verbose logging
- `--help, -h`: Show help

## Error Handling

### Exceptions

The tool handles various exceptions gracefully:

- **ImportError**: Missing dependencies
- **WindowNotFoundError**: Window not found
- **PermissionError**: Insufficient permissions
- **FileNotFoundError**: Invalid output path
- **ValueError**: Invalid parameters

### Logging

The tool uses Python's `logging` module with the following levels:

- **INFO**: Normal operation messages
- **WARNING**: Non-fatal issues
- **ERROR**: Error conditions
- **DEBUG**: Detailed debugging (with --verbose)

## Platform Considerations

### Windows
- No additional permissions required
- Full window management support
- All formats supported

### macOS
- May require Screen Recording permission
- Window activation may have delays
- Some system windows may be protected

### Linux
- Requires X11 or Wayland
- May need additional permissions for some windows
- Window manager dependent behavior

## Integration Examples

### Basic Integration

```python
from screen_capture import ScreenCapture

def capture_app_screenshots():
    capture = ScreenCapture()
    
    # Find and capture application window
    window = capture.find_window_by_title("MyApp")
    if window:
        capture.capture_window(window, "docs/images/app.png")
    
    # Capture desktop for context
    capture.capture_fullscreen("docs/images/desktop.png")
```

### Automated Documentation

```python
import time
from screen_capture import ScreenCapture

def generate_documentation_screenshots():
    capture = ScreenCapture()
    
    # Launch application (external process)
    # ... launch app ...
    
    time.sleep(2)  # Wait for app to load
    
    # Capture main interface
    capture.capture_active_window("docs/main-interface.png")
    
    # Simulate opening dialogs and capture each
    # ... trigger dialog ...
    time.sleep(1)
    capture.capture_active_window("docs/dialog.png")
```

### CI/CD Integration

```python
import subprocess
from screen_capture import ScreenCapture

def ci_screenshot_workflow():
    # Start application in background
    app_process = subprocess.Popen(['python', 'myapp.py'])
    
    try:
        time.sleep(3)  # Wait for startup
        
        capture = ScreenCapture()
        
        # Capture for documentation
        success = capture.capture_window_by_title(
            "MyApp", 
            "artifacts/screenshot.png"
        )
        
        return success
    finally:
        app_process.terminate()
```
