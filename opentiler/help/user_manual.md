
# User Manual

This manual reflects the current UI and menu structure in OpenTiler 1.3.0.

## Main Concepts
- Document Viewer: shows the loaded image/PDF with zoom, rotate, and fit.
- Preview Panel: shows how pages/tiles will be produced.
- Scale Factor: defines the mapping between pixels and real-world units (mm or inches).
- Page Grid: the per-page tiling of the scaled document used to export/print.

## Menus

### File
- Open…: load a document (`PDF`, `PNG/JPG/TIFF`, `SVG`, `DXF`, `FCStd`).
- Open Recent: list of recently opened documents with Clear Recent.
- Save As…: convert the current document to another supported image format.
- Export Tiles…: export the tiled output to PDF or images.
- Print Preview…: open a preview of printed tiles using the current settings.
- Print Tiles…: print the tiles directly to a printer.
- Exit: close the application.

![File Menu](../docs/images/13-file-menu.png)

### Project
- Open Project…: open an OpenTiler project (`.otproj` / `.otprj`).
- Open Recent Projects: quick access to previous projects with Clear.
- Save Project: save current project state.
- Save Project As…: save under a new name.
- Close Project: close the current project.

### Tools
- Scaling Tool: define real-world scale using two points and a known distance.
- Measure Tool: measure distances within the document.
- Unit Converter: convert between mm, inches, and pixels.
- Scale Calculator: compute common scale ratios and factors.
- Printer Calibration…: calibrate safety insets (right/bottom) per orientation.

![Tools Menu](../docs/images/16-tools-menu.png)

### Settings
- Preferences…: set defaults such as page size, overlays (crop/gutter/scale bar), units, and other behaviors.

![Settings Dialog](../docs/images/18-settings-dialog.png)

### Help
- Help Contents: open this help system.
- About: version and credits.

## Typical Workflow
1) File → Open… choose your file (PDF or image preferred).
2) Tools → Scaling Tool: mark two points, enter real-world distance; confirm scale.
3) Check Preview Panel: confirm page size, tile counts, and layout.
4) Optional: Tools → Measure Tool to validate distances at your scale.
5) Export: File → Export Tiles… to PDF or images, or use Print Preview/Print.

## Viewer Controls
- Zoom In/Out: toolbar buttons or Ctrl + +/-.
- Fit to Window: toolbar button or Ctrl+0.
- Rotate Left/Right: toolbar buttons.
- Pan: middle-mouse drag (or scroll while holding a modifier, depending on platform).

## Notes
- Some formats (DXF, FreeCAD) require optional packages. See FAQ.
- Export requires a valid page grid (apply scaling first for best results).
