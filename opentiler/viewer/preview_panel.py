"""
Preview panel for showing tiled layout preview.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QFrame, QSizePolicy, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont


class PreviewPanel(QWidget):
    """Panel for showing real-time tile preview."""

    def __init__(self):
        super().__init__()
        self.tile_count = 0
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("Page Thumbnails")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Scrollable area for page thumbnails
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setMinimumHeight(200)
        self.preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container widget for thumbnails
        self.thumbnail_container = QWidget()
        self.thumbnail_layout = QVBoxLayout(self.thumbnail_container)
        self.thumbnail_layout.setSpacing(10)
        self.thumbnail_layout.setContentsMargins(5, 5, 5, 5)

        # Default message
        self.no_pages_label = QLabel("No pages generated")
        self.no_pages_label.setAlignment(Qt.AlignCenter)
        self.no_pages_label.setStyleSheet("color: gray; font-style: italic;")
        self.thumbnail_layout.addWidget(self.no_pages_label)

        self.preview_scroll.setWidget(self.thumbnail_container)
        layout.addWidget(self.preview_scroll)

        # Info labels
        self.info_label = QLabel("Pages: 0")
        layout.addWidget(self.info_label)

        self.scale_label = QLabel("Scale: Not set")
        layout.addWidget(self.scale_label)

        layout.addStretch()
        self.setLayout(layout)

    def update_preview(self, pixmap, page_grid=None, scale_factor=1.0):
        """Update the preview with individual page thumbnails."""
        # Clear existing thumbnails
        self._clear_thumbnails()

        if not pixmap or not page_grid:
            self.no_pages_label.show()
            self.info_label.setText("Pages: 0")
            self.scale_label.setText("Scale: Not set")
            return

        self.no_pages_label.hide()

        # Generate thumbnail for each page
        for i, page in enumerate(page_grid):
            page_thumbnail = self._create_page_thumbnail(pixmap, page, i + 1)
            self.thumbnail_layout.addWidget(page_thumbnail)

        # Add stretch at the end
        self.thumbnail_layout.addStretch()

        # Update info
        page_count = len(page_grid)
        self.info_label.setText(f"Pages: {page_count}")

        if scale_factor != 1.0:
            self.scale_label.setText(f"Scale: {scale_factor:.6f} mm/px")
        else:
            self.scale_label.setText("Scale: Not set")

    def _clear_thumbnails(self):
        """Clear all existing thumbnail widgets."""
        # Remove all widgets except the no_pages_label
        while self.thumbnail_layout.count() > 0:
            child = self.thumbnail_layout.takeAt(0)
            if child.widget() and child.widget() != self.no_pages_label:
                child.widget().deleteLater()

    def _create_page_thumbnail(self, source_pixmap, page, page_number):
        """Create a thumbnail widget for a single page."""
        # Extract the page area from the source document
        x, y = page['x'], page['y']
        width, height = page['width'], page['height']
        gutter = page.get('gutter', 0)

        # Create page pixmap by cropping from source
        page_pixmap = source_pixmap.copy(int(x), int(y), int(width), int(height))

        # Add crop marks and page info
        page_pixmap = self._add_page_decorations(page_pixmap, page_number, gutter)

        # Create thumbnail widget
        thumbnail_widget = QFrame()
        thumbnail_widget.setFrameStyle(QFrame.Box)
        thumbnail_widget.setStyleSheet("border: 1px solid lightgray; margin: 2px;")

        layout = QVBoxLayout(thumbnail_widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Page number label
        page_label = QLabel(f"Page {page_number}")
        page_label.setAlignment(Qt.AlignCenter)
        page_label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(page_label)

        # Thumbnail image
        thumbnail_label = QLabel()
        thumbnail_label.setAlignment(Qt.AlignCenter)

        # Scale thumbnail to fit preview area (max 150px wide)
        max_width = 150
        scaled_thumbnail = page_pixmap.scaled(
            max_width, max_width,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        thumbnail_label.setPixmap(scaled_thumbnail)
        layout.addWidget(thumbnail_label)

        return thumbnail_widget

    def _add_page_decorations(self, page_pixmap, page_number, gutter_size):
        """Add crop marks, gutter lines, and page number to page thumbnail."""
        # Create a copy to draw on
        result = QPixmap(page_pixmap)
        painter = QPainter(result)

        width = result.width()
        height = result.height()

        # Draw gutter lines (blue) - printable area boundary
        if gutter_size > 1:  # Only if gutter is visible
            gutter_pen = QPen(QColor(0, 100, 255), 2)  # Blue for gutter
            painter.setPen(gutter_pen)

            # Draw gutter rectangle
            painter.drawRect(
                int(gutter_size), int(gutter_size),
                int(width - 2 * gutter_size), int(height - 2 * gutter_size)
            )

        # Draw crop marks (black) - page boundary indicators
        crop_pen = QPen(QColor(0, 0, 0), 1)  # Black for crop marks
        painter.setPen(crop_pen)

        crop_length = 10
        margin = 5

        # Corner crop marks
        # Top-left
        painter.drawLine(0, margin, crop_length, margin)
        painter.drawLine(margin, 0, margin, crop_length)

        # Top-right
        painter.drawLine(width - crop_length, margin, width, margin)
        painter.drawLine(width - margin, 0, width - margin, crop_length)

        # Bottom-left
        painter.drawLine(0, height - margin, crop_length, height - margin)
        painter.drawLine(margin, height - crop_length, margin, height)

        # Bottom-right
        painter.drawLine(width - crop_length, height - margin, width, height - margin)
        painter.drawLine(width - margin, height - crop_length, width - margin, height)

        # Draw page number in corner
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)

        text_pen = QPen(QColor(255, 255, 255), 1)  # White text
        painter.setPen(text_pen)

        # Draw text with black outline for visibility
        text_rect = painter.fontMetrics().boundingRect(f"P{page_number}")
        text_x = width - text_rect.width() - 10
        text_y = height - 10

        # Black outline
        outline_pen = QPen(QColor(0, 0, 0), 1)
        painter.setPen(outline_pen)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    painter.drawText(text_x + dx, text_y + dy, f"P{page_number}")

        # White text
        painter.setPen(text_pen)
        painter.drawText(text_x, text_y, f"P{page_number}")

        painter.end()
        return result


