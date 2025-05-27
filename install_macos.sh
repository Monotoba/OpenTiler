#!/bin/bash
# OpenTiler macOS Installation Script
# 
# This script installs OpenTiler from source on macOS
# Handles Python environment setup, dependencies, and application installation

set -e  # Exit on any error

echo "🍎 OpenTiler macOS Installation"
echo "==============================="
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only"
    exit 1
fi

print_status "Running on macOS"

# Check for Xcode Command Line Tools
echo "🔧 Checking for Xcode Command Line Tools..."
if ! xcode-select -p &> /dev/null; then
    print_warning "Xcode Command Line Tools not found"
    echo "Installing Xcode Command Line Tools..."
    xcode-select --install
    echo "Please complete the Xcode Command Line Tools installation and run this script again"
    exit 1
else
    print_status "Xcode Command Line Tools found"
fi

# Check for Homebrew
echo "🍺 Checking for Homebrew..."
if ! command -v brew &> /dev/null; then
    print_warning "Homebrew not found"
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for this session
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -f "/usr/local/bin/brew" ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    print_status "Homebrew found"
fi

# Check for Python 3.8+
echo "🐍 Checking for Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
        print_status "Python $PYTHON_VERSION found"
        PYTHON_CMD="python3"
    else
        print_warning "Python $PYTHON_VERSION found, but 3.8+ required"
        PYTHON_CMD=""
    fi
else
    print_warning "Python 3 not found"
    PYTHON_CMD=""
fi

# Install Python if needed
if [[ -z "$PYTHON_CMD" ]]; then
    echo "Installing Python 3.10 via Homebrew..."
    brew install python@3.10
    PYTHON_CMD="python3.10"
    print_status "Python 3.10 installed"
fi

# Check for pip
echo "📦 Checking for pip..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    print_error "pip not found"
    echo "Installing pip..."
    $PYTHON_CMD -m ensurepip --upgrade
fi
print_status "pip found"

# Create installation directory
INSTALL_DIR="$HOME/Applications/OpenTiler"
echo "📁 Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Check if we're in the OpenTiler source directory
if [[ ! -f "main.py" || ! -d "opentiler" ]]; then
    print_error "OpenTiler source files not found"
    echo "Please run this script from the OpenTiler project directory"
    echo "Or download the source code first:"
    echo "  git clone https://github.com/Monotoba/OpenTiler.git"
    echo "  cd OpenTiler"
    echo "  ./install_macos.sh"
    exit 1
fi

print_status "OpenTiler source files found"

# Create virtual environment
echo "🔧 Creating virtual environment..."
$PYTHON_CMD -m venv "$INSTALL_DIR/venv"
print_status "Virtual environment created"

# Activate virtual environment
source "$INSTALL_DIR/venv/bin/activate"

# Upgrade pip in virtual environment
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install core requirements
echo "📦 Installing core requirements..."
pip install PySide6 Pillow PyMuPDF

# Install optional dependencies
echo "📦 Installing optional dependencies..."
pip install ezdxf || print_warning "Failed to install ezdxf (CAD support)"
pip install rawpy numpy || print_warning "Failed to install rawpy/numpy (RAW image support)"

print_status "Dependencies installed"

# Copy application files
echo "📋 Copying application files..."
cp -r opentiler "$INSTALL_DIR/"
cp main.py "$INSTALL_DIR/"
cp -r docs "$INSTALL_DIR/" 2>/dev/null || true
cp README.md "$INSTALL_DIR/" 2>/dev/null || true
cp LICENSE "$INSTALL_DIR/" 2>/dev/null || true

print_status "Application files copied"

# Create launcher script
echo "🚀 Creating launcher script..."
LAUNCHER_SCRIPT="$INSTALL_DIR/opentiler_launcher.sh"
cat > "$LAUNCHER_SCRIPT" << 'EOF'
#!/bin/bash
# OpenTiler Launcher Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Change to application directory
cd "$SCRIPT_DIR"

# Launch OpenTiler
python main.py "$@"
EOF

chmod +x "$LAUNCHER_SCRIPT"
print_status "Launcher script created"

# Create desktop application bundle
echo "📱 Creating application bundle..."
APP_BUNDLE="$HOME/Applications/OpenTiler.app"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Create Info.plist
cat > "$APP_BUNDLE/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>OpenTiler</string>
    <key>CFBundleIdentifier</key>
    <string>com.randallmorgan.opentiler</string>
    <key>CFBundleName</key>
    <string>OpenTiler</string>
    <key>CFBundleDisplayName</key>
    <string>OpenTiler</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>OTLR</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSMinimumSystemVersion</key>
    <string>10.14.0</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>PDF Document</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>pdf</string>
            </array>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
        </dict>
        <dict>
            <key>CFBundleTypeName</key>
            <string>Image Document</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>png</string>
                <string>jpg</string>
                <string>jpeg</string>
                <string>tiff</string>
                <string>bmp</string>
                <string>gif</string>
            </array>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
        </dict>
    </array>
</dict>
</plist>
EOF

# Create executable script
cat > "$APP_BUNDLE/Contents/MacOS/OpenTiler" << EOF
#!/bin/bash
# OpenTiler macOS Application Launcher

# Get the bundle directory
BUNDLE_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")/../.." && pwd)"

# Launch the actual application
exec "$LAUNCHER_SCRIPT" "\$@"
EOF

chmod +x "$APP_BUNDLE/Contents/MacOS/OpenTiler"

print_status "Application bundle created"

# Create command-line symlink
echo "🔗 Creating command-line access..."
SYMLINK_DIR="/usr/local/bin"
if [[ -w "$SYMLINK_DIR" ]]; then
    ln -sf "$LAUNCHER_SCRIPT" "$SYMLINK_DIR/opentiler"
    print_status "Command-line access created: opentiler"
else
    print_warning "Cannot create command-line symlink (no write access to $SYMLINK_DIR)"
    print_info "You can manually create it with: sudo ln -sf '$LAUNCHER_SCRIPT' '$SYMLINK_DIR/opentiler'"
fi

# Create uninstaller
echo "🗑️  Creating uninstaller..."
UNINSTALLER="$INSTALL_DIR/uninstall.sh"
cat > "$UNINSTALLER" << EOF
#!/bin/bash
# OpenTiler Uninstaller

echo "Uninstalling OpenTiler..."

# Remove application bundle
rm -rf "$APP_BUNDLE"

# Remove installation directory
rm -rf "$INSTALL_DIR"

# Remove command-line symlink
rm -f "$SYMLINK_DIR/opentiler"

echo "OpenTiler has been uninstalled"
EOF

chmod +x "$UNINSTALLER"

echo
print_status "Installation completed successfully!"
echo
echo "📱 OpenTiler has been installed to:"
echo "   Application Bundle: $APP_BUNDLE"
echo "   Installation Directory: $INSTALL_DIR"
echo
echo "🚀 You can now run OpenTiler:"
echo "   - From Applications folder (OpenTiler.app)"
echo "   - From Spotlight search"
echo "   - From command line: opentiler"
echo "   - Direct launcher: $LAUNCHER_SCRIPT"
echo
echo "🗑️  To uninstall, run: $UNINSTALLER"
echo
print_info "Installation log saved to: $INSTALL_DIR/install.log"

# Save installation info
cat > "$INSTALL_DIR/install.log" << EOF
OpenTiler macOS Installation Log
================================
Date: $(date)
Python: $($PYTHON_CMD --version)
Installation Directory: $INSTALL_DIR
Application Bundle: $APP_BUNDLE
Launcher Script: $LAUNCHER_SCRIPT
Uninstaller: $UNINSTALLER
EOF
