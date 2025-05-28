# OpenTiler Developer Manual

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Development Setup](#development-setup)
5. [Code Organization](#code-organization)
6. [Key Classes and Modules](#key-classes-and-modules)
7. [Data Flow](#data-flow)
8. [Extension Points](#extension-points)
9. [Testing](#testing)
10. [Contributing](#contributing)

## Architecture Overview

OpenTiler follows a modular, object-oriented architecture built on PySide6 (Qt for Python). The application uses the Model-View-Controller (MVC) pattern with clear separation of concerns.

### Design Principles
- **Modularity**: Each component has a specific responsibility
- **Extensibility**: Easy to add new file formats and export options
- **Maintainability**: Clear code structure with comprehensive documentation
- **Cross-Platform**: Qt-based GUI ensures consistent behavior across platforms

### Technology Stack
- **GUI Framework**: PySide6 (Qt 6.x)
- **Image Processing**: Pillow (PIL)
- **PDF Handling**: PyMuPDF (fitz)
- **CAD Support**: ezdxf (optional)
- **RAW Images**: rawpy + numpy (optional)
- **Plugin System**: Custom plugin architecture with hooks
- **Automation**: TCP server for GUI automation and testing
- **Screen Capture**: Cross-platform screenshot tools (mss, pywinctl)
- **Build System**: setuptools
- **Documentation**: Markdown with automated screenshot generation

## Project Structure

```
OpenTiler/
├── main.py                 # Application entry point
├── opentiler/             # Main package
│   ├── __init__.py        # Package initialization
│   ├── main_window.py     # Main application window
│   ├── assets/            # Icons and resources
│   ├── dialogs/           # Dialog windows
│   │   ├── export_dialog.py
│   │   ├── scaling_dialog.py
│   │   ├── settings_dialog.py
│   │   └── unit_converter.py
│   ├── exporter/          # Export functionality
│   │   ├── base_exporter.py
│   │   ├── pdf_exporter.py
│   │   └── image_exporter.py
│   ├── settings/          # Configuration management
│   │   └── config.py
│   ├── utils/             # Utility functions
│   │   ├── file_utils.py
│   │   └── math_utils.py
│   └── viewer/            # Document viewing
│       ├── document_viewer.py
│       └── preview_panel.py
├── docs/                  # Documentation
│   ├── user/             # User documentation
│   ├── developer/        # Developer documentation
│   └── images/           # Screenshots and diagrams
├── requirements.txt       # Python dependencies
├── setup.py              # Installation script
├── CHANGELOG.md          # Version history
├── README.md             # Project overview
└── .gitignore            # Git exclusions
```

## Core Components

### 1. Main Window (`main_window.py`)
- **Purpose**: Primary application window and coordinator
- **Responsibilities**: Menu bar, toolbar, layout management, event coordination
- **Key Methods**: `create_menus()`, `create_toolbars()`, `open_file()`

### 2. Document Viewer (`viewer/document_viewer.py`)
- **Purpose**: Display and interact with loaded documents
- **Responsibilities**: Zoom, pan, rotation, overlay rendering
- **Key Methods**: `load_document()`, `zoom_in()`, `apply_scaling()`

### 3. Preview Panel (`viewer/preview_panel.py`)
- **Purpose**: Show tile layout and page thumbnails
- **Responsibilities**: Tile grid display, page assembly preview
- **Key Methods**: `update_preview()`, `generate_thumbnails()`

### 4. Export System (`exporter/`)
- **Purpose**: Convert documents to printable tiles
- **Components**: Base exporter, PDF exporter, image exporter
- **Key Methods**: `export()`, `create_metadata_page()`

### 5. Settings Management (`settings/config.py`)
- **Purpose**: Persistent configuration storage
- **Responsibilities**: User preferences, default values
- **Key Methods**: `get()`, `set()`, `load_defaults()`

### 6. Plugin System (`plugins/`)
- **Purpose**: Extensible architecture for adding functionality
- **Components**: Plugin manager, base plugin, hook system, content access
- **Key Features**: Before/after hooks, automation support, plugin registry
- **Key Methods**: `register_plugin()`, `execute_hook()`, `get_content()`

### 7. Automation System (`plugins/builtin/automation_plugin.py`)
- **Purpose**: GUI automation for testing and documentation
- **Components**: TCP server, automation client, screenshot capture
- **Key Features**: Remote control, dialog dismissal, screenshot generation
- **Key Methods**: `send_command()`, `capture_screenshot()`, `dismiss_any_dialog()`

## Development Setup

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Installation for Development
```bash
# Clone repository
git clone https://github.com/Monotoba/OpenTiler.git
cd OpenTiler

# Install dependencies
pip install -r requirements.txt

# Install optional dependencies
pip install ezdxf rawpy numpy  # CAD and RAW support
pip install pytest black flake8 mypy  # Development tools

# Run application
python main.py
```

### Development Tools
```bash
# Code formatting
black opentiler/

# Linting
flake8 opentiler/

# Type checking
mypy opentiler/

# Testing
pytest tests/
```

## Code Organization

### Module Dependencies
```
main.py
├── opentiler.main_window
│   ├── opentiler.viewer.document_viewer
│   ├── opentiler.viewer.preview_panel
│   ├── opentiler.dialogs.*
│   ├── opentiler.exporter.*
│   └── opentiler.settings.config
```

### Import Conventions
```python
# Standard library
import os
import sys
from typing import List, Dict, Optional

# Third-party
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

# Local imports
from .settings.config import config
from .viewer.document_viewer import DocumentViewer
```

### Coding Standards
- **PEP 8**: Python style guide compliance
- **Type Hints**: Use typing annotations
- **Docstrings**: Google-style docstrings
- **Error Handling**: Comprehensive exception handling
- **Logging**: Use print() for debugging (consider logging module for production)

## Key Classes and Modules

### MainWindow Class
```python
class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.document_viewer = DocumentViewer()
        self.preview_panel = PreviewPanel()
        self.setup_ui()

    def setup_ui(self):
        """Initialize user interface."""
        self.create_menus()
        self.create_toolbars()
        self.create_layout()
```

### DocumentViewer Class
```python
class DocumentViewer(QScrollArea):
    """Document viewing widget with zoom and pan."""

    document_loaded = Signal(str)  # Emitted when document loads
    scale_changed = Signal(float)  # Emitted when scale changes

    def load_document(self, file_path: str) -> bool:
        """Load document from file path."""

    def apply_scaling(self, scale_factor: float, units: str):
        """Apply real-world scaling to document."""
```

### Export System
```python
class BaseExporter:
    """Base class for all exporters."""

    def export(self, source_pixmap: QPixmap,
               page_grid: List[dict],
               output_path: str,
               **kwargs) -> bool:
        """Export document tiles."""
        raise NotImplementedError

class PDFExporter(BaseExporter):
    """PDF export implementation."""

    def export(self, source_pixmap, page_grid, output_path, **kwargs):
        """Export as multi-page or composite PDF."""
```

## Data Flow

### Document Loading Flow
1. **User Action**: File → Open or drag-and-drop
2. **File Detection**: `file_utils.detect_format()`
3. **Format Loading**: Format-specific loader (PDF, image, RAW, CAD)
4. **Pixmap Creation**: Convert to QPixmap for display
5. **Viewer Update**: `document_viewer.load_document()`
6. **Preview Update**: `preview_panel.update_preview()`

### Scaling Flow
1. **User Input**: Scale tool dialog with two-point measurement
2. **Calculation**: `math_utils.calculate_scale_factor()`
3. **Application**: `document_viewer.apply_scaling()`
4. **Preview Update**: Tile grid recalculation
5. **Settings Save**: Persist scale factor

### Export Flow
1. **Configuration**: Export dialog settings
2. **Tile Generation**: Calculate page grid
3. **Exporter Selection**: Based on format choice
4. **Export Process**: `exporter.export()` with progress tracking
5. **Metadata Creation**: Assembly maps and project info
6. **File Output**: Write to specified location

## Extension Points

### Adding New File Formats
1. **Detection**: Add format to `file_utils.SUPPORTED_FORMATS`
2. **Loader**: Implement loader function in `file_utils.py`
3. **Integration**: Add to `document_viewer._load_document()`

Example:
```python
def load_custom_format(file_path: str) -> QPixmap:
    """Load custom format and return QPixmap."""
    # Implementation here
    return pixmap
```

### Adding New Export Formats
1. **Exporter Class**: Inherit from `BaseExporter`
2. **Implementation**: Override `export()` method
3. **Registration**: Add to export dialog format list
4. **Integration**: Add to export dialog logic

Example:
```python
class SVGExporter(BaseExporter):
    def export(self, source_pixmap, page_grid, output_path, **kwargs):
        """Export as SVG format."""
        # Implementation here
        return True
```

### Adding New Tools
1. **Dialog**: Create dialog class in `dialogs/`
2. **Menu Integration**: Add to main window menu
3. **Toolbar**: Add toolbar button if needed
4. **Functionality**: Implement tool logic

### Plugin System Architecture

OpenTiler features a comprehensive plugin system that allows extending functionality without modifying core code.

#### Plugin Components
- **Plugin Manager**: Manages plugin lifecycle and registration
- **Base Plugin**: Abstract base class for all plugins
- **Hook System**: Before/after hooks for all major operations
- **Content Access**: Secure access to application state and UI elements

#### Creating a Plugin
```python
from plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "My Plugin"
        self.version = "1.0.0"

    def initialize(self, main_window):
        """Initialize plugin with main window reference."""
        self.main_window = main_window
        self.register_hooks()

    def register_hooks(self):
        """Register plugin hooks."""
        self.hook_manager.register_hook('before_document_load', self.before_load)
        self.hook_manager.register_hook('after_scale_apply', self.after_scale)

    def before_load(self, file_path):
        """Called before document loading."""
        self.log_info(f"Loading document: {file_path}")

    def after_scale(self, scale_factor):
        """Called after scale is applied."""
        self.log_info(f"Scale applied: {scale_factor}")
```

#### Automation Plugin

The built-in automation plugin provides GUI automation capabilities:

```python
# Start OpenTiler with automation
python main.py --automation-mode

# Connect from automation client
from tools.automation_client import OpenTilerAutomationClient

client = OpenTilerAutomationClient()
client.connect()

# Execute commands
client.send_command('load_demo_document')
client.send_command('open_scale_tool')
client.send_command('capture_screenshot', {'filename': 'screenshot.png'})
```

#### Available Automation Commands
- **Document Operations**: `load_demo_document`, `fit_to_window`
- **Scale Tool**: `open_scale_tool`, `select_wing_tip_points`, `apply_scale`
- **UI Interaction**: `click_menu_item`, `dismiss_any_dialog`
- **Screenshot Capture**: `capture_screenshot`
- **View Controls**: `zoom_in`, `zoom_out`, `rotate_left`, `rotate_right`

#### Universal Dialog Dismissal

The automation system includes a universal dialog dismissal mechanism:

```python
def dismiss_any_dialog(self):
    """Dismiss any open dialog using multiple strategies."""
    # 1. Find common close buttons (OK, Close, Cancel, etc.)
    # 2. Handle QMessageBox dialogs specifically
    # 3. Try dialog.close(), dialog.accept(), dialog.reject()
    # 4. Send Escape key as fallback
    # 5. Log all attempts for debugging
```

This system can handle any dialog type and is used extensively in documentation generation.

### Documentation Generation System

OpenTiler includes an automated documentation generation system that creates professional screenshots and documentation:

#### Screenshot Automation
```python
# Generate comprehensive documentation
python comprehensive_documentation_workflow.py

# Test specific features
python test_settings_tabs.py
```

#### Generated Documentation Assets
- **Scale Tool Workflow**: Complete 460mm wing scaling process (8 screenshots)
- **Menu System**: All menu items and dialogs (11 screenshots)
- **Settings System**: All settings tabs and configurations (14 screenshots)
- **Professional Quality**: 1600x1000 PNG screenshots with real UI interactions

#### Documentation Workflow Features
- **Real Document Loading**: Uses actual Sky Skanner plan from `plans/original_plans/`
- **Accurate Scaling**: Applies real 460mm wing span measurement
- **Complete UI Coverage**: Every menu, dialog, and settings tab
- **Universal Dialog Handling**: Automatically dismisses any dialog type
- **Error Recovery**: Robust error handling and logging
- **Cross-Platform**: Works on Windows, Linux, and macOS

#### Screenshot Organization
```
docs/images/
├── 01-sky-skanner-loaded.png      # Document loaded
├── 02-fit-to-window.png           # Fit to window
├── 03-scale-tool-opened.png       # Scale tool dialog
├── 04-wing-tips-selected.png      # Wing tips selected
├── 05-distance-460mm.png          # Distance entered
├── 06-success-dialog.png          # Success confirmation
├── 07-scale-applied-complete.png  # Scale applied
├── 08-all-dialogs-closed.png      # Final result
├── 09-file-open-dialog.png        # File operations
├── 10-file-recent-files.png       # Recent files
├── 11-edit-preferences.png        # Edit menu
├── 12-view-zoom-in.png            # View controls
├── 13-view-fit-window.png         # Fit to window
├── 14-view-rotate-left.png        # Rotation
├── 15-view-rotate-right.png       # Rotation
├── 16-tools-scale-tool.png        # Tools menu
├── 17-tools-tile-preview.png      # Tile preview
├── 18-help-about.png              # Help dialogs
├── 19-help-user-manual.png        # User manual
├── test-settings-main.png         # Settings main
├── test-settings-tab-*.png        # All settings tabs
└── ...                           # Additional screenshots
```

#### Integration with Documentation
All screenshots are automatically integrated into:
- **README.md**: Main project overview with workflow examples
- **USER_MANUAL.md**: Complete user guide with step-by-step instructions
- **DEVELOPER_MANUAL.md**: Technical documentation with automation examples

The documentation system ensures that all screenshots show real functionality and are kept up-to-date with the actual application interface.

## Testing

### Test Structure
```
tests/
├── test_file_utils.py     # File handling tests
├── test_math_utils.py     # Mathematical calculations
├── test_exporters.py      # Export functionality
├── test_config.py         # Settings management
└── fixtures/              # Test files
    ├── sample.pdf
    ├── sample.png
    └── sample.dxf
```

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_file_utils.py

# With coverage
pytest --cov=opentiler

# Verbose output
pytest -v
```

### Test Examples
```python
def test_scale_calculation():
    """Test scale factor calculation."""
    from opentiler.utils.math_utils import calculate_scale_factor

    pixel_distance = 100
    real_distance = 5000  # mm
    scale_factor = calculate_scale_factor(pixel_distance, real_distance)

    assert scale_factor == 50.0  # 5000/100
```

## Contributing

### Development Workflow
1. **Fork**: Fork the repository on GitHub
2. **Branch**: Create feature branch (`git checkout -b feature/new-feature`)
3. **Develop**: Implement changes with tests
4. **Test**: Run test suite (`pytest`)
5. **Format**: Format code (`black opentiler/`)
6. **Commit**: Commit changes with clear messages
7. **Push**: Push to your fork
8. **PR**: Create pull request

### Code Review Checklist
- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have docstrings
- [ ] Type hints are used where appropriate
- [ ] Tests are included for new functionality
- [ ] No breaking changes to existing API
- [ ] Documentation is updated if needed

### Commit Message Format
```
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting changes
- refactor: code restructuring
- test: adding tests
- chore: maintenance tasks
```

Example:
```
feat(export): add SVG export format

- Implement SVGExporter class
- Add SVG option to export dialog
- Include tests for SVG export functionality
```

---

*For more technical details, see the inline code documentation and docstrings throughout the codebase.*
