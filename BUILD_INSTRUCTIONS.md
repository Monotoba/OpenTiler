# OpenTiler Build Instructions

## Building Installers for OpenTiler

This document provides instructions for building platform-specific installers for OpenTiler.

## Prerequisites

### All Platforms
```bash
# Install build dependencies
pip install -r installers/requirements-build.txt
```

### Windows Additional Requirements
- **NSIS** (for MSI creation): Download from https://nsis.sourceforge.io/
- **Visual Studio Build Tools** (for some dependencies)

### macOS Additional Requirements
- **Xcode Command Line Tools**: `xcode-select --install`

### Linux Additional Requirements
- **fpm** (for DEB/RPM packages): `gem install fpm`

## Quick Build (Recommended)

### Windows Executable (Easiest)
```bash
# Simple method - creates standalone .exe and installer
python installers/create_windows_exe.py
```

### Windows Installer (Advanced)
```bash
# Advanced method - creates batch installer and portable ZIP
python installers/build_windows_installer.py

# Professional MSI using cx_Freeze (requires Windows)
python installers/build_installer.py --platform windows --method cx_freeze
```

### macOS Application (Recommended)
```bash
# Simple method - creates .app bundle and DMG
python installers/create_macos_app.py
```

### macOS Installation from Source
```bash
# Install from source with full setup
./installers/install_macos.sh
```

### Linux Packages (Recommended)
```bash
# Create DEB and RPM packages
python installers/create_linux_packages.py --format both
```

### Linux Installation from Source
```bash
# Install from source with full setup
./installers/install_linux.sh
```

## Manual Build Process

### 1. Windows MSI Installer

#### Method A: Using cx_Freeze (Recommended)
```bash
# Install cx_Freeze
pip install cx_Freeze

# Run the advanced builder
python installers/build_installer.py --platform windows --method cx_freeze
```

#### Method B: Using PyInstaller + NSIS
```bash
# Step 1: Build executable
python installers/build_windows_installer.py

# Step 2: Install NSIS from https://nsis.sourceforge.io/

# Step 3: Compile installer
cd installer
makensis installer.nsi
```

#### Method C: Simple Batch Installer
```bash
# Creates install.bat and portable ZIP
python installers/build_windows_installer.py
```

### 2. macOS Application and DMG Package

#### Method A: Using create_macos_app.py (Recommended)
```bash
# Install dependencies
pip install py2app pyinstaller dmgbuild

# Build app and DMG
python installers/create_macos_app.py
```

#### Method B: Manual py2app Build
```bash
# Install py2app
pip install py2app

# Create setup.py for py2app
python setup.py py2app

# Create DMG
hdiutil create -volname "OpenTiler" -srcfolder dist/OpenTiler.app -ov -format UDZO OpenTiler-1.0.0.dmg
```

#### Method C: Installation from Source
```bash
# Install from source with full environment setup
./installers/install_macos.sh
```

### 3. Linux Packages

#### DEB Package (Ubuntu/Debian)
```bash
# Install fpm
gem install fpm

# Build DEB package
fpm -s python -t deb -n opentiler -v 1.0.0 \
    --description "Professional Document Scaling and Tiling Application" \
    --url "https://github.com/Monotoba/OpenTiler" \
    --maintainer "Randall Morgan <randall@example.com>" \
    --license "MIT" \
    --depends python3 \
    --depends python3-pip \
    setup.py
```

#### RPM Package (RedHat/CentOS/Fedora)
```bash
# Build RPM package
fpm -s python -t rpm -n opentiler -v 1.0.0 \
    --description "Professional Document Scaling and Tiling Application" \
    --url "https://github.com/Monotoba/OpenTiler" \
    --maintainer "Randall Morgan <randall@example.com>" \
    --license "MIT" \
    --depends python3 \
    --depends python3-pip \
    setup.py
```

## Output Files

### Windows
- `OpenTiler-1.0.0-Setup.exe` (NSIS installer)
- `OpenTiler-1.0.0.msi` (MSI installer)
- `install.bat` (Simple batch installer)
- `OpenTiler-1.0.0-Portable.zip` (Portable version)

### macOS
- `OpenTiler-1.0.0.dmg` (DMG package)
- `OpenTiler.app` (Application bundle)

### Linux
- `opentiler_1.0.0_all.deb` (Debian package)
- `opentiler-1.0.0-1.noarch.rpm` (RPM package)

## Testing Installers

### Windows
1. **MSI/EXE**: Right-click → "Run as administrator"
2. **Batch**: Right-click → "Run as administrator"
3. **Portable**: Extract ZIP and run OpenTiler.exe

### macOS
1. **DMG**: Double-click to mount, drag to Applications
2. **App**: Double-click to run (may need to allow in Security preferences)

### Linux
```bash
# DEB package
sudo dpkg -i opentiler_1.0.0_all.deb
sudo apt-get install -f  # Fix dependencies if needed

# RPM package
sudo rpm -i opentiler-1.0.0-1.noarch.rpm
```

## Troubleshooting

### Common Issues

#### Windows: "Missing DLL" errors
- Install Visual C++ Redistributable
- Use `--add-binary` flag in PyInstaller for specific DLLs

#### macOS: "App is damaged" error
- Code sign the application: `codesign -s "Developer ID" OpenTiler.app`
- Or allow unsigned apps in Security preferences

#### Linux: Dependency issues
- Install system dependencies: `sudo apt-get install python3-dev python3-pip`
- Use virtual environment for clean builds

### Build Environment

#### Recommended Build Environment
```bash
# Create clean build environment
python -m venv build_env
source build_env/bin/activate  # Linux/macOS
build_env\Scripts\activate     # Windows

# Install requirements
pip install -r requirements-build.txt

# Build installer
python build_windows_installer.py
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Build Installers

on: [push, release]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements-build.txt
      - run: python build_windows_installer.py
      - uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: installer/
```

## Distribution

### GitHub Releases
1. Create release tag: `git tag v1.0.0`
2. Push tag: `git push origin v1.0.0`
3. Upload installer files to GitHub release

### Package Repositories
- **Windows**: Consider Windows Package Manager (winget)
- **macOS**: Consider Homebrew cask
- **Linux**: Consider Snap, Flatpak, or distribution repositories

---

For more information, see the [Developer Manual](docs/developer/DEVELOPER_MANUAL.md).
