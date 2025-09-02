"""
Main window for OpenTiler application.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QToolBar, QStatusBar, QSplitter,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QIcon, QKeySequence, QAction, QPainter, QPixmap, QPageSize, QPageLayout, QPen, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PySide6.QtCore import QMarginsF
import os

from .viewer.viewer import DocumentViewer
from .viewer.preview_panel import PreviewPanel
from .dialogs.scaling_dialog import ScalingDialog
from .dialogs.unit_converter import UnitConverterDialog
from .dialogs.scale_calculator import ScaleCalculatorDialog
from .dialogs.settings_dialog import SettingsDialog
from .dialogs.export_dialog import ExportDialog
from .dialogs.save_as_dialog import SaveAsDialog
from .settings.config import Config
from .utils.helpers import calculate_tile_grid, get_page_size_mm, mm_to_pixels, load_icon


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.scaling_dialog = None
        self.settings_dialog = None
        self.export_dialog = None
        self.save_as_dialog = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("OpenTiler")
        self.setWindowIcon(load_icon("opentiler-icon.png", fallback=None))
        self.setMinimumSize(QSize(1024, 768))

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)

        # Create document viewer
        self.document_viewer = DocumentViewer()
        main_splitter.addWidget(self.document_viewer)

        # Create preview panel
        self.preview_panel = PreviewPanel()
        main_splitter.addWidget(self.preview_panel)

        # Set splitter proportions (viewer takes 60%, preview takes 40%)
        main_splitter.setSizes([600, 400])

        # Set central layout
        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        central_widget.setLayout(layout)

        # Create menus and toolbars
        self.create_menus()
        self.create_toolbars()
        self.create_status_bar()

    def create_menus(self):
        """Create application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Open Recent submenu
        self.recent_menu = file_menu.addMenu("Open &Recent")
        self.update_recent_files_menu()

        file_menu.addSeparator()

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_as_document)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction("&Export Tiles...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_document)
        file_menu.addAction(export_action)

        print_action = QAction("&Print Tiles...", self)
        print_action.setShortcut(QKeySequence("Ctrl+P"))
        print_action.triggered.connect(self.print_tiles)
        file_menu.addAction(print_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        scale_tool_action = QAction("&Scaling Tool", self)
        scale_tool_action.setShortcut(QKeySequence("Ctrl+S"))
        scale_tool_action.triggered.connect(self.show_scaling_dialog)
        tools_menu.addAction(scale_tool_action)

        unit_converter_action = QAction("&Unit Converter", self)
        unit_converter_action.setShortcut(QKeySequence("Ctrl+U"))
        unit_converter_action.triggered.connect(self.show_unit_converter)
        tools_menu.addAction(unit_converter_action)

        scale_calculator_action = QAction("Scale &Calculator", self)
        scale_calculator_action.setShortcut(QKeySequence("Ctrl+C"))
        scale_calculator_action.triggered.connect(self.show_scale_calculator)
        tools_menu.addAction(scale_calculator_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")

        preferences_action = QAction("&Preferences...", self)
        preferences_action.setShortcut(QKeySequence("Ctrl+,"))
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)


    def create_toolbars(self):
        """Create application toolbars."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))  # Set consistent icon size
        self.addToolBar(toolbar)

        # Get standard icon theme for fallback
        style = QApplication.style()

        # # Helper function to load custom icon with fallback
        # def load_icon(icon_name, fallback_standard_icon):
        #     icon_path = os.path.join(os.path.dirname(__file__), "assets", f"{icon_name}.png")
        #     if os.path.exists(icon_path):
        #         return QIcon(icon_path)
        #     else:
        #         return style.standardIcon(fallback_standard_icon)

        # NEW ORDER: Open, Export, Print, Rotate Left, Rotate Right, Fit to Window, Zoom In, Zoom Out, Settings, Scale tool

        # 1. Open file action
        open_action = QAction("Open", self)
        open_action.setIcon(style.standardIcon(style.StandardPixmap.SP_DialogOpenButton))  # Use system icon for Open
        open_action.setToolTip("Open document (Ctrl+O)")
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # 2. Export action
        export_action = QAction("Export", self)
        export_action.setIcon(load_icon("export.png", fallback=style.StandardPixmap.SP_DialogSaveButton))
        export_action.setToolTip("Export document as tiles (Ctrl+E)")
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_document)
        toolbar.addAction(export_action)

        # 3. Print action
        print_action = QAction("Print", self)
        print_action.setIcon(load_icon("printer.png", fallback=style.StandardPixmap.SP_FileDialogDetailedView))
        print_action.setToolTip("Print tiles directly (Ctrl+P)")
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_tiles)
        toolbar.addAction(print_action)

        toolbar.addSeparator()

        # 4. Rotate Left action
        rotate_left_action = QAction("Rotate Left", self)
        rotate_left_action.setIcon(load_icon("rotate-left.png", fallback=style.StandardPixmap.SP_BrowserReload))
        rotate_left_action.setToolTip("Rotate document 90° counterclockwise")
        rotate_left_action.triggered.connect(self.document_viewer.rotate_counterclockwise)
        toolbar.addAction(rotate_left_action)

        # 5. Rotate Right action
        rotate_right_action = QAction("Rotate Right", self)
        rotate_right_action.setIcon(load_icon("rotate-right.png", fallback=style.StandardPixmap.SP_BrowserReload))
        rotate_right_action.setToolTip("Rotate document 90° clockwise")
        rotate_right_action.triggered.connect(self.document_viewer.rotate_clockwise)
        toolbar.addAction(rotate_right_action)

        toolbar.addSeparator()

        # 6. Fit to Window action
        fit_action = QAction("Fit to Window", self)
        fit_action.setIcon(load_icon("fit-to-window.png", fallback=style.StandardPixmap.SP_ComputerIcon))
        fit_action.setToolTip("Fit document to window (Ctrl+0)")
        fit_action.setShortcut("Ctrl+0")
        fit_action.triggered.connect(self.document_viewer.zoom_fit)
        toolbar.addAction(fit_action)

        # 7. Zoom In action
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setIcon(load_icon("zoom-in.png", fallback=style.StandardPixmap.SP_FileDialogDetailedView))
        zoom_in_action.setToolTip("Zoom in (+)")
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.document_viewer.zoom_in)
        toolbar.addAction(zoom_in_action)

        # 8. Zoom Out action
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setIcon(load_icon("zoom-out.png", fallback=style.StandardPixmap.SP_FileDialogListView))
        zoom_out_action.setToolTip("Zoom out (-)")
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.document_viewer.zoom_out)
        toolbar.addAction(zoom_out_action)

        toolbar.addSeparator()

        # 9. Settings action (2nd from right end)
        settings_action = QAction("Settings", self)
        settings_action.setIcon(load_icon("settings.png", fallback=style.StandardPixmap.SP_FileDialogDetailedView))
        settings_action.setToolTip("Open application settings (Ctrl+,)")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)

        # 10. Scale tool action (rightmost - most used)
        scale_action = QAction("Scale Tool", self)
        scale_action.setIcon(load_icon("scale-tool.png", fallback=style.StandardPixmap.SP_FileDialogInfoView))
        scale_action.setToolTip("Open scaling tool to set real-world measurements (Ctrl+S)")
        scale_action.setShortcut("Ctrl+S")
        scale_action.triggered.connect(self.show_scaling_dialog)
        toolbar.addAction(scale_action)

        # Quick toggle: Gutter lines (preview only)
        toolbar.addSeparator()
        gutter_action = QAction("Gutters", self)
        gutter_action.setCheckable(True)
        gutter_action.setChecked(self.config.get_gutter_lines_display())
        gutter_action.setIcon(load_icon("gutters.png", fallback=style.StandardPixmap.SP_BrowserStop))
        gutter_action.setToolTip("Toggle gutter (printable area) outlines in preview")
        gutter_action.toggled.connect(self.toggle_gutter_display)
        toolbar.addAction(gutter_action)

        # Quick toggle: Crop marks (preview only)
        crop_action = QAction("Crop Marks", self)
        crop_action.setCheckable(True)
        crop_action.setChecked(self.config.get_crop_marks_display())
        crop_action.setIcon(load_icon("crop-marks.png", fallback=style.StandardPixmap.SP_DialogResetButton))
        crop_action.setToolTip("Toggle crop marks at gutter intersections in preview")
        crop_action.toggled.connect(self.toggle_crop_marks_display)
        toolbar.addAction(crop_action)

        # Quick toggle: Registration marks (preview only)
        toolbar.addSeparator()
        reg_action = QAction("Reg Marks", self)
        reg_action.setCheckable(True)
        reg_action.setChecked(self.config.get_reg_marks_display())
        reg_action.setIcon(load_icon("reg-marks.png", fallback=style.StandardPixmap.SP_DialogYesButton))
        reg_action.setToolTip("Toggle registration marks in preview (circles with crosshairs at printable corners)")
        reg_action.toggled.connect(self.toggle_reg_marks_display)
        toolbar.addAction(reg_action)

    def toggle_reg_marks_display(self, checked: bool):
        """Quickly toggle registration marks visibility in preview."""
        try:
            self.config.set_reg_marks_display(bool(checked))
            # Refresh overlays and thumbnails to reflect the change
            self.on_settings_changed()
        except Exception:
            pass

    def toggle_gutter_display(self, checked: bool):
        """Quickly toggle gutter outline visibility in preview."""
        try:
            self.config.set_gutter_lines_display(bool(checked))
            self.on_settings_changed()
        except Exception:
            pass

    def toggle_crop_marks_display(self, checked: bool):
        """Quickly toggle crop marks visibility in preview."""
        try:
            self.config.set_crop_marks_display(bool(checked))
            self.on_settings_changed()
        except Exception:
            pass

    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def open_file(self):
        """Open a document file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            self.config.get_last_input_dir(),
            "All Supported (*.pdf *.png *.jpg *.jpeg *.tiff *.svg *.dxf *.FCStd);;PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg *.tiff);;SVG Files (*.svg);;DXF Files (*.dxf);;FreeCAD Files (*.FCStd)"
        )

        if file_path:
            self.load_document(file_path)

    def load_document(self, file_path):
        """Load a document from the given file path."""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", f"File not found: {file_path}")
            # Remove from recent files if it doesn't exist
            self.config.remove_recent_file(file_path)
            self.update_recent_files_menu()
            return False

        # Update last input directory
        self.config.set_last_input_dir(os.path.dirname(file_path))

        # Load the document
        if self.document_viewer.load_document(file_path):
            self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")

            # Update title bar with filename
            self.update_title_bar(file_path)

            # Add to recent files
            self.config.add_recent_file(file_path)
            self.update_recent_files_menu()
            return True
        else:
            QMessageBox.warning(self, "Error", f"Failed to load document: {file_path}")
            return False

    def update_title_bar(self, file_path=None):
        """Update the title bar with the current filename."""
        if file_path:
            filename = os.path.basename(file_path)
            self.setWindowTitle(f"OpenTiler - {filename}")
        else:
            # Check if we have a current document
            current_file = getattr(self.document_viewer, 'current_document', None)
            if current_file:
                filename = os.path.basename(current_file)
                self.setWindowTitle(f"OpenTiler - {filename}")
            else:
                self.setWindowTitle("OpenTiler")

    def export_document(self):
        """Export the current document as tiles."""
        # Check if we have a document and page grid
        if not self.document_viewer.current_pixmap:
            QMessageBox.warning(self, "Export", "No document loaded. Please load a document first.")
            return

        if not hasattr(self.document_viewer, 'page_grid') or not self.document_viewer.page_grid:
            QMessageBox.warning(self, "Export", "No tiles generated. Please apply scaling first to generate tiles.")
            return

        # Create and show export dialog
        if not self.export_dialog:
            self.export_dialog = ExportDialog(self)

        # Prepare document information for metadata page
        document_info = self._get_document_info()

        # Set export data
        self.export_dialog.set_export_data(
            self.document_viewer.current_pixmap,
            self.document_viewer.page_grid,
            document_info
        )

        # Show dialog
        self.export_dialog.show()

    def save_as_document(self):
        """Save the current document in a different CAD format."""
        # Check if we have a document
        if not self.document_viewer.current_pixmap:
            QMessageBox.warning(self, "Save As", "No document loaded. Please load a document first.")
            return

        # Create and show save-as dialog
        if not self.save_as_dialog:
            self.save_as_dialog = SaveAsDialog(self)

        # Get current scale factor
        scale_factor = getattr(self.document_viewer, 'scale_factor', 1.0)

        # Set document data
        self.save_as_dialog.set_document_data(
            self.document_viewer.current_pixmap,
            scale_factor
        )

        # Show dialog
        self.save_as_dialog.show()

    def print_tiles(self):
        """Print the current document tiles directly to printer."""
        print("DEBUG: print_tiles() called")

        # Prevent multiple simultaneous print operations
        if hasattr(self, '_printing_in_progress') and self._printing_in_progress:
            print("DEBUG: Print already in progress, ignoring")
            return

        # Set the flag immediately to prevent multiple calls
        self._printing_in_progress = True

        try:

            # Check if we have a document and page grid
            if not self.document_viewer.current_pixmap:
                QMessageBox.warning(self, "Print", "No document loaded. Please load a document first.")
                self._printing_in_progress = False
                return

            if not hasattr(self.document_viewer, 'page_grid') or not self.document_viewer.page_grid:
                QMessageBox.warning(self, "Print", "No tiles generated. Please apply scaling first to generate tiles.")
                self._printing_in_progress = False
                return

            print(f"DEBUG: Found {len(self.document_viewer.page_grid)} tiles to print")

            # Create printer with modern API
            printer = QPrinter(QPrinter.HighResolution)

            # Set default page size and orientation using modern API
            page_size = QPageSize(QPageSize.A4)
            orientation = self._determine_print_orientation()

            printer.setPageSize(page_size)
            # Use millimeter units so margins match configured gutter scale
            printer.setPageLayout(QPageLayout(
                page_size,
                orientation,
                QMarginsF(10, 10, 10, 10),
                QPageLayout.Millimeter
            ))

            # Show print dialog
            print_dialog = QPrintDialog(printer, self)
            print_dialog.setWindowTitle("Print Tiles")

            # Enable print options
            print_dialog.setOptions(
                QPrintDialog.PrintToFile |
                QPrintDialog.PrintSelection |
                QPrintDialog.PrintPageRange |
                QPrintDialog.PrintCurrentPage
            )

            print("DEBUG: Showing print dialog")
            if print_dialog.exec() == QPrintDialog.Accepted:
                print("DEBUG: Print dialog accepted, starting print")
                self._print_tiles_to_printer(printer)
            else:
                print("DEBUG: Print dialog cancelled")
                self._printing_in_progress = False
                return

        except Exception as e:
            print(f"ERROR: Print setup failed: {str(e)}")
            QMessageBox.critical(self, "Print Error", f"Failed to setup printing: {str(e)}")
        finally:
            self._printing_in_progress = False
            print("DEBUG: print_tiles() completed")

    def _print_tiles_to_printer(self, printer):
        """Print tiles to the specified printer."""
        print("DEBUG: _print_tiles_to_printer() called")
        painter = None
        try:
            # Get page grid and source pixmap
            page_grid = self.document_viewer.page_grid
            source_pixmap = self.document_viewer.current_pixmap

            print(f"DEBUG: Printing {len(page_grid)} tiles")
            print(f"DEBUG: Source pixmap size: {source_pixmap.width()}x{source_pixmap.height()}")

            # Create painter for printing
            painter = QPainter()
            if not painter.begin(printer):
                print("ERROR: Failed to start painter")
                QMessageBox.critical(self, "Print Error", "Failed to start printing.")
                return

            print("DEBUG: Painter started successfully")

            # Get printer page size and layout
            page_layout = printer.pageLayout()
            page_rect = page_layout.paintRectPixels(printer.resolution())

            print(f"DEBUG: Print page rect: {page_rect.width()}x{page_rect.height()}")

            # Check if metadata page should be included
            from .settings.config import config
            include_metadata = config.get_include_metadata_page()
            metadata_position = config.get_metadata_page_position()

            print(f"DEBUG: Include metadata page: {include_metadata}, Position: {metadata_position}")

            page_count = 0

            # Add metadata page at the beginning if configured
            if include_metadata and metadata_position == "first":
                print("DEBUG: Printing metadata page first")
                self._print_metadata_page(painter, printer, source_pixmap, page_grid, page_rect)
                page_count += 1

            # Print each tile - align with exporter/preview logic
            for i, page in enumerate(page_grid):
                print(f"DEBUG: Printing tile {i+1}/{len(page_grid)}")

                if page_count > 0 or i > 0:
                    printer.newPage()  # Start new page for each tile (or after metadata page)

                # Create a full tile pixmap including gutters and clip to printable area
                tile_pixmap = self._create_tile_pixmap(source_pixmap, page)

                if tile_pixmap and not tile_pixmap.isNull():
                    print(f"DEBUG: Drawing tile to paint rect: {page_rect.width()}x{page_rect.height()}")
                    # Draw the tile scaled to the printable rect so physical size matches
                    painter.drawPixmap(page_rect, tile_pixmap, tile_pixmap.rect())

                    # Add page information
                    total_pages = len(page_grid) + (1 if include_metadata else 0)
                    current_page = i + 1 + (1 if include_metadata and metadata_position == "first" else 0)
                    self._add_print_page_info(painter, page_rect, current_page, total_pages)
                else:
                    print(f"ERROR: Failed to create tile pixmap for tile {i+1}")

                page_count += 1

            # Add metadata page at the end if configured
            if include_metadata and metadata_position == "last":
                print("DEBUG: Printing metadata page last")
                printer.newPage()
                self._print_metadata_page(painter, printer, source_pixmap, page_grid, page_rect)
                page_count += 1

            painter.end()
            print("DEBUG: Printing completed successfully")

            # Show success message
            total_printed = len(page_grid) + (1 if include_metadata else 0)
            if include_metadata:
                QMessageBox.information(
                    self,
                    "Print Complete",
                    f"Successfully printed {total_printed} pages ({len(page_grid)} tiles + 1 metadata page)."
                )
            else:
                QMessageBox.information(
                    self,
                    "Print Complete",
                    f"Successfully printed {len(page_grid)} tiles."
                )

        except Exception as e:
            print(f"ERROR: Print failed: {str(e)}")
            import traceback
            traceback.print_exc()
            if painter and painter.isActive():
                painter.end()
            QMessageBox.critical(self, "Print Error", f"Failed to print tiles: {str(e)}")

    def _print_metadata_page(self, painter, printer, source_pixmap, page_grid, page_rect):
        """Print a metadata summary page."""
        try:
            print("DEBUG: Generating metadata page for printing")

            # Import metadata page generator
            from .utils.metadata_page import MetadataPageGenerator, create_document_info

            # Create metadata page generator
            metadata_generator = MetadataPageGenerator()

            # Calculate grid dimensions
            if page_grid:
                tiles_x = len(set(page['x'] for page in page_grid))
                tiles_y = len(set(page['y'] for page in page_grid))
            else:
                tiles_x = tiles_y = 0

            # Get document information
            document_info = self._get_document_info()

            # Add additional info for metadata page
            document_info['total_tiles'] = len(page_grid)
            document_info['tiles_x'] = tiles_x
            document_info['tiles_y'] = tiles_y
            document_info['export_format'] = 'Print'
            document_info['dpi'] = printer.resolution()

            # Add source pixmap and page grid for plan view
            document_info['source_pixmap'] = source_pixmap
            document_info['page_grid'] = page_grid

            print(f"DEBUG: Metadata info - tiles: {tiles_x}x{tiles_y}, total: {len(page_grid)}")

            # Generate metadata page at a reasonable size (A4 at 300 DPI)
            # This ensures the metadata page has enough detail to scale up properly
            metadata_size = QSize(2480, 3508)  # A4 at 300 DPI
            metadata_pixmap = metadata_generator.generate_metadata_page(document_info, metadata_size)

            # Draw metadata page to print
            if metadata_pixmap and not metadata_pixmap.isNull():
                print(f"DEBUG: Generated metadata page {metadata_pixmap.width()}x{metadata_pixmap.height()}")
                print(f"DEBUG: Print page size: {page_rect.width()}x{page_rect.height()}")

                # Scale metadata page to fill the entire print page
                # Use IgnoreAspectRatio to fill the page completely
                scaled_metadata = metadata_pixmap.scaled(
                    page_rect.size(),
                    Qt.IgnoreAspectRatio,  # Fill entire page
                    Qt.SmoothTransformation
                )

                print(f"DEBUG: Scaled metadata page to {scaled_metadata.width()}x{scaled_metadata.height()}")

                # Draw at full page size (no centering needed)
                painter.drawPixmap(0, 0, scaled_metadata)
                print("DEBUG: Metadata page printed successfully at full page size")
            else:
                print("ERROR: Failed to generate metadata page pixmap")

        except Exception as e:
            print(f"ERROR: Failed to print metadata page: {str(e)}")
            import traceback
            traceback.print_exc()

    def _create_tile_pixmap(self, source_pixmap, page):
        """Create a pixmap for a single tile."""
        painter = None
        try:
            print(f"DEBUG: Creating tile for page: x={page['x']}, y={page['y']}, w={page['width']}, h={page['height']}")
            print(f"DEBUG: Source pixmap size: {source_pixmap.width()}x{source_pixmap.height()}")

            # Create tile pixmap with the page dimensions
            tile_width = int(page['width'])
            tile_height = int(page['height'])
            tile_pixmap = QPixmap(tile_width, tile_height)
            tile_pixmap.fill(Qt.white)  # Fill with white background

            print(f"DEBUG: Created tile pixmap: {tile_width}x{tile_height}")

            # Paint the source area onto the tile
            painter = QPainter(tile_pixmap)

            # Check if painter is valid
            if not painter.isActive():
                print("ERROR: Painter is not active")
                return QPixmap()

            # Set clipping region to printable area (inside gutters)
            gutter = int(page.get('gutter', 0) or 0)
            if gutter > 0:
                printable_rect = QRect(
                    gutter, gutter,
                    max(0, tile_width - 2 * gutter),
                    max(0, tile_height - 2 * gutter)
                )
                painter.setClipRect(printable_rect)

            # Copy the area directly from source to tile
            # Calculate what part of the source we need to copy
            source_x = max(0, int(page['x']))
            source_y = max(0, int(page['y']))
            source_w = min(source_pixmap.width() - source_x, tile_width)
            source_h = min(source_pixmap.height() - source_y, tile_height)

            # Calculate where to place it on the tile
            dest_x = max(0, -int(page['x']))
            dest_y = max(0, -int(page['y']))

            print(f"DEBUG: Source rect: ({source_x}, {source_y}, {source_w}, {source_h})")
            print(f"DEBUG: Dest position: ({dest_x}, {dest_y})")

            if source_w > 0 and source_h > 0:
                # Copy the source area
                source_rect = QRect(source_x, source_y, source_w, source_h)
                source_crop = source_pixmap.copy(source_rect)

                if not source_crop.isNull():
                    print(f"DEBUG: Drawing source crop {source_crop.width()}x{source_crop.height()} at ({dest_x}, {dest_y})")
                    painter.drawPixmap(dest_x, dest_y, source_crop)
                else:
                    print("ERROR: Source crop is null")
            else:
                print(f"ERROR: Invalid source dimensions: {source_w}x{source_h}")

            # Add gutter lines and page indicators if enabled
            self._add_tile_overlays(painter, tile_pixmap.size(), page)

            painter.end()
            print(f"DEBUG: Tile creation completed successfully")
            return tile_pixmap

        except Exception as e:
            print(f"ERROR creating tile pixmap: {str(e)}")
            import traceback
            traceback.print_exc()
            # Ensure painter is properly ended even on error
            if painter and painter.isActive():
                painter.end()
            return QPixmap()

    def _add_print_page_info(self, painter, page_rect, page_num, total_pages):
        """Add page information to printed tile."""
        from .settings.config import config

        if not config.get_page_indicator_print():
            return

        # Save painter state
        painter.save()

        # Set font and color for page info
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(Qt.black)

        # Add page number in corner
        page_text = f"Page {page_num} of {total_pages}"
        text_rect = painter.fontMetrics().boundingRect(page_text)

        # Position in top-right corner with margin
        margin = 20
        x = page_rect.width() - text_rect.width() - margin
        y = margin + text_rect.height()

        painter.drawText(x, y, page_text)

        # Restore painter state
        painter.restore()

    def _add_tile_overlays(self, painter, tile_size, page):
        """Add gutter lines and indicators to tile."""
        from .settings.config import config

        # Save painter state
        painter.save()

        # Draw gutter lines if enabled
        if config.get_crop_marks_display():
            gutter = page.get('gutter', 0)
            if gutter > 0:
                painter.setPen(Qt.blue)
                painter.setOpacity(0.5)

                # Draw gutter rectangle (drawable area)
                gutter_rect = QRect(
                    int(gutter), int(gutter),
                    int(tile_size.width() - 2 * gutter),
                    int(tile_size.height() - 2 * gutter)
                )
                painter.drawRect(gutter_rect)

        # Registration marks for print/export if enabled
        if config.get_reg_marks_print():
            gutter = int(page.get('gutter', 0) or 0)
            if gutter > 0:
                width = tile_size.width()
                height = tile_size.height()
                # Convert mm to px using document scale (mm/px)
                scale_factor = getattr(self.document_viewer, 'scale_factor', 1.0)
                px_per_mm = (1.0 / scale_factor) if scale_factor and scale_factor > 0 else 2.0
                diameter_mm = config.get_reg_mark_diameter_mm()
                cross_mm = config.get_reg_mark_crosshair_mm()
                radius_px = int((diameter_mm * px_per_mm) / 2)
                cross_len_px = int(cross_mm * px_per_mm)

                # Clip to printable area so only quarters render
                printable_rect = QRect(
                    gutter, gutter,
                    max(0, width - 2 * gutter),
                    max(0, height - 2 * gutter)
                )
                painter.save()
                painter.setClipRect(printable_rect)
                painter.setOpacity(1.0)
                painter.setPen(QPen(Qt.black, 1))

                centers = [
                    (gutter, gutter),
                    (width - gutter, gutter),
                    (gutter, height - gutter),
                    (width - gutter, height - gutter),
                ]
                for cx, cy in centers:
                    painter.drawEllipse(cx - radius_px, cy - radius_px, radius_px * 2, radius_px * 2)
                    painter.drawLine(cx - cross_len_px, cy, cx + cross_len_px, cy)
                    painter.drawLine(cx, cy - cross_len_px, cx, cy + cross_len_px)
                painter.restore()

        # Restore painter state
        painter.restore()

    def show_scaling_dialog(self):
        """Show the scaling dialog."""
        if not self.scaling_dialog:
            self.scaling_dialog = ScalingDialog(self)
            # Connect scaling dialog signals
            self.scaling_dialog.scale_applied.connect(self.document_viewer.set_scale)
            self.scaling_dialog.scale_applied.connect(self.on_scale_applied)
            # Connect point selection from viewer to dialog
            self.document_viewer.point_selected.connect(self.scaling_dialog.on_point_selected)

        # Enable point selection mode in the document viewer
        self.document_viewer.set_point_selection_mode(True)
        self.scaling_dialog.show()

    def on_scale_applied(self, scale_factor):
        """Handle when scale is applied - generate tiles and update preview."""
        if not self.document_viewer.current_pixmap:
            return

        # Get document dimensions in pixels
        pixmap = self.document_viewer.current_pixmap
        doc_width = pixmap.width()
        doc_height = pixmap.height()

        # Get page size from config (default A4)
        page_size = self.config.get_default_page_size()
        page_width_mm, page_height_mm = get_page_size_mm(page_size)

        # Apply orientation preference
        orientation = self.config.get_page_orientation()
        if orientation == "landscape":
            # Force landscape (width > height)
            if page_width_mm < page_height_mm:
                page_width_mm, page_height_mm = page_height_mm, page_width_mm
        elif orientation == "portrait":
            # Force portrait (height > width)
            if page_height_mm < page_width_mm:
                page_width_mm, page_height_mm = page_height_mm, page_width_mm
        # "auto" uses the default page size as-is

        # Convert page size to pixels using document scale
        # scale_factor is mm/pixel, so to get pixels from mm: pixels = mm / scale_factor
        page_width_pixels = page_width_mm / scale_factor if scale_factor > 0 else page_width_mm
        page_height_pixels = page_height_mm / scale_factor if scale_factor > 0 else page_height_mm

        # Safety check: prevent too many tiles
        if page_width_pixels < 50 or page_height_pixels < 50:
            self.status_bar.showMessage(f"Warning: Scale too large - pages would be {page_width_pixels:.0f}x{page_height_pixels:.0f} pixels")
            return

        max_tiles = 100  # Reasonable limit
        estimated_tiles = (doc_width / page_width_pixels) * (doc_height / page_height_pixels)
        if estimated_tiles > max_tiles:
            self.status_bar.showMessage(f"Warning: Scale would generate {estimated_tiles:.0f} tiles (limit: {max_tiles})")
            return

        # Calculate tile grid with gutter support
        gutter_mm = self.config.get_gutter_size_mm()
        gutter_pixels = gutter_mm / scale_factor

        # Generate page grid (pages can overlap where gutters meet)
        page_grid = self._calculate_page_grid_with_gutters(
            doc_width, doc_height,
            page_width_pixels, page_height_pixels,
            gutter_pixels
        )

        # Get scale info for preview
        scale_info = self._get_scale_info()

        # Get document info for metadata page preview
        document_info = self._get_document_info()

        # Update preview panel and document viewer
        self.preview_panel.update_preview(pixmap, page_grid, scale_factor, scale_info, document_info)
        self.document_viewer.set_page_grid(page_grid, gutter_pixels)

        # Update status
        self.status_bar.showMessage(f"Scale applied: {scale_factor:.6f} - {len(page_grid)} pages generated")

    def _calculate_page_grid_with_gutters(self, doc_width, doc_height, page_width, page_height, gutter_size):
        """Calculate page grid where drawable areas tile seamlessly with no gaps."""
        pages = []

        # Calculate step size based on drawable area (printable area inside gutters)
        # This ensures all document content falls within a drawable area
        drawable_width = page_width - (2 * gutter_size)
        drawable_height = page_height - (2 * gutter_size)

        # Ensure drawable dimensions are positive to prevent infinite loops
        if drawable_width <= 0 or drawable_height <= 0:
            print(f"WARNING: Drawable area is non-positive. page_width={page_width}, page_height={page_height}, gutter_size={gutter_size}")
            return [] # Return empty list if drawable area is invalid

        # Step size equals drawable area size for seamless tiling
        step_x = drawable_width
        step_y = drawable_height

        # Start pages offset by negative gutter so drawable areas start at (0,0)
        y = -gutter_size
        row = 0
        while y < doc_height:
            x = -gutter_size
            col = 0
            while x < doc_width:
                # Pages maintain full dimensions even if they extend beyond document
                # This ensures consistent page sizes for printing
                pages.append({
                    'x': x, 'y': y,
                    'width': page_width, 'height': page_height,
                    'row': row, 'col': col,
                    'gutter': gutter_size
                })

                x += step_x
                # Continue until drawable area covers document width
                if x + gutter_size >= doc_width:
                    break
                col += 1

            y += step_y
            # Continue until drawable area covers document height
            if y + gutter_size >= doc_height:
                break
            row += 1

        return pages

    def _determine_print_orientation(self):
        """Determine optimal print orientation based on tile content and user preferences."""
        # Get user preference from settings
        orientation_pref = self.config.get_page_orientation()

        if orientation_pref == "landscape":
            return QPageLayout.Landscape
        elif orientation_pref == "portrait":
            return QPageLayout.Portrait
        elif orientation_pref == "auto":
            # Auto-determine based on tile content
            if not hasattr(self.document_viewer, 'page_grid') or not self.document_viewer.page_grid:
                return QPageLayout.Portrait  # Default

            page_grid = self.document_viewer.page_grid

            # Calculate average tile aspect ratio
            total_aspect_ratio = 0
            valid_tiles = 0

            for page in page_grid:
                width = page.get('width', 0)
                height = page.get('height', 0)
                if width > 0 and height > 0:
                    aspect_ratio = width / height
                    total_aspect_ratio += aspect_ratio
                    valid_tiles += 1

            if valid_tiles > 0:
                avg_aspect_ratio = total_aspect_ratio / valid_tiles

                # If tiles are wider than they are tall, prefer landscape
                if avg_aspect_ratio > 1.2:  # 20% wider than square
                    return QPageLayout.Landscape
                else:
                    return QPageLayout.Portrait
            else:
                return QPageLayout.Portrait  # Default if no valid tiles
        else:
            return QPageLayout.Portrait  # Default fallback

    def _get_scale_info(self):
        """Get scale information from the document viewer for preview display."""
        if not hasattr(self.document_viewer, 'selected_points') or not self.document_viewer.selected_points:
            return None

        if len(self.document_viewer.selected_points) < 2:
            return None

        return {
            'point1': self.document_viewer.selected_points[0],
            'point2': self.document_viewer.selected_points[1],
            'measurement_text': getattr(self.document_viewer, 'measurement_text', '')
        }

    def _get_document_info(self):
        """Get document information for metadata page."""
        document_info = {}

        # Get current document file path
        current_file = getattr(self.document_viewer, 'current_file_path', '')
        if current_file:
            document_info['document_name'] = os.path.splitext(os.path.basename(current_file))[0]
            document_info['original_file'] = current_file
        else:
            document_info['document_name'] = 'Untitled Document'
            document_info['original_file'] = ''

        # Get scale information
        scale_factor = getattr(self.document_viewer, 'scale_factor', 1.0)
        document_info['scale_factor'] = scale_factor

        # Get units from config
        document_info['units'] = self.config.get_default_units()

        # Get page settings
        document_info['page_size'] = self.config.get_default_page_size()
        document_info['page_orientation'] = self.config.get_page_orientation()
        document_info['gutter_size'] = self.config.get_gutter_size_mm()

        # Get output directory from config
        document_info['output_dir'] = self.config.get_last_output_dir()

        return document_info

    def show_unit_converter(self):
        """Show the unit converter dialog."""
        dialog = UnitConverterDialog(self)
        dialog.exec()

    def show_scale_calculator(self):
        """Show the scale calculator dialog."""
        dialog = ScaleCalculatorDialog(self)
        dialog.exec()

    def show_settings(self):
        """Show the settings dialog."""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self)
            # Connect settings changed signal to refresh display
            self.settings_dialog.settings_changed.connect(self.on_settings_changed)

        self.settings_dialog.show()

    def on_settings_changed(self):
        """Handle when settings are changed - refresh display and regenerate tiles if needed."""
        # Refresh the document viewer display to apply new settings
        self.document_viewer.refresh_display()

        # If we have a scale applied, regenerate the page grid with new settings
        if (hasattr(self.document_viewer, 'scale_factor') and
            self.document_viewer.scale_factor != 1.0 and
            self.document_viewer.current_pixmap):

            # Regenerate page grid with current scale and new settings
            self.on_scale_applied(self.document_viewer.scale_factor)

        self.status_bar.showMessage("Settings updated")

    def update_recent_files_menu(self):
        """Update the recent files menu."""
        self.recent_menu.clear()

        recent_files = self.config.get_recent_files()

        if not recent_files:
            # Add disabled "No recent files" action
            no_files_action = QAction("No recent files", self)
            no_files_action.setEnabled(False)
            self.recent_menu.addAction(no_files_action)
        else:
            # Add recent files
            for i, file_path in enumerate(recent_files):
                # Create action with filename and path
                filename = os.path.basename(file_path)
                action_text = f"&{i+1} {filename}"

                action = QAction(action_text, self)
                action.setToolTip(file_path)  # Show full path in tooltip
                action.setData(file_path)  # Store full path in action data
                action.triggered.connect(lambda checked, path=file_path: self.load_document(path))
                self.recent_menu.addAction(action)

                # Add keyboard shortcut for first 9 files
                if i < 9:
                    action.setShortcut(QKeySequence(f"Ctrl+{i+1}"))

            # Add separator and clear action
            self.recent_menu.addSeparator()

            clear_action = QAction("&Clear Recent Files", self)
            clear_action.triggered.connect(self.clear_recent_files)
            self.recent_menu.addAction(clear_action)

    def clear_recent_files(self):
        """Clear all recent files."""
        self.config.clear_recent_files()
        self.update_recent_files_menu()
        self.status_bar.showMessage("Recent files cleared")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About OpenTiler",
            "OpenTiler v0.1.0\n\n"
            "A PySide6-based desktop application for scaling and tiling architectural drawings.\n\n"
            "Author: Randall Morgan\n"
            "License: MIT License with Attribution Requirement\n"
            "Copyright: © 2025 Randall Morgan"
        )
