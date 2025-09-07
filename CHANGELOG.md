# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.2] - 2025-09-07

### Added
- CI test matrix for Python 3.10–3.13; official support set to Python 3.10+.
- mypy configuration (`mypy.ini`) to keep static typing checks practical with Qt/third‑party libs.
- Contributors section and Contributing docs surfaced in app/docs.

### Changed
- Release workflow stabilized (removed YAML heredocs; version checks use `python -c`).
- Lint/format workflows: auto‑format with Black/isort; flake8 configured to align with Black.
- Tests refactored to avoid optional hard deps in CI; integration tests marked/isolated.
- Optional/GUI imports guarded to run in headless CI (Qt shims for helpers).

### Fixed
- Flake8 errors (unused vars/import order/indent) across dialogs, viewer, and plugins.
- Type hint issues (use `typing.Callable`; guard external command types) to satisfy mypy.
- Help/About version strings and in‑app version display synchronized with release.

## [1.3.1] - 2025-09-06

### Added
- Contributing guides: `docs/CONTRIBUTING.md` and in-app help topic `opentiler/help/contributing.md`.

### Changed
- About dialog: adds “Contributors:” section with a call to action inviting community contributions.
- Version references updated to 1.3.1 across code, in-app help, and docs.

### Internal
- Release: bump version to 1.3.1 across code, help, and docs.

## [1.3.0] - 2025-09-06

### Added
- In-app Help improvements:
  - Recursive help navigation with filtering (QTreeWidget-based).
  - Markdown rendering (uses `python-markdown` when available; falls back to Qt Markdown).
  - “Open in Browser” action (renders MD to temp HTML with base href).
  - Topic titles derived from first H1; fallback to filename.
  - Bundled `help.css` and assets; populated help topics under `opentiler/help/`.
- Help toolbar: Print action using `QPrinter/QPrintDialog`.

### CI
- Release workflow: GitHub Actions builds on tag push and creates a release with artifacts; checks `setup.py` version against tag.

## [1.2.0] - 2025-09-02

### Added
- Measurements: multiple overlays with selection, drag endpoints, click-to-select, Delete/Backspace removal; persisted in project state.
- Printing: option to print measurement overlays (line + text) when enabled.
- Settings: convenience toggle “Print measurements (line + text)” tying to existing print flags.

### Changed
- Viewer/Previews: always render measurement overlays; live preview while measuring; show overlays in thumbnails.

### Fixed
- Preview refresh: auto-refresh page thumbnails when measurements change (add/drag/delete).
- Viewer input handling: safer event handling and defaults to avoid bubbling errors; centralized temp cursor handling.

## [1.0.0] - 2025-01-XX

### Added
- **Complete Professional Application**: Full-featured document scaling and tiling
- **Document Support**: PDF, PNG, JPEG, TIFF, SVG, BMP, GIF formats
- **RAW Image Support**: Professional camera RAW formats (.cr2, .nef, .arw, .dng, etc.)
- **CAD Format Support**: DXF and FreeCAD file import/export
- **Advanced Scaling Tools**: Two-point measurement with real-world scaling
- **Professional Tiling**: Multi-page PDF export with metadata pages
- **Composite Export**: Single-page PDF combining all tiles
- **Page Assembly Maps**: Visual guides for tile arrangement
- **Configurable DPI**: 75, 100, 150, 300, 600 DPI options
- **Unit Conversion**: mm ↔ inches with precision
- **Scale Calculator**: Standalone calculation tools
- **Document Rotation**: 90° clockwise/counterclockwise rotation
- **Professional UI**: Toolbar with standard icons and tooltips
- **Settings Persistence**: All preferences saved between sessions
- **Comprehensive Export**: PNG, JPEG, TIFF, PDF formats
- **Error Handling**: Graceful error handling with user guidance
- **Cross-Platform**: Windows 7/10/11, macOS, Linux support

## [1.0.1] - 2025-09-04

### Added
- Contributor guide: `AGENTS.md` with project structure, commands, style, testing, and PR conventions.
- Utilities for tiling: `compute_page_grid_with_gutters`, `compute_page_size_pixels`, and `summarize_page_grid` in `opentiler/utils/helpers.py`.

### Changed
- Viewer overlay: removed red page-edge boundary drawing in the main document viewer; only gutter/crop/registration/page indicators remain.
- Metadata page: removed red page boundaries from the tilemap and legend; shows gutter/printable area and page numbers only.
- Centralized tile slicing: `MainWindow.on_scale_applied` now uses helper `compute_page_grid_with_gutters`; legacy `_calculate_page_grid_with_gutters` now delegates (kept for compatibility).
- Consistent tile counts: `summarize_page_grid` used in preview panel, PDF exporter, and print metadata to compute `tiles_x/tiles_y/total_tiles`.
- Unified tile layout math: preview thumbnails and printed tiles now share `compute_tile_layout` for source/destination/printable rect calculations, ensuring matching on-screen and printed results.
- Exporters aligned: Image and PDF exporters now use `compute_tile_layout` to render each page, eliminating duplicate logic and aligning exported output with preview/print layout.
- Printing fix: Gutter offsets for physical printers are now computed from the printable area (px/mm derived from `QPageLayout.paintRectPixels`) to avoid content clipping at the top/right due to hardware margins and driver differences.
 - Printing fix (refined): Use printable area in millimeters (`QPageLayout.paintRect(QPageLayout.Millimeter)`) to derive per‑axis px/mm from the paint rect, ensuring precise mapping for both PDF and physical printers.

### Notes
- No functional changes to scale/datum overlays or printing logic, except visual removal of red page-edge lines as noted above.

### Changed
- **UI Layout**: Expanded preview panel from 30% to 40% width
- **Preview Height**: Doubled minimum height from 200px to 400px
- **Toolbar Icons**: Replaced text with professional standard icons
- **Export Dialog**: Enhanced with accurate page counts and format options
- **PDF Export**: Complete rewrite with professional quality output
- **Settings Dialog**: Added DPI selection and enhanced options

### Fixed
- **PDF Export Errors**: Fixed QPdfWriter API compatibility issues
- **Page Count Display**: Accurate counting including metadata pages
- **Image Scaling**: Fixed QPixmap.scaled() parameter errors
- **Memory Management**: Proper cleanup and error handling
- **File Format Detection**: Robust format detection and loading
- **Export Pipeline**: Complete export workflow with error recovery

### Security
- **Input Validation**: Comprehensive file format validation
- **Error Handling**: Safe error handling prevents crashes
- **Memory Safety**: Proper resource management and cleanup

## [0.1.0] - 2025-01-XX (Development)

### Added
- Initial project structure and framework
- Basic GUI components and dialogs
- Core document viewing functionality
- Foundation for scaling and export features
