#!/bin/bash
# OpenTiler Linux Installation Script
# 
# This script installs OpenTiler from source on Linux distributions
# Supports Ubuntu/Debian, CentOS/RHEL/Fedora, and Arch Linux

set -e  # Exit on any error

echo "🐧 OpenTiler Linux Installation"
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

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
    else
        DISTRO="unknown"
    fi
    
    print_info "Detected distribution: $DISTRO"
}

# Install system dependencies based on distribution
install_system_deps() {
    echo "📦 Installing system dependencies..."
    
    case $DISTRO in
        ubuntu|debian)
            sudo apt-get update
            sudo apt-get install -y \
                python3 python3-pip python3-venv python3-dev \
                build-essential pkg-config \
                libgl1-mesa-glx libxcb-xinerama0 \
                libfontconfig1 libxkbcommon-x11-0 \
                libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
                libxcb-randr0 libxcb-render-util0 \
                git curl wget
            ;;
        fedora|centos|rhel)
            if command -v dnf &> /dev/null; then
                PKG_MGR="dnf"
            else
                PKG_MGR="yum"
            fi
            
            sudo $PKG_MGR install -y \
                python3 python3-pip python3-devel \
                gcc gcc-c++ make pkgconfig \
                mesa-libGL libxcb xcb-util-wm \
                fontconfig libxkbcommon-x11 \
                xcb-util-image xcb-util-keysyms \
                xcb-util-renderutil \
                git curl wget
            ;;
        arch|manjaro)
            sudo pacman -Sy --noconfirm \
                python python-pip \
                base-devel pkgconf \
                mesa libxcb xcb-util-wm \
                fontconfig libxkbcommon-x11 \
                xcb-util-image xcb-util-keysyms \
                xcb-util-renderutil \
                git curl wget
            ;;
        opensuse*)
            sudo zypper install -y \
                python3 python3-pip python3-devel \
                gcc gcc-c++ make pkg-config \
                Mesa-libGL1 libxcb1 xcb-util-wm \
                fontconfig libxkbcommon-x11-0 \
                xcb-util-image xcb-util-keysyms \
                xcb-util-renderutil \
                git curl wget
            ;;
        *)
            print_warning "Unknown distribution. Please install Python 3.8+, pip, and development tools manually."
            print_info "Required packages: python3, python3-pip, python3-dev, build-essential, Qt5 libraries"
            ;;
    esac
    
    print_status "System dependencies installed"
}

# Check Python version
check_python() {
    echo "🐍 Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 8 ]]; then
            print_status "Python $PYTHON_VERSION found"
            PYTHON_CMD="python3"
        else
            print_error "Python $PYTHON_VERSION found, but 3.8+ required"
            exit 1
        fi
    else
        print_error "Python 3 not found"
        exit 1
    fi
}

# Create installation directory
create_install_dir() {
    INSTALL_DIR="$HOME/.local/share/opentiler"
    echo "📁 Creating installation directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    print_status "Installation directory created"
}

# Check if we're in the OpenTiler source directory
check_source() {
    if [[ ! -f "main.py" || ! -d "opentiler" ]]; then
        print_error "OpenTiler source files not found"
        echo "Please run this script from the OpenTiler project directory"
        echo "Or download the source code first:"
        echo "  git clone https://github.com/Monotoba/OpenTiler.git"
        echo "  cd OpenTiler"
        echo "  ./install_linux.sh"
        exit 1
    fi
    
    print_status "OpenTiler source files found"
}

# Create virtual environment and install dependencies
setup_python_env() {
    echo "🔧 Creating virtual environment..."
    $PYTHON_CMD -m venv "$INSTALL_DIR/venv"
    print_status "Virtual environment created"
    
    # Activate virtual environment
    source "$INSTALL_DIR/venv/bin/activate"
    
    # Upgrade pip
    echo "⬆️  Upgrading pip..."
    pip install --upgrade pip
    
    # Install core requirements
    echo "📦 Installing core requirements..."
    pip install PySide6 Pillow PyMuPDF
    
    # Install optional dependencies
    echo "📦 Installing optional dependencies..."
    pip install ezdxf || print_warning "Failed to install ezdxf (CAD support)"
    pip install rawpy numpy || print_warning "Failed to install rawpy/numpy (RAW image support)"
    
    print_status "Python environment setup complete"
}

