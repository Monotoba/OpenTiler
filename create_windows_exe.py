#!/usr/bin/env python3
"""
Simple Windows Executable Creator for OpenTiler

This script creates a standalone Windows executable using PyInstaller.
Run this on a Windows machine to create the .exe file.

Usage:
    python create_windows_exe.py
"""

import sys
import os
import subprocess
from pathlib import Path

def create_windows_executable():
    """Create Windows executable using PyInstaller."""
    
    print("🚀 Creating OpenTiler Windows Executable...")
    
    # Check if we're on Windows
    if sys.platform != "win32":
        print("⚠️  This script should be run on Windows to create Windows executables.")
        print("   You can still run it to generate the spec file for later use.")
    
    # Install PyInstaller if not available
    try:
        import PyInstaller
        print("✅ PyInstaller is available")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Create the PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "OpenTiler",
        "--onefile",  # Single executable file
        "--windowed",  # No console window
        "--clean",
        "--noconfirm",
        
        # Add data files
        "--add-data", "opentiler/assets;opentiler/assets",
        "--add-data", "docs;docs",
        "--add-data", "README.md;.",
        "--add-data", "LICENSE;.",
        
        # Hidden imports for PySide6
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui", 
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PySide6.QtPrintSupport",
        
        # Hidden imports for OpenTiler modules
        "--hidden-import", "opentiler",
        "--hidden-import", "opentiler.viewer",
        "--hidden-import", "opentiler.dialogs",
        "--hidden-import", "opentiler.exporter",
        "--hidden-import", "opentiler.settings",
        "--hidden-import", "opentiler.utils",
        "--hidden-import", "opentiler.formats",
        
        # Exclude unnecessary modules
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "scipy",
        "--exclude-module", "pandas",
        
        "main.py"
    ]
    
    # Add icon if available
    icon_path = Path("opentiler/assets/app_icon.ico")
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
        print(f"✅ Using icon: {icon_path}")
    else:
        print("ℹ️  No app icon found (opentiler/assets/app_icon.ico)")
    
    print("🔨 Building executable...")
    print("   This may take several minutes...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executable created successfully!")
        
        # Check if the executable was created
        exe_path = Path("dist/OpenTiler.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executable: {exe_path}")
            print(f"📏 Size: {size_mb:.1f} MB")
            
            # Create a simple installer batch file
            create_installer_batch()
            
        else:
            print("❌ Executable not found in expected location")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    return True

def create_installer_batch():
    """Create a simple batch file installer."""
    
    batch_content = '''@echo off
echo OpenTiler Installation
echo =====================

set "INSTALL_DIR=%PROGRAMFILES%\\OpenTiler"
set "EXE_PATH=%~dp0OpenTiler.exe"

echo.
echo Installing OpenTiler to: %INSTALL_DIR%
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    if errorlevel 1 (
        echo ERROR: Could not create installation directory.
        echo Please run as Administrator.
        pause
        exit /b 1
    )
)

REM Copy executable
copy "%EXE_PATH%" "%INSTALL_DIR%\\OpenTiler.exe"
if errorlevel 1 (
    echo ERROR: Could not copy executable.
    echo Please run as Administrator.
    pause
    exit /b 1
)

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\OpenTiler.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\OpenTiler.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'OpenTiler - Professional Document Scaling and Tiling'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\OpenTiler" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\OpenTiler"
)
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\OpenTiler\\OpenTiler.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\OpenTiler.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'OpenTiler - Professional Document Scaling and Tiling'; $Shortcut.Save()"

echo.
echo ✅ Installation completed successfully!
echo.
echo OpenTiler has been installed to: %INSTALL_DIR%
echo Desktop shortcut created: %USERPROFILE%\\Desktop\\OpenTiler.lnk
echo Start menu shortcut created in OpenTiler folder
echo.
echo You can now run OpenTiler from:
echo - Desktop shortcut
echo - Start menu
echo - Or directly: %INSTALL_DIR%\\OpenTiler.exe
echo.
pause
'''
    
    batch_path = Path("dist/install_opentiler.bat")
    with open(batch_path, 'w') as f:
        f.write(batch_content)
    
    print(f"📝 Installer created: {batch_path}")
    print("   Users can run this batch file to install OpenTiler")

def create_portable_package():
    """Create a portable ZIP package."""
    
    import zipfile
    
    print("📦 Creating portable package...")
    
    zip_path = Path("dist/OpenTiler-Portable.zip")
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add executable
            exe_path = Path("dist/OpenTiler.exe")
            if exe_path.exists():
                zipf.write(exe_path, "OpenTiler.exe")
            
            # Add documentation
            docs = ["README.md", "LICENSE"]
            for doc in docs:
                if Path(doc).exists():
                    zipf.write(doc, doc)
            
            # Add user manual
            user_manual = Path("docs/user/USER_MANUAL.md")
            if user_manual.exists():
                zipf.write(user_manual, "USER_MANUAL.md")
        
        print(f"✅ Portable package created: {zip_path}")
        
    except Exception as e:
        print(f"❌ Failed to create portable package: {e}")

def main():
    """Main function."""
    
    print("OpenTiler Windows Executable Builder")
    print("====================================")
    print()
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("❌ main.py not found. Please run this script from the OpenTiler project root.")
        return 1
    
    # Create executable
    if create_windows_executable():
        create_portable_package()
        
        print()
        print("🎉 Build completed successfully!")
        print()
        print("📁 Output files in dist/ directory:")
        print("   - OpenTiler.exe (standalone executable)")
        print("   - install_opentiler.bat (installer script)")
        print("   - OpenTiler-Portable.zip (portable package)")
        print()
        print("📋 Distribution options:")
        print("   1. Share OpenTiler.exe directly (standalone)")
        print("   2. Share install_opentiler.bat + OpenTiler.exe (installer)")
        print("   3. Share OpenTiler-Portable.zip (portable package)")
        
        return 0
    else:
        print("❌ Build failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
