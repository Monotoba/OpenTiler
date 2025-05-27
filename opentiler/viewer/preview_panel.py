"""
Preview panel for showing tiled layout preview.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QFrame, QSizePolicy, QHBoxLayout
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont

from ..dialogs.page_viewer_dialog import ClickablePageThumbnail


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

        # Create a blank page pixmap with the correct page dimensions
        # This maintains the page orientation and shows empty areas
        page_pixmap = QPixmap(int(width), int(height))
        page_pixmap.fill(Qt.white)  # Fill with white background

        # Draw the document content onto the page
        painter = QPainter(page_pixmap)

        # Calculate the area of the source that overlaps with this page
        source_rect = source_pixmap.rect()
        page_rect = QRect(int(x), int(y), int(width), int(height))

        # Find intersection
        intersection = source_rect.intersected(page_rect)

        if not intersection.isEmpty():
            # Copy the intersecting area from source to page
            source_crop = source_pixmap.copy(intersection)

            # Calculate where to place it on the page
            dest_x = intersection.x() - x
            dest_y = intersection.y() - y

            painter.drawPixmap(int(dest_x), int(dest_y), source_crop)

        painter.end()

        # Add crop marks and page info based on settings
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

        # Clickable thumbnail image
        # Scale thumbnail to fit preview area while maintaining aspect ratio
        max_width = 150
        max_height = 200
        scaled_thumbnail = page_pixmap.scaled(
            max_width, max_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Create clickable thumbnail that opens in floating viewer
        thumbnail_label = ClickablePageThumbnail(
            page_pixmap,  # Full-size page for viewer
            page_number,
            page,  # Page info dict
            self
        )
        thumbnail_label.setPixmap(scaled_thumbnail)
        thumbnail_label.setAlignment(Qt.AlignCenter)
        thumbnail_label.setToolTip(f"Click to view Page {page_number} in detail")
        layout.addWidget(thumbnail_label)

        return thumbnail_widget

    def _add_page_decorations(self, page_pixmap, page_number, gutter_size):
        """Add crop marks, gutter lines, and page number to page thumbnail."""
        # Import config here to avoid circular imports
        from ..settings.config import config

        # Create a copy to draw on
        result = QPixmap(page_pixmap)
        painter = QPainter(result)

        width = result.width()
        height = result.height()

        # Draw gutter lines (blue) - printable area boundary
        if gutter_size > 1 and config.get_gutter_lines_display():  # Only if gutter is visible and enabled
            gutter_pen = QPen(QColor(0, 100, 255), 2)  # Blue for gutter
            painter.setPen(gutter_pen)

            # Draw gutter rectangle
            painter.drawRect(
                int(gutter_size), int(gutter_size),
                int(width - 2 * gutter_size), int(height - 2 * gutter_size)
            )

        # Draw crop marks at gutter intersections (not page corners)
        if config.get_crop_marks_display():
            crop_pen = QPen(QColor(0, 0, 0), 1)  # Black for crop marks
            painter.setPen(crop_pen)

            crop_length = 8

            # Crop marks at gutter line intersections
            gutter_left = int(gutter_size)
            gutter_right = int(width - gutter_size)
            gutter_top = int(gutter_size)
            gutter_bottom = int(height - gutter_size)

            # Top-left gutter corner
            painter.drawLine(gutter_left - crop_length, gutter_top, gutter_left + crop_length, gutter_top)
            painter.drawLine(gutter_left, gutter_top - crop_length, gutter_left, gutter_top + crop_length)

            # Top-right gutter corner
            painter.drawLine(gutter_right - crop_length, gutter_top, gutter_right + crop_length, gutter_top)
            painter.drawLine(gutter_right, gutter_top - crop_length, gutter_right, gutter_top + crop_length)

            # Bottom-left gutter corner
            painter.drawLine(gutter_left - crop_length, gutter_bottom, gutter_left + crop_length, gutter_bottom)
            painter.drawLine(gutter_left, gutter_bottom - crop_length, gutter_left, gutter_bottom + crop_length)

            # Bottom-right gutter corner
            painter.drawLine(gutter_right - crop_length, gutter_bottom, gutter_right + crop_length, gutter_bottom)
            painter.drawLine(gutter_right, gutter_bottom - crop_length, gutter_right, gutter_bottom + crop_length)

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
            font.setPointSize(max(6, font_size // 2))  # Scale down for thumbnail
            if font_style == "bold":
                font.setBold(True)
            elif font_style == "italic":
                font.setItalic(True)
            painter.setFont(font)

            # Set up color with alpha
            color = QColor(font_color)
            color.setAlpha(alpha)
            text_pen = QPen(color, 1)

            # Calculate text position within printable area (inside gutters)
            text = f"P{page_number}"
            text_rect = painter.fontMetrics().boundingRect(text)
            margin = 3  # Smaller margin for thumbnails

            # Define printable area (inside gutters)
            printable_x = gutter_size
            printable_y = gutter_size
            printable_width = width - (2 * gutter_size)
            printable_height = height - (2 * gutter_size)

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
                text_x = printable_x + (printable_width - text_rect.width()) // 2
                text_y = printable_y + (printable_height + text_rect.height()) // 2

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