# Copy application files
copy_app_files() {
    echo "📋 Copying application files..."
    cp -r opentiler "$INSTALL_DIR/"
    cp main.py "$INSTALL_DIR/"
    cp -r docs "$INSTALL_DIR/" 2>/dev/null || true
    cp README.md "$INSTALL_DIR/" 2>/dev/null || true
    cp LICENSE "$INSTALL_DIR/" 2>/dev/null || true
    
    print_status "Application files copied"
}

# Create launcher script
create_launcher() {
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
}

# Create desktop entry
create_desktop_entry() {
    echo "🖥️  Creating desktop entry..."
    
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    
    DESKTOP_FILE="$DESKTOP_DIR/opentiler.desktop"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=OpenTiler
Comment=Professional Document Scaling and Tiling Application
Exec=$INSTALL_DIR/opentiler_launcher.sh %F
Icon=$INSTALL_DIR/opentiler/assets/app_icon.png
Terminal=false
Categories=Graphics;Office;Engineering;
MimeType=application/pdf;image/png;image/jpeg;image/tiff;image/bmp;image/gif;application/dxf;
StartupNotify=true
StartupWMClass=OpenTiler
EOF

    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    
    print_status "Desktop entry created"
}

# Create command-line symlink
create_cli_access() {
    echo "🔗 Creating command-line access..."
    
    BIN_DIR="$HOME/.local/bin"
    mkdir -p "$BIN_DIR"
    
    ln -sf "$INSTALL_DIR/opentiler_launcher.sh" "$BIN_DIR/opentiler"
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.bashrc"
        print_info "Added $BIN_DIR to PATH in ~/.bashrc"
        print_info "Run 'source ~/.bashrc' or restart terminal to use 'opentiler' command"
    fi
    
    print_status "Command-line access created"
}

# Create uninstaller
create_uninstaller() {
    echo "🗑️  Creating uninstaller..."
    UNINSTALLER="$INSTALL_DIR/uninstall.sh"
    cat > "$UNINSTALLER" << EOF
#!/bin/bash
# OpenTiler Uninstaller

echo "Uninstalling OpenTiler..."

# Remove desktop entry
rm -f "$HOME/.local/share/applications/opentiler.desktop"

# Remove command-line symlink
rm -f "$HOME/.local/bin/opentiler"

# Remove installation directory
rm -rf "$INSTALL_DIR"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

echo "OpenTiler has been uninstalled"
echo "Note: You may want to remove the PATH entry from ~/.bashrc manually"
EOF

    chmod +x "$UNINSTALLER"
    print_status "Uninstaller created"
}

# Main installation function
main() {
    echo "Starting OpenTiler installation..."
    echo
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "Please do not run this script as root"
        print_info "Installation will be performed for the current user"
        exit 1
    fi
    
    # Detect distribution
    detect_distro
    
    # Install system dependencies
    install_system_deps
    
    # Check Python
    check_python
    
    # Check source files
    check_source
    
    # Create installation directory
    create_install_dir
    
    # Setup Python environment
    setup_python_env
    
    # Copy application files
    copy_app_files
    
    # Create launcher
    create_launcher
    
    # Create desktop entry
    create_desktop_entry
    
    # Create command-line access
    create_cli_access
    
    # Create uninstaller
    create_uninstaller
    
    echo
    print_status "Installation completed successfully!"
    echo
    echo "🐧 OpenTiler has been installed to:"
    echo "   Installation Directory: $INSTALL_DIR"
    echo "   Desktop Entry: $HOME/.local/share/applications/opentiler.desktop"
    echo "   Command-line: $HOME/.local/bin/opentiler"
    echo
    echo "🚀 You can now run OpenTiler:"
    echo "   - From applications menu (search for 'OpenTiler')"
    echo "   - From command line: opentiler"
    echo "   - Direct launcher: $INSTALL_DIR/opentiler_launcher.sh"
    echo
    echo "🗑️  To uninstall, run: $INSTALL_DIR/uninstall.sh"
    echo
    print_info "Installation log saved to: $INSTALL_DIR/install.log"
    
    # Save installation info
    cat > "$INSTALL_DIR/install.log" << EOF
OpenTiler Linux Installation Log
=================================
Date: $(date)
Distribution: $DISTRO
Python: $($PYTHON_CMD --version)
Installation Directory: $INSTALL_DIR
Desktop Entry: $HOME/.local/share/applications/opentiler.desktop
Command-line: $HOME/.local/bin/opentiler
Launcher Script: $INSTALL_DIR/opentiler_launcher.sh
Uninstaller: $INSTALL_DIR/uninstall.sh
EOF
}

# Run main function
main "$@"
