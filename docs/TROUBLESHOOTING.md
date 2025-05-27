# OpenTiler Troubleshooting Guide

## Quick Diagnostic Commands

### Check System Status
```bash
# System information
python --version
pip --version
echo $VIRTUAL_ENV  # Should show virtual environment path

# Check installed packages
pip list | grep -E "(PySide6|PyPDF2|ezdxf|matplotlib)"

# Test OpenTiler modules
python -c "
from opentiler.formats.dxf_handler import DXFHandler
from opentiler.formats.freecad_handler import FreeCADHandler
print('DXF:', DXFHandler.is_available())
print('FreeCAD:', FreeCADHandler.is_available())
"
```

---

## Application Won't Start

### Error: "No module named 'PySide6'"
**Cause:** Core dependencies not installed

**Solution:**
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install missing dependencies
pip install PySide6 PyPDF2
```

### Error: "python: command not found"
**Cause:** Python not installed or not in PATH

**Solutions:**
```bash
# Linux/Mac: Use python3 explicitly
python3 main.py

# Windows: Add Python to PATH or reinstall with PATH option
# Or use full path: C:\Python310\python.exe main.py
```

### Error: "Permission denied"
**Cause:** File permissions or virtual environment issues

**Solutions:**
```bash
# Linux/Mac: Check file permissions
chmod +x main.py

# Windows: Run as Administrator or use --user flag
pip install --user PySide6 PyPDF2

# Or recreate virtual environment
rm -rf venv && python -m venv venv
```

### Application crashes immediately
**Cause:** Qt/GUI initialization issues

**Solutions:**
```bash
# Linux: Install Qt dependencies
sudo apt install qt5-default libqt5gui5

# Set Qt platform
export QT_QPA_PLATFORM=xcb

# Check display
echo $DISPLAY  # Should show :0 or similar

# For headless systems
xvfb-run python main.py
```

---

## File Loading Issues

### "Failed to load PDF"
**Causes and Solutions:**

1. **Corrupted PDF:**
   ```bash
   # Test with different PDF viewer first
   # Try re-exporting from original software
   ```

2. **Encrypted/Protected PDF:**
   ```bash
   # Remove password protection first
   # Or use "Print to PDF" to create unprotected copy
   ```

3. **Very large PDF:**
   ```bash
   # Reduce file size or resolution
   # Split into smaller files if possible
   ```

### "DXF support not available"
**Solution:**
```bash
# Install DXF dependencies
pip install ezdxf matplotlib

