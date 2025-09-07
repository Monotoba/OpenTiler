# OpenTiler User Manual

Note: In-app help (Help → Help Contents) is available in OpenTiler 1.3.0 and reflects the current menus and tools.

![OpenTiler Hero](../images/opentiler-hero-image.png)

*Professional document scaling and tiling for architects, engineers, and professionals*

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Loading Documents](#loading-documents)
5. [Scaling Documents](#scaling-documents)
6. [Tiling and Export](#tiling-and-export)
7. [Settings and Configuration](#settings-and-configuration)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Introduction

OpenTiler is a professional desktop application for scaling and tiling large documents for printing. It's designed for architects, engineers, and anyone who needs to print large-format documents on standard printers.

### Key Features
- **Document Support**: PDF, images, RAW camera files, CAD formats
- **Precise Scaling**: Real-world measurement tools
- **Professional Tiling**: Multi-page PDF export with assembly guides
- **Configurable Quality**: 75-600 DPI output options
- **Cross-Platform**: Windows, macOS, Linux support

## Installation

### System Requirements
- **Operating System**: Windows 7/10/11, macOS 10.14+, Linux (Ubuntu/Debian/Arch)
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 500MB free space

### Installation Methods

#### Method 1: Using pip (Recommended)
```bash
pip install opentiler
```

#### Method 2: From Source
```bash
git clone https://github.com/Monotoba/OpenTiler.git
cd OpenTiler
pip install -r requirements.txt
python main.py
```

#### Method 3: Platform-Specific Installers
- **Windows**: MSI installer (use `installers/create_windows_exe.py`)
- **macOS**: DMG package (use `installers/create_macos_app.py`)
- **Linux**: DEB/RPM packages (use build scripts in installers/ folder)
- **Note**: See `BUILD_INSTRUCTIONS.md` for creating installers

#### Method 4: Platform Installation Scripts
```bash
# macOS: Automated installation from source
./installers/install_macos.sh

# Linux: Automated installation from source
./installers/install_linux.sh
```

#### Method 5: Linux Packages
```bash
# Create DEB and RPM packages
python installers/create_linux_packages.py --format both

# Install DEB package
sudo dpkg -i opentiler_*.deb && sudo apt-get install -f

# Install RPM package
sudo rpm -i opentiler-*.rpm
```

### Optional Dependencies

#### For CAD File Support
```bash
pip install ezdxf
```

#### For RAW Image Support
```bash
pip install rawpy numpy
```

## Getting Started

### First Launch
1. Launch OpenTiler from your applications menu or command line
2. The main window opens with three panels:
   - **Document Viewer** (left): Shows your loaded document
   - **Preview Panel** (right): Shows tile layout and thumbnails
   - **Toolbar** (top): Quick access to common functions

### Main Interface Overview

OpenTiler features a clean, professional interface designed for efficient workflow:

![OpenTiler Main Interface](../images/01-sky-skanner-loaded.png)

The main interface consists of:
1. **Menu Bar** - Access to all application functions
2. **Toolbar** - Quick access to common tools
3. **Document Viewer** - Main area for viewing and working with documents
4. **Preview Panel** - Shows how the document will be tiled
5. **Status Bar** - Displays current document information and status

#### Menu System

OpenTiler provides comprehensive menu access to all features:

**File Menu**
![File Menu](../images/13-file-menu.png)

**Edit Menu**
![Edit Menu](../images/14-edit-menu.png)

**View Menu**
![View Menu](../images/15-view-menu.png)

**Tools Menu**
![Tools Menu](../images/16-tools-menu.png)

**Help Menu**
![Help Menu](../images/17-help-menu.png)

#### Individual Menu Functions

**File Operations**
- **File → Open**: Load documents from your computer
  ![File Open Dialog](../images/09-file-open-dialog.png)

- **File → Recent Files**: Quick access to recently opened documents
  ![Recent Files](../images/10-file-recent-files.png)

**View Controls**
- **View → Zoom In**: Increase document magnification
  ![Zoom In Result](../images/12-view-zoom-in.png)

- **View → Fit to Window**: Automatically fit document to viewer
  ![Fit to Window](../images/13-view-fit-window.png)

- **View → Rotate Left/Right**: Rotate document orientation
  ![Rotate Left](../images/14-view-rotate-left.png)
  ![Rotate Right](../images/15-view-rotate-right.png)

**Tools Access**
- **Tools → Scale Tool**: Open the scaling measurement dialog
  ![Scale Tool](../images/16-tools-scale-tool.png)

- **Tools → Tile Preview**: Access tile preview functionality
  ![Tile Preview](../images/17-tools-tile-preview.png)

**Settings and Help**
- **Edit → Preferences**: Access application settings
  ![Preferences](../images/11-edit-preferences.png)

- **Help → About**: View application information
  ![About Dialog](../images/18-help-about.png)

- **Help → User Manual**: Access this documentation
  ![User Manual](../images/19-help-user-manual.png)

#### Toolbar Icons
- 📁 **Open**: Load a document
- 🔍+ **Zoom In**: Increase document zoom
- 🔍- **Zoom Out**: Decrease document zoom
- 🖥️ **Fit to Window**: Fit document to viewer
- 📏 **Scale Tool**: Set real-world measurements
- 🔄 **Rotate**: Rotate document 90°
- 💾 **Export**: Export tiled document
- ⚙️ **Settings**: Application preferences

#### Menu Bar
- **File**: Open, recent files, export, exit
- **View**: Zoom, rotation, display options
- **Tools**: Scaling, unit converter, calculator
- **Settings**: Preferences and configuration
- **Help**: User manual, about

## Loading Documents

### Supported Formats

#### Standard Formats
- **PDF**: Multi-page and single-page documents (Multi-page not yet supported)
- **Images**: PNG, JPEG, TIFF, BMP, GIF, SVG
- **RAW**: Camera RAW formats (.cr2, .nef, .arw, .dng, .orf, .rw2, .pef, .srw, .raf)

#### CAD Formats (with ezdxf)
- **DXF**: AutoCAD Drawing Exchange Format
- **FreeCAD**: FreeCAD native format

### Loading a Document
1. Click **File → Open** or press `Ctrl+O`
2. Browse to your document file
3. Select the file and click **Open**
4. The document appears in the viewer

### Document with Sky Skanner Example

Here's OpenTiler with the Sky Skanner architectural plan loaded:

![OpenTiler with Document Loaded](../images/opentiler-with-document.png)

The document viewer shows:
- **Document content** in the main viewing area
- **Current zoom level** in the status bar
- **Document dimensions** and scale information
- **Navigation controls** for panning and zooming

### Recent Files
- Access recently opened files via **File → Recent Files**
- Configure the number of recent files in Settings

## Scaling Documents

### Why Scale Documents?
Scaling ensures that measurements in your printed tiles match real-world dimensions. This is crucial for architectural drawings, engineering plans, and technical documents.

### Using the Scale Tool

#### Step 1: Open the Scale Tool
Click the **📏 Scale Tool** button or **Tools → Scaling Dialog**:

![Scale Tool Dialog](../images/03-scale-tool-opened.png)

The scaling dialog opens with measurement tools and input fields.

#### Step 2: Select Two Points on Known Distance
Click two points on a known measurement in your document. For example, selecting wing tips on an aircraft plan:

![Wing Tips Selected](../images/04-wing-tips-selected.png)

The selected points are marked and the pixel distance is calculated automatically.

#### Step 3: Enter Real-World Distance
Input the actual real-world distance between the selected points:

![Distance Entered](../images/05-distance-460mm.png)

In this example, we're setting the wing span to 460mm.

#### Step 4: Apply the Scale
Click "Apply" to set the scale factor:

![Success Dialog](../images/06-success-dialog.png)

A success dialog confirms the scale has been applied.

#### Step 5: Scale Applied Successfully
The document is now properly scaled for accurate measurements:

![Scale Applied](../images/07-scale-applied-complete.png)

![Final Scaled Document](../images/08-all-dialogs-closed.png)

#### Two-Point Measurement Method Summary
1. **Select Known Distance**: Click two points on a known measurement
2. **Enter Real Distance**: Input the actual real-world distance
3. **Choose Units**: Select mm or inches
4. **Apply Scale**: Click "Apply" to set the scale factor
5. **Confirm**: Click "OK" on the success dialog

#### Example: Scaling the Sky Skanner Aircraft Plan
1. Open the Sky Skanner plan in OpenTiler
2. Use the Scale Tool to select the wing tips (460mm span)
3. Enter "460" in the real distance field
4. Select "mm" as the unit
5. Click "Apply" - your document is now properly scaled for 460mm wing span

### Scale Calculator
Access **Tools → Scale Calculator** for:
- Converting between different scales (1:100, 1:50, etc.)
- Calculating dimensions at different scales
- Planning print sizes

### Unit Converter
Access **Tools → Unit Converter** for:
- Converting between millimeters and inches
- Precise unit conversions for measurements

## Tiling and Export

### Understanding Tiling
Tiling breaks large documents into smaller pages that fit on standard printers. Each tile overlaps slightly (gutter) for easy assembly.

### Preview Panel

The preview panel shows how your document will be tiled:

![OpenTiler Preview Panel](../images/opentiler-preview-panel.png)

The preview shows:
- **Individual tiles** as separate pages
- **Overlap areas** between adjacent tiles
- **Crop marks** at tile boundaries
- **Page numbers** for assembly reference

### Setting Up Tiling
1. Load and scale your document
2. Click **💾 Export** or **File → Export Document**
3. Configure export settings:
   - **Format**: Choose export format
   - **Page Size**: A4, Letter, A3, etc.
   - **DPI**: Quality setting (75-600 DPI)
   - **Gutter**: Overlap between tiles (default: 10mm)

### Export Formats

#### PDF Formats
- **Multi-page PDF**: Each tile as separate page + metadata page
- **Single-page Composite**: All tiles combined in one page

#### Image Formats
- **PNG**: High quality, lossless
- **JPEG**: Smaller files, good for photos
- **TIFF**: Professional quality, large files

### Metadata Pages
Automatically included with PDF exports:
- **Project Information**: Document name, scale, date
- **Page Assembly Map**: Visual guide showing tile arrangement
- **Tile Grid**: Numbered tiles for easy assembly

### Export Process
1. Configure settings in export dialog
2. Click **Export**
3. Choose output location and filename
4. Wait for export completion
5. Check output folder for generated files

## Settings and Configuration

### Accessing Settings
Click **⚙️ Settings** button or **Settings → Preferences** to open the comprehensive settings dialog:

![Settings Dialog Main](../images/test-settings-main.png)

Settings are automatically saved between sessions and organized into multiple tabs for easy navigation.

### General Settings Tab
Configure basic application preferences:

![General Settings](../images/test-settings-tab-general.png)

- **Default Units**: mm or inches
- **Default DPI**: 75, 100, 150, 300, or 600 DPI
- **Default Page Size**: A4, Letter, A3, etc.
- **Recent Files**: Number of recent files to remember
- **Language**: Application language settings
- **Theme**: Light or dark interface theme

### Display Settings Tab
Control how documents and tiles are displayed:

![Display Settings](../images/test-settings-tab-display.png)

- **Page Indicators**: Show page numbers on tiles
- **Crop Marks**: Show cutting guides at tile boundaries
- **Scale Lines**: Display measurement lines on documents
- **Grid Display**: Show tile grid overlay
- **Zoom Behavior**: Mouse wheel and zoom controls
- **Pan Controls**: Middle mouse button for panning

### Tiling Settings Tab
Configure tile layout and overlap settings:

![Tiling Settings](../images/test-settings-tab-tiling.png)

- **Tile Overlap**: Gutter size between tiles (recommended: 10mm)
- **Page Orientation**: Portrait or landscape per plan
- **Tile Size**: Custom tile dimensions
- **Assembly Guides**: Include assembly instructions
- **Crop Mark Style**: Line style and thickness

### Page Settings Tab
Control page layout and printing options:

![Page Settings](../images/test-settings-tab-page.png)

- **Page Size**: A4, Letter, A3, Legal, Custom
- **Margins**: Page margins for printing
- **Orientation**: Portrait or landscape
- **Print Quality**: DPI settings for output
- **Paper Type**: Plain, photo, technical drawing

### Scale Settings Tab
Configure scaling tool behavior:

![Scale Settings](../images/test-settings-tab-scale.png)

- **Default Units**: Preferred measurement units
- **Precision**: Decimal places for measurements
- **Scale Tool Behavior**: Point selection and measurement
- **Unit Conversion**: Automatic unit conversions
- **Scale Factor Display**: Show current scale factor

### Export Settings Tab
Control export formats and quality:

![Export Settings](../images/test-settings-tab-export.png)

- **Include Metadata Page**: Add assembly guide page
- **Metadata Position**: First or last page
- **Default Export Format**: PDF, PNG, JPEG, or TIFF
- **Output Directory**: Default save location
- **Quality Settings**: Compression and DPI options
- **File Naming**: Automatic file naming patterns

### Advanced Settings Tab
Configure advanced options and performance:

![Advanced Settings](../images/test-settings-tab-advanced.png)

- **Memory Usage**: RAM allocation for large documents
- **Performance**: Rendering and processing options
- **Debug Mode**: Enable detailed logging
- **Plugin Settings**: Configure installed plugins
- **Automation**: Enable automation server
- **Cache Settings**: Temporary file management

## Troubleshooting

### Common Issues

#### "Export Failed" Error
1. Check output directory permissions
2. Ensure sufficient disk space
3. Try a different output location
4. Check console output for detailed errors

#### Document Won't Load
1. Verify file format is supported
2. Check file isn't corrupted
3. For RAW files, install `rawpy`: `pip install rawpy`
4. For CAD files, install `ezdxf`: `pip install ezdxf`

#### Poor Print Quality
1. Increase DPI setting (try 300 or 600)
2. Check source document resolution
3. Ensure proper scaling is applied
4. Use PNG format for highest quality

#### Tiles Don't Align
1. Verify scale factor is correctly set
2. Check gutter settings (10mm recommended)
3. Use crop marks for precise cutting
4. Follow page assembly map carefully

### Getting Help
- Check this manual for solutions
- Review FAQ section below
- Check GitHub issues for known problems
- Contact support for technical assistance

## FAQ

### General Questions

**Q: What file formats does OpenTiler support?**
A: PDF, PNG, JPEG, TIFF, BMP, GIF, SVG, and with optional libraries: RAW camera files and CAD formats (DXF, FreeCAD).

**Q: Can I print on different paper sizes?**
A: Yes, OpenTiler supports A4, Letter, A3, and other standard page sizes.

**Q: How accurate is the scaling?**
A: Very accurate when properly calibrated. Use the two-point measurement method for best results.

### Technical Questions

**Q: Why do I need to scale documents?**
A: Scaling ensures printed measurements match real-world dimensions, essential for technical drawings.

**Q: What DPI should I use?**
A: 300 DPI for most uses, 600 DPI for highest quality, 150 DPI for faster processing.

**Q: How do gutters work?**
A: Gutters provide overlap between tiles for cutting and alignment. 10mm is recommended for most uses.

### Installation Questions

**Q: Do I need Python installed?**
A: For source installation, yes. Platform-specific installers include Python.

**Q: Can I run this on older Windows versions?**
A: Windows 7 and newer are supported with appropriate Python versions.

**Q: What about Linux distributions?**
A: Tested on Ubuntu/Debian and Arch Linux. Should work on most modern distributions.

### Installation and Dependencies

**Q: How do I install optional dependencies?**
A: Use pip to install specific features:
- CAD support: `pip install ezdxf`
- RAW images: `pip install rawpy numpy`
- All optional: `pip install opentiler[all]`

**Q: Can I use OpenTiler without installing Python?**
A: Yes, download platform-specific installers (.msi for Windows, .dmg for macOS, .deb/.rpm for Linux) that include Python.

**Q: What if I get import errors?**
A: Ensure all dependencies are installed. Run `pip install -r requirements.txt` in the OpenTiler directory.

---

*For more help, visit the [OpenTiler GitHub repository](https://github.com/Monotoba/OpenTiler) or check the developer documentation.*
