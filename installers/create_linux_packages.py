#!/usr/bin/env python3
"""
Linux Package Builder for OpenTiler

Creates DEB and RPM packages for Linux distributions.
Requires fpm (Effing Package Management) to be installed.

Usage:
    python create_linux_packages.py --format deb
    python create_linux_packages.py --format rpm
    python create_linux_packages.py --format both
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class LinuxPackageBuilder:
    """Build Linux packages for OpenTiler."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.package_dir = self.project_root / "packages"

        # Package metadata
        self.package_name = "opentiler"
        self.version = "1.0.0"
        self.description = "Professional Document Scaling and Tiling Application"
        self.maintainer = "Randall Morgan <randall@example.com>"
        self.url = "https://github.com/Monotoba/OpenTiler"
        self.license = "MIT"

    def check_fpm(self):
        """Check if fpm is installed."""
        try:
            subprocess.run(["fpm", "--version"], capture_output=True, check=True)
            print("✅ fpm found")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ fpm not found")
            print("Install fpm with: gem install fpm")
            print(
                "Or on Ubuntu/Debian: sudo apt-get install ruby-dev build-essential && gem install fpm"
            )
            return False

    def prepare_package_structure(self):
        """Prepare package directory structure."""
        print("📁 Preparing package structure...")

        # Clean and create directories
        if self.package_dir.exists():
            shutil.rmtree(self.package_dir)
        self.package_dir.mkdir(exist_ok=True)

        # Create standard Linux directory structure
        dirs = [
            "usr/share/opentiler",
            "usr/bin",
            "usr/share/applications",
            "usr/share/pixmaps",
            "usr/share/doc/opentiler",
        ]

        for dir_path in dirs:
            (self.package_dir / dir_path).mkdir(parents=True, exist_ok=True)

        print("  ✅ Directory structure created")

    def copy_application_files(self):
        """Copy application files to package structure."""
        print("📋 Copying application files...")

        # Copy main application
        app_dest = self.package_dir / "usr/share/opentiler"

        # Copy Python files
        shutil.copytree("opentiler", app_dest / "opentiler")
        shutil.copy2("main.py", app_dest)

        # Copy documentation
        doc_dest = self.package_dir / "usr/share/doc/opentiler"
        for doc in ["README.md", "LICENSE"]:
            if Path(doc).exists():
                shutil.copy2(doc, doc_dest)

        if Path("docs").exists():
            shutil.copytree("docs", doc_dest / "docs")

        print("  ✅ Application files copied")

    def create_launcher_script(self):
        """Create launcher script."""
        print("🚀 Creating launcher script...")

        launcher_content = """#!/bin/bash
# OpenTiler Launcher Script

# Application directory
APP_DIR="/usr/share/opentiler"

# Check if virtual environment exists, create if not
VENV_DIR="$HOME/.local/share/opentiler/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Setting up OpenTiler environment..."
    mkdir -p "$(dirname "$VENV_DIR")"
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install PySide6 Pillow PyMuPDF
    pip install ezdxf || true
    pip install rawpy numpy || true
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Launch OpenTiler
cd "$APP_DIR"
python main.py "$@"
"""

        launcher_path = self.package_dir / "usr/bin/opentiler"
        with open(launcher_path, "w") as f:
            f.write(launcher_content)

        launcher_path.chmod(0o755)
        print("  ✅ Launcher script created")

    def create_desktop_entry(self):
        """Create desktop entry file."""
        print("🖥️  Creating desktop entry...")

        desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=OpenTiler
Comment=Professional Document Scaling and Tiling Application
Exec=opentiler %F
Icon=opentiler
Terminal=false
Categories=Graphics;Office;Engineering;
MimeType=application/pdf;image/png;image/jpeg;image/tiff;image/bmp;image/gif;application/dxf;
StartupNotify=true
StartupWMClass=OpenTiler
"""

        desktop_path = self.package_dir / "usr/share/applications/opentiler.desktop"
        with open(desktop_path, "w") as f:
            f.write(desktop_content)

        print("  ✅ Desktop entry created")

    def copy_icon(self):
        """Copy application icon."""
        print("🎨 Copying application icon...")

        icon_source = Path("opentiler/assets/app_icon.png")
        if icon_source.exists():
            icon_dest = self.package_dir / "usr/share/pixmaps/opentiler.png"
            shutil.copy2(icon_source, icon_dest)
            print("  ✅ Icon copied")
        else:
            print("  ⚠️  No icon found, using default")

    def create_post_install_script(self):
        """Create post-installation script."""
        print("📝 Creating post-install script...")

        postinst_content = """#!/bin/bash
# OpenTiler post-installation script

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

# Update MIME database
if command -v update-mime-database >/dev/null 2>&1; then
    update-mime-database /usr/share/mime
fi

