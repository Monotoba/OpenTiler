# OpenTiler Installers

This directory contains all the installation and build scripts for creating OpenTiler installers across different platforms.

## 📁 Directory Contents

### 🪟 Windows Installers
- **`create_windows_exe.py`** - Simple standalone executable creator (recommended)
- **`build_windows_installer.py`** - Advanced installer with NSIS support
- **`build_installer.py`** - Professional MSI installer using cx_Freeze

### 🍎 macOS Installers
- **`create_macos_app.py`** - Native .app bundle and DMG creator (recommended)
- **`install_macos.sh`** - Automated source installation script

### 🐧 Linux Installers
- **`create_linux_packages.py`** - DEB and RPM package creator (recommended)
- **`install_linux.sh`** - Automated source installation script

### 📦 Build Dependencies
- **`requirements-build.txt`** - Build dependencies for all platforms

## 🚀 Quick Start

### Windows
```bash
# Install build dependencies
pip install -r installers/requirements-build.txt

# Create standalone executable (easiest)
python installers/create_windows_exe.py

# Or create advanced installer
python installers/build_windows_installer.py
```

### macOS
```bash
# Install build dependencies
pip install -r installers/requirements-build.txt

# Create .app bundle and DMG (recommended)
python installers/create_macos_app.py

# Or install from source
./installers/install_macos.sh
```

### Linux
```bash
# Install build dependencies
pip install -r installers/requirements-build.txt

# Create DEB and RPM packages (recommended)
python installers/create_linux_packages.py --format both

# Or install from source
./installers/install_linux.sh
```

## 📋 Output Files

### Windows
- `OpenTiler.exe` - Standalone executable
- `OpenTiler-1.0.0-Setup.exe` - NSIS installer
- `OpenTiler-1.0.0.msi` - MSI installer
- `install_opentiler.bat` - Batch installer
- `OpenTiler-Portable.zip` - Portable package

### macOS
- `OpenTiler.app` - Native application bundle
- `OpenTiler-1.0.0.dmg` - DMG installer
- `install_opentiler_macos.sh` - Installation script

### Linux
- `opentiler_1.0.0_all.deb` - Debian package
- `opentiler-1.0.0-1.noarch.rpm` - RPM package

## 🔧 Prerequisites

### All Platforms
```bash
pip install -r installers/requirements-build.txt
```

### Windows Additional
- **NSIS** (for MSI creation): Download from https://nsis.sourceforge.io/
- **Visual Studio Build Tools** (for some dependencies)

### macOS Additional
- **Xcode Command Line Tools**: `xcode-select --install`

### Linux Additional
- **fpm** (for DEB/RPM packages): `gem install fpm`

## 📖 Documentation

For detailed build instructions, see:
- **[BUILD_INSTRUCTIONS.md](../BUILD_INSTRUCTIONS.md)** - Complete build guide
- **[USER_MANUAL.md](../docs/user/USER_MANUAL.md)** - Installation instructions for end users

## 🎯 Recommended Usage

### For End Users
1. **Windows**: Download and run `OpenTiler.exe` or use the installer
2. **macOS**: Download and install `OpenTiler-1.0.0.dmg`
3. **Linux**: Install the appropriate `.deb` or `.rpm` package

### For Developers
1. **Windows**: Use `create_windows_exe.py` for simple builds
2. **macOS**: Use `create_macos_app.py` for native apps
3. **Linux**: Use `create_linux_packages.py` for distribution packages

## 🔍 Script Details

### Windows Scripts
- **create_windows_exe.py**: Creates standalone executable using PyInstaller
- **build_windows_installer.py**: Creates NSIS-based installer with registry integration
- **build_installer.py**: Creates professional MSI using cx_Freeze

### macOS Scripts
- **create_macos_app.py**: Creates native .app bundle using py2app or PyInstaller
- **install_macos.sh**: Automated installation with Homebrew and environment setup

### Linux Scripts
- **create_linux_packages.py**: Creates DEB/RPM packages using fpm
- **install_linux.sh**: Multi-distribution installation with package manager detection

## 🛠️ Build Environment

For best results, build on the target platform:
- **Windows**: Build on Windows for Windows installers
- **macOS**: Build on macOS for macOS applications
- **Linux**: Build on Linux for Linux packages

## 📞 Support

If you encounter issues with the installers:
1. Check the build logs for error messages
2. Ensure all prerequisites are installed
3. Review the troubleshooting section in BUILD_INSTRUCTIONS.md
4. Open an issue on GitHub with details about your environment

## 🎉 Success!

Once built, your installers will be ready for distribution to end users across all major desktop platforms!
