"""
Floating page viewer dialog for inspecting individual tiles.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPixmap, QPainter, QCursor, QKeySequence, QShortcut, QPen, QColor, QFont

from ..viewer.viewer import PanScrollArea


class PageViewerDialog(QDialog):
    """Dialog for viewing individual page tiles with pan and zoom."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page_pixmap = None
        self.zoom_factor = 1.0
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Page Viewer")
        self.setModal(False)  # Allow interaction with main window
        self.resize(800, 600)

        layout = QVBoxLayout()

        # Title bar with page info
        self.title_label = QLabel("Page Viewer")
        self.title_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; padding: 5px; "
            "background-color: #e8e8e8; color: #333; border-bottom: 1px solid #ccc;"
        )
        layout.addWidget(self.title_label)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        # Zoom controls
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar_layout.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar_layout.addWidget(zoom_out_btn)

        zoom_fit_btn = QPushButton("Fit to Window")
        zoom_fit_btn.clicked.connect(self.zoom_fit)
        toolbar_layout.addWidget(zoom_fit_btn)

        zoom_100_btn = QPushButton("100%")
        zoom_100_btn.clicked.connect(self.zoom_100)
        toolbar_layout.addWidget(zoom_100_btn)

        toolbar_layout.addStretch()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        toolbar_layout.addWidget(close_btn)

        toolbar_widget = QFrame()
        toolbar_widget.setLayout(toolbar_layout)
        toolbar_widget.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                padding: 5px;
                border-bottom: 1px solid #555;
            }
            QPushButton {
                background-color: #404040;
                color: white;
                border: 1px solid #555;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #777;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        layout.addWidget(toolbar_widget)

        # Create custom scroll area with panning support
        self.scroll_area = PanScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignCenter)

        # Enable mouse wheel zoom
        self.scroll_area.wheelEvent = self.wheel_event

        # Create image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.image_label.setText("No page loaded")
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

        # Add keyboard shortcuts
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.close)

        # Zoom shortcuts
        zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        zoom_in_shortcut.activated.connect(self.zoom_in)

        zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out_shortcut.activated.connect(self.zoom_out)

        zoom_fit_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        zoom_fit_shortcut.activated.connect(self.zoom_fit)

        zoom_100_shortcut = QShortcut(QKeySequence("Ctrl+1"), self)
        zoom_100_shortcut.activated.connect(self.zoom_100)

    def show_page(self, page_pixmap, page_number, page_info=None, scale_info=None):
        """Show a specific page in the viewer."""
        self.current_page_pixmap = page_pixmap.copy()
        self.page_info = page_info
        self.scale_info = scale_info
        self.zoom_factor = 1.0

        # Update title
        title = f"Page {page_number}"
        if page_info:
            title += f" - {page_info.get('width', 0):.0f}x{page_info.get('height', 0):.0f} pixels"
        self.title_label.setText(title)

        self._update_display()
        self.show()

    def _update_display(self):
        """Update the display with current zoom."""
        if not self.current_page_pixmap:
            return

        # Add scale line/text overlay if available
        display_pixmap = self._add_scale_overlay(self.current_page_pixmap)

        # Apply zoom
        if self.zoom_factor != 1.0:
            size = display_pixmap.size() * self.zoom_factor
            scaled = display_pixmap.scaled(
                size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        else:
            scaled = display_pixmap

        self.image_label.setPixmap(scaled)
        self.image_label.resize(scaled.size())

    def _add_scale_overlay(self, pixmap):
        """Add scale line and text overlay to the pixmap."""
        if not (self.scale_info and self.page_info):
            return pixmap

        # Import config here to avoid circular imports
        from ..settings.config import config

        # Only draw if scale line display is enabled
        if not config.get_scale_line_display():
            return pixmap

        # Extract scale information
        point1 = self.scale_info.get('point1')
        point2 = self.scale_info.get('point2')
        measurement_text = self.scale_info.get('measurement_text', '')

        if not (point1 and point2):
            return pixmap

        # Get page boundaries in document coordinates
        page_x = self.page_info['x']
        page_y = self.page_info['y']
        page_doc_width = self.page_info['width']
        page_doc_height = self.page_info['height']

        # Check if either scaling point is within this page
        p1_in_page = (page_x <= point1[0] <= page_x + page_doc_width and
                      page_y <= point1[1] <= page_y + page_doc_height)
        p2_in_page = (page_x <= point2[0] <= page_x + page_doc_width and
                      page_y <= point2[1] <= page_y + page_doc_height)

        # Check if the line crosses this page (simple bounding box check)
        line_left = min(point1[0], point2[0])
        line_right = max(point1[0], point2[0])
        line_top = min(point1[1], point2[1])
        line_bottom = max(point1[1], point2[1])

        page_right = page_x + page_doc_width
        page_bottom = page_y + page_doc_height

        line_crosses_page = not (line_right < page_x or line_left > page_right or
                               line_bottom < page_y or line_top > page_bottom)

        if not (p1_in_page or p2_in_page or line_crosses_page):
            return pixmap

        # Create a copy to draw on
        result = QPixmap(pixmap)
        painter = QPainter(result)

        # Convert document coordinates to page coordinates
        p1_page_x = point1[0] - page_x
        p1_page_y = point1[1] - page_y
        p2_page_x = point2[0] - page_x
        p2_page_y = point2[1] - page_y

        # Scale to page pixmap coordinates
        scale_x = pixmap.width() / page_doc_width
        scale_y = pixmap.height() / page_doc_height

        p1_x = p1_page_x * scale_x
        p1_y = p1_page_y * scale_y
        p2_x = p2_page_x * scale_x
        p2_y = p2_page_y * scale_y

        # Set up pen for scale line
        pen = QPen(QColor(255, 0, 0), 3)  # Red color, 3px width for page viewer
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)

        # Draw scale line
        painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

        # Draw scale points
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        if p1_in_page:
            painter.drawEllipse(int(p1_x - 5), int(p1_y - 5), 10, 10)
        if p2_in_page:
            painter.drawEllipse(int(p2_x - 5), int(p2_y - 5), 10, 10)

        # Draw measurement text if enabled and line midpoint is in page
        if config.get_scale_text_display() and measurement_text:
            mid_x = (p1_x + p2_x) / 2
            mid_y = (p1_y + p2_y) / 2

            # Check if midpoint is within page bounds
            if 0 <= mid_x <= pixmap.width() and 0 <= mid_y <= pixmap.height():
                # Set up font for measurement text (larger for page viewer)
                font = painter.font()
                font.setPointSize(14)
                font.setBold(True)
                painter.setFont(font)

                # Set up pen for red text
                text_pen = QPen(QColor(255, 0, 0), 1)
                painter.setPen(text_pen)

                # Calculate text position (above the line)
                text_rect = painter.fontMetrics().boundingRect(measurement_text)
                text_x = mid_x - text_rect.width() / 2
                text_y = mid_y - 15  # 15 pixels above the line

                # Draw background rectangle for better visibility
                bg_rect = text_rect.adjusted(-5, -2, 5, 2)
                bg_rect.moveTopLeft(QPoint(int(text_x - 5), int(text_y - text_rect.height() - 2)))
                painter.fillRect(bg_rect, QColor(255, 255, 255, 200))  # Semi-transparent white

                # Draw the measurement text
                painter.drawText(int(text_x), int(text_y), measurement_text)

        painter.end()
        return result

    def zoom_in(self):
        """Zoom in on the page."""
        self.zoom_factor *= 1.25
        self._update_display()

    def zoom_out(self):
        """Zoom out on the page."""
        self.zoom_factor /= 1.25
        self._update_display()

    def zoom_fit(self):
        """Fit page to window."""
        if not self.current_page_pixmap:
            return

        # Calculate zoom factor to fit in scroll area
        scroll_size = self.scroll_area.size()
        pixmap_size = self.current_page_pixmap.size()

        # Account for scroll bars and margins
        available_width = scroll_size.width() - 50
        available_height = scroll_size.height() - 50

        zoom_x = available_width / pixmap_size.width()
        zoom_y = available_height / pixmap_size.height()

        self.zoom_factor = min(zoom_x, zoom_y, 1.0)  # Don't zoom in beyond 100%
        self._update_display()

    def zoom_100(self):
        """Set zoom to 100%."""
        self.zoom_factor = 1.0
        self._update_display()

    def wheel_event(self, event):
        """Handle mouse wheel events for zooming."""
        # Always zoom with wheel (no Ctrl needed since panning handles navigation)
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        event.accept()