echo "OpenTiler installed successfully!"
echo "You can now run it from the applications menu or with 'opentiler' command."
"""

        postinst_path = self.package_dir / "postinst"
        with open(postinst_path, "w") as f:
            f.write(postinst_content)

        postinst_path.chmod(0o755)
        print("  ✅ Post-install script created")

    def create_pre_remove_script(self):
        """Create pre-removal script."""
        print("📝 Creating pre-remove script...")

        prerm_content = """#!/bin/bash
# OpenTiler pre-removal script

# Clean up user virtual environments
find /home -name ".local/share/opentiler" -type d 2>/dev/null | while read dir; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
    fi
done

echo "OpenTiler cleanup completed."
"""

        prerm_path = self.package_dir / "prerm"
        with open(prerm_path, "w") as f:
            f.write(prerm_content)

        prerm_path.chmod(0o755)
        print("  ✅ Pre-remove script created")

    def build_deb_package(self):
        """Build DEB package using fpm."""
        print("📦 Building DEB package...")

        cmd = [
            "fpm",
            "-s",
            "dir",
            "-t",
            "deb",
            "-n",
            self.package_name,
            "-v",
            self.version,
            "--description",
            self.description,
            "--maintainer",
            self.maintainer,
            "--url",
            self.url,
            "--license",
            self.license,
            "--depends",
            "python3",
            "--depends",
            "python3-pip",
            "--depends",
            "python3-venv",
            "--depends",
            "python3-dev",
            "--depends",
            "libgl1-mesa-glx",
            "--depends",
            "libxcb-xinerama0",
            "--after-install",
            str(self.package_dir / "postinst"),
            "--before-remove",
            str(self.package_dir / "prerm"),
            "--package",
            str(self.dist_dir),
            "-C",
            str(self.package_dir),
            "usr",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ DEB package created successfully!")
                deb_files = list(self.dist_dir.glob("*.deb"))
                if deb_files:
                    print(f"  📦 Package: {deb_files[0]}")
                return True
            else:
                print(f"  ❌ DEB build failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ❌ DEB build error: {e}")
            return False

    def build_rpm_package(self):
        """Build RPM package using fpm."""
        print("📦 Building RPM package...")

        cmd = [
            "fpm",
            "-s",
            "dir",
            "-t",
            "rpm",
            "-n",
            self.package_name,
            "-v",
            self.version,
            "--description",
            self.description,
            "--maintainer",
            self.maintainer,
            "--url",
            self.url,
            "--license",
            self.license,
            "--depends",
            "python3",
            "--depends",
            "python3-pip",
            "--depends",
            "python3-devel",
            "--depends",
            "mesa-libGL",
            "--depends",
            "libxcb",
            "--after-install",
            str(self.package_dir / "postinst"),
            "--before-remove",
            str(self.package_dir / "prerm"),
            "--package",
            str(self.dist_dir),
            "-C",
            str(self.package_dir),
            "usr",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("  ✅ RPM package created successfully!")
                rpm_files = list(self.dist_dir.glob("*.rpm"))
                if rpm_files:
                    print(f"  📦 Package: {rpm_files[0]}")
                return True
            else:
                print(f"  ❌ RPM build failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ❌ RPM build error: {e}")
            return False

    def build_packages(self, formats):
        """Build packages in specified formats."""
        print("🚀 Building OpenTiler Linux packages...")

        # Check prerequisites
        if not self.check_fpm():
            return False

        # Prepare package structure
        self.prepare_package_structure()
        self.copy_application_files()
        self.create_launcher_script()
        self.create_desktop_entry()
        self.copy_icon()
        self.create_post_install_script()
        self.create_pre_remove_script()

        # Create dist directory
        self.dist_dir.mkdir(exist_ok=True)

        # Build packages
        success = True
        if "deb" in formats:
            success &= self.build_deb_package()

        if "rpm" in formats:
            success &= self.build_rpm_package()

        if success:
            print("\n🎉 Package build completed successfully!")
            print(f"\n📁 Output packages in: {self.dist_dir}")

            # List created packages
            packages = list(self.dist_dir.glob("*.deb")) + list(
                self.dist_dir.glob("*.rpm")
            )
            for package in packages:
                print(f"   📦 {package.name}")

            print("\n📋 Installation instructions:")
            print("   DEB: sudo dpkg -i opentiler_*.deb && sudo apt-get install -f")
            print("   RPM: sudo rpm -i opentiler-*.rpm")

        return success


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Build OpenTiler Linux packages")
    parser.add_argument(
        "--format",
        choices=["deb", "rpm", "both"],
        default="both",
        help="Package format to build",
    )

    args = parser.parse_args()

    # Check if main.py exists
    if not Path("main.py").exists():
        print(
            "❌ main.py not found. Please run this script from the OpenTiler project root."
        )
        return 1

    # Determine formats to build
    if args.format == "both":
        formats = ["deb", "rpm"]
    else:
        formats = [args.format]

    # Build packages
    builder = LinuxPackageBuilder()
    success = builder.build_packages(formats)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
