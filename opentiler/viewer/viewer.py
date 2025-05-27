"""
Document viewer widget for OpenTiler.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel,
    QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, Signal, QPoint
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QCursor

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

from PIL import Image
import io


class ClickableLabel(QLabel):
    """A QLabel that can handle mouse clicks for point selection."""

    clicked = Signal(QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(event.pos())
        super().mousePressEvent(event)


class DocumentViewer(QWidget):
    """Widget for viewing and interacting with documents."""

    # Signals
    document_loaded = Signal(str)  # Emitted when a document is loaded
    scale_changed = Signal(float)  # Emitted when scale changes
    point_selected = Signal(float, float)  # Emitted when a point is selected (x, y)

    def __init__(self):
        super().__init__()
        self.current_document = None
        self.current_pixmap = None
        self.zoom_factor = 1.0
        self.scale_factor = 1.0  # Real-world scale
        self.rotation = 0
        self.point_selection_mode = False
        self.selected_points = []  # Store selected points for scaling
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        # Create clickable image label
        self.image_label = ClickableLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.image_label.setText("No document loaded")
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Connect click signal
        self.image_label.clicked.connect(self.on_image_clicked)

        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

    def load_document(self, file_path):
        """Load a document from file path."""
        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Error", f"File not found: {file_path}")
            return False

        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.pdf':
                return self._load_pdf(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                return self._load_image(file_path)
            elif file_ext == '.svg':
                return self._load_svg(file_path)
            else:
                QMessageBox.critical(self, "Error", f"Unsupported file format: {file_ext}")
                return False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load document: {str(e)}")
            return False

    def _load_pdf(self, file_path):
        """Load a PDF document."""
        if not HAS_PYMUPDF:
            QMessageBox.critical(self, "Error", "PyMuPDF is required to load PDF files.")
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
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # Convert PIL image to QPixmap
            img_bytes = io.BytesIO()
            pil_image.save(img_bytes, format='PNG')
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

        # Draw selected points if in point selection mode
        if self.point_selection_mode and self.selected_points:
            scaled = self._draw_selected_points(scaled)

        self.image_label.setPixmap(scaled)

    def _draw_selected_points(self, pixmap):
        """Draw selected points on the pixmap."""
        if not self.selected_points:
            return pixmap

        # Create a copy to draw on
        result = QPixmap(pixmap)
        painter = QPainter(result)

        # Set up pen for drawing points
        pen = QPen(QColor(255, 0, 0), 3)  # Red color, 3px width
        painter.setPen(pen)

        # Draw each selected point
        for i, (x, y) in enumerate(self.selected_points):
            # Convert original coordinates to current display coordinates
            display_x = x * self.zoom_factor
            display_y = y * self.zoom_factor

            # Draw a circle at the point
            painter.drawEllipse(int(display_x - 5), int(display_y - 5), 10, 10)

            # Draw point number
            painter.drawText(int(display_x + 10), int(display_y - 10), f"P{i + 1}")

        # Draw line between points if we have two
        if len(self.selected_points) == 2:
            p1_x = self.selected_points[0][0] * self.zoom_factor
            p1_y = self.selected_points[0][1] * self.zoom_factor
            p2_x = self.selected_points[1][0] * self.zoom_factor
            p2_y = self.selected_points[1][1] * self.zoom_factor

            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

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

    def set_point_selection_mode(self, enabled):
        """Enable or disable point selection mode."""
        self.point_selection_mode = enabled
        if enabled:
            self.image_label.setCursor(QCursor(Qt.CrossCursor))
            self.selected_points.clear()
        else:
            self.image_label.setCursor(QCursor(Qt.ArrowCursor))

    def on_image_clicked(self, pos):
        """Handle image click for point selection."""
        if not self.point_selection_mode or not self.current_pixmap:
            return

        # Convert click position to image coordinates
        label_size = self.image_label.size()
        pixmap_size = self.image_label.pixmap().size() if self.image_label.pixmap() else QSize(1, 1)

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

            self.point_selected.emit(original_x, original_y)
            self.selected_points.append((original_x, original_y))

            # Update display to show selected points
            self._update_display()