# Verify installation
python -c "import ezdxf; print('ezdxf version:', ezdxf.__version__)"
```

### "FreeCAD support not available"
**Solutions:**

1. **Install FreeCAD:**
   ```bash
   # Linux
   sudo apt install freecad
   # or sudo snap install freecad
   
   # macOS
   brew install --cask freecad
   
   # Windows: Download from freecadweb.org
   ```

2. **Verify FreeCAD installation:**
   ```bash
   # Test command availability
   which freecad
   freecad --version
   ```

3. **Restart OpenTiler** after installing FreeCAD

### "Unsupported file format"
**Supported formats:**
- PDF (.pdf)
- Images: PNG (.png), JPEG (.jpg, .jpeg), TIFF (.tiff, .tif)
- SVG (.svg)
- DXF (.dxf) - requires ezdxf
- FreeCAD (.FCStd) - requires FreeCAD

**Solutions:**
- Convert file to supported format
- Check file extension is correct
- Verify file is not corrupted

---

## Performance Issues

### Application runs slowly
**Solutions:**

1. **Reduce file size:**
   ```bash
   # For images: reduce resolution
   # For PDFs: optimize in original software
   # For DXF: simplify drawing, remove unnecessary elements
   ```

2. **System optimization:**
   ```bash
   # Close other applications
   # Increase virtual memory/swap
   # Use 64-bit Python if available
   ```

3. **Memory monitoring:**
   ```bash
   # Linux: Monitor memory usage
   top -p $(pgrep -f python)
   
   # Windows: Use Task Manager
   # macOS: Use Activity Monitor
   ```

### Large files won't load
**File size limits:**
- Images: ~500MB recommended maximum
- PDFs: ~100MB recommended maximum
- DXF: Depends on complexity, not just file size

**Solutions:**
1. **Reduce resolution/quality in source application**
2. **Split large drawings into sections**
3. **Use more powerful hardware**
4. **Process files in smaller chunks**

---

## Scaling and Measurement Issues

### Scale line not visible
**Causes and Solutions:**

1. **Scale line display disabled:**
   ```bash
   # Check Settings → Display → Scale Line Display
   # Enable "Show scale line" option
   ```

2. **Scale points not set:**
   ```bash
   # Use Tools → Scaling to set measurement points
   # Select two points with known distance
   ```

3. **Scale line outside visible area:**
   ```bash
   # Zoom out to see entire document
   # Check if scale points are within document bounds
   ```

### Incorrect measurements
**Solutions:**

1. **Verify scale points:**
   - Ensure points are placed accurately
   - Use zoom for precise placement
   - Check measurement text matches known distance

2. **Check units:**
   - Verify measurement units (mm, inches, etc.)
   - Ensure consistent units throughout

3. **Recalibrate:**
   - Clear existing scale points
   - Set new measurement with known dimension

### Tiles don't align properly
**Causes and Solutions:**

1. **Incorrect gutter settings:**
   ```bash
   # Adjust gutter size in tiling settings
   # Ensure gutters are large enough for overlap
   ```

2. **Printer scaling:**
   ```bash
   # Use "Actual Size" or "100%" in printer settings
   # Disable "Fit to page" or "Scale to fit"
   ```

3. **Paper size mismatch:**
   ```bash
   # Ensure all tiles printed on same paper size
   # Check page setup in export dialog
   ```

---

## Export and Printing Issues

### Export fails
**Solutions:**

1. **Check output directory permissions:**
   ```bash
   # Ensure write access to output folder
   # Try exporting to different location
   ```

2. **Disk space:**
   ```bash
   # Check available disk space
   df -h  # Linux/Mac
   # Windows: Check drive properties
   ```

3. **File format issues:**
   ```bash
   # Try different export format
   # Check if specific format dependencies installed
   ```

### Print scaling incorrect
**Solutions:**

1. **Printer settings:**
   - Use "Actual Size" or "100%" scaling
   - Disable "Fit to page"
   - Check page margins

2. **Verify with test print:**
   ```bash
   # Print single tile first
   # Measure scale line on printed output
   # Should match measurement text exactly
   ```

3. **Driver issues:**
   ```bash
   # Update printer drivers
   # Try different print quality settings
   ```

---

## CAD Integration Issues

### DXF files won't open
**Solutions:**

1. **Check DXF version:**
   ```bash
   # OpenTiler supports AutoCAD 2010+ format
   # Save as older DXF version in CAD software
   ```

2. **File corruption:**
   ```bash
   # Try opening in AutoCAD/LibreCAD first
   # Re-export from original CAD software
   ```

3. **Complex drawings:**
   ```bash
   # Simplify drawing (remove unnecessary layers)
   # Break complex drawings into sections
   ```

### FreeCAD integration problems
**Solutions:**

1. **Command-line mode limitations:**
   ```bash
   # Some features only work with full Python API
   # Try installing FreeCAD via package manager instead of snap
   ```

2. **File compatibility:**
   ```bash
   # Ensure .FCStd file is from compatible FreeCAD version
   # Try exporting as different format from FreeCAD
   ```

---

## Environment Issues

### Virtual environment problems
**Solutions:**

1. **Recreate environment:**
   ```bash
   # Remove existing environment
   rm -rf venv
   
   # Create new environment
   python -m venv venv
   source venv/bin/activate
   pip install PySide6 PyPDF2 ezdxf matplotlib
   ```

2. **Path issues:**
   ```bash
   # Verify virtual environment is activated
   which python  # Should point to venv/bin/python
   echo $VIRTUAL_ENV  # Should show venv path
   ```

### Package conflicts
**Solutions:**

1. **Clean installation:**
   ```bash
   # Uninstall conflicting packages
   pip uninstall PySide6 PyQt5 PyQt6
   
   # Reinstall clean
   pip install PySide6
   ```

2. **Dependency resolution:**
   ```bash
   # Check for conflicts
   pip check
   
   # Force reinstall if needed
   pip install --force-reinstall PySide6
   ```

---

## Debug Mode

### Enable verbose logging
```bash
# Run with debug output
python -v main.py

# Qt debug output
export QT_LOGGING_RULES="*=true"
python main.py

# Python warnings
python -W all main.py
```

### Collect diagnostic information
```bash
# System info
python -c "
import sys, platform
print('Python:', sys.version)
print('Platform:', platform.platform())
print('Architecture:', platform.architecture())
"

# Package versions
pip list | grep -E "(PySide6|PyPDF2|ezdxf|matplotlib)"

# OpenTiler status
python -c "
try:
    from opentiler.formats.dxf_handler import DXFHandler
    from opentiler.formats.freecad_handler import FreeCADHandler
    print('DXF Support:', DXFHandler.is_available())
    print('FreeCAD Support:', FreeCADHandler.is_available())
    print('FreeCAD Status:', FreeCADHandler.get_availability_status())
except Exception as e:
    print('Error:', e)
"
```

---

## Getting Help

### Before reporting issues:

1. **Try the solutions above**
2. **Check FAQ.md for common questions**
3. **Verify installation with diagnostic commands**
4. **Test with different files to isolate the problem**

### When reporting bugs, include:

1. **System information:**
   ```bash
   python --version
   pip list | grep -E "(PySide6|PyPDF2|ezdxf|matplotlib)"
   ```

2. **Error messages:** Full traceback from terminal

3. **Steps to reproduce:** Exact sequence that causes the issue

4. **File information:** Type, size, and source of problematic files

5. **Environment:** Virtual environment, operating system, etc.

---

*For additional help, see FAQ.md or create an issue on GitHub with the diagnostic information above.*
