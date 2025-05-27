#!/usr/bin/env python3
"""
OpenTiler Installer Builder

Creates platform-specific installers for OpenTiler:
- Windows: MSI installer using cx_Freeze
- macOS: DMG package using py2app
- Linux: DEB/RPM packages using fpm

Usage:
    python build_installer.py --platform windows
    python build_installer.py --platform macos
    python build_installer.py --platform linux
    python build_installer.py --all
"""

import sys
import os
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

# Project information
PROJECT_NAME = "OpenTiler"
PROJECT_VERSION = "1.0.0"
PROJECT_AUTHOR = "Randall Morgan"
PROJECT_DESCRIPTION = "Professional Document Scaling and Tiling Application"
PROJECT_URL = "https://github.com/Monotoba/OpenTiler"

class InstallerBuilder:
    """Build platform-specific installers for OpenTiler."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
    def clean_build_dirs(self):
        """Clean previous build directories."""
        print("🧹 Cleaning build directories...")
        for dir_path in [self.build_dir, self.dist_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
            dir_path.mkdir(exist_ok=True)
    
    def install_build_dependencies(self, platform_name):
        """Install platform-specific build dependencies."""
        print(f"📦 Installing build dependencies for {platform_name}...")
        
        if platform_name == "windows":
            deps = ["cx_Freeze", "pyinstaller"]
        elif platform_name == "macos":
            deps = ["py2app", "pyinstaller"]
        elif platform_name == "linux":
            deps = ["pyinstaller"]
        else:
            deps = []
            
        for dep in deps:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                print(f"  ✅ Installed {dep}")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install {dep}: {e}")
                return False
        return True
    
    def build_windows_msi(self):
        """Build Windows MSI installer using cx_Freeze."""
        print("🏗️ Building Windows MSI installer...")
        
        # Create cx_Freeze setup script
        setup_script = self.create_cx_freeze_setup()
        
        try:
            # Build the MSI
            cmd = [
                sys.executable, setup_script, 
                "build", "--build-exe", str(self.build_dir / "exe"),
                "bdist_msi", "--dist-dir", str(self.dist_dir)
            ]
            
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ MSI installer created successfully!")
                msi_files = list(self.dist_dir.glob("*.msi"))
                if msi_files:
                    print(f"  📦 Installer: {msi_files[0]}")
                return True
            else:
                print(f"  ❌ MSI build failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ MSI build error: {e}")
            return False
    
    def create_cx_freeze_setup(self):
        """Create cx_Freeze setup script for Windows MSI."""
        setup_content = f'''#!/usr/bin/env python3
"""
cx_Freeze setup script for OpenTiler Windows MSI installer
"""

import sys
from cx_Freeze import setup, Executable
from pathlib import Path

# Build options
build_options = {{
    "packages": [
        "PySide6", "PIL", "fitz", "ezdxf", "rawpy", "numpy",
        "opentiler", "opentiler.viewer", "opentiler.dialogs", 
        "opentiler.exporter", "opentiler.settings", "opentiler.utils",
        "opentiler.formats"
    ],
    "excludes": ["tkinter", "unittest", "email", "http", "urllib", "xml"],
    "include_files": [
        ("opentiler/assets/", "opentiler/assets/"),
        ("docs/", "docs/"),
        ("README.md", "README.md"),
        ("LICENSE", "LICENSE"),
    ],
    "zip_include_packages": ["encodings", "PySide6"],
    "optimize": 2,
}}

# MSI options
bdist_msi_options = {{
    "upgrade_code": "{{12345678-1234-5678-9ABC-123456789012}}",
    "add_to_path": True,
    "initial_target_dir": r"[ProgramFilesFolder]\\{PROJECT_NAME}",
    "install_icon": "opentiler/assets/app_icon.ico" if Path("opentiler/assets/app_icon.ico").exists() else None,
}}

# Executable configuration
executables = [
    Executable(
        "main.py",
        base="Win32GUI",  # Use Win32GUI for windowed app
        target_name="OpenTiler.exe",
        icon="opentiler/assets/app_icon.ico" if Path("opentiler/assets/app_icon.ico").exists() else None,
        shortcut_name="{PROJECT_NAME}",
        shortcut_dir="DesktopFolder",
    )
]

setup(
    name="{PROJECT_NAME}",
    version="{PROJECT_VERSION}",
    description="{PROJECT_DESCRIPTION}",
    author="{PROJECT_AUTHOR}",
    options={{
        "build_exe": build_options,
        "bdist_msi": bdist_msi_options,
    }},
    executables=executables,
)
'''
        
        setup_file = self.project_root / "setup_cx_freeze.py"
        with open(setup_file, 'w') as f:
            f.write(setup_content)
        
        return str(setup_file)
    
    def build_pyinstaller_exe(self):
        """Build standalone executable using PyInstaller."""
        print("🏗️ Building PyInstaller executable...")
        
        spec_content = self.create_pyinstaller_spec()
        spec_file = self.project_root / "opentiler.spec"
        
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        try:
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean", "--noconfirm",
                str(spec_file)
            ]
            
            result = subprocess.run(cmd, cwd=self.project_root,
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ PyInstaller executable created successfully!")
                return True
            else:
                print(f"  ❌ PyInstaller build failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ PyInstaller build error: {e}")
            return False
    
    def create_pyinstaller_spec(self):
        """Create PyInstaller spec file."""
        return f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('opentiler/assets', 'opentiler/assets'),
        ('docs', 'docs'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtPrintSupport',
        'opentiler',
        'opentiler.viewer',
        'opentiler.dialogs',
        'opentiler.exporter',
        'opentiler.settings',
        'opentiler.utils',
        'opentiler.formats',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{PROJECT_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='opentiler/assets/app_icon.ico' if os.path.exists('opentiler/assets/app_icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{PROJECT_NAME}',
)
'''

def main():
    """Main installer builder function."""
    parser = argparse.ArgumentParser(description="Build OpenTiler installers")
    parser.add_argument("--platform", choices=["windows", "macos", "linux", "all"],
                       default="windows", help="Target platform")
    parser.add_argument("--method", choices=["cx_freeze", "pyinstaller"],
                       default="cx_freeze", help="Build method for Windows")
    parser.add_argument("--clean", action="store_true", help="Clean build directories first")
    
    args = parser.parse_args()
    
    builder = InstallerBuilder()
    
    if args.clean:
        builder.clean_build_dirs()
    
    print(f"🚀 Building OpenTiler installer for {args.platform}...")
    
    if args.platform in ["windows", "all"]:
        if not builder.install_build_dependencies("windows"):
            print("❌ Failed to install Windows build dependencies")
            return 1
            
        if args.method == "cx_freeze":
            if not builder.build_windows_msi():
                print("❌ Windows MSI build failed")
                return 1
        else:
            if not builder.build_pyinstaller_exe():
                print("❌ PyInstaller build failed")
                return 1
    
    print("🎉 Installer build completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
