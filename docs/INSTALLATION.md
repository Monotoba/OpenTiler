# OpenTiler Installation Guide

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Operating System: Windows 10+, macOS 10.14+, or Linux
- May run on earlier versions of Windows and macOS, but not tested.

### Basic Installation
```bash
# 1. Create virtual environment (recommended)
python -m venv opentiler-env

# 2. Activate virtual environment
# Linux/Mac:
source opentiler-env/bin/activate
# Windows:
opentiler-env\Scripts\activate

# 3. Install core dependencies
pip install PySide6 PyPDF2

# 4. Install optional CAD dependencies
pip install ezdxf matplotlib

# 5. Run OpenTiler
python main.py
```

---

## Detailed Platform Instructions

### Windows Installation

#### Method 1: Using Python from python.org (Recommended)

1. **Install Python:**
   - Download Python 3.10+ from https://python.org/downloads/
   - ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
   - Choose "Install for all users" if you have admin rights

2. **Verify Python installation:**
   ```cmd
   python --version
   pip --version
   ```

3. **Create project directory:**
   ```cmd
   mkdir C:\OpenTiler
   cd C:\OpenTiler
   ```

4. **Set up virtual environment:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

5. **Install dependencies:**

   **Basic Installation (Recommended for most users):**
   ```cmd
   pip install -r requirements.txt
   ```

   **Full Installation (All features):**
   ```cmd
   pip install -r requirements.txt
   pip install -r requirements-optional.txt
   ```

   **Developer Installation:**
   ```cmd
   pip install -r requirements-dev.txt
   ```

6. **Download OpenTiler source code** and run:
   ```cmd
   python main.py
   ```

#### Method 2: Using Anaconda/Miniconda

1. **Install Anaconda:** Download from https://anaconda.com/products/distribution

2. **Create conda environment:**
   ```cmd
   conda create -n opentiler python=3.10
   conda activate opentiler
   ```

3. **Install dependencies:**
   ```cmd
   conda install -c conda-forge pyside6
   pip install -r requirements.txt
   pip install -r requirements-optional.txt
   ```

#### Windows Troubleshooting

**Issue: "python is not recognized"**
```cmd
# Add Python to PATH manually:
# 1. Open System Properties → Environment Variables
# 2. Add to PATH: C:\Python310 and C:\Python310\Scripts
# 3. Restart Command Prompt
```

**Issue: Permission denied**
```cmd
# Run Command Prompt as Administrator, or use:
pip install --user PySide6 PyPDF2 ezdxf matplotlib
```

### Linux Installation

#### Ubuntu/Debian

1. **Update system:**
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. **Install Python and pip:**
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```

3. **Install system dependencies:**
   ```bash
   # For Qt/GUI support
   sudo apt install python3-pyqt5 python3-pyqt5.qtsvg

   # For matplotlib
   sudo apt install python3-matplotlib

   # Optional: For FreeCAD
   sudo apt install freecad
   ```

4. **Create virtual environment:**
   ```bash
   python3 -m venv opentiler-env
   source opentiler-env/bin/activate
   ```

5. **Install Python dependencies:**

   **Basic Installation:**
   ```bash
   pip install -r requirements.txt
   ```

   **Full Installation (All features):**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-optional.txt
   ```

#### CentOS/RHEL/Fedora

1. **Install Python:**
   ```bash
   # CentOS/RHEL
   sudo yum install python3 python3-pip

   # Fedora
   sudo dnf install python3 python3-pip
   ```

2. **Install development tools:**
   ```bash
   # CentOS/RHEL
   sudo yum groupinstall "Development Tools"
   sudo yum install python3-devel

   # Fedora
   sudo dnf groupinstall "Development Tools"
   sudo dnf install python3-devel
   ```

3. **Continue with virtual environment setup** (same as Ubuntu)

#### Arch Linux

```bash
# Install Python and dependencies
sudo pacman -S python python-pip python-virtualenv

# Optional: FreeCAD
sudo pacman -S freecad

# Create virtual environment and install packages
python -m venv opentiler-env
source opentiler-env/bin/activate
pip install PySide6 PyPDF2 ezdxf matplotlib
```

### macOS Installation

#### Method 1: Using Homebrew (Recommended)

1. **Install Homebrew:**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python:**
   ```bash
   brew install python
   ```

3. **Create virtual environment:**
   ```bash
   python3 -m venv opentiler-env
   source opentiler-env/bin/activate
   ```

