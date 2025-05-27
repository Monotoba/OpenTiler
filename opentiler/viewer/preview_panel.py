"""
Preview panel for showing tiled layout preview.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QFrame, QSizePolicy, QHBoxLayout
)
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont

from ..dialogs.page_viewer_dialog import ClickablePageThumbnail
from ..utils.metadata_page import MetadataPageGenerator, create_document_info
from ..settings.config import config


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

    def update_preview(self, pixmap, page_grid=None, scale_factor=1.0, scale_info=None, document_info=None):
        """Update the preview with individual page thumbnails."""
        # Clear existing thumbnails
        self._clear_thumbnails()

        if not pixmap or not page_grid:
            self.no_pages_label.show()
            self.info_label.setText("Pages: 0")
            self.scale_label.setText("Scale: Not set")
            return

        self.no_pages_label.hide()

        # Check if metadata page should be included and its position
        include_metadata = config.get_include_metadata_page()
        metadata_position = config.get_metadata_page_position()

        page_number = 1

        # Add metadata page at the beginning if configured
        if include_metadata and metadata_position == "first":
            metadata_thumbnail = self._create_metadata_thumbnail(pixmap, page_grid, scale_factor, document_info)
            if metadata_thumbnail:
                self.thumbnail_layout.addWidget(metadata_thumbnail)
                page_number += 1

        # Generate thumbnail for each tile page
        for i, page in enumerate(page_grid):
            page_thumbnail = self._create_page_thumbnail(pixmap, page, page_number, scale_info)
            self.thumbnail_layout.addWidget(page_thumbnail)
            page_number += 1

        # Add metadata page at the end if configured
        if include_metadata and metadata_position == "last":
            metadata_thumbnail = self._create_metadata_thumbnail(pixmap, page_grid, scale_factor, document_info)
            if metadata_thumbnail:
                self.thumbnail_layout.addWidget(metadata_thumbnail)

        # Add stretch at the end
        self.thumbnail_layout.addStretch()

        # Update info
        tile_count = len(page_grid)
        total_pages = tile_count + (1 if include_metadata else 0)

        if include_metadata:
            self.info_label.setText(f"Pages: {total_pages} ({tile_count} tiles + 1 metadata)")
        else:
            self.info_label.setText(f"Pages: {tile_count}")

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

    def _create_page_thumbnail(self, source_pixmap, page, page_number, scale_info=None):
        """Create a thumbnail widget for a single page."""
        # Extract the page area from the source document
        x, y = page['x'], page['y']
        width, height = page['width'], page['height']
        gutter = page.get('gutter', 0)

        # Create a blank page pixmap with the correct page dimensions
        # This maintains the page orientation and shows empty areas
        page_pixmap = QPixmap(int(width), int(height))
        page_pixmap.fill(Qt.white)  # Fill with white background

        # Draw the document content onto the page, clipped to printable area
        painter = QPainter(page_pixmap)

        # Set clipping region to printable area (inside gutters)
        printable_rect = QRect(
            int(gutter), int(gutter),
            int(width - 2 * gutter), int(height - 2 * gutter)
        )
        painter.setClipRect(printable_rect)

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

        # Add crop marks, page info, and scale line/text based on settings
        page_pixmap = self._add_page_decorations(page_pixmap, page_number, gutter, page, scale_info)

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
            self,
            scale_info  # Scale info for page viewer
        )
        thumbnail_label.setPixmap(scaled_thumbnail)
        thumbnail_label.setAlignment(Qt.AlignCenter)
        thumbnail_label.setToolTip(f"Click to view Page {page_number} in detail")
        layout.addWidget(thumbnail_label)

        return thumbnail_widget

    def _create_metadata_thumbnail(self, source_pixmap, page_grid, scale_factor, document_info):
        """Create a thumbnail widget for the metadata page."""
        try:
            # Create metadata page generator
            metadata_generator = MetadataPageGenerator()

            # Calculate grid dimensions
            if page_grid:
                tiles_x = len(set(page['x'] for page in page_grid))
                tiles_y = len(set(page['y'] for page in page_grid))
            else:
                tiles_x = tiles_y = 0

            # Create document info for metadata page
            if document_info:
                doc_info = document_info.copy()
                doc_info.update({
                    'doc_width': source_pixmap.width(),
                    'doc_height': source_pixmap.height(),
                    'tiles_x': tiles_x,
                    'tiles_y': tiles_y,
                    'total_tiles': tiles_x * tiles_y,
                    'scale_factor': scale_factor,
                })
            else:
                doc_info = create_document_info(
                    document_name='Preview Document',
                    original_file='',
                    scale_factor=scale_factor,
                    units=config.get_default_units(),
                    doc_width=source_pixmap.width(),
                    doc_height=source_pixmap.height(),
                    tiles_x=tiles_x,
                    tiles_y=tiles_y,
                    page_size=config.get_default_page_size(),
                    gutter_size=config.get_gutter_size_mm(),
                )

            # Generate metadata page (A4 size for preview)
            metadata_pixmap = metadata_generator.generate_metadata_page(doc_info)

            # Create thumbnail widget
            thumbnail_widget = QFrame()
            thumbnail_widget.setFrameStyle(QFrame.Box)
            thumbnail_widget.setStyleSheet("border: 2px solid #0078d4; margin: 2px; background-color: #f0f8ff;")

            layout = QVBoxLayout(thumbnail_widget)
            layout.setContentsMargins(5, 5, 5, 5)

            # Metadata page label
            page_label = QLabel("Metadata Page")
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setStyleSheet("font-weight: bold; color: #0078d4;")
            layout.addWidget(page_label)

            # Clickable thumbnail image
            max_width = 150
            max_height = 200
            scaled_thumbnail = metadata_pixmap.scaled(
                max_width, max_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Create clickable thumbnail for metadata page
            thumbnail_label = ClickablePageThumbnail(
                metadata_pixmap,  # Full-size metadata page for viewer
                "Metadata",       # Page identifier
                {'type': 'metadata', 'width': metadata_pixmap.width(), 'height': metadata_pixmap.height()},  # Page info
                self,
                None  # No scale info for metadata page
            )
            thumbnail_label.setPixmap(scaled_thumbnail)
            thumbnail_label.setAlignment(Qt.AlignCenter)
            thumbnail_label.setToolTip("Click to view Metadata Page in detail")
            layout.addWidget(thumbnail_label)

            return thumbnail_widget

        except Exception as e:
            print(f"Error creating metadata thumbnail: {str(e)}")
            return None

    def _add_page_decorations(self, page_pixmap, page_number, gutter_size, page_info=None, scale_info=None):
        """Add crop marks, gutter lines, page number, and scale line/text to page thumbnail."""
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

            # Set up font - use larger size for thumbnails to ensure visibility
            font = QFont()
            thumbnail_font_size = max(8, min(font_size, 14))  # Ensure readable size for thumbnails
            font.setPointSize(thumbnail_font_size)
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

        # Draw scale line and text if this page contains the scaling points
        if scale_info and page_info:
            self._draw_scale_line_on_page(painter, scale_info, page_info, width, height)

        painter.end()
        return result

    def _draw_scale_line_on_page(self, painter, scale_info, page_info, page_width, page_height):
        """Draw scale line and text on page if it contains the scaling points."""
        # Import config here to avoid circular imports
        from ..settings.config import config

        # Only draw if scale line display is enabled
        if not config.get_scale_line_display():
            return

        # Extract scale information
        point1 = scale_info.get('point1')
        point2 = scale_info.get('point2')
        measurement_text = scale_info.get('measurement_text', '')

        if not (point1 and point2):
            return

        # Get page boundaries in document coordinates
        page_x = page_info['x']
        page_y = page_info['y']
        page_doc_width = page_info['width']
        page_doc_height = page_info['height']

        # Check if either scaling point is within this page
        p1_in_page = (page_x <= point1[0] <= page_x + page_doc_width and
                      page_y <= point1[1] <= page_y + page_doc_height)
        p2_in_page = (page_x <= point2[0] <= page_x + page_doc_width and
                      page_y <= point2[1] <= page_y + page_doc_height)

        # Check if the line crosses this page
        line_crosses_page = self._line_intersects_page(point1, point2, page_info)

        if not (p1_in_page or p2_in_page or line_crosses_page):
            return

        # Convert document coordinates to page coordinates
        p1_page_x = point1[0] - page_x
        p1_page_y = point1[1] - page_y
        p2_page_x = point2[0] - page_x
        p2_page_y = point2[1] - page_y

        # Scale to page pixmap coordinates
        scale_x = page_width / page_doc_width
        scale_y = page_height / page_doc_height

        p1_x = p1_page_x * scale_x
        p1_y = p1_page_y * scale_y
        p2_x = p2_page_x * scale_x
        p2_y = p2_page_y * scale_y

        # Set up pen for scale line
        pen = QPen(QColor(255, 0, 0), 2)  # Red color, 2px width
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)

        # Draw scale line (clipped to page boundaries)
        painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

        # Draw scale points
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        if p1_in_page:
            painter.drawEllipse(int(p1_x - 3), int(p1_y - 3), 6, 6)
        if p2_in_page:
            painter.drawEllipse(int(p2_x - 3), int(p2_y - 3), 6, 6)

        # Draw measurement text if enabled and line midpoint is in page
        if config.get_scale_text_display() and measurement_text:
            mid_x = (p1_x + p2_x) / 2
            mid_y = (p1_y + p2_y) / 2

            # Check if midpoint is within page bounds
            if 0 <= mid_x <= page_width and 0 <= mid_y <= page_height:
                # Set up font for measurement text (smaller for thumbnails)
                font = painter.font()
                font.setPointSize(8)
                font.setBold(True)
                painter.setFont(font)

                # Set up pen for red text
                text_pen = QPen(QColor(255, 0, 0), 1)
                painter.setPen(text_pen)

                # Calculate text position (above the line)
                text_rect = painter.fontMetrics().boundingRect(measurement_text)
                text_x = mid_x - text_rect.width() / 2
                text_y = mid_y - 8  # 8 pixels above the line

                # Draw background rectangle for better visibility
                bg_rect = text_rect.adjusted(-2, -1, 2, 1)
                bg_rect.moveTopLeft(QPoint(int(text_x - 2), int(text_y - text_rect.height() - 1)))
                painter.fillRect(bg_rect, QColor(255, 255, 255, 200))  # Semi-transparent white

                # Draw the measurement text
                painter.drawText(int(text_x), int(text_y), measurement_text)

    def _line_intersects_page(self, point1, point2, page_info):
        """Check if a line intersects with the page boundaries."""
        # Simple bounding box intersection check
        page_x = page_info['x']
        page_y = page_info['y']
        page_right = page_x + page_info['width']
        page_bottom = page_y + page_info['height']

        # Line bounding box
        line_left = min(point1[0], point2[0])
        line_right = max(point1[0], point2[0])
        line_top = min(point1[1], point2[1])
        line_bottom = max(point1[1], point2[1])

        # Check if bounding boxes intersect
        return not (line_right < page_x or line_left > page_right or
                   line_bottom < page_y or line_top > page_bottom)