class ClickablePageThumbnail(QLabel):
    """A clickable page thumbnail that opens in the page viewer."""

    def __init__(self, page_pixmap, page_number, page_info, parent=None, scale_info=None):
        super().__init__(parent)
        self.page_pixmap = page_pixmap
        self.page_number = page_number
        self.page_info = page_info
        self.scale_info = scale_info
        self.page_viewer = None

        # Set up the thumbnail
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            "border: 2px solid #ddd; border-radius: 5px; padding: 2px; "
            "background-color: white;"
        )
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # Add hover effect
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """Handle mouse click to open page viewer."""
        if event.button() == Qt.LeftButton:
            self.open_page_viewer()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        self.setStyleSheet(
            "border: 2px solid #0078d4; border-radius: 5px; padding: 2px; "
            "background-color: #f0f8ff;"
        )
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave to remove hover effect."""
        self.setStyleSheet(
            "border: 2px solid #ddd; border-radius: 5px; padding: 2px; "
            "background-color: white;"
        )
        super().leaveEvent(event)

    def open_page_viewer(self):
        """Open the page in a floating viewer window."""
        if not self.page_viewer:
            self.page_viewer = PageViewerDialog(self.parent())

        self.page_viewer.show_page(self.page_pixmap, self.page_number, self.page_info, self.scale_info)
        self.page_viewer.raise_()
        self.page_viewer.activateWindow()
