"""
Main window for OpenTiler application.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QSplitter,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QRect, QRectF, QPoint
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
from .dialogs.printer_calibration import PrinterCalibrationDialog
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

        calib_action = QAction("&Printer Calibration...", self)
        calib_action.triggered.connect(self.show_printer_calibration)
        tools_menu.addAction(calib_action)

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
                # Do not override user-selected page size/orientation after dialog
                include_metadata = self.config.get_include_metadata_page()
                metadata_position = self.config.get_metadata_page_position()
                # Proceed with normal printing (tiles + metadata) using calibrated mapping
                self._print_tiles_to_printer(printer)
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
            pr_px_reported = layout.paintRectPixels(printer.resolution())
            pr_mm_reported = layout.paintRect(QPageLayout.Millimeter)
            full_mm = layout.fullRect(QPageLayout.Millimeter)

            # Derive px/mm from reported printable
            px_per_mm_x = pr_px_reported.width() / pr_mm_reported.width() if pr_mm_reported.width() > 0 else 0
            px_per_mm_y = pr_px_reported.height() / pr_mm_reported.height() if pr_mm_reported.height() > 0 else 0

            # Apply calibration to define effective printable RECT IN DEVICE COORDS (no viewport trickery)
            ori = layout.orientation()
            ori_name = "landscape" if ori == QPageLayout.Landscape else "portrait"
            h_mm, v_mm = self.config.get_print_calibration(ori_name)
            calib_px_x = int(round(h_mm * px_per_mm_x))
            calib_px_y = int(round(v_mm * px_per_mm_y))
            eff_rect = QRect(
                pr_px_reported.x(),
                pr_px_reported.y(),
                max(1, pr_px_reported.width() - calib_px_x),
                max(1, pr_px_reported.height() - calib_px_y),
            )
            pr_mm = QRectF(
                0.0,
                0.0,
                max(0.0, pr_mm_reported.width() - h_mm),
                max(0.0, pr_mm_reported.height() - v_mm),
            )

            # Compute inner (gutter) rect in device pixels using configured gutter (mm)
            gutter_mm = self.config.get_gutter_size_mm()
            g_px_x = int(round(gutter_mm * px_per_mm_x))
            g_px_y = int(round(gutter_mm * px_per_mm_y))
            dest_inner = QRect(
                eff_rect.x() + g_px_x,
                eff_rect.y() + g_px_y,
                max(0, eff_rect.width() - 2 * g_px_x),
                max(0, eff_rect.height() - 2 * g_px_y),
            )

            # Clear background within effective printable area
            painter.fillRect(eff_rect, Qt.white)
            painter.setRenderHint(QPainter.Antialiasing, False)

            # Draw effective printable area outline using filled 1px bars inset from edges
            painter.setOpacity(1.0)
            w, h = eff_rect.width(), eff_rect.height()
            if w > 2 and h > 2:
                # Left
                painter.fillRect(QRect(eff_rect.left(), eff_rect.top(), 1, h - 1), QColor(0, 160, 0))
                # Top
                painter.fillRect(QRect(eff_rect.left(), eff_rect.top(), w - 1, 1), QColor(0, 160, 0))
                # Right (inset by 1px)
                painter.fillRect(QRect(eff_rect.left() + w - 2, eff_rect.top(), 1, h - 1), QColor(0, 160, 0))
                # Bottom (inset by 1px)
                painter.fillRect(QRect(eff_rect.left(), eff_rect.top() + h - 2, w - 1, 1), QColor(0, 160, 0))

            # Draw inner gutter rectangle (blue) with slight transparency and inset 1px borders
            painter.setOpacity(0.25)
            painter.fillRect(dest_inner, QColor(0, 100, 255, 40))
            painter.setOpacity(1.0)
            iw = dest_inner.width(); ih = dest_inner.height()
            ix = dest_inner.x(); iy = dest_inner.y()
            if iw > 2 and ih > 2:
                # Left
                painter.fillRect(QRect(ix, iy, 1, ih - 1), QColor(0, 100, 255))
                # Top
                painter.fillRect(QRect(ix, iy, iw - 1, 1), QColor(0, 100, 255))
                # Right (inset by 1px)
                painter.fillRect(QRect(ix + iw - 2, iy, 1, ih - 1), QColor(0, 100, 255))
                # Bottom (inset by 1px)
                painter.fillRect(QRect(ix, iy + ih - 2, iw - 1, 1), QColor(0, 100, 255))

            # Additional reference box: 10 mm (1 cm) inside the inner gutter rectangle
            inset_x = int(round(10.0 * px_per_mm_x))
            inset_y = int(round(10.0 * px_per_mm_y))
            ref_x = ix + inset_x
            ref_y = iy + inset_y
            ref_w = max(0, iw - 2 * inset_x)
            ref_h = max(0, ih - 2 * inset_y)
            if ref_w > 2 and ref_h > 2:
                # Draw 1px black borders (filled bars) fully inside
                painter.setOpacity(1.0)
                # Left
                painter.fillRect(QRect(ref_x, ref_y, 1, ref_h - 1), Qt.black)
                # Top
                painter.fillRect(QRect(ref_x, ref_y, ref_w - 1, 1), Qt.black)
                # Right (inset)
                painter.fillRect(QRect(ref_x + ref_w - 2, ref_y, 1, ref_h - 1), Qt.black)
                # Bottom (inset)
                painter.fillRect(QRect(ref_x, ref_y + ref_h - 2, ref_w - 1, 1), Qt.black)

            # Center crosshair in printable area
            cx = eff_rect.left() + eff_rect.width() // 2
            cy = eff_rect.top() + eff_rect.height() // 2
            painter.setPen(QPen(QColor(120, 120, 120), 1, Qt.DashLine))
            painter.drawLine(eff_rect.left(), cy, eff_rect.left() + eff_rect.width(), cy)
            painter.drawLine(cx, eff_rect.top(), cx, eff_rect.top() + eff_rect.height())

            # Add a 10 cm scale bar along the bottom of the EFFECTIVE printable area
            try:
                from .utils.overlays import draw_scale_bar
                from .settings.config import config
                mm_per_px = 1.0 / px_per_mm_x if px_per_mm_x > 0 else (1.0 / (printer.resolution() / 25.4))
                painter.save()
                painter.translate(eff_rect.left(), eff_rect.top())
                draw_scale_bar(
                    painter,
                    eff_rect.width(),
                    eff_rect.height(),
                    0,              # no gutter
                    mm_per_px,
                    'mm',
                    'Page-S',
                    0.0,
                    10.0,
                    int(config.get_scale_bar_opacity()),
                    float(config.get_scale_bar_thickness_mm()),
                    float(config.get_scale_bar_padding_mm()),
                )
                painter.restore()
            except Exception:
                pass

            # Labels
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            font = painter.font(); font.setPointSize(10); painter.setFont(font)
            fm = painter.fontMetrics()
            label_lines = [
                f"Full page (mm): {full_mm.width():.2f} x {full_mm.height():.2f}",
                f"Printable (mm): {pr_mm.width():.2f} x {pr_mm.height():.2f}",
                f"Printable (px): {pr_px.width()} x {pr_px.height()} @ {printer.resolution()} DPI",
                f"px/mm: {px_per_mm_x:.3f} (x), {px_per_mm_y:.3f} (y)",
                f"Gutter: {gutter_mm:.2f} mm -> {g_px_x} px (x), {g_px_y} px (y)",
                f"Inner rect (px): x={dest_inner.x()}, y={dest_inner.y()}, w={dest_inner.width()}, h={dest_inner.height()}",
            ]
            tx = 10
            ty = fm.ascent() + 6
            for line in label_lines:
                painter.drawText(tx, ty, line)
                ty += fm.height() + 2

        finally:
            painter.end()

    def print_debug_page(self):
        """Show a print dialog and print a single debug layout page only."""
        printer = QPrinter(QPrinter.HighResolution)
        # Use current orientation preference
        try:
            ori = self._determine_print_orientation()
            pl = QPageLayout(self._qpagesize_from_name(self.config.get_default_page_size()), ori, QMarginsF(0, 0, 0, 0), QPageLayout.Millimeter)
            printer.setPageLayout(pl)
        except Exception:
            pass

        dlg = QPrintDialog(printer, self)
        dlg.setWindowTitle("Print Debug Page")
        if dlg.exec() != QPrintDialog.Accepted:
            return
        self._print_debug_layout_page(printer)

    def _print_tiles_to_printer(self, printer):
        """Print tiles to the specified printer."""
        print("DEBUG: _print_tiles_to_printer() called")
        painter = None
        try:
            # Get source pixmap
            source_pixmap = self.document_viewer.current_pixmap

            # Build a calibration-aware page grid based on the ACTUAL printer page size/orientation
            # to ensure printed coverage exactly matches the stepping (no overlaps or gaps).
            try:
                pl = printer.pageLayout()
                pr_mm = pl.paintRect(QPageLayout.Millimeter)
                # Resolve page size in document pixels from printer PRINTABLE mm and document scale
                scale_factor = getattr(self.document_viewer, 'scale_factor', 1.0) or 1.0
                page_width_px = float(pr_mm.width()) / float(scale_factor)
                page_height_px = float(pr_mm.height()) / float(scale_factor)
                gutter_mm = self.config.get_gutter_size_mm()
                gutter_px = float(gutter_mm) / float(scale_factor)
                # Calibration reduce steps in document px for this printer orientation
                ori_name = 'landscape' if pl.orientation() == QPageLayout.Landscape else 'portrait'
                h_mm, v_mm = self.config.get_print_calibration(ori_name)
                calib_step_x_px = max(0.0, float(h_mm) / float(scale_factor))
                calib_step_y_px = max(0.0, float(v_mm) / float(scale_factor))

                # Document dimensions in pixels
                doc_width = source_pixmap.width()
                doc_height = source_pixmap.height()

                from .utils.helpers import compute_page_grid_with_gutters
                page_grid = compute_page_grid_with_gutters(
                    doc_width_px=doc_width,
                    doc_height_px=doc_height,
                    page_width_px=page_width_px,
                    page_height_px=page_height_px,
                    gutter_px=gutter_px,
                    calib_reduce_step_x_px=calib_step_x_px,
                    calib_reduce_step_y_px=calib_step_y_px,
                )
            except Exception:
                # Fallback to existing grid if recompute fails
                page_grid = getattr(self.document_viewer, 'page_grid', [])

            print(f"DEBUG: Printing {len(page_grid)} tiles")
            print(f"DEBUG: Source pixmap size: {source_pixmap.width()}x{source_pixmap.height()}")

            # Create painter for printing
            painter = QPainter()
            if not painter.begin(printer):
                print("ERROR: Failed to start painter")
                QMessageBox.critical(self, "Print Error", "Failed to start printing.")
                return

            print("DEBUG: Painter started successfully")

            # Helper to (re)compute printable rect (legacy behavior)
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

            # Build ordered page list (metadata + tiles) then honor printer's page range
            ordered_pages: list[object] = []
            if include_metadata and metadata_position == "first":
                ordered_pages.append("metadata")
            ordered_pages.extend(list(range(len(page_grid))))
            if include_metadata and metadata_position == "last":
                ordered_pages.append("metadata")

            total_pages_overall = len(ordered_pages)
            prange = printer.printRange()
            from_page = 1
            to_page = total_pages_overall
            if prange == QPrinter.PageRange:
                fp = int(printer.fromPage() or 1)
                tp = int(printer.toPage() or total_pages_overall)
                if 1 <= fp <= total_pages_overall and 1 <= tp <= total_pages_overall and tp >= fp:
                    from_page, to_page = fp, tp
            print(f"DEBUG: Requested print range: {from_page}-{to_page} (range enum={prange})")

            printed_count = 0
            overall_index = 0
            first_printed = True
            for entry in ordered_pages:
                overall_index += 1
                if overall_index < from_page or overall_index > to_page:
                    continue
                if not first_printed:
                    printer.newPage()
                page_rect = printable_rect()

                if entry == "metadata":
                    print("DEBUG: Printing metadata page (within range)")
                    self._print_metadata_page(painter, printer, source_pixmap, page_grid, page_rect)
                    printed_count += 1
                    first_printed = False
                    continue

                i = int(entry)
                page = page_grid[i]
                print(f"DEBUG: Printing tile {i+1}/{len(page_grid)} (overall {overall_index})")

                # Create a full tile pixmap including gutters and clip to printable area
                tile_pixmap = self._create_tile_pixmap(source_pixmap, page)

                if tile_pixmap and not tile_pixmap.isNull():
                    print(f"DEBUG: Drawing tile to paint rect: {page_rect.width()}x{page_rect.height()}")

                    # Resolve printer-axis px/mm from the reported printable rect
                    # so gutters and calibration map correctly in device space.
                    pl = printer.pageLayout()
                    pr_mm_rect = pl.paintRect(QPageLayout.Millimeter)
                    # Fallback to device DPI if needed
                    ppmm_fallback = (printer.resolution() / 25.4) if printer.resolution() > 0 else 11.811
                    px_per_mm_x = page_rect.width() / pr_mm_rect.width() if pr_mm_rect.width() > 0 else ppmm_fallback
                    px_per_mm_y = page_rect.height() / pr_mm_rect.height() if pr_mm_rect.height() > 0 else ppmm_fallback

                    # Gutters in device px (axis-specific)
                    gutter_mm = self.config.get_gutter_size_mm()
                    g_px_x = int(round(gutter_mm * px_per_mm_x))
                    g_px_y = int(round(gutter_mm * px_per_mm_y))

                    # Apply printer calibration: reserve a margin on right/bottom only
                    try:
                        ori_name = 'landscape' if pl.orientation() == QPageLayout.Landscape else 'portrait'
                        h_mm, v_mm = self.config.get_print_calibration(ori_name)
                        calib_px_x = max(0, int(round(h_mm * px_per_mm_x)))
                        calib_px_y = max(0, int(round(v_mm * px_per_mm_y)))
                    except Exception:
                        calib_px_x = 0
                        calib_px_y = 0

                    # Source (inner) rect from tile pixmap
                    g_tile = int(page.get('gutter', 0) or 0)
                    src_inner = QRect(
                        g_tile,
                        g_tile,
                        max(0, tile_pixmap.width() - 2 * g_tile),
                        max(0, tile_pixmap.height() - 2 * g_tile),
                    )

                    # Desired destination size in device px for exact physical scaling:
                    # dest_px = src_px * (mm/px_document) * (px/mm_printer)
                    doc_mm_per_px = getattr(self.document_viewer, 'scale_factor', 1.0)
                    desired_w_px = int(round(src_inner.width() * doc_mm_per_px * px_per_mm_x))
                    desired_h_px = int(round(src_inner.height() * doc_mm_per_px * px_per_mm_y))

                    # Available inner area after gutters and calibration on the page
                    avail_x = page_rect.x() + g_px_x
                    avail_y = page_rect.y() + g_px_y
                    avail_w = max(0, page_rect.width() - 2 * g_px_x - calib_px_x)
                    avail_h = max(0, page_rect.height() - 2 * g_px_y - calib_px_y)

                    # Destination rect anchored at left/top of printable area.
                    # Keep 1:1 mapping from document px to device px; do not shrink to avail
                    # (the calibrated right/bottom will be clipped by clip_rect).
                    dest_inner = QRect(avail_x, avail_y, desired_w_px, desired_h_px)

                    # Clip to available area to avoid drawing into calibrated margins
                    clip_rect = QRect(avail_x, avail_y, avail_w, avail_h)

                    painter.save()
                    painter.setClipRect(clip_rect)
                    painter.drawPixmap(dest_inner, tile_pixmap, src_inner)
                    painter.restore()

                    # Draw simple gutter rectangle overlay for visual guidance
                    if self.config.get_gutter_lines_print():
                        painter.save()
                        # Draw 1px filled bars for gutter rectangle inside the clipped printable area
                        iw = clip_rect.width(); ih = clip_rect.height()
                        ix = clip_rect.x(); iy = clip_rect.y()
                        painter.setOpacity(1.0)
                        if iw > 2 and ih > 2:
                            painter.fillRect(QRect(ix, iy, 1, ih - 1), Qt.blue)  # Left
                            painter.fillRect(QRect(ix, iy, iw - 1, 1), Qt.blue)  # Top
                            painter.fillRect(QRect(ix + iw - 2, iy, 1, ih - 1), Qt.blue)  # Right inset
                            painter.fillRect(QRect(ix, iy + ih - 2, iw - 1, 1), Qt.blue)  # Bottom inset
                    painter.restore()

                    # Re-draw scale bar in printer space to guarantee physical length,
                    # inside the calibrated clip area (prevents truncation or scaling).
                    try:
                        from .utils.overlays import draw_scale_bar
                        units = self.config.get_default_units()
                        location = self.config.get_scale_bar_location()
                        opacity = self.config.get_scale_bar_opacity()
                        length_in = self.config.get_scale_bar_length_in()
                        length_cm = self.config.get_scale_bar_length_cm()
                        thickness_mm = self.config.get_scale_bar_thickness_mm()
                        padding_mm = self.config.get_scale_bar_padding_mm()
                        # Use printer px/mm mapping for exact physical sizing (horizontal axis)
                        mm_per_px_printer = 1.0 / (px_per_mm_x if px_per_mm_x > 0 else (printer.resolution() / 25.4))
                        # Temporarily translate to clip origin so overlay aligns to calibrated area
                        painter.save()
                        painter.translate(clip_rect.x(), clip_rect.y())
                        draw_scale_bar(
                            painter,
                            clip_rect.width(),
                            clip_rect.height(),
                            0,  # no gutters here
                            mm_per_px_printer,
                            units,
                            location,
                            length_in,
                            length_cm,
                            opacity,
                            thickness_mm,
                            padding_mm,
                        )
                        painter.restore()
                    except Exception:
                        pass

                    # Registration marks in printer space at calibrated inner corners, if enabled
                    try:
                        if self.config.get_reg_marks_print():
                            from .settings.config import config
                            diameter_mm = config.get_reg_mark_diameter_mm()
                            cross_mm = config.get_reg_mark_crosshair_mm()
                            radius_x = int(round((diameter_mm * px_per_mm_x) / 2.0))
                            radius_y = int(round((diameter_mm * px_per_mm_y) / 2.0))
                            radius_px = max(1, min(radius_x, radius_y))
                            cross_len_px = max(1, int(round(cross_mm * min(px_per_mm_x, px_per_mm_y))))

                            # Use the calibrated clip rect as the inner area so right/bottom fall within bounds
                            inner = clip_rect
                            # Inclusive right/bottom; subtract 1px to avoid edge-clipping on some drivers
                            left = inner.left()
                            top = inner.top()
                            right = inner.x() + inner.width() - 1
                            bottom = inner.y() + inner.height() - 1

                            painter.save()
                            painter.setClipRect(inner, Qt.ReplaceClip)
                            painter.setOpacity(1.0)
                            painter.setPen(QPen(Qt.black, 1))

                            centers = [
                                (left, top),
                                (right, top),
                                (left, bottom),
                                (right, bottom),
                            ]
                            for cx, cy in centers:
                                painter.drawEllipse(cx - radius_px, cy - radius_px, radius_px * 2, radius_px * 2)
                                painter.drawLine(cx - cross_len_px, cy, cx + cross_len_px, cy)
                                painter.drawLine(cx, cy - cross_len_px, cx, cy + cross_len_px)
                            painter.restore()
                    except Exception:
                        pass

                    # Add page information using overall numbering
                    self._add_print_page_info(painter, page_rect, overall_index, total_pages_overall)
                    printed_count += 1
                    first_printed = False
                else:
                    print(f"ERROR: Failed to create tile pixmap for tile {i+1}")

            if printed_count == 0:
                print("DEBUG: No pages fell within requested range; nothing printed.")

            painter.end()
            print("DEBUG: Printing completed successfully")

            # Show success message
            QMessageBox.information(
                self,
                "Print Complete",
                f"Successfully printed {printed_count} page(s)."
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

                # Draw metadata at the printable rect origin
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

        # Resolve page size in pixels for PREVIEW using the printer's printable area (paintRect)
        # so the preview matches actual printed coverage. This does NOT affect the print path.
        page_size = self.config.get_default_page_size()
        orientation_pref = self.config.get_page_orientation()
        try:
            # Decide preview orientation: honor explicit setting; for 'auto', use doc aspect
            if orientation_pref == 'landscape':
                preview_orientation = QPageLayout.Landscape
            elif orientation_pref == 'portrait':
                preview_orientation = QPageLayout.Portrait
            else:  # 'auto'
                preview_orientation = QPageLayout.Landscape if doc_width >= doc_height else QPageLayout.Portrait

            # Configure a QPrinter to retrieve printable area for the page size/orientation
            from PySide6.QtPrintSupport import QPrinter
            qps_id = self._qpagesize_from_name(page_size)
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPageSize(qps_id))
            printer.setPageLayout(QPageLayout(QPageSize(qps_id), preview_orientation, QMarginsF(0, 0, 0, 0), QPageLayout.Millimeter))
            pr_mm = printer.pageLayout().paintRect(QPageLayout.Millimeter)
            # Convert printable mm to document pixels via scale (mm/px)
            page_width_pixels = float(pr_mm.width()) / float(scale_factor)
            page_height_pixels = float(pr_mm.height()) / float(scale_factor)
        except Exception:
            # Fallback to generic page size if printer metrics unavailable
            page_width_pixels, page_height_pixels = compute_page_size_pixels(
                scale_factor_mm_per_px=scale_factor,
                page_size_name=page_size,
                orientation=orientation_pref,
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

        # Calculate tile grid with gutter support and calibration-aware stepping
        gutter_mm = self.config.get_gutter_size_mm()
        gutter_pixels = gutter_mm / scale_factor

        # Apply per-orientation calibration to step size so content isn't lost to non-printable right/bottom
        # Determine effective orientation actually used for the grid from resolved pixel dimensions
        ori_for_grid = 'landscape' if page_width_pixels > page_height_pixels else 'portrait'
        h_mm, v_mm = self.config.get_print_calibration(ori_for_grid)
        calib_step_x_px = max(0.0, float(h_mm) / float(scale_factor) if scale_factor > 0 else 0.0)
        calib_step_y_px = max(0.0, float(v_mm) / float(scale_factor) if scale_factor > 0 else 0.0)

        # Generate page grid (pages can overlap where gutters meet)
        page_grid = compute_page_grid_with_gutters(
            doc_width_px=doc_width,
            doc_height_px=doc_height,
            page_width_px=page_width_pixels,
            page_height_px=page_height_pixels,
            gutter_px=gutter_pixels,
            calib_reduce_step_x_px=calib_step_x_px,
            calib_reduce_step_y_px=calib_step_y_px,
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
            calib_reduce_step_x_px=0.0,
            calib_reduce_step_y_px=0.0,
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

    def show_printer_calibration(self):
        dlg = PrinterCalibrationDialog(self, self.config)
        dlg.exec()

    def print_ladder_test(self, orientation: str):
        """Print a single-page ladder test for the given orientation (portrait|landscape).

        Refactor highlights:
        - Adds concise instructions directly beneath the page title.
        - Adds a clear vertical ladder with stair-step labels to improve readability.
        - Cleans up mapping notes and avoids overlapping labels via stepped layout.
        """
        printer = QPrinter(QPrinter.HighResolution)
        # Preselect orientation; user can override in dialog
        try:
            if (orientation or "portrait").lower() == "landscape":
                printer.setPageOrientation(QPageLayout.Landscape)
            else:
                printer.setPageOrientation(QPageLayout.Portrait)
        except Exception:
            pass

        dlg = QPrintDialog(printer, self)
        dlg.setWindowTitle("Print Ladder Test")
        if dlg.exec() != QPrintDialog.Accepted:
            return

        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.critical(self, "Print Error", "Failed to start printing.")
            return

        try:
            pl = printer.pageLayout()
            pr_px = pl.paintRectPixels(printer.resolution())  # reported printable in pixels
            pr_mm = pl.paintRect(QPageLayout.Millimeter)      # reported printable in millimeters

            # Map logical coords to reported printable area (no calibration)
            painter.setViewport(pr_px)
            painter.setWindow(0, 0, pr_px.width(), pr_px.height())

            # px/mm per axis from reported printable
            px_per_mm_x = pr_px.width() / pr_mm.width() if pr_mm.width() > 0 else 0
            px_per_mm_y = pr_px.height() / pr_mm.height() if pr_mm.height() > 0 else 0

            w, h = pr_px.width(), pr_px.height()
            painter.fillRect(QRect(0, 0, w, h), Qt.white)
            painter.setPen(Qt.black)

            # Title block
            title_font = painter.font(); title_font.setBold(True); title_font.setPointSize(24)
            painter.setFont(title_font)
            tfm = painter.fontMetrics()
            title = "OpenTiler Calibration Test Page"
            tw = tfm.horizontalAdvance(title)
            top_margin_px = int(round(10.0 * px_per_mm_y))  # 10 mm top margin
            painter.drawText(max(0, (w - tw) // 2), top_margin_px + tfm.ascent(), title)

            # Orientation subtitle + brief instructions near top
            painter.setPen(Qt.black)
            sub_font = painter.font(); sub_font.setBold(False); sub_font.setPointSize(12)
            painter.setFont(sub_font)
            sfm = painter.fontMetrics()
            ori_title = 'Landscape' if pl.orientation() == QPageLayout.Landscape else 'Portrait'
            subtitle = f"Orientation: {ori_title}"
            # Draw subtitle aligned left within printable area
            sub_y = top_margin_px + tfm.height() + sfm.ascent() + 4
            painter.drawText(int(round(10.0 * px_per_mm_x)), sub_y, subtitle)

            # Instructions block directly under title (centered, multi-line)
            section_name = f"{ori_title} Calibration"
            painter.setFont(sub_font)
            instr_lines = [
                "Instructions:",
                "1) Print at 100% (no printer scaling / no ‘Fit to page’).",
                "2) On this page, find the largest visible tick on each ladder.",
                "3) Open Tools → Printer Calibration.",
                f"4) In {section_name}: enter RIGHT ladder value into Horizontal (right).",
                f"5) In {section_name}: enter BOTTOM ladder value into Vertical (bottom).",
                "6) Click Save to store calibration values.",
                "7) Reprint the ladder and fine‑tune if needed.",
            ]
            if w > 0:
                # Compute panel extents and center it
                line_h = sfm.height()
                max_line_w = max(sfm.horizontalAdvance(s) for s in instr_lines)
                pad_x = 12
                pad_y = 8
                panel_w = max_line_w + pad_x
                panel_h = len(instr_lines) * line_h + pad_y
                # Left-justify: align panel with left printable margin (10 mm)
                panel_x = int(round(10.0 * px_per_mm_x))
                # Place panel fully below subtitle: leave at least one full line + 3 mm gap
                panel_y = sub_y + line_h + int(round(3.0 * px_per_mm_y))
                # Background for clarity
                painter.fillRect(QRect(panel_x, panel_y - sfm.ascent(), panel_w, panel_h), Qt.white)
                painter.setPen(Qt.black)
                painter.drawRect(QRect(panel_x, panel_y - sfm.ascent(), panel_w, panel_h))
                # Draw lines centered in the panel
                draw_y = panel_y
                for s in instr_lines:
                    # Left-justified text inside the panel with small left padding
                    painter.drawText(panel_x + (pad_x // 3), draw_y, s)
                    draw_y += line_h

            # Draw center crosshair for reference
            cx, cy = w // 2, h // 2
            painter.setPen(QPen(Qt.black, 0))
            painter.drawLine(0, cy, w, cy)
            painter.drawLine(cx, 0, cx, h)

            # Draw reference boxes FIRST so ladders/labels are on top
            painter.setPen(QPen(Qt.black, 0))
            # Outer effective box (reported printable) inset bars
            if w > 2 and h > 2:
                painter.fillRect(QRect(0, 0, 1, h - 1), Qt.black)
                painter.fillRect(QRect(0, 0, w - 1, 1), Qt.black)
                painter.fillRect(QRect(w - 2, 0, 1, h - 1), Qt.black)
                painter.fillRect(QRect(0, h - 2, w - 1, 1), Qt.black)

            # 10 mm inner box
            inset_x = int(round(10.0 * px_per_mm_x)); inset_y = int(round(10.0 * px_per_mm_y))
            ix = inset_x; iy = inset_y; iw = max(0, w - 2 * inset_x); ih = max(0, h - 2 * inset_y)
            if iw > 2 and ih > 2:
                painter.fillRect(QRect(ix, iy, 1, ih - 1), Qt.black)
                painter.fillRect(QRect(ix, iy, iw - 1, 1), Qt.black)
                painter.fillRect(QRect(ix + iw - 2, iy, 1, ih - 1), Qt.black)
                painter.fillRect(QRect(ix, iy + ih - 2, iw - 1, 1), Qt.black)

            # Add a 10 cm scale bar at the bottom of the printable area (Page-S),
            # matching the style/logic used on tile pages.
            try:
                from .utils.overlays import draw_scale_bar
                from .settings.config import config
                # mm/px derived from printer mapping; use X axis for consistent horizontal bar
                mm_per_px = 1.0 / px_per_mm_x if px_per_mm_x > 0 else (1.0 / (printer.resolution() / 25.4))
                draw_scale_bar(
                    painter,
                    w,  # treat printable area as the whole tile surface for placement
                    h,
                    0,  # no gutters on the debug page
                    mm_per_px,
                    'mm',            # force metric scale (10 cm)
                    'Page-S',        # bottom of printable area
                    0.0,             # length_in (unused for metric)
                    10.0,            # 10 cm scale
                    int(config.get_scale_bar_opacity()),
                    float(config.get_scale_bar_thickness_mm()),
                    float(config.get_scale_bar_padding_mm()),
                )
            except Exception:
                pass

            # Right-edge ladder: ticks every 1 mm
            # Labels: 30, 25, 20, 15, 10, 5, 0 (stair-stepped vertically with leader lines)
            ladder_mm = 30
            base_x = w - 2  # inset from right by 1px
            painter.setPen(QPen(Qt.black, 0))
            tick_long = int(round(6.0 * px_per_mm_y))
            tick_short = int(round(3.0 * px_per_mm_y))
            ladder_font = painter.font(); ladder_font.setBold(True); ladder_font.setPointSize(18)
            painter.setFont(ladder_font)
            ladder_fm = painter.fontMetrics()
            label_pad = 4
            # Draw ticks
            for mm in range(0, ladder_mm + 1):
                x = base_x - int(round(mm * px_per_mm_x))
                tick = tick_long if mm % 5 == 0 else tick_short
                painter.drawLine(x, cy - tick, x, cy + tick)
            # Stair-step labels with leader lines for 30,25,20,15,10,5,0
            stair_vals = [30, 25, 20, 15, 10, 5, 0]
            for idx, mm in enumerate(stair_vals):
                x = base_x - int(round(mm * px_per_mm_x))
                label = f"{mm}"
                lw = ladder_fm.horizontalAdvance(label)
                lh = ladder_fm.height()
                # Step up each subsequent label to avoid overlap
                step_dy = idx * (lh + max(6, int(round(2.0 * px_per_mm_y))))
                by = max(0, cy - tick_long - lh - max(8, int(round(3.0 * px_per_mm_y))) - step_dy)
                bx = max(0, x - lw - (label_pad + 2) - int(round(2.0 * px_per_mm_x)))
                # Background box
                painter.fillRect(QRect(bx, by, lw + label_pad + 2, lh + label_pad // 2), Qt.white)
                painter.setPen(Qt.black)
                painter.drawText(bx + label_pad // 2, by + ladder_fm.ascent(), label)
                # Leader line from tick top to label box right edge
                painter.drawLine(x, cy - tick_long, bx + lw + label_pad + 2, by + ladder_fm.ascent())
            # Mapping note for right ladder (smaller font)
            painter.setFont(sub_font); sfm = painter.fontMetrics()
            right_note = f"Right ladder → {section_name} → Horizontal (right)"
            rnw = sfm.horizontalAdvance(right_note)
            painter.drawText(max(0, base_x - int(round(40 * px_per_mm_x)) - rnw), max(sfm.height() + 2, cy - max(40, 3 * tick_long)), right_note)

            # Bottom-edge vertical ladder (ticks every 1 mm from bottom, at mid-width)
            # Bottom ladder ticks (0..30 mm from bottom), baseline slightly inset to avoid clipping
            for mm in range(0, ladder_mm + 1):
                y = h - 3 - int(round(mm * px_per_mm_y))
                tick = tick_long if mm % 5 == 0 else tick_short
                painter.drawLine(cx - tick, y, cx + tick, y)
            # Stair-step labels for 30,25,20,15,10,5,0 (start near right, step rightward)
            painter.setFont(ladder_font); ladder_fm = painter.fontMetrics()
            for idx, mm in enumerate(stair_vals):
                y = h - 3 - int(round(mm * px_per_mm_y))
                label = f"{mm}"
                lw = ladder_fm.horizontalAdvance(label)
                lh = ladder_fm.height()
                step_dx = idx * int(round(8.0 * px_per_mm_x))
                bx = min(w - lw - (label_pad + 2), cx + tick_long + 6 + step_dx)
                by = max(0, y - lh - (label_pad // 2))
                painter.fillRect(QRect(bx, by, lw + label_pad + 2, lh + label_pad // 2), Qt.white)
                painter.setPen(Qt.black)
                painter.drawText(bx + label_pad // 2, y - 4, label)
                # Leader line from tick end to label box left edge
                painter.drawLine(cx + tick_long, y, bx, y)
            # Mapping note for bottom ladder — position ABOVE the ladder, left-justified to the centerline
            painter.setFont(sub_font); sfm = painter.fontMetrics()
            bottom_note = f"Bottom ladder → {section_name} → Vertical (bottom)"
            top_y = h - 3 - int(round(ladder_mm * px_per_mm_y))
            # Use a larger safety gap (≈8 mm) to avoid overlapping ladder ticks
            gap_y_px = int(round(8.0 * px_per_mm_y))
            # Place baseline so entire text sits well above the top tick (account for descent)
            note_y = max(sfm.height() + 2, top_y - gap_y_px - sfm.descent() - 1)
            bnw = sfm.horizontalAdvance(bottom_note)
            # Place so that right edge sits slightly left of centerline to avoid label overlap
            note_x = max(4, cx - bnw - int(round(2.0 * px_per_mm_x)))
            painter.drawText(note_x, note_y, bottom_note)

            # (reference boxes moved earlier)
        finally:
            painter.end()

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
