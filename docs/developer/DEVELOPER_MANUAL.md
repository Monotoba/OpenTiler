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
- **Build System**: setuptools
- **Documentation**: Markdown + Sphinx

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
