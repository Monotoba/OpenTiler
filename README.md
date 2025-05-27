# OpenTiler

A PySide6-based desktop application for scaling and tiling architectural drawings, blueprints, and technical documents.

## Features

- Load and view PDF, image, and SVG documents
- Accurate scaling based on real-world measurements
- Interactive scaling tool with point selection
- Unit conversion between mm and inches
- Scale calculator for planning
- Tile preview and export functionality
- Support for multiple document formats

## Requirements

- Python 3.10+
- PySide6
- Pillow (PIL)
- PyMuPDF

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Monotoba/OpenTiler.git
cd OpenTiler
```

2. Create and activate a virtual environment:
```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

### Basic Workflow

1. **Load Document**: Use File → Open to load a PDF, image, or SVG file
2. **Set Scale**: Use Tools → Scaling Tool to set real-world scale
   - Click two points on the document
   - Enter the real-world distance between them
   - Apply the scale
3. **Preview Tiles**: View the tile layout in the preview panel
4. **Export**: Use File → Export to save tiled output

### Tools

- **Scaling Tool**: Set document scale by measuring known distances
- **Unit Converter**: Convert between millimeters and inches
- **Scale Calculator**: Calculate scale factors and dimensions

## Supported Formats

### Input
- **PDF**: Single and multi-page documents
- **Images**: PNG, JPEG, TIFF, BMP
- **Vector**: SVG files

### Output
- Multi-page PDF
- Individual image tiles
- Composite images

## Configuration

The application stores settings automatically, including:
- Default units (mm/inches)
- Default DPI (300)
- Last used directories
- Window layout

## Development

### Project Structure
```
opentiler/
├── main.py              # Application entry point
├── opentiler/
│   ├── main_app.py      # Main application
│   ├── main_window.py   # Main window
│   ├── viewer/          # Document viewer components
│   ├── dialogs/         # Dialog windows
│   ├── exporter/        # Export functionality
│   ├── settings/        # Configuration management
│   └── utils/           # Utility functions
├── docs/                # Documentation
└── tests/               # Unit tests
```

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black opentiler/
flake8 opentiler/
mypy opentiler/
```

## License

MIT License with Attribution Requirement

## Author

Randall Morgan

## Copyright

© 2025 Randall Morgan
