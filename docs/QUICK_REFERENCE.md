# OpenTiler Quick Reference

## 🚨 Emergency Fixes

### Complete Reset
```bash
# Remove virtual environment and reinstall everything
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install PySide6 PyPDF2 ezdxf matplotlib
```

### Dependency Issues
```bash
# DXF support missing
pip install ezdxf matplotlib

# FreeCAD not detected (Linux)
sudo apt install freecad
# or sudo snap install freecad

# Core dependencies missing
pip install PySide6 PyPDF2
```

## 🔍 Quick Diagnostics

### Check Installation Status
```bash
python --version
pip list | grep -E "(PySide6|PyPDF2|ezdxf|matplotlib)"
```

### Test OpenTiler Modules
```bash
python -c "
from opentiler.formats.dxf_handler import DXFHandler
from opentiler.formats.freecad_handler import FreeCADHandler
print('DXF Support:', DXFHandler.is_available())
print('FreeCAD Support:', FreeCADHandler.is_available())
"
```

## 🐛 Common Error Solutions

| Error Message | Quick Fix |
|---------------|-----------|
| `No module named 'PySide6'` | `pip install PySide6` |
| `No module named 'ezdxf'` | `pip install ezdxf matplotlib` |
| `python: command not found` | Use `python3` or add Python to PATH |
| `Permission denied` | Use virtual environment or `--user` flag |
| `DXF support not available` | `pip install ezdxf matplotlib` |
| `FreeCAD support not available` | Install FreeCAD, restart OpenTiler |

## 📱 Platform-Specific Quick Fixes

### Windows
```cmd
# Python not found
# Add to PATH: C:\Python310 and C:\Python310\Scripts

# Permission issues
pip install --user PySide6 PyPDF2 ezdxf matplotlib

# FreeCAD installation
# Download from freecadweb.org and install
```

### Linux (Ubuntu/Debian)
```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv freecad

# Install OpenTiler dependencies
pip install PySide6 PyPDF2 ezdxf matplotlib
```

### macOS
```bash
# Install Python via Homebrew
brew install python

# Install FreeCAD
brew install --cask freecad

# Install dependencies
pip install PySide6 PyPDF2 ezdxf matplotlib
```

## 🎯 File Format Issues

### Supported Formats
- ✅ PDF (.pdf)
- ✅ PNG (.png), JPEG (.jpg), TIFF (.tiff)
- ✅ SVG (.svg)
- ✅ DXF (.dxf) - requires `ezdxf matplotlib`
- ✅ FreeCAD (.FCStd) - requires FreeCAD installation

### File Won't Load
1. **Check file format** - Ensure it's supported
2. **Test file size** - Very large files (>100MB) may be slow
3. **Verify file integrity** - Try opening in other software first
4. **Check permissions** - Ensure file is readable

## ⚡ Performance Quick Fixes

### Slow Performance
```bash
# Close other applications
# Reduce file size/resolution
# Use 64-bit Python
# Increase system memory
```

### Memory Issues
```bash
# Monitor memory usage
top -p $(pgrep -f python)  # Linux
# Use Task Manager (Windows) or Activity Monitor (macOS)
```

## 🖨️ Printing Issues

### Scale Problems
- ✅ Use "Actual Size" or "100%" in printer settings
- ✅ Disable "Fit to page" or "Scale to fit"
- ✅ Measure printed scale line to verify accuracy

### Tile Alignment
- ✅ Check gutter settings in OpenTiler
- ✅ Ensure consistent paper size for all tiles
- ✅ Use crop marks for precise alignment

## 🔧 CAD Integration Quick Fixes

### DXF Issues
```bash
# Install dependencies
pip install ezdxf matplotlib

# Check DXF version (use AutoCAD 2010+ format)
# Simplify complex drawings
# Remove unnecessary layers
```

### FreeCAD Issues
```bash
# Linux
sudo apt install freecad

# macOS  
brew install --cask freecad

# Windows: Download from freecadweb.org
# Restart OpenTiler after installation
```

## 🚀 Quick Start Commands

### New Installation
```bash
# 1. Create virtual environment
python -m venv opentiler-env
source opentiler-env/bin/activate

# 2. Install dependencies
pip install PySide6 PyPDF2 ezdxf matplotlib

# 3. Run OpenTiler
python main.py
```

### Verify Installation
```bash
# Test all components
python -c "
import sys
print('Python:', sys.version)

modules = ['PySide6', 'PyPDF2', 'ezdxf', 'matplotlib']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}: OK')
    except ImportError:
        print(f'❌ {module}: Missing')
"
```

## 📞 Getting Help

### Before Asking for Help
1. ✅ Try the emergency fixes above
2. ✅ Run diagnostic commands
3. ✅ Check the full [FAQ](FAQ.md)
4. ✅ Review [Troubleshooting Guide](TROUBLESHOOTING.md)

### When Reporting Issues
Include this information:
```bash
# System info
python --version
pip list | grep -E "(PySide6|PyPDF2|ezdxf|matplotlib)"

# OpenTiler status
python -c "
from opentiler.formats.dxf_handler import DXFHandler
from opentiler.formats.freecad_handler import FreeCADHandler
print('DXF:', DXFHandler.is_available())
print('FreeCAD:', FreeCADHandler.is_available())
"

# Error message (full traceback)
# Steps to reproduce
# File type and size (if applicable)
```

## 🎓 Learning Resources

### Documentation
- 📖 [Installation Guide](INSTALLATION.md) - Complete setup instructions
- ❓ [FAQ](FAQ.md) - Comprehensive question and answer guide
- 🔧 [Troubleshooting](TROUBLESHOOTING.md) - Detailed problem solving

### External Resources
- 🔗 [ezdxf Documentation](https://ezdxf.readthedocs.io/)
- 🔗 [FreeCAD Wiki](https://wiki.freecadweb.org/)
- 🔗 [PySide6 Documentation](https://doc.qt.io/qtforpython/)

---

*Keep this reference handy for quick problem solving!*

*For detailed explanations, see the full documentation in the [docs](README.md) folder.*