4. **Install dependencies:**

   **Basic Installation:**
   ```bash
   pip install -r requirements.txt
   ```

   **Full Installation (All features):**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-optional.txt
   ```

5. **Optional: Install FreeCAD:**
   ```bash
   brew install --cask freecad
   ```

#### Method 2: Using MacPorts

```bash
# Install MacPorts, then:
sudo port install python310 py310-pip
sudo port select --set python3 python310

# Continue with virtual environment setup
```

#### Method 3: Using python.org installer

1. Download Python 3.10+ from https://python.org/downloads/mac-osx/
2. Install the package
3. Continue with virtual environment setup

#### macOS Troubleshooting

**Issue: SSL certificate errors**
```bash
# Update certificates
/Applications/Python\ 3.10/Install\ Certificates.command

# Or install with trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org PySide6 PyPDF2 ezdxf matplotlib
```

**Issue: Command not found**
```bash
# Add to ~/.zshrc or ~/.bash_profile:
export PATH="/usr/local/bin:$PATH"
export PATH="/opt/homebrew/bin:$PATH"  # For Apple Silicon Macs
```

---

## FreeCAD Installation

### Windows
1. Download from https://www.freecadweb.org/downloads.php
2. Run installer with default settings
3. Optional: Add to PATH for command-line access

### Linux
```bash
# Ubuntu/Debian
sudo apt install freecad

# Or use Snap
sudo snap install freecad

# Or download AppImage
wget https://github.com/FreeCAD/FreeCAD/releases/download/0.21.2/FreeCAD_0.21.2-Linux-x86_64.AppImage
chmod +x FreeCAD_0.21.2-Linux-x86_64.AppImage
sudo mv FreeCAD_0.21.2-Linux-x86_64.AppImage /usr/local/bin/freecad
```

### macOS
1. Download DMG from https://www.freecadweb.org/downloads.php
2. Drag FreeCAD to Applications folder
3. Optional: Add to PATH in ~/.zshrc:
   ```bash
   export PATH="/Applications/FreeCAD.app/Contents/MacOS:$PATH"
   ```

---

## Verification

### Test Installation
```bash
# Activate virtual environment
source opentiler-env/bin/activate  # Linux/Mac
# or opentiler-env\Scripts\activate  # Windows

# Test core functionality
python -c "
import sys
print('Python version:', sys.version)

try:
    import PySide6
    print('✅ PySide6:', PySide6.__version__)
except ImportError:
    print('❌ PySide6 not available')

try:
    import PyPDF2
    print('✅ PyPDF2 available')
except ImportError:
    print('❌ PyPDF2 not available')

try:
    import ezdxf
    print('✅ ezdxf:', ezdxf.__version__)
except ImportError:
    print('❌ ezdxf not available')

try:
    import matplotlib
    print('✅ matplotlib:', matplotlib.__version__)
except ImportError:
    print('❌ matplotlib not available')
"
```

### Test OpenTiler
```bash
# Run OpenTiler
python main.py

# Test format support
python -c "
from opentiler.formats.dxf_handler import DXFHandler
from opentiler.formats.freecad_handler import FreeCADHandler

print('DXF Support:', DXFHandler.is_available())
print('FreeCAD Support:', FreeCADHandler.is_available())
print('FreeCAD Status:', FreeCADHandler.get_availability_status())
"
```

---

## Common Installation Issues

### Python Version Issues
```bash
# Check Python version
python --version

# If too old, install newer version:
# Windows: Download from python.org
# Linux: sudo apt install python3.10
# macOS: brew install python@3.10
```

### Virtual Environment Issues
```bash
# If venv module not available:
# Linux: sudo apt install python3-venv
# Or use virtualenv: pip install virtualenv

# Create with virtualenv:
virtualenv opentiler-env
```

### Dependency Conflicts
```bash
# Clear pip cache
pip cache purge

# Upgrade pip
pip install --upgrade pip

# Force reinstall
pip install --force-reinstall PySide6 PyPDF2 ezdxf matplotlib
```

### Qt/GUI Issues
```bash
# Linux: Install Qt dependencies
sudo apt install qt5-default libqt5gui5 libqt5widgets5

# Set Qt platform if needed
export QT_QPA_PLATFORM=xcb  # Linux
```

---

## Next Steps

After successful installation:

1. **Read the User Guide:** `docs/USER_GUIDE.md`
2. **Check the FAQ:** `docs/FAQ.md` for troubleshooting
3. **Try the examples:** Load a sample PDF and test scaling
4. **Configure settings:** Adjust preferences in Settings menu

---

*For additional help, see FAQ.md or create an issue on GitHub.*
