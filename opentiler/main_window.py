"""
Main window for OpenTiler application.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QToolBar, QStatusBar, QSplitter,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QKeySequence, QAction

from .viewer.viewer import DocumentViewer
from .viewer.preview_panel import PreviewPanel
from .dialogs.scaling_dialog import ScalingDialog
from .dialogs.unit_converter import UnitConverterDialog
from .dialogs.scale_calculator import ScaleCalculatorDialog
from .settings.config import Config
from .utils.helpers import calculate_tile_grid, get_page_size_mm, mm_to_pixels


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.scaling_dialog = None
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

        # Set splitter proportions (viewer takes 70%, preview takes 30%)
        main_splitter.setSizes([700, 300])

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

        file_menu.addSeparator()

        export_action = QAction("&Export...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_document)
        file_menu.addAction(export_action)

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

    def create_toolbars(self):
        """Create application toolbars."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Open file action
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # Zoom actions
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.document_viewer.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.document_viewer.zoom_out)
        toolbar.addAction(zoom_out_action)

        zoom_fit_action = QAction("Fit to Window", self)
        zoom_fit_action.triggered.connect(self.document_viewer.zoom_fit)
        toolbar.addAction(zoom_fit_action)

        toolbar.addSeparator()

        # Scaling tool action
        scale_action = QAction("Scale Tool", self)
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
            "",
            "All Supported (*.pdf *.png *.jpg *.jpeg *.tiff *.svg);;PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg *.tiff);;SVG Files (*.svg)"
        )

        if file_path:
            self.document_viewer.load_document(file_path)
            self.status_bar.showMessage(f"Loaded: {file_path}")

    def export_document(self):
        """Export the current document."""
        # TODO: Implement export functionality
        QMessageBox.information(self, "Export", "Export functionality will be implemented soon.")

    def show_scaling_dialog(self):
        """Show the scaling dialog."""
        if not self.scaling_dialog:
            self.scaling_dialog = ScalingDialog(self)
            # Connect scaling dialog signals
            self.scaling_dialog.scale_applied.connect(self.document_viewer.set_scale)
            self.scaling_dialog.scale_applied.connect(self.on_scale_applied)

        # Enable point selection mode in the document viewer
        self.document_viewer.set_point_selection_mode(True)
        self.scaling_dialog.show()

        # Connect point selection from viewer to dialog
        self.document_viewer.point_selected.connect(self.scaling_dialog.on_point_selected)

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

        # Update preview panel and document viewer
        self.preview_panel.update_preview(pixmap, page_grid, scale_factor)
        self.document_viewer.set_page_grid(page_grid, gutter_pixels)

        # Update status
        self.status_bar.showMessage(f"Scale applied: {scale_factor:.6f} - {len(page_grid)} pages generated")

    def _calculate_page_grid_with_gutters(self, doc_width, doc_height, page_width, page_height, gutter_size):
        """Calculate page grid where gutters meet on single lines."""
        pages = []

        # Calculate step size (printable area)
        step_x = page_width - (2 * gutter_size)  # Pages overlap by 2*gutter
        step_y = page_height - (2 * gutter_size)

        y = 0
        row = 0
        while y < doc_height:
            x = 0
            col = 0
            while x < doc_width:
                # Calculate actual page dimensions
                actual_width = min(page_width, doc_width - x)
                actual_height = min(page_height, doc_height - y)

                pages.append({
                    'x': x, 'y': y,
                    'width': actual_width, 'height': actual_height,
                    'row': row, 'col': col,
                    'gutter': gutter_size
                })

                x += step_x
                if x >= doc_width:
                    break
                col += 1

            y += step_y
            if y >= doc_height:
                break
            row += 1

        return pages

    def show_unit_converter(self):
        """Show the unit converter dialog."""
        dialog = UnitConverterDialog(self)
        dialog.exec()

    def show_scale_calculator(self):
        """Show the scale calculator dialog."""
        dialog = ScaleCalculatorDialog(self)
        dialog.exec()

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
