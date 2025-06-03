"""
Main window for OpenTiler application.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QToolBar, QStatusBar, QSplitter,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QIcon, QKeySequence, QAction, QPainter, QPixmap, QPageSize, QPageLayout
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
from .utils.helpers import calculate_tile_grid, get_page_size_mm, mm_to_pixels


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

        # Helper function to load custom icon with fallback
        def load_icon(icon_name, fallback_standard_icon):
            icon_path = os.path.join(os.path.dirname(__file__), "assets", f"{icon_name}.png")
            if os.path.exists(icon_path):
                return QIcon(icon_path)
            else:
                return style.standardIcon(fallback_standard_icon)

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
        export_action.setIcon(load_icon("export", style.StandardPixmap.SP_DialogSaveButton))
        export_action.setToolTip("Export document as tiles (Ctrl+E)")
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_document)
        toolbar.addAction(export_action)

        # 3. Print action
        print_action = QAction("Print", self)
        print_action.setIcon(load_icon("printer", style.StandardPixmap.SP_FileDialogDetailedView))
        print_action.setToolTip("Print tiles directly (Ctrl+P)")
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_tiles)
        toolbar.addAction(print_action)

        toolbar.addSeparator()

        # 4. Rotate Left action
        rotate_left_action = QAction("Rotate Left", self)
        rotate_left_action.setIcon(load_icon("rotate-left", style.StandardPixmap.SP_BrowserReload))
        rotate_left_action.setToolTip("Rotate document 90° counterclockwise")
        rotate_left_action.triggered.connect(self.document_viewer.rotate_counterclockwise)
        toolbar.addAction(rotate_left_action)

        # 5. Rotate Right action
        rotate_right_action = QAction("Rotate Right", self)
        rotate_right_action.setIcon(load_icon("rotate-right", style.StandardPixmap.SP_BrowserReload))
        rotate_right_action.setToolTip("Rotate document 90° clockwise")
        rotate_right_action.triggered.connect(self.document_viewer.rotate_clockwise)
        toolbar.addAction(rotate_right_action)

        toolbar.addSeparator()

        # 6. Fit to Window action
        fit_action = QAction("Fit to Window", self)
        fit_action.setIcon(load_icon("fit-to-window", style.StandardPixmap.SP_ComputerIcon))
        fit_action.setToolTip("Fit document to window (Ctrl+0)")
        fit_action.setShortcut("Ctrl+0")
        fit_action.triggered.connect(self.document_viewer.zoom_fit)
        toolbar.addAction(fit_action)

        # 7. Zoom In action
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setIcon(load_icon("zoom-in", style.StandardPixmap.SP_FileDialogDetailedView))
        zoom_in_action.setToolTip("Zoom in (+)")
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.document_viewer.zoom_in)
        toolbar.addAction(zoom_in_action)

        # 8. Zoom Out action
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setIcon(load_icon("zoom-out", style.StandardPixmap.SP_FileDialogListView))
        zoom_out_action.setToolTip("Zoom out (-)")
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.document_viewer.zoom_out)
        toolbar.addAction(zoom_out_action)

        toolbar.addSeparator()

        # 9. Settings action (2nd from right end)
        settings_action = QAction("Settings", self)
        settings_action.setIcon(load_icon("settings", style.StandardPixmap.SP_FileDialogDetailedView))
        settings_action.setToolTip("Open application settings (Ctrl+,)")
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)

        # 10. Scale tool action (rightmost - most used)
        scale_action = QAction("Scale Tool", self)
        scale_action.setIcon(load_icon("scale-tool", style.StandardPixmap.SP_FileDialogInfoView))
        scale_action.setToolTip("Open scaling tool to set real-world measurements (Ctrl+S)")
        scale_action.setShortcut("Ctrl+S")
        scale_action.triggered.connect(self.show_scaling_dialog)
        toolbar.addAction(scale_action)

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

            # Add to recent files
            self.config.add_recent_file(file_path)
            self.update_recent_files_menu()
            return True
        else:
            QMessageBox.warning(self, "Error", f"Failed to load document: {file_path}")
            return False

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
        # Check if we have a document and page grid
        if not self.document_viewer.current_pixmap:
            QMessageBox.warning(self, "Print", "No document loaded. Please load a document first.")
            return

        if not hasattr(self.document_viewer, 'page_grid') or not self.document_viewer.page_grid:
            QMessageBox.warning(self, "Print", "No tiles generated. Please apply scaling first to generate tiles.")
            return

        # Create printer with modern API
        printer = QPrinter(QPrinter.HighResolution)

        # Set default page size and orientation using modern API
        page_size = QPageSize(QPageSize.A4)
        orientation = self._determine_print_orientation()

        printer.setPageSize(page_size)
        printer.setPageLayout(QPageLayout(
            page_size,
            orientation,
            QMarginsF(10, 10, 10, 10)  # 10mm margins
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

        if print_dialog.exec() == QPrintDialog.Accepted:
            self._print_tiles_to_printer(printer)

    def _print_tiles_to_printer(self, printer):
        """Print tiles to the specified printer."""
        try:
            # Get page grid and source pixmap
            page_grid = self.document_viewer.page_grid
            source_pixmap = self.document_viewer.current_pixmap

            # Create painter for printing
            painter = QPainter()
            if not painter.begin(printer):
                QMessageBox.critical(self, "Print Error", "Failed to start printing.")
                return

            # Get printer page size and layout
            page_layout = printer.pageLayout()
            page_rect = page_layout.paintRectPixels(printer.resolution())

            # Print each tile
            for i, page in enumerate(page_grid):
                if i > 0:
                    printer.newPage()  # Start new page for each tile

                # Create tile pixmap
                tile_pixmap = self._create_tile_pixmap(source_pixmap, page)

                if tile_pixmap and not tile_pixmap.isNull():
                    # Determine if this tile should be rotated for better fit
                    tile_aspect = tile_pixmap.width() / tile_pixmap.height()
                    page_aspect = page_rect.width() / page_rect.height()

                    # Check if rotating the tile would provide a better fit
                    should_rotate = False
                    if page_layout.orientation() == QPageLayout.Portrait and tile_aspect > 1.5:
                        # Wide tile on portrait page - consider rotating
                        should_rotate = True
                    elif page_layout.orientation() == QPageLayout.Landscape and tile_aspect < 0.7:
                        # Tall tile on landscape page - consider rotating
                        should_rotate = True

                    # Apply rotation if beneficial
                    if should_rotate:
                        transform = tile_pixmap.transform()
                        transform = transform.rotate(90)
                        tile_pixmap = tile_pixmap.transformed(transform)

                    # Scale tile to fit printer page while maintaining aspect ratio
                    scaled_tile = tile_pixmap.scaled(
                        page_rect.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )

                    # Center the tile on the page
                    x = (page_rect.width() - scaled_tile.width()) // 2
                    y = (page_rect.height() - scaled_tile.height()) // 2

                    # Draw the tile
                    painter.drawPixmap(x, y, scaled_tile)

                    # Add page information (optional)
                    self._add_print_page_info(painter, page_rect, i + 1, len(page_grid))

            painter.end()

            # Show success message
            QMessageBox.information(
                self,
                "Print Complete",
                f"Successfully printed {len(page_grid)} tiles."
            )

        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print tiles: {str(e)}")

    def _create_tile_pixmap(self, source_pixmap, page):
        """Create a pixmap for a single tile."""
        painter = None
        try:
            # Extract the tile area from source pixmap
            tile_rect = QRect(
                int(page['x']),
                int(page['y']),
                int(page['width']),
                int(page['height'])
            )

            # Create tile pixmap
            tile_pixmap = QPixmap(tile_rect.size())
            tile_pixmap.fill(Qt.white)  # Fill with white background

            # Paint the source area onto the tile
            painter = QPainter(tile_pixmap)

            # Check if painter is valid
            if not painter.isActive():
                print("Error: Painter is not active")
                return QPixmap()

            # Calculate source rectangle (clamp to source pixmap bounds)
            source_rect = QRect(
                max(0, int(page['x'])),
                max(0, int(page['y'])),
                min(int(page['width']), source_pixmap.width() - max(0, int(page['x']))),
                min(int(page['height']), source_pixmap.height() - max(0, int(page['y'])))
            )

            # Only draw if source rectangle is valid
            if not source_rect.isEmpty() and source_rect.isValid():
                # Calculate destination position (offset if page extends beyond source)
                dest_x = max(0, -int(page['x']))
                dest_y = max(0, -int(page['y']))

                # Draw the source area using correct signature
                # Use the copy method to extract the source rectangle first
                source_crop = source_pixmap.copy(source_rect)
                if not source_crop.isNull():
                    painter.drawPixmap(dest_x, dest_y, source_crop)

            # Add gutter lines and page indicators if enabled
            self._add_tile_overlays(painter, tile_pixmap.size(), page)

            painter.end()
            return tile_pixmap

        except Exception as e:
            print(f"Error creating tile pixmap: {str(e)}")
            # Ensure painter is properly ended even on error
            if painter and painter.isActive():
                painter.end()
            return QPixmap()

    def _add_print_page_info(self, painter, page_rect, page_num, total_pages):
        """Add page information to printed tile."""
        from .settings.config import config

        if not config.get_show_page_indicators():
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
        if config.get_show_crop_marks():
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
