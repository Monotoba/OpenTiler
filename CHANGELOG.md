# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
