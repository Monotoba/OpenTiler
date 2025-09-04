"""
Main window for OpenTiler application.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QSplitter,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QIcon, QKeySequence, QAction, QPainter, QPixmap, QPageSize, QPageLayout, QPen, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PySide6.QtCore import QMarginsF
import os
import json
import zipfile
from pathlib import Path
import tempfile

from .viewer.viewer import DocumentViewer
from .viewer.preview_panel import PreviewPanel
from .dialogs.scaling_dialog import ScalingDialog
from .dialogs.unit_converter import UnitConverterDialog
from .dialogs.scale_calculator import ScaleCalculatorDialog
from .dialogs.settings_dialog import SettingsDialog
from .dialogs.export_dialog import ExportDialog
from .dialogs.save_as_dialog import SaveAsDialog
from .settings.config import Config
from .utils.helpers import (
    calculate_tile_grid,
    get_page_size_mm,
    mm_to_pixels,
    load_icon,
    compute_page_grid_with_gutters,
    summarize_page_grid,
    compute_page_size_pixels,
)
from .utils.overlays import draw_scale_bar
from .utils.app_logger import configure_from_config, get_logger


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.scaling_dialog = None
        self.settings_dialog = None
        self.export_dialog = None
        self.save_as_dialog = None
        # Project state
        self.current_project_path = None
        self._project_dirty = False
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        # Configure logging from current settings
        try:
            configure_from_config(self.config)
        except Exception:
            pass
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
        # Mark project dirty when user selects or drags points
        try:
            self.document_viewer.point_selected.connect(lambda *_: self._mark_project_dirty())
            self.document_viewer.points_updated.connect(lambda *_: self._mark_project_dirty())
        except Exception:
            pass

        # Create preview panel
        self.preview_panel = PreviewPanel()
        main_splitter.addWidget(self.preview_panel)

        # Set splitter proportions (viewer ~80%, preview ~20%) at startup
        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 1)

        # Set central layout
        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        central_widget.setLayout(layout)

        # Create menus and toolbars
        self.create_menus()
        self.create_toolbars()
        self.create_status_bar()

        # Optionally open last project on startup
        try:
            if self.config.get_open_last_project_on_startup():
                recent = self.config.get_recent_projects()
                if recent:
                    last = recent[0]
                    if os.path.exists(last):
                        self._open_project_path(last)
        except Exception:
            pass

        # Logger for main window
        self.log = get_logger('projects')

    def create_menus(self):
        """Create application menus in order: File, Project, Tools, Settings, Help."""
        menubar = self.menuBar()

        # File menu (first)
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

        # Project menu (second)
        project_menu = menubar.addMenu("&Project")

        proj_open_action = QAction("&Open Project...", self)
        proj_open_action.triggered.connect(self.open_project)
        project_menu.addAction(proj_open_action)

        # Recent Projects submenu
        self.recent_projects_menu = project_menu.addMenu("Open &Recent Projects")
        self.update_recent_projects_menu()

        project_menu.addSeparator()

        proj_save_action = QAction("&Save Project", self)
        proj_save_action.triggered.connect(self.save_project)
        project_menu.addAction(proj_save_action)

        proj_save_as_action = QAction("Save Project &As...", self)
        proj_save_as_action.triggered.connect(self.save_project_as)
        project_menu.addAction(proj_save_as_action)

        project_menu.addSeparator()

        proj_close_action = QAction("&Close Project", self)
        proj_close_action.triggered.connect(self.close_project)
        project_menu.addAction(proj_close_action)

        # Tools menu (third)
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

        # Settings menu (fourth)
        settings_menu = menubar.addMenu("&Settings")

        preferences_action = QAction("&Preferences...", self)
        preferences_action.setShortcut(QKeySequence("Ctrl+,"))
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)

        # Help menu (last)
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)


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

        # Overlays group: Gutters, Crop Marks, Registration Marks as submenu in toolbar
        toolbar.addSeparator()
        gutter_action = QAction("Gutters", self)
        gutter_action.setCheckable(True)
        gutter_action.setChecked(self.config.get_gutter_lines_display())
        gutter_action.setToolTip("Toggle gutter (printable area) outlines in preview")
        gutter_action.toggled.connect(self.toggle_gutter_display)

        crop_action = QAction("Crop Marks", self)
        crop_action.setCheckable(True)
        crop_action.setChecked(self.config.get_crop_marks_display())
        crop_action.setToolTip("Toggle crop marks at gutter intersections in preview")
        crop_action.toggled.connect(self.toggle_crop_marks_display)

        reg_action = QAction("Reg Marks", self)
        reg_action.setCheckable(True)
        reg_action.setChecked(self.config.get_reg_marks_display())
        reg_action.setToolTip("Toggle registration marks in preview (circles with crosshairs at printable corners)")
        reg_action.toggled.connect(self.toggle_reg_marks_display)

        overlays_menu = QMenu("Overlays", self)
        overlays_menu.addAction(gutter_action)
        overlays_menu.addAction(crop_action)
        overlays_menu.addAction(reg_action)
        # Scale bar toggle
        scale_bar_action = QAction("Scale Bar", self)
        scale_bar_action.setCheckable(True)
        scale_bar_action.setChecked(self.config.get_scale_bar_display())
        scale_bar_action.setToolTip("Toggle scale bar overlay in preview")
        scale_bar_action.toggled.connect(self.toggle_scale_bar_display)
        overlays_menu.addAction(scale_bar_action)
        overlays_menu_action = overlays_menu.menuAction()
        # Use an eye icon if present; fall back to an info-like icon
        overlays_menu_action.setIcon(load_icon("eye.png", fallback=style.StandardPixmap.SP_FileDialogInfoView))
        toolbar.addAction(overlays_menu_action)

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

    def toggle_scale_bar_display(self, checked: bool):
        """Quickly toggle scale bar visibility in preview."""
        try:
            self.config.set_scale_bar_display(bool(checked))
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
            self._mark_project_dirty()
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
        get_logger('printing').debug("print_tiles() called")

        # Prevent multiple simultaneous print operations
        if hasattr(self, '_printing_in_progress') and self._printing_in_progress:
            get_logger('printing').warning("Print already in progress; ignoring new request")
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

            get_logger('printing').info(f"Printing {len(self.document_viewer.page_grid)} tiles")

            # Create printer with modern API
            printer = QPrinter(QPrinter.HighResolution)

            # Set default page size and orientation using modern API
            cfg_page_name = self.config.get_default_page_size()
            page_size_id = self._qpagesize_from_name(cfg_page_name)
            page_size = QPageSize(page_size_id)
            orientation = self._determine_print_orientation()

            # Apply initial layout before showing dialog
            printer.setPageSize(page_size)
            printer.setPageLayout(QPageLayout(
                page_size,
                orientation,
                QMarginsF(0, 0, 0, 0),
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

            get_logger('printing').debug("Showing print dialog")
            if print_dialog.exec() == QPrintDialog.Accepted:
                get_logger('printing').debug("Print dialog accepted; starting print")
                # Decide first page orientation: metadata-first => Portrait; else tile orientation
                include_metadata = self.config.get_include_metadata_page()
                metadata_position = self.config.get_metadata_page_position()
                first_orientation = (QPageLayout.Portrait if (include_metadata and metadata_position == "first")
                                     else self._determine_print_orientation())
                printer.setPageSize(page_size)
                try:
                    printer.setPageOrientation(first_orientation)
                except Exception:
                    pass
                printer.setPageLayout(QPageLayout(
                    page_size,
                    first_orientation,
                    QMarginsF(0, 0, 0, 0),
                    QPageLayout.Millimeter
                ))
                # TEMP: Debug printable vs gutter mapping — print diagnostic page only
                try:
                    self._print_debug_layout_page(printer)
                finally:
                    pass
                # To restore normal printing, replace the call above with:
                # self._print_tiles_to_printer(printer)
            else:
                get_logger('printing').info("Print dialog cancelled")
                self._printing_in_progress = False
                return

        except Exception as e:
            get_logger('printing').error(f"Print setup failed: {str(e)}")
            QMessageBox.critical(self, "Print Error", f"Failed to setup printing: {str(e)}")
        finally:
            self._printing_in_progress = False
            get_logger('printing').debug("print_tiles() completed")

    def _print_debug_layout_page(self, printer):
        """TEMP: Print a single diagnostic page outlining printable area and gutter mapping.

        Draws:
        - Printable area (green outline)
        - Inner gutter-mapped area (blue outline/fill)
        - Labels with dimensions in mm and px, and derived px/mm per axis
        """
        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.critical(self, "Print Error", "Failed to start printing (debug page).")
            return

        try:
            layout = printer.pageLayout()
            pr_px = layout.paintRectPixels(printer.resolution())
            pr_mm = layout.paintRect(QPageLayout.Millimeter)
            full_mm = layout.fullRect(QPageLayout.Millimeter)

            # Derive px/mm per axis from printable area
            px_per_mm_x = pr_px.width() / pr_mm.width() if pr_mm.width() > 0 else 0
            px_per_mm_y = pr_px.height() / pr_mm.height() if pr_mm.height() > 0 else 0

            # Compute inner (gutter) rect in device pixels using configured gutter (mm)
            gutter_mm = self.config.get_gutter_size_mm()
            g_px_x = int(round(gutter_mm * px_per_mm_x))
            g_px_y = int(round(gutter_mm * px_per_mm_y))
            dest_inner = QRect(
                pr_px.x() + g_px_x,
                pr_px.y() + g_px_y,
                max(0, pr_px.width() - 2 * g_px_x),
                max(0, pr_px.height() - 2 * g_px_y),
            )

            # Clear background (within printable area only)
            painter.fillRect(pr_px, Qt.white)

            # Draw printable area outline
            painter.setPen(QPen(QColor(0, 160, 0), 2))
            painter.setOpacity(1.0)
            painter.drawRect(pr_px)

            # Draw inner gutter rectangle (blue) with slight transparency
            painter.setPen(QPen(QColor(0, 100, 255), 2))
            painter.setOpacity(0.25)
            painter.fillRect(dest_inner, QColor(0, 100, 255, 40))
            painter.setOpacity(1.0)
            painter.drawRect(dest_inner)

            # Center crosshair in printable area
            cx = pr_px.x() + pr_px.width() // 2
            cy = pr_px.y() + pr_px.height() // 2
            painter.setPen(QPen(QColor(120, 120, 120), 1, Qt.DashLine))
            painter.drawLine(pr_px.x(), cy, pr_px.x() + pr_px.width(), cy)
            painter.drawLine(cx, pr_px.y(), cx, pr_px.y() + pr_px.height())

            # Labels
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            font = painter.font(); font.setPointSize(10); painter.setFont(font)
            label_lines = [
                f"Full page (mm): {full_mm.width():.2f} x {full_mm.height():.2f}",
                f"Printable (mm): {pr_mm.width():.2f} x {pr_mm.height():.2f}",
                f"Printable (px): {pr_px.width()} x {pr_px.height()} @ {printer.resolution()} DPI",
                f"px/mm: {px_per_mm_x:.3f} (x), {px_per_mm_y:.3f} (y)",
                f"Gutter: {gutter_mm:.2f} mm -> {g_px_x} px (x), {g_px_y} px (y)",
                f"Inner rect (px): x={dest_inner.x()}, y={dest_inner.y()}, w={dest_inner.width()}, h={dest_inner.height()}",
            ]
            tx = pr_px.x() + 10
            ty = pr_px.y() + 20
            for line in label_lines:
                painter.drawText(tx, ty, line)
                ty += 16

        finally:
            painter.end()

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

            # Helper to (re)compute printable rect
            def printable_rect():
                pl = printer.pageLayout()
                return pl.paintRectPixels(printer.resolution())

            # Capture page size to reuse when switching orientation
            page_layout = printer.pageLayout()
            page_size = page_layout.pageSize()
            page_rect = printable_rect()
            print(f"DEBUG: Initial print page rect: {page_rect.width()}x{page_rect.height()}")

            # Check if metadata page should be included
            from .settings.config import config
            include_metadata = config.get_include_metadata_page()
            metadata_position = config.get_metadata_page_position()

            print(f"DEBUG: Include metadata page: {include_metadata}, Position: {metadata_position}")

            page_count = 0

            # Add metadata page at the beginning (portrait) if configured
            if include_metadata and metadata_position == "first":
                print("DEBUG: Printing metadata page first (portrait)")
                # Orientation for first page already set by caller
                page_rect = printable_rect()
                self._print_metadata_page(painter, printer, source_pixmap, page_grid, page_rect)
                page_count += 1
                # Prepare tile orientation to apply on next newPage in loop
                tile_orientation = self._determine_print_orientation()
                try:
                    printer.setPageLayout(QPageLayout(page_size, tile_orientation, QMarginsF(0, 0, 0, 0), QPageLayout.Millimeter))
                except Exception:
                    pass

            # Print each tile - align with exporter/preview logic
            for i, page in enumerate(page_grid):
                print(f"DEBUG: Printing tile {i+1}/{len(page_grid)}")

                if page_count > 0 or i > 0:
                    printer.newPage()  # Start new page for each tile (or after metadata page)
                    # Ensure tile orientation remains applied
                    tile_orientation = self._determine_print_orientation()
                    try:
                        printer.setPageLayout(QPageLayout(page_size, tile_orientation, QMarginsF(0, 0, 0, 0), QPageLayout.Millimeter))
                    except Exception:
                        pass
                    page_rect = printable_rect()

                # Create a full tile pixmap including gutters and clip to printable area
                tile_pixmap = self._create_tile_pixmap(source_pixmap, page)

                if tile_pixmap and not tile_pixmap.isNull():
                    print(f"DEBUG: Drawing tile to paint rect: {page_rect.width()}x{page_rect.height()}")
                    # Map the tile's drawable (inside gutters) to an inner rect on paper defined in mm
                    # Compute px/mm from the actual printable area to avoid driver-dependent offsets
                    gutter_mm = self.config.get_gutter_size_mm()
                    # Page physical size in mm from the current layout
                    current_layout = printer.pageLayout()
                    # Use the printable area in millimeters, not the full page size
                    pr_mm = current_layout.paintRect(QPageLayout.Millimeter)
                    pr_w_mm = pr_mm.width()
                    pr_h_mm = pr_mm.height()
                    # Derive px/mm based on the current printable rect dimensions
                    px_per_mm_x = page_rect.width() / pr_w_mm if pr_w_mm > 0 else 0
                    px_per_mm_y = page_rect.height() / pr_h_mm if pr_h_mm > 0 else 0
                    g_px_x = int(round(gutter_mm * px_per_mm_x))
                    g_px_y = int(round(gutter_mm * px_per_mm_y))

                    # Source (inner) rect from tile pixmap
                    g_tile = int(page.get('gutter', 0) or 0)
                    src_inner = QRect(g_tile, g_tile,
                                      max(0, tile_pixmap.width() - 2 * g_tile),
                                      max(0, tile_pixmap.height() - 2 * g_tile))

                    # Destination inner rect on paper (leave mm gutters on page)
                    dest_inner = QRect(page_rect.x() + g_px_x,
                                       page_rect.y() + g_px_y,
                                       max(0, page_rect.width() - 2 * g_px_x),
                                       max(0, page_rect.height() - 2 * g_px_y))

                    painter.drawPixmap(dest_inner, tile_pixmap, src_inner)

                    # Draw simple gutter rectangle overlay for visual guidance
                    if self.config.get_gutter_lines_print():
                        painter.save()
                        painter.setPen(QPen(Qt.blue, 1))
                        painter.drawRect(dest_inner)
                        painter.restore()

                    # Add page information
                    total_pages = len(page_grid) + (1 if include_metadata else 0)
                    current_page = i + 1 + (1 if include_metadata and metadata_position == "first" else 0)
                    self._add_print_page_info(painter, page_rect, current_page, total_pages)
                else:
                    print(f"ERROR: Failed to create tile pixmap for tile {i+1}")

                page_count += 1

            # Add metadata page at the end (portrait) if configured
            if include_metadata and metadata_position == "last":
                print("DEBUG: Printing metadata page last (portrait)")
                printer.newPage()
                try:
                    printer.setPageLayout(QPageLayout(page_size, QPageLayout.Portrait, QMarginsF(0, 0, 0, 0), QPageLayout.Millimeter))
                except Exception:
                    pass
                page_rect = printable_rect()
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
            get_logger('printing').error(f"Print failed: {str(e)}")
            import traceback
            traceback.print_exc()
            if painter and painter.isActive():
                painter.end()
            QMessageBox.critical(self, "Print Error", f"Failed to print tiles: {str(e)}")

    def _qpagesize_from_name(self, name: str):
        """Map config page size string to QPageSize.SizeId."""
        mapping = {
            'A0': QPageSize.A0,
            'A1': QPageSize.A1,
            'A2': QPageSize.A2,
            'A3': QPageSize.A3,
            'A4': QPageSize.A4,
            'Letter': QPageSize.Letter,
            'Legal': QPageSize.Legal,
            'Tabloid': QPageSize.Tabloid,
        }
        return mapping.get((name or 'A4').strip(), QPageSize.A4)

    def _print_metadata_page(self, painter, printer, source_pixmap, page_grid, page_rect):
        """Print a metadata summary page."""
        try:
            print("DEBUG: Generating metadata page for printing")

            # Import metadata page generator
            from .utils.metadata_page import MetadataPageGenerator, create_document_info

            # Create metadata page generator
            metadata_generator = MetadataPageGenerator()

            # Calculate grid dimensions
            summary = summarize_page_grid(page_grid or [])
            tiles_x = summary['tiles_x']
            tiles_y = summary['tiles_y']

            # Get document information
            document_info = self._get_document_info()

            # Add additional info for metadata page
            document_info['total_tiles'] = summary['total_tiles']
            document_info['tiles_x'] = tiles_x
            document_info['tiles_y'] = tiles_y
            document_info['export_format'] = 'Print'
            document_info['dpi'] = printer.resolution()

            # Add source pixmap and page grid for plan view
            document_info['source_pixmap'] = source_pixmap
            document_info['page_grid'] = page_grid

            print(f"DEBUG: Metadata info - tiles: {tiles_x}x{tiles_y}, total: {len(page_grid)}")

            # Generate metadata page sized exactly to the printable rect
            metadata_pixmap = metadata_generator.generate_metadata_page(document_info, page_rect.size())

            # Draw metadata page to print
            if metadata_pixmap and not metadata_pixmap.isNull():
                print(f"DEBUG: Generated metadata page {metadata_pixmap.width()}x{metadata_pixmap.height()}")
                print(f"DEBUG: Print page size: {page_rect.width()}x{page_rect.height()}")

                # Draw metadata at the printable rect origin (already sized)
                painter.drawPixmap(page_rect.x(), page_rect.y(), metadata_pixmap)
                print("DEBUG: Metadata page printed at printable area size")
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

            # Compute standardized tile layout (shared with preview path)
            from .utils.helpers import compute_tile_layout
            layout = compute_tile_layout(page, source_pixmap.width(), source_pixmap.height())
            tile_width = int(layout['tile_width'])
            tile_height = int(layout['tile_height'])
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
            gutter = int(layout['gutter'])
            if gutter > 0:
                painter.setClipRect(layout['printable_rect'])

            # Copy the area directly from source to tile
            src_rect = layout['source_rect']
            dx, dy = layout['dest_pos']

            print(f"DEBUG: Source rect: ({src_rect.x()}, {src_rect.y()}, {src_rect.width()}, {src_rect.height()})")
            print(f"DEBUG: Dest position: ({dx}, {dy})")

            if src_rect.width() > 0 and src_rect.height() > 0:
                source_crop = source_pixmap.copy(src_rect)
                if not source_crop.isNull():
                    print(f"DEBUG: Drawing source crop {source_crop.width()}x{source_crop.height()} at ({dx}, {dy})")
                    painter.drawPixmap(int(dx), int(dy), source_crop)
                else:
                    print("ERROR: Source crop is null")
            else:
                print(f"ERROR: Invalid source dimensions: {src_rect.width()}x{src_rect.height()}")

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

        # Scale bar overlay for print/export if enabled
        if config.get_scale_bar_print():
            try:
                gutter = int(page.get('gutter', 0) or 0)
                width = tile_size.width()
                height = tile_size.height()
                units = self.config.get_default_units()
                location = self.config.get_scale_bar_location()
                opacity = self.config.get_scale_bar_opacity()
                length_in = self.config.get_scale_bar_length_in()
                length_cm = self.config.get_scale_bar_length_cm()
                thickness_mm = self.config.get_scale_bar_thickness_mm()
                padding_mm = self.config.get_scale_bar_padding_mm()
                scale_factor = getattr(self.document_viewer, 'scale_factor', 1.0)
                draw_scale_bar(
                    painter,
                    width,
                    height,
                    gutter,
                    scale_factor,
                    units,
                    location,
                    length_in,
                    length_cm,
                    opacity,
                    thickness_mm,
                    padding_mm,
                )
            except Exception:
                pass

        # Print the scale line/text if enabled
        try:
            if config.get_scale_line_print():
                scale_info = self._get_scale_info()
                if scale_info:
                    point1 = scale_info.get('point1')
                    point2 = scale_info.get('point2')
                    measurement_text = scale_info.get('measurement_text', '')
                    if point1 and point2:
                        # Page boundaries in document coords
                        page_x = page['x']
                        page_y = page['y']
                        page_doc_w = page['width']
                        page_doc_h = page['height']

                        # Convert to tile pixmap coords
                        p1_x = (point1[0] - page_x) * (tile_size.width() / page_doc_w)
                        p1_y = (point1[1] - page_y) * (tile_size.height() / page_doc_h)
                        p2_x = (point2[0] - page_x) * (tile_size.width() / page_doc_w)
                        p2_y = (point2[1] - page_y) * (tile_size.height() / page_doc_h)

                        pen = QPen(QColor(255, 0, 0), 2)
                        pen.setStyle(Qt.CustomDashLine)
                        pen.setDashPattern([8, 3, 2, 3, 2, 3])
                        painter.setPen(pen)
                        painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

                        # Optional text
                        if config.get_scale_text_print() and measurement_text:
                            mid_x = (p1_x + p2_x) / 2
                            mid_y = (p1_y + p2_y) / 2
                            font = painter.font()
                            font.setPointSize(10)
                            font.setBold(True)
                            painter.setFont(font)
                            text_pen = QPen(QColor(255, 0, 0), 1)
                            painter.setPen(text_pen)
                            text_rect = painter.fontMetrics().boundingRect(measurement_text)
                            tx = mid_x - text_rect.width() / 2
                            ty = mid_y - 12
                            bg_rect = text_rect.adjusted(-3, -2, 3, 2)
                            bg_rect.moveTopLeft(QPoint(int(tx - 3), int(ty - text_rect.height() - 2)))
                            painter.fillRect(bg_rect, QColor(255, 255, 255, 200))
                            painter.drawText(int(tx), int(ty), measurement_text)
        except Exception:
            pass

        # Print the datum line if enabled
        try:
            if config.get_datum_line_print():
                scale_info = self._get_scale_info()
                if scale_info:
                    point1 = scale_info.get('point1')
                    point2 = scale_info.get('point2')
                    if point1 and point2:
                        page_x = page['x']
                        page_y = page['y']
                        page_doc_w = page['width']
                        page_doc_h = page['height']
                        p1_x = (point1[0] - page_x) * (tile_size.width() / page_doc_w)
                        p1_y = (point1[1] - page_y) * (tile_size.height() / page_doc_h)
                        p2_x = (point2[0] - page_x) * (tile_size.width() / page_doc_w)
                        p2_y = (point2[1] - page_y) * (tile_size.height() / page_doc_h)

                        datum_pen = QPen(QColor(config.get_datum_line_color()), max(1, config.get_datum_line_width_px()))
                        style = str(config.get_datum_line_style()).lower()
                        if style == 'solid':
                            datum_pen.setStyle(Qt.SolidLine)
                        elif style == 'dash':
                            datum_pen.setStyle(Qt.DashLine)
                        elif style == 'dot':
                            datum_pen.setStyle(Qt.DotLine)
                        elif style == 'dashdot':
                            datum_pen.setStyle(Qt.DashDotLine)
                        elif style == 'dashdotdot':
                            datum_pen.setStyle(Qt.DashDotDotLine)
                        elif style == 'dot-dash-dot':
                            datum_pen.setStyle(Qt.CustomDashLine)
                            datum_pen.setDashPattern([8, 3, 2, 3, 2, 3])
                        painter.setPen(datum_pen)
                        painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))
        except Exception:
            pass

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
            # Connect point dragging updates
            try:
                self.document_viewer.points_updated.connect(self.scaling_dialog.on_point_moved)
            except Exception:
                pass

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

        # Resolve page size in pixels using scale and orientation
        page_size = self.config.get_default_page_size()
        orientation = self.config.get_page_orientation()
        page_width_pixels, page_height_pixels = compute_page_size_pixels(
            scale_factor_mm_per_px=scale_factor,
            page_size_name=page_size,
            orientation=orientation,
        )

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
        page_grid = compute_page_grid_with_gutters(
            doc_width_px=doc_width,
            doc_height_px=doc_height,
            page_width_px=page_width_pixels,
            page_height_px=page_height_pixels,
            gutter_px=gutter_pixels,
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
        self._mark_project_dirty()

    def _calculate_page_grid_with_gutters(self, doc_width, doc_height, page_width, page_height, gutter_size):
        """Deprecated: use utils.helpers.compute_page_grid_with_gutters()."""
        return compute_page_grid_with_gutters(
            doc_width_px=doc_width,
            doc_height_px=doc_height,
            page_width_px=page_width,
            page_height_px=page_height,
            gutter_px=gutter_size,
        )

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
        current_file = getattr(self.document_viewer, 'current_document', '')
        if current_file:
            document_info['document_name'] = os.path.splitext(os.path.basename(current_file))[0]
            document_info['original_file'] = current_file
        else:
            document_info['document_name'] = 'Untitled Document'
            document_info['original_file'] = ''

        # Project name (if any)
        if getattr(self, 'current_project_path', None):
            document_info['project_name'] = os.path.splitext(os.path.basename(self.current_project_path))[0]
        else:
            document_info['project_name'] = ''

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
        self._mark_project_dirty()

    # ----------------------
    # Project management
    # ----------------------

    def _mark_project_dirty(self):
        self._project_dirty = True
        self._update_window_title()

    def _clear_project_dirty(self):
        self._project_dirty = False
        self._update_window_title()

    def _update_window_title(self):
        base = "OpenTiler"
        if self.current_project_path:
            name = os.path.basename(self.current_project_path)
            dirty = "*" if self._project_dirty else ""
            self.setWindowTitle(f"{base} - {name}{dirty}")
        else:
            self.setWindowTitle(base)

    def _confirm_save_if_dirty(self):
        if not self._project_dirty:
            return True
        reply = QMessageBox.question(
            self,
            "Save Project",
            "The project has unsaved changes. Save now?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            return self.save_project()
        if reply == QMessageBox.No:
            return True
        return False

    def _snapshot_config(self):
        c = self.config
        return {
            # General / page
            'default_units': c.get_default_units(),
            'default_dpi': c.get_default_dpi(),
            'default_page_size': c.get_default_page_size(),
            'page_orientation': c.get_page_orientation(),
            'gutter_size_mm': c.get_gutter_size_mm(),
            # Overlays
            'gutter_lines_display': c.get_gutter_lines_display(),
            'gutter_lines_print': c.get_gutter_lines_print(),
            'crop_marks_display': c.get_crop_marks_display(),
            'crop_marks_print': c.get_crop_marks_print(),
            'reg_marks_display': c.get_reg_marks_display(),
            'reg_marks_print': c.get_reg_marks_print(),
            'reg_mark_diameter_mm': c.get_reg_mark_diameter_mm(),
            'reg_mark_crosshair_mm': c.get_reg_mark_crosshair_mm(),
            # Scale bar
            'scale_bar_display': c.get_scale_bar_display(),
            'scale_bar_print': c.get_scale_bar_print(),
            'scale_bar_location': c.get_scale_bar_location(),
            'scale_bar_opacity': c.get_scale_bar_opacity(),
            'scale_bar_length_in': c.get_scale_bar_length_in(),
            'scale_bar_length_cm': c.get_scale_bar_length_cm(),
            'scale_bar_thickness_mm': c.get_scale_bar_thickness_mm(),
            'scale_bar_padding_mm': c.get_scale_bar_padding_mm(),
            # Page indicator
            'page_indicator_display': c.get_page_indicator_display(),
            'page_indicator_print': c.get_page_indicator_print(),
            'page_indicator_position': c.get_page_indicator_position(),
            'page_indicator_font_size': c.get_page_indicator_font_size(),
            'page_indicator_font_color': c.get_page_indicator_font_color(),
            'page_indicator_font_style': c.get_page_indicator_font_style(),
            'page_indicator_alpha': c.get_page_indicator_alpha(),
            # Scale line/text
            'scale_line_display': c.get_scale_line_display(),
            'scale_line_print': c.get_scale_line_print(),
            'scale_text_display': c.get_scale_text_display(),
            'scale_text_print': c.get_scale_text_print(),
            # Datum line
            'datum_line_display': c.get_datum_line_display(),
            'datum_line_print': c.get_datum_line_print(),
            'datum_line_color': c.get_datum_line_color(),
            'datum_line_style': c.get_datum_line_style(),
            'datum_line_width_px': c.get_datum_line_width_px(),
            # Metadata page
            'include_metadata_page': c.get_include_metadata_page(),
            'metadata_page_position': c.get_metadata_page_position(),
        }

    def _apply_config_snapshot(self, snap: dict):
        c = self.config
        try:
            # Apply with defaults if missing
            c.set_default_units(snap.get('default_units', c.get_default_units()))
            c.set_default_dpi(snap.get('default_dpi', c.get_default_dpi()))
            c.set_default_page_size(snap.get('default_page_size', c.get_default_page_size()))
            c.set_page_orientation(snap.get('page_orientation', c.get_page_orientation()))
            c.set_gutter_size_mm(snap.get('gutter_size_mm', c.get_gutter_size_mm()))

            c.set_gutter_lines_display(snap.get('gutter_lines_display', c.get_gutter_lines_display()))
            c.set_gutter_lines_print(snap.get('gutter_lines_print', c.get_gutter_lines_print()))
            c.set_crop_marks_display(snap.get('crop_marks_display', c.get_crop_marks_display()))
            c.set_crop_marks_print(snap.get('crop_marks_print', c.get_crop_marks_print()))
            c.set_reg_marks_display(snap.get('reg_marks_display', c.get_reg_marks_display()))
            c.set_reg_marks_print(snap.get('reg_marks_print', c.get_reg_marks_print()))
            c.set_reg_mark_diameter_mm(snap.get('reg_mark_diameter_mm', c.get_reg_mark_diameter_mm()))
            c.set_reg_mark_crosshair_mm(snap.get('reg_mark_crosshair_mm', c.get_reg_mark_crosshair_mm()))

            c.set_scale_bar_display(snap.get('scale_bar_display', c.get_scale_bar_display()))
            c.set_scale_bar_print(snap.get('scale_bar_print', c.get_scale_bar_print()))
            c.set_scale_bar_location(snap.get('scale_bar_location', c.get_scale_bar_location()))
            c.set_scale_bar_opacity(snap.get('scale_bar_opacity', c.get_scale_bar_opacity()))
            c.set_scale_bar_length_in(snap.get('scale_bar_length_in', c.get_scale_bar_length_in()))
            c.set_scale_bar_length_cm(snap.get('scale_bar_length_cm', c.get_scale_bar_length_cm()))
            c.set_scale_bar_thickness_mm(snap.get('scale_bar_thickness_mm', c.get_scale_bar_thickness_mm()))
            c.set_scale_bar_padding_mm(snap.get('scale_bar_padding_mm', c.get_scale_bar_padding_mm()))

            c.set_page_indicator_display(snap.get('page_indicator_display', c.get_page_indicator_display()))
            c.set_page_indicator_print(snap.get('page_indicator_print', c.get_page_indicator_print()))
            c.set_page_indicator_position(snap.get('page_indicator_position', c.get_page_indicator_position()))
            c.set_page_indicator_font_size(snap.get('page_indicator_font_size', c.get_page_indicator_font_size()))
            c.set_page_indicator_font_color(snap.get('page_indicator_font_color', c.get_page_indicator_font_color()))
            c.set_page_indicator_font_style(snap.get('page_indicator_font_style', c.get_page_indicator_font_style()))
            c.set_page_indicator_alpha(snap.get('page_indicator_alpha', c.get_page_indicator_alpha()))

            c.set_scale_line_display(snap.get('scale_line_display', c.get_scale_line_display()))
            c.set_scale_line_print(snap.get('scale_line_print', c.get_scale_line_print()))
            c.set_scale_text_display(snap.get('scale_text_display', c.get_scale_text_display()))
            c.set_scale_text_print(snap.get('scale_text_print', c.get_scale_text_print()))

            # Datum line
            c.set_datum_line_display(snap.get('datum_line_display', c.get_datum_line_display()))
            c.set_datum_line_print(snap.get('datum_line_print', c.get_datum_line_print()))
            c.set_datum_line_color(snap.get('datum_line_color', c.get_datum_line_color()))
            c.set_datum_line_style(snap.get('datum_line_style', c.get_datum_line_style()))
            c.set_datum_line_width_px(snap.get('datum_line_width_px', c.get_datum_line_width_px()))

            c.set_include_metadata_page(snap.get('include_metadata_page', c.get_include_metadata_page()))
            c.set_metadata_page_position(snap.get('metadata_page_position', c.get_metadata_page_position()))
        except Exception:
            pass

    def _gather_project_state(self):
        viewer = self.document_viewer
        state = {
            'version': 1,
            'document_path': getattr(viewer, 'current_document', '') or '',
            'document_name': os.path.basename(getattr(viewer, 'current_document', '') or '') or 'Untitled',
            'viewer': {
                'scale_factor': getattr(viewer, 'scale_factor', 1.0),
                'selected_points': getattr(viewer, 'selected_points', []),
                'measurement_text': getattr(viewer, 'measurement_text', ''),
                'rotation': getattr(viewer, 'rotation', 0),
                'zoom_factor': getattr(viewer, 'zoom_factor', 1.0),
            },
            'config': self._snapshot_config(),
        }
        return state

    def _apply_project_state(self, state: dict, original_path: str | None = None):
        # Apply config first
        self._apply_config_snapshot(state.get('config', {}))

        doc_path = original_path or state.get('document_path')
        if doc_path and os.path.exists(doc_path):
            self.load_document(doc_path)
        # Apply viewer state
        viewer = self.document_viewer
        vstate = state.get('viewer', {})
        viewer.set_scale(vstate.get('scale_factor', 1.0))
        pts = vstate.get('selected_points') or []
        viewer.selected_points = pts
        viewer.set_measurement_text(vstate.get('measurement_text', ''))
        viewer.rotation = vstate.get('rotation', 0)
        viewer.zoom_factor = vstate.get('zoom_factor', 1.0)

        # Regenerate tiling based on scale
        if viewer.scale_factor and viewer.current_pixmap:
            self.on_scale_applied(viewer.scale_factor)
        else:
            viewer.refresh_display()

    def save_project(self):
        """Save current project to existing path or prompt Save As."""
        if not self.current_project_path:
            return self.save_project_as()
        try:
            self._save_project_to_path(self.current_project_path)
            self._clear_project_dirty()
            self.status_bar.showMessage(f"Project saved: {self.current_project_path}")
            self.config.add_recent_project(self.current_project_path)
            self.update_recent_projects_menu()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Save Project", f"Failed to save project: {str(e)}")
            return False

    def save_project_as(self):
        """Prompt for a project file and save."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project As",
            self.config.get_last_output_dir(),
            "OpenTiler Project (*.otprj);;Legacy: JSON Project (*.otproj);;Legacy: Zipped Project (*.otprjz)"
        )
        if not path:
            return False
        # Ensure extension based on storage mode if user didn't specify
        if not (path.endswith('.otproj') or path.endswith('.otprjz') or path.endswith('.otprj')):
            # Default to modern single-asset project
            path += '.otprj'
        try:
            self._save_project_to_path(path)
            self.current_project_path = path
            self.config.set_last_output_dir(os.path.dirname(path))
            self._clear_project_dirty()
            self.status_bar.showMessage(f"Project saved: {path}")
            self.config.add_recent_project(path)
            self.update_recent_projects_menu()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Save Project", f"Failed to save project: {str(e)}")
            return False

    def _save_project_to_path(self, path: str):
        state = self._gather_project_state()
        # Decide embed by extension (modern .otprj and legacy .otprjz both zip+embed)
        if path.endswith('.otprjz') or path.endswith('.otprj'):
            # Embed original file if available
            original_path = state.get('document_path')
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('project.json', json.dumps(state, indent=2))
                if original_path and os.path.exists(original_path):
                    arcname = f"original/{os.path.basename(original_path)}"
                    zf.write(original_path, arcname)
        else:
            # Legacy: Plain JSON project
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            # Optional sidecar compressed original based on setting
            mode = self.config.get_project_original_storage()
            if mode == 'sidecar':
                self._write_sidecar_original(state.get('document_path'), path)

    def _write_sidecar_original(self, original_path: str | None, project_path: str):
        if not original_path or not os.path.exists(original_path):
            return
        base, _ = os.path.splitext(project_path)
        sidecar = base + '.dat'
        # Zip the single original file into the sidecar
        try:
            with zipfile.ZipFile(sidecar, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(original_path, os.path.basename(original_path))
        except Exception:
            pass

    def open_project(self):
        """Open an existing project file (.otproj or .otprjz)."""
        if not self._confirm_save_if_dirty():
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            self.config.get_last_input_dir(),
            "OpenTiler Project (*.otprj *.otprjz *.otproj)"
        )
        if not path:
            return
        self._open_project_path(path)

    def _open_project_path(self, path: str):
        """Open a project from a given path (no file dialog)."""
        try:
            if path.endswith('.otprjz') or path.endswith('.otprj'):
                with zipfile.ZipFile(path, 'r') as zf:
                    with zf.open('project.json') as jf:
                        state = json.loads(jf.read().decode('utf-8'))
                    # Extract original to cache folder next to project
                    original_members = [m for m in zf.namelist() if m.startswith('original/') and not m.endswith('/')]
                    extracted_path = None
                    if original_members:
                        cache_dir = os.path.join(os.path.dirname(path), '.opentiler_cache')
                        os.makedirs(cache_dir, exist_ok=True)
                        member = original_members[0]
                        out_path = os.path.join(cache_dir, os.path.basename(member))
                        with zf.open(member) as src, open(out_path, 'wb') as dst:
                            dst.write(src.read())
                        extracted_path = out_path
                # If no embedded original, attempt to use referenced path or relink
                if not extracted_path:
                    extracted_path = self._maybe_relink_original(state)
                # Set current project path before applying state so metadata sees it
                self.current_project_path = path
                self._apply_project_state(state, extracted_path)
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                # Try sidecar first
                base, _ = os.path.splitext(path)
                sidecar = base + '.dat'
                extracted_path = None
                if os.path.exists(sidecar):
                    try:
                        with zipfile.ZipFile(sidecar, 'r') as zf:
                            # Extract first file entry
                            members = [m for m in zf.namelist() if not m.endswith('/')]
                            if members:
                                cache_dir = os.path.join(os.path.dirname(path), '.opentiler_cache')
                                os.makedirs(cache_dir, exist_ok=True)
                                member = members[0]
                                out_path = os.path.join(cache_dir, os.path.basename(member))
                                with zf.open(member) as src, open(out_path, 'wb') as dst:
                                    dst.write(src.read())
                                extracted_path = out_path
                    except Exception:
                        extracted_path = None
                if not extracted_path:
                    extracted_path = self._maybe_relink_original(state)
                # Set current project path before applying state so metadata sees it
                self.current_project_path = path
                self._apply_project_state(state, extracted_path)
            self._clear_project_dirty()
            self.status_bar.showMessage(f"Project opened: {path}")
            # Add to recent projects
            self.config.add_recent_project(path)
            self.update_recent_projects_menu()
        except Exception as e:
            QMessageBox.critical(self, "Open Project", f"Failed to open project: {str(e)}")

    def _maybe_relink_original(self, state: dict):
        """If original file is missing, prompt user to relink. Returns chosen path or None."""
        orig = state.get('document_path')
        if orig and os.path.exists(orig):
            return orig
        # Prompt user to locate the original file
        reply = QMessageBox.question(
            self,
            "Missing Original",
            "The original document for this project is missing. Would you like to locate it?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            start_dir = os.path.dirname(orig) if orig else self.config.get_last_input_dir()
            file_path, _ = QFileDialog.getOpenFileName(self, "Locate Original Document", start_dir,
                "All Supported (*.pdf *.png *.jpg *.jpeg *.tiff *.svg *.dxf *.FCStd);;All Files (*)")
            if file_path:
                # Update state so further saves reference the new path
                state['document_path'] = file_path
                return file_path
        return None

    def close_project(self):
        """Close current project, prompting to save if dirty."""
        if not self._confirm_save_if_dirty():
            return
        # Clear viewer and preview
        self.document_viewer.current_pixmap = None
        self.document_viewer.current_document = None
        self.document_viewer.selected_points = []
        self.document_viewer.zoom_factor = 1.0
        self.document_viewer.rotation = 0
        self.document_viewer.page_grid = []
        self.document_viewer.gutter_size = 0
        self.document_viewer.refresh_display()
        self.preview_panel.update_preview(None, None)
        self.current_project_path = None
        self._clear_project_dirty()
        self.status_bar.showMessage("Project closed")

    def closeEvent(self, event):
        # Prompt to save project on app exit
        if self._confirm_save_if_dirty():
            event.accept()
        else:
            event.ignore()

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

    def update_recent_projects_menu(self):
        """Update the recent projects submenu under Project menu."""
        if not hasattr(self, 'recent_projects_menu') or self.recent_projects_menu is None:
            return
        self.recent_projects_menu.clear()

        recent_projects = self.config.get_recent_projects()
        if not recent_projects:
            no_proj_action = QAction("No recent projects", self)
            no_proj_action.setEnabled(False)
            self.recent_projects_menu.addAction(no_proj_action)
        else:
            for i, path in enumerate(recent_projects):
                name = os.path.basename(path)
                action_text = f"&{i+1} {name}"
                act = QAction(action_text, self)
                act.setToolTip(path)
                act.setData(path)
                act.triggered.connect(lambda checked, p=path: self._open_project_path(p))
                self.recent_projects_menu.addAction(act)
            self.recent_projects_menu.addSeparator()
            clear_action = QAction("&Clear Recent Projects", self)
            clear_action.triggered.connect(self.config.clear_recent_projects)
            # Also refresh menu after clearing
            clear_action.triggered.connect(self.update_recent_projects_menu)
            self.recent_projects_menu.addAction(clear_action)

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
