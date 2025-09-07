"""
Document viewer widget for OpenTiler.
"""

import os

from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import QColor, QCursor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QLabel, QMessageBox, QScrollArea, QSizePolicy,
                               QVBoxLayout, QWidget)

try:
    import fitz  # PyMuPDF

    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    import numpy as np
    import rawpy

    HAS_RAWPY = True
except ImportError:
    HAS_RAWPY = False

import io

from PIL import Image


class PanScrollArea(QScrollArea):
    """Custom scroll area that handles middle mouse button panning."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.panning = False
        self.last_pan_point = QPoint()
        self.parent_viewer = None

    def set_parent_viewer(self, viewer):
        """Set reference to parent viewer."""
        self.parent_viewer = viewer

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MiddleButton:
            # Start panning with middle mouse button
            self.panning = True
            self.last_pan_point = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events for panning."""
        if self.panning:
            # Calculate pan delta
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()

            # Apply panning to scroll bars
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()

            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())

            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.MiddleButton and self.panning:
            self.panning = False
            # Restore appropriate cursor
            if self.parent_viewer and self.parent_viewer.point_selection_mode:
                self.setCursor(QCursor(Qt.CrossCursor))
            else:
                self.setCursor(QCursor(Qt.OpenHandCursor))
            event.accept()
            return
        super().mouseReleaseEvent(event)


