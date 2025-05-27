Here is the revised and reorganized specification for **OpenTiler**, rewritten in a **professional, technical, and friendly** tone, with grammar and spelling corrected, structure improved, and the **scale calculator tool** integrated as requested.

---

# OpenTiler – Functional Specification & Implementation Plan

## Project Title

**OpenTiler**

---

## Overview

**OpenTiler** is a PySide6-based desktop application tailored for loading scanned architectural drawings, blueprints, and technical documents. It enables users—ranging from hobbyists and makers to engineers and designers—to:

* Accurately scale documents based on real-world measurements
* Annotate and preview tile layouts
* Export documents into tiled, printable formats for precise real-world use

The tool is designed with usability and accuracy in mind, facilitating exacting print and digital output based on real-world measurements and scaling.

---

## Target Technologies

| Component             | Technology Used                  |
| --------------------- | -------------------------------- |
| Programming Language  | Python 3.11+                     |
| GUI Framework         | PySide6 (Qt for Python)          |
| Image Handling        | Pillow (PIL), pdf2image, PyMuPDF |
| Vector Graphics       | QtSvg, cairosvg                  |
| PDF Generation        | reportlab, PyMuPDF, QtPDF        |
| Unit Testing          | pytest                           |
| CI/CD & Quality Tools | flake8, mypy, black, coverage.py |

---

## Supported Input Formats

### 1. Document Types

* **Raster Formats**: PNG, JPEG, TIFF, RAW image formats
* **Vector Formats**: PDF (single/multi-page), SVG

### 2. PDF Specifics

* Multi-page support with individual scaling per page
* Option to copy the scale from the first page across all pages

### 3. DPI (Resolution)

* Configurable DPI options: **75**, **100**, **150**, **300** (default), **600**

---

## Core Features

### 1. Document Viewer & Controls

* Scrollable, zoomable image/PDF viewer
* Middle-mouse panning and toolbar controls
* Rotation: 0°, 90°, 180°, 270°
* Toggle display of tile grid, gutters, and overlaps
* Real-time tile preview panel

---

### 2. Scaling Tool

#### Purpose

Allows users to define real-world scale by selecting two points and entering the real-world distance between them.

#### Interface

* Accessible via toolbar or menu
* Opens a **Scaling Dialog** (dockable or floating)

#### Workflow

1. **Select Tool** → **Scaling Dialog** appears
2. User selects two points on the document
3. Coordinates for both points displayed in dialog
4. User enters real-world distance and selects units (mm or inches)
5. Scale ratio is calculated and applied

#### Features

* Supports scales both < 1.000 and ≥ 1.000
* Precision: 3+ decimal places
* Units: millimeters or inches (floating-point values)
* Visual feedback:

  * **Red lines** = tile boundaries
  * **Blue lines** = gutters
  * **Transparent hashed area** = gutter overlaps
* Crosshair cursor and zoom assist during point selection
* Display coordinates and distance in both the **Scaling Dialog** and **Status Bar**

---

### 3. Scale Calculator Tool (New)

#### Purpose

Provides a standalone calculator for converting between real-world dimensions and scale values, helping users plan documents and tiling layout prior to measurement.

#### Interface

* Accessible via the Tools menu
* Launches the **ScaleCalculatorDialog**

#### Features

* Input fields:

  * Real-world length
  * Measured (document) length
* Output:

  * Calculated scale factor (e.g., 1:75, 2.5:1)
  * Reverse calculation: Enter scale + one length to get the other
* Supports inches and millimeters
* Auto-updating results
* Useful for preparing document scaling in advance

---

### 4. Unit Conversion Tool

* Convert between inches and millimeters
* Real-time updates as the user types
* Available from the Tools menu or via shortcut

---

### 5. Tiling and Exporting

#### Tile Calculation Based On:

* User-defined scale
* DPI setting
* Page size (A4, Letter, etc.)
* Orientation and gutter settings

#### Output Formats

* Multi-page PDF
* Multi-page raster image set
* Composite single-page image or PDF

#### Export Details

* Configurable output directory (default or per session)
* Fixed tile size matching selected paper size
* Partial tiles are padded to full-page size
* Embedded metadata including:

  * Scale
  * DPI
  * Timestamp
  * Document title
* Optional metadata summary page in exports

---

### 6. Configuration & Preferences

* Default units (mm or in)
* Default DPI: **300**
* Default input/output directories
* Last used settings persisted
* Theme customization (if implemented)
* Page size default: **A4**

---

## GUI Layout

### Main Window

* **Menu Bar**: File, Edit, Tools, Settings, Help
* **Toolbar**: Load, Zoom, Pan, Scale Tool, Export
* **Status Bar**: Zoom level, scale, tile count, current measurement
* **Viewer Panel**: Scrollable and zoomable document area
* **Preview Panel**: Real-time tiled page previews

---

### Dialogs

#### ScalingDialog

* Point 1 and Point 2 coordinates
* Real-world distance entry
* Unit selector
* Apply / Cancel buttons

#### UnitConverterDialog

* Input field
* Unit dropdowns (mm/in)
* Real-time conversion output

#### ScaleCalculatorDialog (New)

* Inputs: document length and real-world length
* Unit selectors for both
* Output: scale factor (as ratio and decimal)
* Optional reverse calculation (given scale and one dimension)

#### SettingsDialog

* Units, DPI, directories
* Interface themes (optional)

---

## Acceptance Criteria

| Feature          | Criteria                                                   |
| ---------------- | ---------------------------------------------------------- |
| File Loading     | Accepts valid file types and displays first page           |
| Measurement Tool | Accurate selection of two points with visible feedback     |
| Scaling Dialog   | Accepts mm/in, floating-point, accurate scale              |
| Tiling           | Accurate grid layout with gutters, DPI, and paper size     |
| Exporting        | PDF and image exports with correct layout, metadata        |
| Unit Conversion  | Converts mm ↔ inches correctly                             |
| Scale Calculator | Calculates correct scale from two lengths, both directions |

---

## Development Guidelines

* **UI Construction**: Use `.ui` files where possible (Qt Designer)

* **Code Organization**:

  ```
  opentiler/
  ├── main.py
  ├── viewer/
  │   ├── viewer.py
  │   └── zoompan.py
  ├── dialogs/
  │   ├── scaling_dialog.py
  │   ├── unit_converter.py
  │   ├── scale_calculator.py
  ├── exporter/
  │   ├── pdf_exporter.py
  │   ├── image_exporter.py
  ├── settings/
  │   └── config.py
  └── utils/
      └── helpers.py
  ```

* **Architecture**: MVC or component-based structure

* **Testing**: pytest for unit and integration testing

* **Versioning**: Follow [SemVer](https://semver.org/)

* **VCS**: git with structured commits and CI/CD

* **Formatting & Linting**: `black`, `flake8`, `mypy`

* **Documentation**:

  * `README.md`
  * `CONTRIBUTING.md`
  * `CODE_OF_CONDUCT.md`
  * `LICENSE` (MIT + attribution)
  * `CHANGELOG.md`

---

## Optional Future Features

* Annotations (text, lines, arrows)
* Snap-to-grid tools
* Batch page scaling
* Grid overlays
* Auto-measurement (AI-assisted point recognition)
* Theme editor and export presets

---

## Project Metadata

* **Project Author**: Randall Morgan
* **GitHub**: [github.com/Monotoba/OpenTiler](https://github.com/Monotoba/OpenTiler)
* **License**: MIT License with Attribution Requirement
* **Copyright**:
  © 2025 Randall Morgan

---


