# OpenTiler FAQ

## Table of Contents
- [Installation Issues](#installation-issues)
- [DXF Support](#dxf-support)
- [FreeCAD Support](#freecad-support)
- [Common Errors](#common-errors)
- [Troubleshooting](#troubleshooting)
- [Platform-Specific Issues](#platform-specific-issues)

---

## Installation Issues

### Q: How do I install OpenTiler's dependencies?

**A:** OpenTiler requires Python 3.10+ and several optional dependencies for full functionality:

#### Core Dependencies (Required)
```bash
pip install PySide6 PyPDF2
```

#### CAD Format Dependencies (Optional)
```bash
# For DXF support
pip install ezdxf matplotlib

# FreeCAD requires separate installation (see FreeCAD section)
```

---

## DXF Support

### Q: How do I enable DXF import/export support?

**A:** Install the required Python packages:

#### Windows
```cmd
# Using pip
pip install ezdxf matplotlib

# Using conda
conda install -c conda-forge ezdxf matplotlib
```

#### Linux (Ubuntu/Debian)
```bash
# Using pip
pip install ezdxf matplotlib

# Using apt (if available)
sudo apt install python3-matplotlib
pip install ezdxf
```

#### macOS
```bash
# Using pip
pip install ezdxf matplotlib

# Using Homebrew + pip
brew install python
pip3 install ezdxf matplotlib
```

### Q: I get "DXF support not available" - how do I fix this?

**A:** Follow these steps:

1. **Verify installation:**
   ```bash
   python -c "import ezdxf; print('ezdxf version:', ezdxf.__version__)"
   python -c "import matplotlib; print('matplotlib version:', matplotlib.__version__)"
   ```

2. **If import fails, reinstall:**
   ```bash
   pip uninstall ezdxf matplotlib
   pip install ezdxf matplotlib
   ```

3. **Check virtual environment:**
   ```bash
   # Make sure you're in the correct environment
   which python
   pip list | grep -E "(ezdxf|matplotlib)"
   ```

### Q: DXF files won't open - what's wrong?

**A:** Common issues and solutions:

1. **File corruption:** Try opening the DXF in AutoCAD or LibreCAD first
2. **Version compatibility:** OpenTiler supports AutoCAD 2010+ format
3. **Large files:** Very large DXF files may take time to process
4. **Memory issues:** Close other applications and try again

---

## FreeCAD Support

### Q: How do I install FreeCAD for OpenTiler integration?

**A:** FreeCAD installation varies by platform:

#### Windows
1. **Download installer:**
   - Visit https://www.freecadweb.org/downloads.php
   - Download the Windows installer (64-bit recommended)
   - Run installer with default settings

2. **Add to PATH (optional):**
   - Add `C:\Program Files\FreeCAD 0.21\bin` to system PATH
   - Restart OpenTiler after installation

3. **Verify installation:**
   ```cmd
   # Test FreeCAD command
   "C:\Program Files\FreeCAD 0.21\bin\FreeCAD.exe" --version
   ```

#### Linux (Ubuntu/Debian)
```bash
# Method 1: APT package manager
sudo apt update
sudo apt install freecad

# Method 2: Snap package
sudo snap install freecad

# Method 3: AppImage (latest version)
wget https://github.com/FreeCAD/FreeCAD/releases/download/0.21.2/FreeCAD_0.21.2-Linux-x86_64.AppImage
chmod +x FreeCAD_0.21.2-Linux-x86_64.AppImage
sudo mv FreeCAD_0.21.2-Linux-x86_64.AppImage /usr/local/bin/freecad
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# Fedora
sudo dnf install freecad

# CentOS/RHEL (enable EPEL first)
sudo yum install epel-release
sudo yum install freecad
```

#### macOS
1. **Download DMG:**
   - Visit https://www.freecadweb.org/downloads.php
   - Download the macOS DMG file
   - Drag FreeCAD to Applications folder

2. **Command line access:**
   ```bash
   # Add to PATH in ~/.zshrc or ~/.bash_profile
   export PATH="/Applications/FreeCAD.app/Contents/MacOS:$PATH"
   ```

### Q: I get "FreeCAD support not available" - how do I fix this?

**A:** Troubleshooting steps:

1. **Check FreeCAD installation:**
   ```bash
   # Test if FreeCAD command exists
   which freecad
   freecad --version
   ```

2. **For snap installations:**
   ```bash
   # Check snap installation
   snap list | grep freecad
   /snap/bin/freecad --version
   ```

3. **Python module detection:**
   ```bash
   # Check if Python can find FreeCAD modules
   python -c "import sys; sys.path.append('/usr/lib/freecad/lib'); import FreeCAD"
   ```

4. **Restart OpenTiler** after installing FreeCAD

### Q: FreeCAD shows "Command-line only" - is this normal?

**A:** Yes! This is expected for most installations:

- **Full Python API:** Available when FreeCAD Python modules are accessible
- **Command-line only:** Normal for snap, AppImage, and standard installations
- **Functionality:** Both modes support file import/export operations
- **Performance:** Command-line mode works well for OpenTiler's needs

---

## Common Errors

### Q: "ModuleNotFoundError: No module named 'ezdxf'"

**A:** DXF dependencies not installed:
```bash
pip install ezdxf matplotlib
```

### Q: "QPixmap: Cannot create a QPixmap when no GUI is available"

**A:** Qt/GUI initialization issue:
1. Make sure you're running OpenTiler with a display
2. On Linux, check `DISPLAY` environment variable
3. Try running with `xvfb-run` if on headless system

### Q: "Failed to load module 'xapp-gtk3-module'"

**A:** This is a harmless warning on some Linux systems:
```bash
# Optional: Install the module to suppress warning
sudo apt install xapp-gtk3-module
```

### Q: Application crashes when opening DXF/FreeCAD files

**A:** Memory or compatibility issue:
1. **Check file size:** Very large files may exceed memory
2. **Update dependencies:** Ensure latest versions installed
3. **Check file format:** Verify file isn't corrupted
4. **Restart application:** Clear any cached state

---

## Troubleshooting

### Q: How do I check what dependencies are installed?

**A:** Use these diagnostic commands:

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(PySide6|ezdxf|matplotlib)"

# Test OpenTiler dependencies
python -c "
try:
    import PySide6; print('✅ PySide6:', PySide6.__version__)
except ImportError: print('❌ PySide6 not available')

try:
    import ezdxf; print('✅ ezdxf:', ezdxf.__version__)
except ImportError: print('❌ ezdxf not available')

try:
    import matplotlib; print('✅ matplotlib:', matplotlib.__version__)
except ImportError: print('❌ matplotlib not available')
"
```

### Q: How do I enable debug mode?

**A:** Run OpenTiler with debug output:

```bash
# Enable Python debug mode
python -v main.py

# Enable Qt debug output
export QT_LOGGING_RULES="*=true"
python main.py

# Check OpenTiler format support
python -c "
from opentiler.formats.dxf_handler import DXFHandler
from opentiler.formats.freecad_handler import FreeCADHandler

print('DXF Support:', DXFHandler.is_available())
print('FreeCAD Support:', FreeCADHandler.is_available())
print('FreeCAD Status:', FreeCADHandler.get_availability_status())
"
```

### Q: Virtual environment issues?

**A:** Virtual environment troubleshooting:

```bash
# Check if in virtual environment
echo $VIRTUAL_ENV

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Recreate virtual environment if needed
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Platform-Specific Issues

### Windows

#### Q: "python is not recognized as an internal or external command"

**A:** Python not in PATH:
1. Reinstall Python with "Add to PATH" option checked
2. Or manually add Python to PATH:
   - Add `C:\Python310` and `C:\Python310\Scripts` to PATH
   - Restart command prompt

#### Q: Permission denied errors during installation

**A:** Run as administrator:
```cmd
# Run Command Prompt as Administrator
pip install ezdxf matplotlib
```

### Linux

#### Q: "Permission denied" when installing packages

**A:** Use user installation or virtual environment:
```bash
# User installation
pip install --user ezdxf matplotlib

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install ezdxf matplotlib
```

#### Q: Missing development headers

**A:** Install development packages:
```bash
# Ubuntu/Debian
sudo apt install python3-dev python3-pip

# CentOS/RHEL
sudo yum install python3-devel python3-pip
```

### macOS

#### Q: "command not found: python"

**A:** Python not installed or not in PATH:
```bash
# Install Python via Homebrew
brew install python

# Or use python3 explicitly
python3 main.py
```

#### Q: SSL certificate errors during pip install

**A:** Update certificates:
```bash
# Update certificates
/Applications/Python\ 3.10/Install\ Certificates.command

# Or use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org ezdxf matplotlib
```

---

## Getting Help

### Q: Where can I get more help?

**A:** Additional resources:

1. **Check logs:** Look for error messages in terminal output
2. **GitHub Issues:** Report bugs at [project repository]
3. **Documentation:** Check other files in the `docs/` folder
4. **Dependencies:**
   - ezdxf documentation: https://ezdxf.readthedocs.io/
   - FreeCAD documentation: https://wiki.freecadweb.org/
   - PySide6 documentation: https://doc.qt.io/qtforpython/

### Q: How do I report a bug?

**A:** Include this information:

1. **System info:**
   ```bash
   python --version
   pip list | grep -E "(PySide6|ezdxf|matplotlib)"
   ```

2. **Error message:** Full traceback from terminal

3. **Steps to reproduce:** Exact steps that cause the issue

4. **File info:** Type and size of file causing problems (if applicable)

---

## Advanced Troubleshooting

### Q: How do I completely reset OpenTiler?

**A:** Complete reset procedure:

```bash
# 1. Remove virtual environment
rm -rf venv

# 2. Clear any cached files
rm -rf __pycache__ opentiler/__pycache__ opentiler/*/__pycache__

# 3. Recreate environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# 4. Reinstall dependencies
pip install PySide6 PyPDF2 ezdxf matplotlib
```

### Q: Performance issues with large files?

**A:** Optimization tips:

1. **Memory management:**
   - Close other applications
   - Use 64-bit Python
   - Consider file size limits (>100MB may be slow)

2. **DXF optimization:**
   - Simplify DXF files in CAD software first
   - Remove unnecessary layers and objects
   - Use DXF 2010 format for best compatibility

3. **Image optimization:**
   - Reduce image resolution if possible
   - Use PNG instead of TIFF for better performance
   - Consider splitting very large images

### Q: Network/firewall issues during installation?

**A:** Bypass network restrictions:

```bash
# Use different index
pip install -i https://pypi.python.org/simple/ ezdxf matplotlib

# Use proxy
pip install --proxy http://proxy.company.com:8080 ezdxf matplotlib

# Download manually and install
pip download ezdxf matplotlib
pip install ezdxf-*.whl matplotlib-*.whl
```

---

## Development and Customization

### Q: How do I modify OpenTiler for my needs?

**A:** Development setup:

```bash
# 1. Clone/download source code
git clone [repository-url]
cd OpenTiler

# 2. Create development environment
python -m venv dev-env
source dev-env/bin/activate

# 3. Install in development mode
pip install -e .
pip install ezdxf matplotlib

# 4. Make changes to source code
# 5. Test changes
python main.py
```

### Q: How do I add support for new file formats?

**A:** Create a new format handler:

1. **Create handler file:** `opentiler/formats/new_format_handler.py`
2. **Implement required methods:** `load_format()`, `save_as_format()`
3. **Update main viewer:** Add format to `viewer.py`
4. **Update dialogs:** Add to Save-As and import dialogs
5. **Test thoroughly:** Verify import/export functionality

### Q: Can I use OpenTiler as a library?

**A:** Yes! Example usage:

```python
from opentiler.formats.dxf_handler import DXFHandler
from opentiler.formats.freecad_handler import FreeCADHandler

# Load DXF file
dxf_handler = DXFHandler()
pixmap = dxf_handler.load_dxf("drawing.dxf")

# Convert and save
freecad_handler = FreeCADHandler()
freecad_handler.save_as_freecad(pixmap, "output.FCStd", scale_factor=0.1)
```

---

## Integration with Other Software

### Q: How do I use OpenTiler with AutoCAD?

**A:** AutoCAD workflow:

1. **Export from AutoCAD:**
   - Save as DXF (AutoCAD 2010 or later)
   - Or export as high-resolution PDF

2. **Process in OpenTiler:**
   - Load DXF/PDF file
   - Apply scaling using known measurements
   - Export tiles for printing

3. **Return to AutoCAD:**
   - Use Save-As to export scaled DXF
   - Import back into AutoCAD if needed

### Q: Integration with FreeCAD workflows?

**A:** FreeCAD integration:

1. **From FreeCAD:**
   - Save as .FCStd file
   - Or export as PDF/SVG

2. **In OpenTiler:**
   - Load .FCStd file (command-line mode)
   - Apply scaling and generate tiles
   - Save-As .FCStd with scale information

3. **Back to FreeCAD:**
   - Open saved .FCStd file
   - Scale information preserved in annotations

### Q: Working with architectural software?

**A:** Professional workflow:

1. **Supported formats:**
   - PDF exports from Revit, ArchiCAD, etc.
   - DXF exports from any CAD software
   - High-resolution image exports

2. **Best practices:**
   - Use PDF for best quality
   - Include scale references in original drawings
   - Export at highest available resolution

3. **Quality control:**
   - Verify scale accuracy after import
   - Use measurement tools to confirm dimensions
   - Check tile alignment before printing

---

## Printing and Assembly

### Q: Best practices for printing tiles?

**A:** Professional printing tips:

1. **Printer settings:**
   - Use highest quality/resolution
   - Disable scaling ("Actual Size" or "100%")
   - Use borderless printing if available

2. **Paper selection:**
   - Use consistent paper type across all tiles
   - Consider paper weight for durability
   - Matte finish reduces glare for assembly

3. **Quality control:**
   - Print test page first
   - Measure scale line on printed output
   - Verify dimensions match expected values

### Q: How do I assemble printed tiles?

**A:** Assembly guidance:

1. **Preparation:**
   - Lay out tiles in order
   - Check page numbers and orientation
   - Ensure all tiles printed at same scale

2. **Alignment:**
   - Use crop marks for precise alignment
   - Overlap tiles at gutter lines
   - Use scale references to verify accuracy

3. **Joining:**
   - Use removable tape for temporary assembly
   - Consider lamination for permanent assembly
   - Trim excess margins if needed

### Q: Scale verification after printing?

**A:** Verification process:

1. **Measure scale line:**
   - Use ruler to measure printed scale line
   - Should match the measurement text exactly
   - If incorrect, check printer scaling settings

2. **Check known dimensions:**
   - Measure known features in the drawing
   - Compare to expected real-world dimensions
   - Adjust scale factor if needed

3. **Tile alignment:**
   - Verify tiles align properly at gutters
   - Check that features continue across tile boundaries
   - Ensure no gaps or overlaps in content

---

## Frequently Asked Questions Summary

### Quick Reference

| Issue | Solution |
|-------|----------|
| DXF not working | `pip install ezdxf matplotlib` |
| FreeCAD not detected | Install FreeCAD, restart OpenTiler |
| Import fails | Check file format and size |
| Slow performance | Reduce file size, close other apps |
| Print scaling wrong | Use "Actual Size" in printer settings |
| Tiles don't align | Check gutter settings and crop marks |
| Python not found | Add Python to PATH or use full path |
| Permission errors | Use virtual environment or --user flag |

### Emergency Fixes

```bash
# Complete reinstall
pip uninstall PySide6 PyPDF2 ezdxf matplotlib
pip install PySide6 PyPDF2 ezdxf matplotlib

# Reset virtual environment
rm -rf venv && python -m venv venv
source venv/bin/activate && pip install PySide6 PyPDF2 ezdxf matplotlib

# Test installation
python -c "from opentiler.formats.dxf_handler import DXFHandler; print('DXF:', DXFHandler.is_available())"
```

---

*Last updated: December 2024*
*For more help, check the GitHub repository or create an issue with your specific problem.*