class ClickableLabel(QLabel):
    """A QLabel that can handle mouse clicks for point selection and panning."""

    clicked = Signal(QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.panning = False
        self.last_pan_point = QPoint()
        self.parent_viewer = None
        self.dragging = False
        self.dragging_index = None  # 0 or 1
        self.hit_radius = 16  # pixels in display space
        self.dragging_measure = False

    def set_parent_viewer(self, viewer):
        """Set reference to parent viewer for panning."""
        self.parent_viewer = viewer

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton and self.parent_viewer:
            # Ensure viewer gets focus for Delete handling
            try:
                self.parent_viewer.setFocus()
            except Exception:
                pass
        if (
            event.button() == Qt.LeftButton
            and self.parent_viewer
            and self.parent_viewer.point_selection_mode
        ):
            mods = event.modifiers()
            # If two points exist, start dragging the nearest endpoint (no modifier required)
            if len(self.parent_viewer.selected_points) >= 2:
                # Compute display-space endpoints
                p1 = self.parent_viewer.selected_points[0]
                p2 = self.parent_viewer.selected_points[1]
                z = max(0.0001, self.parent_viewer.zoom_factor)
                p1_disp = QPoint(int(p1[0] * z), int(p1[1] * z))
                p2_disp = QPoint(int(p2[0] * z), int(p2[1] * z))

                # Find click position relative to image
                label_size = self.size()
                pixmap_size = self.pixmap().size() if self.pixmap() else QSize(1, 1)
                x_offset = (label_size.width() - pixmap_size.width()) // 2
                y_offset = (label_size.height() - pixmap_size.height()) // 2
                click_disp = event.pos() - QPoint(x_offset, y_offset)

                # Check proximity
                def within(a: QPoint, b: QPoint, r: int) -> bool:
                    dx = a.x() - b.x()
                    dy = a.y() - b.y()
                    return (dx * dx + dy * dy) <= r * r

                # Choose nearest endpoint unconditionally to improve grab reliability
                d1 = (click_disp.x() - p1_disp.x()) ** 2 + (
                    click_disp.y() - p1_disp.y()
                ) ** 2
                d2 = (click_disp.x() - p2_disp.x()) ** 2 + (
                    click_disp.y() - p2_disp.y()
                ) ** 2
                self.dragging = True
                self.dragging_index = 0 if d1 <= d2 else 1
                self.setCursor(QCursor(Qt.ClosedHandCursor))
                event.accept()
                return
            # Otherwise treat as point selection click only if we still need points
            if len(self.parent_viewer.selected_points) < 2:
                self.clicked.emit(event.pos())
            else:
                # Optional: pick nearest endpoint to start dragging immediately
                # without requiring precise hit
                # Compute distance to both and pick if within 2x hit radius
                try:
                    d1 = (click_disp.x() - p1_disp.x()) ** 2 + (
                        click_disp.y() - p1_disp.y()
                    ) ** 2
                    d2 = (click_disp.x() - p2_disp.x()) ** 2 + (
                        click_disp.y() - p2_disp.y()
                    ) ** 2
                    r2 = (self.hit_radius * 2) ** 2
                    if d1 <= r2 or d2 <= r2:
                        self.dragging = True
                        self.dragging_index = 0 if d1 <= d2 else 1
                        self.setCursor(QCursor(Qt.ClosedHandCursor))
                        event.accept()
                        return
                except Exception:
                    pass
        elif event.button() == Qt.LeftButton and self.parent_viewer:
            # Not in point selection: allow selecting existing measurement for delete
            if self.pixmap():
                label_size = self.size()
                pixmap_size = self.pixmap().size() if self.pixmap() else QSize(1, 1)
                x_offset = (label_size.width() - pixmap_size.width()) // 2
                y_offset = (label_size.height() - pixmap_size.height()) // 2
                image_x = event.pos().x() - x_offset
                image_y = event.pos().y() - y_offset
                image_x = max(0, min(image_x, pixmap_size.width()))
                image_y = max(0, min(image_y, pixmap_size.height()))
                z = max(0.0001, self.parent_viewer.zoom_factor)
                original_x = image_x / z
                original_y = image_y / z
                # Try selecting a measurement
                if self.parent_viewer.select_measurement_at(original_x, original_y):
                    # If selection occurred, also check if near an endpoint to start dragging
                    idx = self.parent_viewer.selected_measure_index
                    if idx is not None and 0 <= idx < len(
                        self.parent_viewer.measurements
                    ):
                        z = max(0.0001, self.parent_viewer.zoom_factor)
                        m = self.parent_viewer.measurements[idx]
                        p1 = QPoint(int(m["p1"][0] * z), int(m["p1"][1] * z))
                        p2 = QPoint(int(m["p2"][0] * z), int(m["p2"][1] * z))
                        cur = QPoint(int(image_x), int(image_y))
                        d1 = (cur.x() - p1.x()) ** 2 + (cur.y() - p1.y()) ** 2
                        d2 = (cur.x() - p2.x()) ** 2 + (cur.y() - p2.y()) ** 2
                        r2 = (self.hit_radius) ** 2
                        if d1 <= r2 or d2 <= r2:
                            self.dragging = True
                            self.dragging_measure = True
                            self.dragging_index = 0 if d1 <= d2 else 1
                            self.setCursor(QCursor(Qt.ClosedHandCursor))
                    self.parent_viewer._update_display()
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for endpoint dragging and live preview (on label)."""
        # Live preview of measurement when one point is selected
        try:
            if (
                self.parent_viewer
                and self.parent_viewer.point_selection_mode
                and not self.dragging
                and self.pixmap()
            ):
                if len(self.parent_viewer.selected_points) == 1:
                    label_size = self.size()
                    pixmap_size = self.pixmap().size()
                    x_offset = (label_size.width() - pixmap_size.width()) // 2
                    y_offset = (label_size.height() - pixmap_size.height()) // 2
                    image_x = event.pos().x() - x_offset
                    image_y = event.pos().y() - y_offset
                    # Clamp to pixmap bounds
                    image_x = max(0, min(image_x, pixmap_size.width()))
                    image_y = max(0, min(image_y, pixmap_size.height()))
                    z = max(0.0001, self.parent_viewer.zoom_factor)
                    original_x = image_x / z
                    original_y = image_y / z
                    if self.parent_viewer.temp_cursor_pos != (original_x, original_y):
                        self.parent_viewer.temp_cursor_pos = (original_x, original_y)
                        self.parent_viewer._update_display()
        except Exception:
            pass

        # Hover highlight and drag initiation
        if self.parent_viewer and self.parent_viewer.point_selection_mode:
            # Hover highlight for endpoints when we have two points
            if len(self.parent_viewer.selected_points) >= 2 and self.pixmap():
                try:
                    p1 = self.parent_viewer.selected_points[0]
                    p2 = self.parent_viewer.selected_points[1]
                    z = max(0.0001, self.parent_viewer.zoom_factor)
                    p1_disp = QPoint(int(p1[0] * z), int(p1[1] * z))
                    p2_disp = QPoint(int(p2[0] * z), int(p2[1] * z))
                    label_size = self.size()
                    pixmap_size = self.pixmap().size()
                    x_offset = (label_size.width() - pixmap_size.width()) // 2
                    y_offset = (label_size.height() - pixmap_size.height()) // 2
                    cur_disp = event.pos() - QPoint(x_offset, y_offset)
                    d1 = (cur_disp.x() - p1_disp.x()) ** 2 + (
                        cur_disp.y() - p1_disp.y()
                    ) ** 2
                    d2 = (cur_disp.x() - p2_disp.x()) ** 2 + (
                        cur_disp.y() - p2_disp.y()
                    ) ** 2
                    r2 = (self.hit_radius) ** 2
                    new_hover = None
                    if d1 <= r2 or d2 <= r2:
                        new_hover = 0 if d1 <= d2 else 1
                    if new_hover != self.parent_viewer.hover_endpoint:
                        self.parent_viewer.hover_endpoint = new_hover
                        self.parent_viewer._update_display()
                except Exception:
                    pass
            # Forgiving capture when moving with button held near an endpoint
            if (
                (not self.dragging)
                and (event.buttons() & Qt.LeftButton)
                and len(self.parent_viewer.selected_points) >= 2
                and self.pixmap()
            ):
                p1 = self.parent_viewer.selected_points[0]
                p2 = self.parent_viewer.selected_points[1]
                z = max(0.0001, self.parent_viewer.zoom_factor)
                p1_disp = QPoint(int(p1[0] * z), int(p1[1] * z))
                p2_disp = QPoint(int(p2[0] * z), int(p2[1] * z))
                label_size = self.size()
                pixmap_size = self.pixmap().size()
                x_offset = (label_size.width() - pixmap_size.width()) // 2
                y_offset = (label_size.height() - pixmap_size.height()) // 2
                cur_disp = event.pos() - QPoint(x_offset, y_offset)
                d1 = (cur_disp.x() - p1_disp.x()) ** 2 + (
                    cur_disp.y() - p1_disp.y()
                ) ** 2
                d2 = (cur_disp.x() - p2_disp.x()) ** 2 + (
                    cur_disp.y() - p2_disp.y()
                ) ** 2
                r2 = (self.hit_radius * 2) ** 2
                if d1 <= r2 or d2 <= r2:
                    self.dragging = True
                    self.dragging_index = 0 if d1 <= d2 else 1
                    self.setCursor(QCursor(Qt.ClosedHandCursor))

        # Update point during drag for scaling selection
        if (
            self.dragging
            and not self.dragging_measure
            and self.parent_viewer
            and self.parent_viewer.point_selection_mode
            and self.dragging_index is not None
            and self.pixmap()
        ):
            # Map cursor to image coords
            label_size = self.size()
            pixmap_size = self.pixmap().size()
            x_offset = (label_size.width() - pixmap_size.width()) // 2
            y_offset = (label_size.height() - pixmap_size.height()) // 2
            image_x = event.pos().x() - x_offset
            image_y = event.pos().y() - y_offset
            # Clamp
            image_x = max(0, min(image_x, pixmap_size.width()))
            image_y = max(0, min(image_y, pixmap_size.height()))
            z = max(0.0001, self.parent_viewer.zoom_factor)
            original_x = image_x / z
            original_y = image_y / z
            pts = list(self.parent_viewer.selected_points)
            if len(pts) >= 2:
                pts[self.dragging_index] = (original_x, original_y)
                self.parent_viewer.selected_points = pts
                try:
                    self.parent_viewer.points_updated.emit(
                        original_x, original_y, int(self.dragging_index)
                    )
                except Exception:
                    pass
                self.parent_viewer._update_display()
            event.accept()
            return

        # Update endpoint during drag for a persisted measurement
        if (
            self.dragging
            and self.dragging_measure
            and self.parent_viewer
            and self.pixmap()
        ):
            label_size = self.size()
            pixmap_size = self.pixmap().size()
            x_offset = (label_size.width() - pixmap_size.width()) // 2
            y_offset = (label_size.height() - pixmap_size.height()) // 2
            image_x = event.pos().x() - x_offset
            image_y = event.pos().y() - y_offset
            image_x = max(0, min(image_x, pixmap_size.width()))
            image_y = max(0, min(image_y, pixmap_size.height()))
            z = max(0.0001, self.parent_viewer.zoom_factor)
            original_x = image_x / z
            original_y = image_y / z
            idx = self.parent_viewer.selected_measure_index
            if idx is not None and 0 <= idx < len(self.parent_viewer.measurements):
                m = dict(self.parent_viewer.measurements[idx])
                if self.dragging_index == 0:
                    m["p1"] = (original_x, original_y)
                else:
                    m["p2"] = (original_x, original_y)
                # Update text based on new geometry
                m["text"] = self.parent_viewer._format_measurement_text(
                    m["p1"], m["p2"]
                )
                self.parent_viewer.measurements[idx] = m
                self.parent_viewer._update_display()
                try:
                    self.parent_viewer.measurements_changed.emit()
                except Exception:
                    pass
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.dragging_index = None
            self.dragging_measure = False
            # Restore cursor
            if self.parent_viewer and self.parent_viewer.point_selection_mode:
                self.setCursor(QCursor(Qt.CrossCursor))
            else:
                self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        # Ensure cursor reflects selection mode even if outer viewport set a different cursor
        if getattr(self, "parent_viewer", None):
            if self.parent_viewer.point_selection_mode:
                self.setCursor(QCursor(Qt.CrossCursor))
            else:
                self.setCursor(QCursor(Qt.OpenHandCursor))
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Clear hover highlight on leave
        if (
            getattr(self, "parent_viewer", None)
            and self.parent_viewer.hover_endpoint is not None
        ):
            self.parent_viewer.hover_endpoint = None
            try:
                self.parent_viewer._update_display()
            except Exception:
                pass
        super().leaveEvent(event)


class DocumentViewer(QWidget):
    """Widget for viewing and interacting with documents."""

    # Signals
    document_loaded = Signal(str)  # Emitted when a document is loaded
    scale_changed = Signal(float)  # Emitted when scale changes
    point_selected = Signal(float, float)  # Emitted when a point is selected (x, y)
    points_updated = Signal(
        float, float, int
    )  # Emitted when an endpoint is dragged (x, y, index)
    measurements_changed = Signal()  # Emitted when measurements change

    def __init__(self):
        super().__init__()
        self.current_document = None
        self.current_pixmap = None
        self.zoom_factor = 1.0
        self.scale_factor = 1.0  # Real-world scale
        self.rotation = 0
        self.point_selection_mode = False
        self.selected_points = []  # Store selected points for scaling
        self.tile_grid = []  # Store tile grid for display
        self.page_grid = []  # Store page grid for display
        self.gutter_size = 0  # Gutter size in pixels
        self.measurement_text = ""  # Store measurement text for display
        self.hover_endpoint = None  # which endpoint is hovered (0/1)
        self.temp_cursor_pos = None  # live cursor pos in image coords for preview
        # Safety defaults in case events bubble unexpectedly
        self.dragging = False
        self.dragging_index = None
        # Multiple measurements support
        self.measurements = []  # list of { 'p1':(x,y), 'p2':(x,y), 'text':str }
        self.selected_measure_index = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Create custom scroll area with panning support
        self.scroll_area = PanScrollArea()
        self.scroll_area.setWidgetResizable(
            False
        )  # Don't resize widget to fit - allow scrolling
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.set_parent_viewer(self)

        # Install event filter on scroll area to capture wheel events
        self.scroll_area.installEventFilter(self)
        self.scroll_area.viewport().installEventFilter(self)

        # Create clickable image label
        self.image_label = ClickableLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.image_label.setText("No document loaded")
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Connect click signal and set parent viewer reference
        self.image_label.clicked.connect(self.on_image_clicked)
        self.image_label.set_parent_viewer(self)

        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

        # Initialize panning state
        self.panning = False
        self.last_pan_point = QPoint()
        # Accept focus for Delete key handling
        self.setFocusPolicy(Qt.StrongFocus)

    def load_document(self, file_path):
        """Load a document from file path."""
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Error", f"File not found: {file_path}")
            return False

        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == ".pdf":
                return self._load_pdf(file_path)
            elif file_ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                return self._load_image(file_path)
            elif file_ext == ".svg":
                return self._load_svg(file_path)
            elif file_ext == ".dxf":
                return self._load_dxf(file_path)
            elif file_ext.lower() == ".fcstd":
                return self._load_freecad(file_path)
            elif file_ext.lower() in [
                ".raw",
                ".cr2",
                ".nef",
                ".arw",
                ".dng",
                ".orf",
                ".rw2",
                ".pef",
                ".srw",
                ".raf",
            ]:
                return self._load_raw(file_path)
            else:
                QMessageBox.critical(
                    self, "Error", f"Unsupported file format: {file_ext}"
                )
                return False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load document: {str(e)}")
            return False

    def _load_pdf(self, file_path):
        """Load a PDF document."""
        if not HAS_PYMUPDF:
            QMessageBox.critical(
                self, "Error", "PyMuPDF is required to load PDF files."
            )
            return False

        try:
            doc = fitz.open(file_path)
            if len(doc) == 0:
                QMessageBox.critical(self, "Error", "PDF document is empty.")
                return False

            # Load first page
            page = doc[0]
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)

            # Convert to QPixmap
            img_data = pix.tobytes("ppm")
            qimg = QPixmap()
            qimg.loadFromData(img_data)

            self.current_pixmap = qimg
            self.current_document = file_path
            self._update_display()
            self.document_loaded.emit(file_path)

            doc.close()
            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF: {str(e)}")
            return False

    def _load_image(self, file_path):
        """Load an image document."""
        try:
            # Use PIL to load the image for better format support
            pil_image = Image.open(file_path)

            # Convert to RGB if necessary
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")

            # Convert PIL image to QPixmap
            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            qimg = QPixmap()
            qimg.loadFromData(img_bytes.getvalue())

            self.current_pixmap = qimg
            self.current_document = file_path
            self._update_display()
            self.document_loaded.emit(file_path)

            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
            return False

    def _load_svg(self, file_path):
        """Load an SVG document."""
        # For now, we'll use QPixmap's built-in SVG support
        try:
            qimg = QPixmap(file_path)
            if qimg.isNull():
                QMessageBox.critical(self, "Error", "Failed to load SVG file.")
                return False

            self.current_pixmap = qimg
            self.current_document = file_path
            self._update_display()
            self.document_loaded.emit(file_path)

            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load SVG: {str(e)}")
            return False

    def _load_dxf(self, file_path):
        """Load a DXF document."""
        try:
            from ..formats.dxf_handler import DXFHandler

            dxf_handler = DXFHandler()
            pixmap = dxf_handler.load_dxf(file_path)

            if pixmap and not pixmap.isNull():
                self.current_pixmap = pixmap
                self.current_document = file_path
                self._update_display()
                self.document_loaded.emit(file_path)
                return True
            else:
                QMessageBox.critical(self, "Error", "Failed to load DXF file.")
                return False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load DXF: {str(e)}")
            return False

    def _load_freecad(self, file_path):
        """Load a FreeCAD document."""
        try:
            from ..formats.freecad_handler import FreeCADHandler

            freecad_handler = FreeCADHandler()
            pixmap = freecad_handler.load_freecad(file_path)

            if pixmap and not pixmap.isNull():
                self.current_pixmap = pixmap
                self.current_document = file_path
                self._update_display()
                self.document_loaded.emit(file_path)
                return True
            else:
                QMessageBox.critical(self, "Error", "Failed to load FreeCAD file.")
                return False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load FreeCAD: {str(e)}")
            return False

    def _load_raw(self, file_path):
        """Load a RAW image file."""
        if not HAS_RAWPY:
            QMessageBox.critical(
                self,
                "RAW Support Required",
                "RAW image support requires 'rawpy' package.\n"
                "Install with: pip install rawpy",
            )
            return False

        try:
            # Load RAW file
            with rawpy.imread(file_path) as raw:
                # Process RAW to RGB
                rgb = raw.postprocess(
                    use_camera_wb=True,  # Use camera white balance
                    half_size=False,  # Full resolution
                    no_auto_bright=True,  # Disable auto brightness
                    output_bps=8,  # 8-bit output
                )

            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(rgb)

            # Convert PIL Image to QPixmap
            # First convert to bytes
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)

            # Load into QPixmap
            qimg = QPixmap()
            qimg.loadFromData(img_buffer.getvalue())

            self.current_pixmap = qimg
            self.current_document = file_path
            self._update_display()
            self.document_loaded.emit(file_path)

            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load RAW image: {str(e)}")
            return False

    def _update_display(self):
        """Update the display with current pixmap and transformations."""
        if not self.current_pixmap:
            return

        # Apply rotation
        if self.rotation != 0:
            transform = self.current_pixmap.transformed(
                self.current_pixmap.transform().rotate(self.rotation)
            )
        else:
            transform = self.current_pixmap

        # Apply zoom
        if self.zoom_factor != 1.0:
            size = transform.size() * self.zoom_factor
            scaled = transform.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            scaled = transform

        # Draw selected points if in point selection mode OR if we have scale points to show
        if (self.point_selection_mode and self.selected_points) or (
            len(self.selected_points) >= 2
        ):
            scaled = self._draw_selected_points(scaled)

        # Draw existing measurements (persisted)
        if self.measurements:
            scaled = self._draw_measurements(scaled)

        # Draw page grid overlay if pages are defined
        if self.page_grid:
            scaled = self._draw_page_grid_overlay(scaled)
        # Draw tile grid overlay if tiles are defined (legacy support)
        elif self.tile_grid:
            scaled = self._draw_tile_grid_overlay(scaled)

        self.image_label.setPixmap(scaled)

        # Resize the label to match the pixmap size for proper scrolling
        self.image_label.resize(scaled.size())

    def _draw_selected_points(self, pixmap):
        """Draw selected points on the pixmap."""
        if not self.selected_points:
            return pixmap

        # Create a copy to draw on
        result = QPixmap(pixmap)
        painter = QPainter(result)

        # Prepare painter; specific pens are set for each element below

        # Draw endpoint handles only while the scaling tool is open
        if self.point_selection_mode:
            handle_radius = 8  # pixels in display space
            for i, (x, y) in enumerate(self.selected_points):
                # Convert original coordinates to current display coordinates
                display_x = x * self.zoom_factor
                display_y = y * self.zoom_factor

                # Handle style: filled circle with outline; highlight if hovered
                if self.hover_endpoint == i:
                    fill = QColor(255, 255, 0, 220)  # yellow highlight
                    outline = QPen(QColor(0, 0, 0), 2)
                else:
                    fill = QColor(0, 150, 255, 220)  # cyan
                    outline = QPen(QColor(0, 0, 0), 2)
                painter.setPen(outline)
                painter.setBrush(fill)
                painter.drawEllipse(
                    int(display_x - handle_radius),
                    int(display_y - handle_radius),
                    handle_radius * 2,
                    handle_radius * 2,
                )
                painter.setBrush(Qt.NoBrush)

                # Draw point number label slightly offset
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                painter.drawText(
                    int(display_x + handle_radius + 4),
                    int(display_y - handle_radius - 2),
                    f"P{i + 1}",
                )

        # Live preview: if one point selected and in selection mode, draw a temp line to cursor
        if (
            self.point_selection_mode
            and len(self.selected_points) == 1
            and self.temp_cursor_pos is not None
        ):
            from ..settings.config import config

            p1_x = self.selected_points[0][0] * self.zoom_factor
            p1_y = self.selected_points[0][1] * self.zoom_factor
            p2_x = self.temp_cursor_pos[0] * self.zoom_factor
            p2_y = self.temp_cursor_pos[1] * self.zoom_factor
            if config.get_scale_line_display():
                pen = QPen(QColor(255, 0, 0), 2)
                pen.setStyle(Qt.CustomDashLine)
                pen.setDashPattern([8, 3, 2, 3, 2, 3])
                painter.setPen(pen)
                painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

        # Draw line between points if we have two
        if len(self.selected_points) == 2:
            # Import config here to avoid circular imports
            from ..settings.config import config

            p1_x = self.selected_points[0][0] * self.zoom_factor
            p1_y = self.selected_points[0][1] * self.zoom_factor
            p2_x = self.selected_points[1][0] * self.zoom_factor
            p2_y = self.selected_points[1][1] * self.zoom_factor

            # Draw scale line (red dot–dash–dot) if enabled
            if config.get_scale_line_display():
                pen = QPen(QColor(255, 0, 0), 2)
                pen.setStyle(Qt.CustomDashLine)
                pen.setDashPattern([8, 3, 2, 3, 2, 3])
                painter.setPen(pen)
                painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

            # Draw datum line if enabled
            if config.get_datum_line_display():
                datum_pen = QPen(
                    QColor(config.get_datum_line_color()),
                    max(1, config.get_datum_line_width_px()),
                )
                style = str(config.get_datum_line_style()).lower()
                if style == "solid":
                    datum_pen.setStyle(Qt.SolidLine)
                elif style == "dash":
                    datum_pen.setStyle(Qt.DashLine)
                elif style == "dot":
                    datum_pen.setStyle(Qt.DotLine)
                elif style == "dashdot":
                    datum_pen.setStyle(Qt.DashDotLine)
                elif style == "dashdotdot":
                    datum_pen.setStyle(Qt.DashDotDotLine)
                elif style == "dot-dash-dot":
                    datum_pen.setStyle(Qt.CustomDashLine)
                    datum_pen.setDashPattern([8, 3, 2, 3, 2, 3])
                else:
                    datum_pen.setStyle(Qt.DashLine)
                painter.setPen(datum_pen)
                painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

            # Draw measurement text with smart placement if available and enabled
            if self.measurement_text and config.get_scale_text_display():
                # Calculate midpoint of the line
                mid_x = (p1_x + p2_x) / 2
                mid_y = (p1_y + p2_y) / 2

                # Set up font for measurement text
                font = painter.font()
                font.setPointSize(12)
                font.setBold(True)
                painter.setFont(font)

                # Set up pen for red text
                text_pen = QPen(QColor(255, 0, 0), 1)
                painter.setPen(text_pen)

                # Calculate geometry
                dx = p2_x - p1_x
                dy = p2_y - p1_y
                dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
                ux, uy = dx / dist, dy / dist
                # Perpendicular unit vector
                px, py = -uy, ux

                text_rect = painter.fontMetrics().boundingRect(self.measurement_text)
                margin = 10
                offset = 14  # perpendicular offset

                # Decide placement: center if enough length, else near p2 end
                if dist >= (text_rect.width() + margin * 2):
                    # Centered above the line
                    text_x = mid_x - text_rect.width() / 2 + px * 0
                    text_y = mid_y - 0
                    # move perpendicular up by offset
                    text_x += px * offset
                    text_y += py * offset
                else:
                    # Place near p2 end, offset perpendicular
                    text_x = p2_x - text_rect.width() / 2 + px * offset
                    text_y = p2_y - text_rect.height() / 2 + py * offset

                # Background for readability
                bg_rect = text_rect.adjusted(-5, -2, 5, 2)
                bg_rect.moveTopLeft(QPoint(int(text_x - 5), int(text_y - 2)))
                painter.fillRect(bg_rect, QColor(255, 255, 255, 200))

                # Draw text baseline at computed position
                painter.drawText(
                    int(text_x), int(text_y + text_rect.height()), self.measurement_text
                )

        painter.end()
        return result

    def _draw_measurements(self, pixmap):
        """Draw all persisted measurements on the pixmap."""
        if not self.measurements:
            return pixmap
        from ..settings.config import config

        result = QPixmap(pixmap)
        painter = QPainter(result)
        for idx, m in enumerate(self.measurements):
            p1_x = m["p1"][0] * self.zoom_factor
            p1_y = m["p1"][1] * self.zoom_factor
            p2_x = m["p2"][0] * self.zoom_factor
            p2_y = m["p2"][1] * self.zoom_factor

            # Line style (always draw measurements on-screen)
            pen = QPen(
                QColor(255, 0, 0), 2 if self.selected_measure_index != idx else 3
            )
            pen.setStyle(Qt.CustomDashLine)
            pen.setDashPattern([8, 3, 2, 3, 2, 3])
            painter.setPen(pen)
            painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

            # Label
            label = m.get("text", "")
            if label:
                font = painter.font()
                font.setPointSize(12)
                font.setBold(True)
                painter.setFont(font)
                text_pen = QPen(QColor(255, 0, 0), 1)
                painter.setPen(text_pen)
                mid_x = (p1_x + p2_x) / 2
                mid_y = (p1_y + p2_y) / 2
                dx, dy = (p2_x - p1_x), (p2_y - p1_y)
                dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
                ux, uy = dx / dist, dy / dist
                px, py = -uy, ux
                text_rect = painter.fontMetrics().boundingRect(label)
                margin = 10
                offset = 14
                if dist >= (text_rect.width() + margin * 2):
                    tx = mid_x + px * offset - text_rect.width() / 2
                    ty = mid_y + py * offset
                else:
                    tx = p2_x + px * offset - text_rect.width() / 2
                    ty = p2_y + py * offset - text_rect.height() / 2
                bg = text_rect.adjusted(-5, -2, 5, 2)
                bg.moveTopLeft(QPoint(int(tx - 5), int(ty - 2)))
                painter.fillRect(bg, QColor(255, 255, 255, 200))
                painter.drawText(int(tx), int(ty + text_rect.height()), label)

            # Endpoint handles (always draw; highlight if selected)
            handle_radius = 5
            if self.selected_measure_index == idx:
                painter.setBrush(QColor(255, 255, 0, 220))
                painter.setPen(QPen(QColor(0, 0, 0), 1))
            else:
                painter.setBrush(QColor(255, 255, 255, 220))
                painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawEllipse(
                int(p1_x - handle_radius),
                int(p1_y - handle_radius),
                handle_radius * 2,
                handle_radius * 2,
            )
            painter.drawEllipse(
                int(p2_x - handle_radius),
                int(p2_y - handle_radius),
                handle_radius * 2,
                handle_radius * 2,
            )

        painter.end()
        return result

    def _format_measurement_text(self, p1, p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        px_dist = (dx * dx + dy * dy) ** 0.5
        scale = float(getattr(self, "scale_factor", 1.0) or 1.0)
        if scale > 0:
            mm = px_dist * scale
            inches = mm / 25.4
            return f"{mm:.2f} mm ({inches:.3f} in)"
        return ""

    def select_measurement_at(self, x, y):
        """Select a measurement by proximity to endpoints or line. x,y in original coords."""
        if not self.measurements:
            self.selected_measure_index = None
            return False
        # Tolerance in display pixels
        tol = 12
        z = max(0.0001, self.zoom_factor)
        click = (x * z, y * z)

        def dist2(ax, ay, bx, by):
            dx = ax - bx
            dy = ay - by
            return dx * dx + dy * dy

        best_idx = None
        best_d2 = (tol * tol) + 1
        for idx, m in enumerate(self.measurements):
            p1 = (m["p1"][0] * z, m["p1"][1] * z)
            p2 = (m["p2"][0] * z, m["p2"][1] * z)
            # endpoint proximity
            d2p1 = dist2(click[0], click[1], p1[0], p1[1])
            d2p2 = dist2(click[0], click[1], p2[0], p2[1])
            d2min = min(d2p1, d2p2)
            # line distance (point to segment)
            vx, vy = (p2[0] - p1[0], p2[1] - p1[1])
            seg_len2 = max(1.0, vx * vx + vy * vy)
            t = ((click[0] - p1[0]) * vx + (click[1] - p1[1]) * vy) / seg_len2
            t = max(0.0, min(1.0, t))
            proj = (p1[0] + t * vx, p1[1] + t * vy)
            d2line = dist2(click[0], click[1], proj[0], proj[1])
            d2 = min(d2min, d2line)
            if d2 <= tol * tol and d2 < best_d2:
                best_d2 = d2
                best_idx = idx
        self.selected_measure_index = best_idx
        return best_idx is not None

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            if (
                self.selected_measure_index is not None
                and 0 <= self.selected_measure_index < len(self.measurements)
            ):
                self.measurements.pop(self.selected_measure_index)
                self.selected_measure_index = None
                self._update_display()
                try:
                    self.measurements_changed.emit()
                except Exception:
                    pass
                event.accept()
                return
        super().keyPressEvent(event)

    def _draw_tile_grid_overlay(self, pixmap):
        """Draw tile grid overlay on the document."""
        if not self.tile_grid:
            return pixmap

        # Create a copy to draw on
        result = QPixmap(pixmap)
        painter = QPainter(result)

        # Set up pen for tile boundaries
        pen = QPen(QColor(0, 150, 255), 2)  # Blue lines for tile boundaries
        painter.setPen(pen)

        # Draw each tile rectangle
        for i, (x, y, width, height) in enumerate(self.tile_grid):
            # Scale coordinates according to current zoom
            scaled_x = x * self.zoom_factor
            scaled_y = y * self.zoom_factor
            scaled_width = width * self.zoom_factor
            scaled_height = height * self.zoom_factor

            # Draw tile boundary
            painter.drawRect(
                int(scaled_x), int(scaled_y), int(scaled_width), int(scaled_height)
            )

            # Draw tile number in the center
            center_x = scaled_x + scaled_width / 2
            center_y = scaled_y + scaled_height / 2

            # Set up text pen
            text_pen = QPen(QColor(255, 255, 255), 1)
            painter.setPen(text_pen)
            painter.drawText(int(center_x - 10), int(center_y), f"{i + 1}")

            # Reset pen for next rectangle
            painter.setPen(pen)

        painter.end()
        return result

    def _draw_page_grid_overlay(self, pixmap):
        """Draw page grid overlay (gutter lines, crop/registration marks)."""
        if not self.page_grid:
            return pixmap

        # Import config here to avoid circular imports
        from ..settings.config import config

        # Calculate the canvas size needed to show all pages (including partial ones)
        max_x = max_y = 0
        for page in self.page_grid:
            page_right = (page["x"] + page["width"]) * self.zoom_factor
            page_bottom = (page["y"] + page["height"]) * self.zoom_factor
            max_x = max(max_x, page_right)
            max_y = max(max_y, page_bottom)

        # Expand canvas if needed to show all page boundaries
        canvas_width = max(pixmap.width(), int(max_x))
        canvas_height = max(pixmap.height(), int(max_y))

        # Create expanded canvas if needed
        if canvas_width > pixmap.width() or canvas_height > pixmap.height():
            result = QPixmap(canvas_width, canvas_height)
            result.fill(Qt.white)  # Fill with white background

            # Draw the original pixmap onto the expanded canvas
            canvas_painter = QPainter(result)
            canvas_painter.drawPixmap(0, 0, pixmap)
            canvas_painter.end()
        else:
            result = QPixmap(pixmap)

        painter = QPainter(result)

        # Draw each page
        for i, page in enumerate(self.page_grid):
            x = page["x"] * self.zoom_factor
            y = page["y"] * self.zoom_factor
            width = page["width"] * self.zoom_factor
            height = page["height"] * self.zoom_factor
            gutter = page["gutter"] * self.zoom_factor

            # Omit drawing the outer page boundary in the main viewer
            # (previously a red rectangle around each page).

            # Draw blue gutter lines (printable area boundary) - if enabled
            if config.get_gutter_lines_display() and gutter > 1:
                gutter_pen = QPen(QColor(0, 100, 255), 1)  # Blue lines for gutters
                painter.setPen(gutter_pen)

                # Inner rectangle for printable area
                gutter_x = x + gutter
                gutter_y = y + gutter
                gutter_width = width - (2 * gutter)
                gutter_height = height - (2 * gutter)

                if gutter_width > 0 and gutter_height > 0:
                    painter.drawRect(
                        int(gutter_x),
                        int(gutter_y),
                        int(gutter_width),
                        int(gutter_height),
                    )

            # Crop marks at printable-area corners (gutter intersections), if enabled
            if config.get_crop_marks_display() and gutter > 0:
                crop_pen = QPen(QColor(0, 0, 0), 1)
                painter.setPen(crop_pen)

                crop_length = 8  # pixels in display space (post-zoom)

                gutter_left = int(x + gutter)
                gutter_right = int(x + width - gutter)
                gutter_top = int(y + gutter)
                gutter_bottom = int(y + height - gutter)

                # Top-left
                painter.drawLine(
                    gutter_left - crop_length,
                    gutter_top,
                    gutter_left + crop_length,
                    gutter_top,
                )
                painter.drawLine(
                    gutter_left,
                    gutter_top - crop_length,
                    gutter_left,
                    gutter_top + crop_length,
                )
                # Top-right
                painter.drawLine(
                    gutter_right - crop_length,
                    gutter_top,
                    gutter_right + crop_length,
                    gutter_top,
                )
                painter.drawLine(
                    gutter_right,
                    gutter_top - crop_length,
                    gutter_right,
                    gutter_top + crop_length,
                )
                # Bottom-left
                painter.drawLine(
                    gutter_left - crop_length,
                    gutter_bottom,
                    gutter_left + crop_length,
                    gutter_bottom,
                )
                painter.drawLine(
                    gutter_left,
                    gutter_bottom - crop_length,
                    gutter_left,
                    gutter_bottom + crop_length,
                )
                # Bottom-right
                painter.drawLine(
                    gutter_right - crop_length,
                    gutter_bottom,
                    gutter_right + crop_length,
                    gutter_bottom,
                )
                painter.drawLine(
                    gutter_right,
                    gutter_bottom - crop_length,
                    gutter_right,
                    gutter_bottom + crop_length,
                )

            # Registration marks at printable-area corners (quarters), if enabled
            if config.get_reg_marks_display() and page.get("gutter", 0) > 0:
                try:
                    # Convert mm to pixels using document scale (mm/px)
                    diameter_mm = config.get_reg_mark_diameter_mm()
                    cross_mm = config.get_reg_mark_crosshair_mm()
                    scale_factor = getattr(self, "scale_factor", 1.0)
                    px_per_mm_doc = (
                        (1.0 / scale_factor)
                        if scale_factor and scale_factor > 0
                        else 2.0
                    )
                    # Scale by current zoom because we're drawing on the zoomed pixmap
                    radius_px = int(
                        (diameter_mm * px_per_mm_doc * self.zoom_factor) / 2
                    )
                    cross_len_px = int(cross_mm * px_per_mm_doc * self.zoom_factor)

                    # Clip to printable area so only quarters render per page
                    printable_rect = QRect(
                        int(x + gutter),
                        int(y + gutter),
                        int(max(0, width - 2 * gutter)),
                        int(max(0, height - 2 * gutter)),
                    )
                    painter.save()
                    painter.setClipRect(printable_rect)
                    painter.setOpacity(1.0)
                    painter.setPen(QPen(QColor(0, 0, 0), 1))

                    centers = [
                        (int(x + gutter), int(y + gutter)),
                        (int(x + width - gutter), int(y + gutter)),
                        (int(x + gutter), int(y + height - gutter)),
                        (int(x + width - gutter), int(y + height - gutter)),
                    ]

                    for cx, cy in centers:
                        painter.drawEllipse(
                            cx - radius_px, cy - radius_px, radius_px * 2, radius_px * 2
                        )
                        painter.drawLine(cx - cross_len_px, cy, cx + cross_len_px, cy)
                        painter.drawLine(cx, cy - cross_len_px, cx, cy + cross_len_px)

                    painter.restore()
                except Exception:
                    pass

            # Draw page number based on settings
            if config.get_page_indicator_display():
                # Get settings
                font_size = config.get_page_indicator_font_size()
                font_color = config.get_page_indicator_font_color()
                font_style = config.get_page_indicator_font_style()
                alpha = config.get_page_indicator_alpha()
                position = config.get_page_indicator_position()

                # Set up font
                font = QFont()
                font.setPointSize(font_size)
                if font_style == "bold":
                    font.setBold(True)
                elif font_style == "italic":
                    font.setItalic(True)
                painter.setFont(font)

                # Set up color with alpha
                color = QColor(font_color)
                color.setAlpha(alpha)
                painter.setPen(QPen(color, 1))

                # Calculate text position within printable area (inside gutters)
                text = f"P{i + 1}"
                text_rect = painter.fontMetrics().boundingRect(text)
                margin = 5

                # Define printable area (inside gutters)
                printable_x = x + gutter
                printable_y = y + gutter
                printable_width = width - (2 * gutter)
                printable_height = height - (2 * gutter)

                if position == "upper-left":
                    text_x = printable_x + margin
                    text_y = printable_y + margin + text_rect.height()
                elif position == "upper-right":
                    text_x = printable_x + printable_width - text_rect.width() - margin
                    text_y = printable_y + margin + text_rect.height()
                elif position == "bottom-left":
                    text_x = printable_x + margin
                    text_y = printable_y + printable_height - margin
                elif position == "bottom-right":
                    text_x = printable_x + printable_width - text_rect.width() - margin
                    text_y = printable_y + printable_height - margin
                else:  # center-page
                    text_x = printable_x + (printable_width - text_rect.width()) / 2
                    text_y = printable_y + (printable_height + text_rect.height()) / 2

                # Draw text with outline for visibility (if alpha is high enough)
                if alpha > 128:  # Only draw outline if text is reasonably opaque
                    outline_color = QColor(0, 0, 0)
                    outline_color.setAlpha(
                        min(255, alpha + 50)
                    )  # Slightly more opaque outline
                    painter.setPen(QPen(outline_color, 1))
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                painter.drawText(
                                    int(text_x + dx), int(text_y + dy), text
                                )

                # Draw main text with alpha
                painter.setPen(QPen(color, 1))
                painter.drawText(int(text_x), int(text_y), text)

        painter.end()
        return result

    def zoom_in(self):
        """Zoom in on the document."""
        self.zoom_factor *= 1.25
        self._update_display()

    def zoom_out(self):
        """Zoom out on the document."""
        self.zoom_factor /= 1.25
        self._update_display()

    def zoom_fit(self):
        """Fit document to window."""
        if not self.current_pixmap:
            return

        # Calculate zoom factor to fit in scroll area
        scroll_size = self.scroll_area.size()
        pixmap_size = self.current_pixmap.size()

        zoom_x = scroll_size.width() / pixmap_size.width()
        zoom_y = scroll_size.height() / pixmap_size.height()

        self.zoom_factor = min(zoom_x, zoom_y) * 0.9  # 90% to leave some margin
        self._update_display()

    def rotate_clockwise(self):
        """Rotate document 90 degrees clockwise."""
        self.rotation = (self.rotation + 90) % 360
        self._update_display()

    def rotate_counterclockwise(self):
        """Rotate document 90 degrees counterclockwise."""
        self.rotation = (self.rotation - 90) % 360
        self._update_display()

    def set_scale(self, scale_factor):
        """Set the real-world scale factor."""
        self.scale_factor = scale_factor
        self.scale_changed.emit(scale_factor)

    def set_tile_grid(self, tile_grid):
        """Set the tile grid for display overlay."""
        self.tile_grid = tile_grid
        self._update_display()

    def set_page_grid(self, page_grid, gutter_size):
        """Set the page grid with gutter information for display overlay."""
        self.page_grid = page_grid
        self.gutter_size = gutter_size
        self._update_display()

    def set_point_selection_mode(self, enabled):
        """Enable or disable point selection mode."""
        self.point_selection_mode = enabled
        if enabled:
            self.scroll_area.viewport().setCursor(QCursor(Qt.CrossCursor))
            self.image_label.setCursor(QCursor(Qt.CrossCursor))
            self.selected_points.clear()
            self.measurement_text = ""
            self.temp_cursor_pos = None
        else:
            self.scroll_area.viewport().setCursor(QCursor(Qt.OpenHandCursor))
            self.image_label.setCursor(QCursor(Qt.OpenHandCursor))
            # Clear hover state so handles disappear
            self.hover_endpoint = None
            self.temp_cursor_pos = None

    def set_measurement_text(self, text):
        """Set the measurement text to display above the scaling line."""
        self.measurement_text = text
        self._update_display()

    def refresh_display(self):
        """Refresh the display to apply any setting changes."""
        self._update_display()

    def on_image_clicked(self, pos):
        """Handle image click for point selection."""
        if not self.current_pixmap:
            return

        # Convert click position to image coordinates
        label_size = self.image_label.size()
        pixmap_size = (
            self.image_label.pixmap().size()
            if self.image_label.pixmap()
            else QSize(1, 1)
        )

        # Calculate the actual image position within the label
        x_offset = (label_size.width() - pixmap_size.width()) // 2
        y_offset = (label_size.height() - pixmap_size.height()) // 2

        # Adjust click position relative to the actual image
        image_x = pos.x() - x_offset
        image_y = pos.y() - y_offset

        # Check if click is within image bounds
        if 0 <= image_x <= pixmap_size.width() and 0 <= image_y <= pixmap_size.height():
            # Convert to original image coordinates (accounting for zoom)
            original_x = image_x / self.zoom_factor
            original_y = image_y / self.zoom_factor

            if self.point_selection_mode:
                self.point_selected.emit(original_x, original_y)
                self.selected_points.append((original_x, original_y))
                # Finalize a measurement when we have two points
                if len(self.selected_points) >= 2:
                    p1 = self.selected_points[0]
                    p2 = self.selected_points[1]
                    text = self._format_measurement_text(p1, p2)
                    self.measurements.append({"p1": p1, "p2": p2, "text": text})
                    try:
                        self.measurements_changed.emit()
                    except Exception:
                        pass
                    # Prepare for next measurement
                    self.selected_points.clear()
                    self.temp_cursor_pos = None
                # Update display
                self._update_display()
            else:
                # Selection mode off: allow selecting an existing measurement for deletion
                self.select_measurement_at(original_x, original_y)
                self._update_display()

    def eventFilter(self, obj, event):
        """Event filter to handle wheel events for zooming."""
        if obj in (self.scroll_area, self.scroll_area.viewport()):
            if event.type() == QEvent.Type.Wheel:
                # Handle mouse wheel for zooming
                delta = event.angleDelta().y()
                if delta > 0:
                    self.zoom_in()
                else:
                    self.zoom_out()
                return True
        return False

    # Removed: mis-placed QLabel handlers were erroneously added on DocumentViewer
