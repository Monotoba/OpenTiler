#!/usr/bin/env python3
"""
Simple Windows Installer Builder for OpenTiler

Creates a Windows MSI installer using PyInstaller + NSIS or Inno Setup
This is a simpler alternative that works reliably across different Windows versions.

Usage:
    python build_windows_installer.py
"""

import sys
import os
import subprocess
import shutil
import tempfile
from pathlib import Path

class WindowsInstallerBuilder:
    """Build Windows installer for OpenTiler."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.installer_dir = self.project_root / "installer"
        
    def clean_dirs(self):
        """Clean build directories."""
        print("🧹 Cleaning build directories...")
        for dir_path in [self.build_dir, self.dist_dir, self.installer_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
        
        self.installer_dir.mkdir(exist_ok=True)
    
    def install_dependencies(self):
        """Install required build dependencies."""
        print("📦 Installing build dependencies...")
        
        dependencies = ["pyinstaller"]
        
        for dep in dependencies:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                             check=True, capture_output=True)
                print(f"  ✅ Installed {dep}")
            except subprocess.CalledProcessError:
                print(f"  ❌ Failed to install {dep}")
                return False
        return True
    
    def build_executable(self):
        """Build standalone executable using PyInstaller."""
        print("🏗️ Building standalone executable...")
        
        # Create PyInstaller command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--name", "OpenTiler",
            "--onedir",  # Create directory instead of single file for better performance
            "--windowed",  # No console window
            "--clean",
            "--noconfirm",
            "--distpath", str(self.dist_dir),
            "--workpath", str(self.build_dir),
            
            # Add data files
            "--add-data", "opentiler/assets;opentiler/assets",
            "--add-data", "docs;docs",
            "--add-data", "README.md;.",
            "--add-data", "LICENSE;.",
            
            # Hidden imports
            "--hidden-import", "PySide6.QtCore",
            "--hidden-import", "PySide6.QtGui",
            "--hidden-import", "PySide6.QtWidgets",
            "--hidden-import", "PySide6.QtPrintSupport",
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
            
            "main.py"
        ]
        
        # Add icon if available
        icon_path = self.project_root / "opentiler" / "assets" / "app_icon.ico"
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ Executable built successfully!")
                return True
            else:
                print(f"  ❌ Build failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Build error: {e}")
            return False
    
    def create_nsis_script(self):
        """Create NSIS installer script."""
        nsis_script = f'''
; OpenTiler NSIS Installer Script
; Generated automatically

!define APPNAME "OpenTiler"
!define COMPANYNAME "Randall Morgan"
!define DESCRIPTION "Professional Document Scaling and Tiling Application"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/Monotoba/OpenTiler"
!define UPDATEURL "https://github.com/Monotoba/OpenTiler/releases"
!define ABOUTURL "https://github.com/Monotoba/OpenTiler"
!define INSTALLSIZE 150000  ; Estimate in KB

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\\${{APPNAME}}"
Name "${{APPNAME}}"
Icon "opentiler\\assets\\app_icon.ico"
outFile "OpenTiler-${{VERSIONMAJOR}}.${{VERSIONMINOR}}.${{VERSIONBUILD}}-Setup.exe"

!include LogicLib.nsh
!include MUI2.nsh

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "opentiler\\assets\\app_icon.ico"
!define MUI_UNICON "opentiler\\assets\\app_icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; Languages
!insertmacro MUI_LANGUAGE "English"

Section "install"
    SetOutPath $INSTDIR
    
    ; Copy application files
    File /r "dist\\OpenTiler\\*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${{APPNAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk" "$INSTDIR\\OpenTiler.exe"
    CreateShortCut "$DESKTOP\\${{APPNAME}}.lnk" "$INSTDIR\\OpenTiler.exe"
    
    ; Registry entries
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayName" "${{APPNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "QuietUninstallString" "$\\"$INSTDIR\\uninstall.exe$\\" /S"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "InstallLocation" "$\\"$INSTDIR$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayIcon" "$\\"$INSTDIR\\OpenTiler.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "Publisher" "${{COMPANYNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "HelpLink" "${{HELPURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "URLUpdateInfo" "${{UPDATEURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "URLInfoAbout" "${{ABOUTURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayVersion" "${{VERSIONMAJOR}}.${{VERSIONMINOR}}.${{VERSIONBUILD}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "VersionMajor" ${{VERSIONMAJOR}}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "VersionMinor" ${{VERSIONMINOR}}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "EstimatedSize" ${{INSTALLSIZE}}
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk"
    RMDir "$SMPROGRAMS\\${{APPNAME}}"
    Delete "$DESKTOP\\${{APPNAME}}.lnk"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}"
SectionEnd
'''
        
        script_path = self.installer_dir / "installer.nsi"
        with open(script_path, 'w') as f:
            f.write(nsis_script)
        
        return script_path
    
    def create_batch_installer(self):
        """Create a simple batch file installer as fallback."""
        print("📦 Creating batch installer...")
        
        batch_content = f'''@echo off
echo Installing OpenTiler...

set INSTALL_DIR=%PROGRAMFILES%\\OpenTiler

echo Creating installation directory...
mkdir "%INSTALL_DIR%" 2>nul

echo Copying files...
xcopy /E /I /Y "dist\\OpenTiler\\*" "%INSTALL_DIR%\\"

echo Creating shortcuts...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\OpenTiler.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\OpenTiler.exe'; $Shortcut.Save()"

echo Installation complete!
echo OpenTiler has been installed to: %INSTALL_DIR%
echo Desktop shortcut created.
pause
'''
        
        batch_path = self.installer_dir / "install.bat"
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        print(f"  ✅ Batch installer created: {batch_path}")
        return batch_path
    
    def create_portable_zip(self):
        """Create portable ZIP package."""
        print("📦 Creating portable ZIP package...")
        
        zip_path = self.installer_dir / "OpenTiler-1.0.0-Portable.zip"
        
        try:
            shutil.make_archive(
                str(zip_path.with_suffix('')),
                'zip',
                str(self.dist_dir),
                'OpenTiler'
            )
            print(f"  ✅ Portable ZIP created: {zip_path}")
            return True
        except Exception as e:
            print(f"  ❌ ZIP creation failed: {e}")
            return False
    
    def build(self):
        """Build complete Windows installer package."""
        print("🚀 Building OpenTiler Windows Installer...")
        
        # Clean and prepare
        self.clean_dirs()
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Build executable
        if not self.build_executable():
            return False
        
        # Create installers
        self.create_batch_installer()
        self.create_portable_zip()
        
        # Create NSIS script (user can compile manually)
        nsis_script = self.create_nsis_script()
        print(f"  📝 NSIS script created: {nsis_script}")
        print("     To create MSI: Install NSIS and run 'makensis installer.nsi'")
        
        print("\n🎉 Windows installer build completed!")
        print(f"📁 Output directory: {self.installer_dir}")
        print("📦 Available packages:")
        print("   - install.bat (Simple installer)")
        print("   - OpenTiler-1.0.0-Portable.zip (Portable version)")
        print("   - installer.nsi (NSIS script for MSI creation)")
        
        return True

def main():
    """Main function."""
    builder = WindowsInstallerBuilder()
    success = builder.build()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
