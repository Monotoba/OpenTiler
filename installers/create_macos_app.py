#!/usr/bin/env python3
"""
macOS Application Builder for OpenTiler

Creates a native macOS .app bundle and DMG installer for OpenTiler.
Run this on macOS to create the .app and .dmg files.

Usage:
    python create_macos_app.py
"""

import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def check_macos():
    """Check if we're running on macOS."""
    if sys.platform != "darwin":
        print("⚠️  This script should be run on macOS to create macOS applications.")
        print("   You can still run it to generate build files for later use.")
        return False
    return True


def install_dependencies():
    """Install required build dependencies."""
    print("📦 Installing build dependencies...")

    dependencies = ["py2app", "pyinstaller", "dmgbuild"]

    for dep in dependencies:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                check=True,
                capture_output=True,
            )
            print(f"  ✅ Installed {dep}")
        except subprocess.CalledProcessError:
            print(f"  ❌ Failed to install {dep}")
            return False
    return True


def create_py2app_setup():
    """Create setup.py for py2app."""

    setup_content = '''#!/usr/bin/env python3
"""
py2app setup script for OpenTiler macOS application
"""

from setuptools import setup
import py2app
import sys
import os

# Application information
APP_NAME = "OpenTiler"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Professional Document Scaling and Tiling Application"

# Main script
APP = ['main.py']

# Data files to include
DATA_FILES = [
    ('opentiler/assets', ['opentiler/assets']),
    ('docs', ['docs']),
    ('', ['README.md', 'LICENSE']),
]

# Options for py2app
OPTIONS = {
    'py2app': {
        'app': APP,
        'data_files': DATA_FILES,
        'options': {
            'argv_emulation': True,
            'iconfile': 'opentiler/assets/app_icon.icns' if os.path.exists('opentiler/assets/app_icon.icns') else None,
            'plist': {
                'CFBundleName': APP_NAME,
                'CFBundleDisplayName': APP_NAME,
                'CFBundleGetInfoString': APP_DESCRIPTION,
                'CFBundleIdentifier': 'com.randallmorgan.opentiler',
                'CFBundleVersion': APP_VERSION,
                'CFBundleShortVersionString': APP_VERSION,
                'NSHumanReadableCopyright': 'Copyright © 2024 Randall Morgan. All rights reserved.',
                'NSHighResolutionCapable': True,
                'LSMinimumSystemVersion': '10.14.0',
                'CFBundleDocumentTypes': [
                    {
                        'CFBundleTypeName': 'PDF Document',
                        'CFBundleTypeExtensions': ['pdf'],
                        'CFBundleTypeRole': 'Viewer',
                        'LSHandlerRank': 'Alternate',
                    },
                    {
                        'CFBundleTypeName': 'Image Document',
                        'CFBundleTypeExtensions': ['png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif'],
                        'CFBundleTypeRole': 'Viewer',
                        'LSHandlerRank': 'Alternate',
                    },
                    {
                        'CFBundleTypeName': 'CAD Document',
                        'CFBundleTypeExtensions': ['dxf', 'dwg'],
                        'CFBundleTypeRole': 'Viewer',
                        'LSHandlerRank': 'Alternate',
                    },
                ],
            },
            'packages': [
                'PySide6',
                'opentiler',
                'PIL',
                'fitz',
            ],
            'includes': [
                'PySide6.QtCore',
                'PySide6.QtGui',
                'PySide6.QtWidgets',
                'PySide6.QtPrintSupport',
                'opentiler.viewer',
                'opentiler.dialogs',
                'opentiler.exporter',
                'opentiler.settings',
                'opentiler.utils',
                'opentiler.formats',
            ],
            'excludes': [
                'tkinter',
                'matplotlib',
                'scipy',
                'pandas',
                'numpy.distutils',
            ],
            'optimize': 2,
            'compressed': True,
            'semi_standalone': False,
            'site_packages': True,
        }
    }
}

if __name__ == '__main__':
    setup(
        app=APP,
        data_files=DATA_FILES,
        options=OPTIONS,
        setup_requires=['py2app'],
    )
'''

    setup_file = Path("setup_py2app.py")
    with open(setup_file, "w") as f:
        f.write(setup_content)

    return setup_file


