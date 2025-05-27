"""
Document viewer widget for OpenTiler.
"""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel,
    QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QSize, Signal, QPoint, QEvent
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QCursor, QFont

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

from PIL import Image
import io


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

    def set_parent_viewer(self, viewer):
        """Set reference to parent viewer for panning."""
        self.parent_viewer = viewer

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            # Point selection mode
            if self.parent_viewer and self.parent_viewer.point_selection_mode:
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
        self.tile_grid = []  # Store tile grid for display
        self.page_grid = []  # Store page grid for display
        self.gutter_size = 0  # Gutter size in pixels
        self.measurement_text = ""  # Store measurement text for display
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Create custom scroll area with panning support
        self.scroll_area = PanScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Don't resize widget to fit - allow scrolling
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

            # Draw measurement text above the line if available
            if self.measurement_text:
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

                # Calculate text position (above the line)
                text_rect = painter.fontMetrics().boundingRect(self.measurement_text)
                text_x = mid_x - text_rect.width() / 2
                text_y = mid_y - 15  # 15 pixels above the line

                # Draw background rectangle for better visibility
                bg_rect = text_rect.adjusted(-5, -2, 5, 2)
                bg_rect.moveTopLeft(QPoint(int(text_x - 5), int(text_y - text_rect.height() - 2)))
                painter.fillRect(bg_rect, QColor(255, 255, 255, 200))  # Semi-transparent white

                # Draw the measurement text
                painter.drawText(int(text_x), int(text_y), self.measurement_text)

        painter.end()
        return result

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
            painter.drawRect(int(scaled_x), int(scaled_y), int(scaled_width), int(scaled_height))

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
        """Draw page grid overlay with red page boundaries and blue gutter lines."""
        if not self.page_grid:
            return pixmap

        # Import config here to avoid circular imports
        from ..settings.config import config

        # Calculate the canvas size needed to show all pages (including partial ones)
        max_x = max_y = 0
        for page in self.page_grid:
            page_right = (page['x'] + page['width']) * self.zoom_factor
            page_bottom = (page['y'] + page['height']) * self.zoom_factor
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
            x = page['x'] * self.zoom_factor
            y = page['y'] * self.zoom_factor
            width = page['width'] * self.zoom_factor
            height = page['height'] * self.zoom_factor
            gutter = page['gutter'] * self.zoom_factor

            # Draw red page boundary (actual paper edge) - always shown
            page_pen = QPen(QColor(255, 0, 0), 2)  # Red lines for page edges
            painter.setPen(page_pen)
            painter.drawRect(int(x), int(y), int(width), int(height))

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
                    painter.drawRect(int(gutter_x), int(gutter_y), int(gutter_width), int(gutter_height))

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
                    outline_color.setAlpha(min(255, alpha + 50))  # Slightly more opaque outline
                    painter.setPen(QPen(outline_color, 1))
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                painter.drawText(int(text_x + dx), int(text_y + dy), text)

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
        else:
            self.scroll_area.viewport().setCursor(QCursor(Qt.OpenHandCursor))
            self.image_label.setCursor(QCursor(Qt.OpenHandCursor))

    def set_measurement_text(self, text):
        """Set the measurement text to display above the scaling line."""
        self.measurement_text = text
        self._update_display()

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

        return super().eventFilter(obj, event)