def build_app_with_py2app():
    """Build macOS app using py2app."""
    print("🏗️ Building macOS application with py2app...")

    # Create setup script
    setup_file = create_py2app_setup()

    try:
        # Clean previous builds
        for dir_name in ["build", "dist"]:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)

        # Build the app
        cmd = [sys.executable, str(setup_file), "py2app"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("  ✅ macOS application built successfully!")

            app_path = Path("dist/OpenTiler.app")
            if app_path.exists():
                print(f"  📱 Application: {app_path}")
                return app_path
            else:
                print("  ❌ Application not found in expected location")
                return None
        else:
            print(f"  ❌ Build failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"  ❌ Build error: {e}")
        return None
    finally:
        # Clean up setup file
        if setup_file.exists():
            setup_file.unlink()


def build_app_with_pyinstaller():
    """Build macOS app using PyInstaller."""
    print("🏗️ Building macOS application with PyInstaller...")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "OpenTiler",
        "--onedir",
        "--windowed",
        "--clean",
        "--noconfirm",
        # Add data files
        "--add-data",
        "opentiler/assets:opentiler/assets",
        "--add-data",
        "docs:docs",
        "--add-data",
        "README.md:.",
        "--add-data",
        "LICENSE:.",
        # Hidden imports
        "--hidden-import",
        "PySide6.QtCore",
        "--hidden-import",
        "PySide6.QtGui",
        "--hidden-import",
        "PySide6.QtWidgets",
        "--hidden-import",
        "PySide6.QtPrintSupport",
        "--hidden-import",
        "opentiler",
        "--hidden-import",
        "opentiler.viewer",
        "--hidden-import",
        "opentiler.dialogs",
        "--hidden-import",
        "opentiler.exporter",
        "--hidden-import",
        "opentiler.settings",
        "--hidden-import",
        "opentiler.utils",
        "--hidden-import",
        "opentiler.formats",
        # Exclude unnecessary modules
        "--exclude-module",
        "tkinter",
        "--exclude-module",
        "matplotlib",
        "--exclude-module",
        "scipy",
        "main.py",
    ]

    # Add icon if available
    icon_path = Path("opentiler/assets/app_icon.icns")
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
        print(f"  ✅ Using icon: {icon_path}")
    else:
        print("  ℹ️  No app icon found (opentiler/assets/app_icon.icns)")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("  ✅ PyInstaller build successful!")

            app_path = Path("dist/OpenTiler.app")
            if app_path.exists():
                print(f"  📱 Application: {app_path}")
                return app_path
            else:
                print("  ❌ Application not found in expected location")
                return None
        else:
            print(f"  ❌ PyInstaller build failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"  ❌ PyInstaller build error: {e}")
        return None


def create_dmg(app_path):
    """Create DMG installer."""
    print("📦 Creating DMG installer...")

    if not app_path or not app_path.exists():
        print("  ❌ No application found to package")
        return None

    dmg_path = Path("dist/OpenTiler-1.0.0.dmg")

    try:
        # Create temporary directory for DMG contents
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Copy app to temp directory
            app_dest = temp_path / "OpenTiler.app"
            shutil.copytree(app_path, app_dest)

            # Create Applications symlink
            applications_link = temp_path / "Applications"
            applications_link.symlink_to("/Applications")

            # Copy documentation
            docs_dir = temp_path / "Documentation"
            docs_dir.mkdir()

            for doc in ["README.md", "LICENSE"]:
                if Path(doc).exists():
                    shutil.copy2(doc, docs_dir)

            user_manual = Path("docs/user/USER_MANUAL.md")
            if user_manual.exists():
                shutil.copy2(user_manual, docs_dir / "User Manual.md")

            # Create DMG using hdiutil
            cmd = [
                "hdiutil",
                "create",
                "-volname",
                "OpenTiler",
                "-srcfolder",
                str(temp_path),
                "-ov",
                "-format",
                "UDZO",
                str(dmg_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"  ✅ DMG created: {dmg_path}")

                # Get DMG size
                size_mb = dmg_path.stat().st_size / (1024 * 1024)
                print(f"  📏 Size: {size_mb:.1f} MB")

                return dmg_path
            else:
                print(f"  ❌ DMG creation failed: {result.stderr}")
                return None

    except Exception as e:
        print(f"  ❌ DMG creation error: {e}")
        return None


def create_installer_script():
    """Create installation script for macOS."""

    script_content = """#!/bin/bash
# OpenTiler macOS Installation Script

echo "OpenTiler macOS Installation"
echo "============================"
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "Please do not run this script as root/sudo"
   echo "Installation will be performed for the current user"
   exit 1
fi

APP_NAME="OpenTiler.app"
INSTALL_DIR="/Applications"
DMG_PATH="./OpenTiler-1.0.0.dmg"

echo "Installing OpenTiler to: $INSTALL_DIR"
echo

# Check if DMG exists
if [ ! -f "$DMG_PATH" ]; then
    echo "❌ DMG file not found: $DMG_PATH"
    echo "Please ensure OpenTiler-1.0.0.dmg is in the current directory"
    exit 1
fi

# Mount DMG
echo "📦 Mounting DMG..."
MOUNT_POINT=$(hdiutil attach "$DMG_PATH" | grep "/Volumes" | awk '{print $3}')

if [ -z "$MOUNT_POINT" ]; then
    echo "❌ Failed to mount DMG"
    exit 1
fi

echo "✅ DMG mounted at: $MOUNT_POINT"

# Copy application
echo "📱 Installing application..."
if [ -d "$MOUNT_POINT/$APP_NAME" ]; then
    # Remove existing installation
    if [ -d "$INSTALL_DIR/$APP_NAME" ]; then
        echo "🗑️  Removing existing installation..."
        rm -rf "$INSTALL_DIR/$APP_NAME"
    fi
    
    # Copy new application
    cp -R "$MOUNT_POINT/$APP_NAME" "$INSTALL_DIR/"
    
    if [ $? -eq 0 ]; then
        echo "✅ Application installed successfully!"
    else
        echo "❌ Failed to copy application"
        hdiutil detach "$MOUNT_POINT" >/dev/null 2>&1
        exit 1
    fi
else
    echo "❌ Application not found in DMG"
    hdiutil detach "$MOUNT_POINT" >/dev/null 2>&1
    exit 1
fi

# Unmount DMG
echo "📤 Unmounting DMG..."
hdiutil detach "$MOUNT_POINT" >/dev/null 2>&1

echo
echo "🎉 Installation completed successfully!"
echo
echo "OpenTiler has been installed to: $INSTALL_DIR/$APP_NAME"
echo
echo "You can now run OpenTiler from:"
echo "- Applications folder"
echo "- Spotlight search"
echo "- Launchpad"
echo
echo "To uninstall, simply drag OpenTiler.app to the Trash"
"""

    script_path = Path("dist/install_opentiler_macos.sh")
    with open(script_path, "w") as f:
        f.write(script_content)

    # Make executable
    script_path.chmod(0o755)

    print(f"📝 Installation script created: {script_path}")
    return script_path


def main():
    """Main function."""
    print("OpenTiler macOS Application Builder")
    print("===================================")
    print()

    # Check if main.py exists
    if not Path("main.py").exists():
        print(
            "❌ main.py not found. Please run this script from the OpenTiler project root."
        )
        return 1

    # Check macOS
    is_macos = check_macos()

    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return 1

    # Try py2app first, fallback to PyInstaller
    app_path = build_app_with_py2app()
    if not app_path:
        print("🔄 py2app failed, trying PyInstaller...")
        app_path = build_app_with_pyinstaller()

    if not app_path:
        print("❌ Both build methods failed")
        return 1

    # Create DMG
    dmg_path = create_dmg(app_path)

    # Create installer script
    script_path = create_installer_script()

    print()
    print("🎉 macOS build completed successfully!")
    print()
    print("📁 Output files in dist/ directory:")
    if app_path:
        print(f"   - {app_path.name} (macOS application)")
    if dmg_path:
        print(f"   - {dmg_path.name} (DMG installer)")
    if script_path:
        print(f"   - {script_path.name} (installation script)")
    print()
    print("📋 Distribution options:")
    print("   1. Share .dmg file (recommended)")
    print("   2. Share .app bundle directly")
    print("   3. Use installation script for automated deployment")

    return 0


if __name__ == "__main__":
    sys.exit(main())
