"""
Preview panel for showing tiled layout preview.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor


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
        title_label = QLabel("Tile Preview")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Preview area
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setMinimumHeight(200)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setText("No document loaded")
        self.preview_label.setStyleSheet("border: 1px solid lightgray; background-color: white;")
        self.preview_label.setMinimumSize(200, 150)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.preview_scroll.setWidget(self.preview_label)
        layout.addWidget(self.preview_scroll)

        # Info labels
        self.info_label = QLabel("Tiles: 0")
        layout.addWidget(self.info_label)

        self.scale_label = QLabel("Scale: Not set")
        layout.addWidget(self.scale_label)

        layout.addStretch()
        self.setLayout(layout)

    def update_preview(self, pixmap, tile_grid=None, scale_factor=1.0):
        """Update the preview with current document and tiling."""
        if not pixmap:
            self.preview_label.setText("No document loaded")
            self.info_label.setText("Tiles: 0")
            self.scale_label.setText("Scale: Not set")
            return

        # Create a scaled down version for preview
        preview_size = self.preview_label.size()
        scaled_pixmap = pixmap.scaled(
            preview_size * 0.8,  # 80% of available space
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Draw tile grid if provided
        if tile_grid:
            scaled_pixmap = self._draw_tile_grid(scaled_pixmap, tile_grid)

        self.preview_label.setPixmap(scaled_pixmap)

        # Update info
        tile_count = len(tile_grid) if tile_grid else 0
        self.info_label.setText(f"Tiles: {tile_count}")

        if scale_factor != 1.0:
            self.scale_label.setText(f"Scale: {scale_factor:.3f}")
        else:
            self.scale_label.setText("Scale: Not set")

    def _draw_tile_grid(self, pixmap, tile_grid):
        """Draw tile grid overlay on pixmap."""
        if not tile_grid:
            return pixmap

        # Create a copy to draw on
        result = QPixmap(pixmap)
        painter = QPainter(result)

        # Set up pen for grid lines
        pen = QPen(QColor(255, 0, 0), 1)  # Red lines for page boundaries
        painter.setPen(pen)

        # Calculate scale factor for preview
        preview_width = result.width()
        preview_height = result.height()

        # Handle both old format (tuples) and new format (dictionaries)
        if tile_grid:
            # Check if it's the new page grid format (dictionaries)
            if isinstance(tile_grid[0], dict):
                # New page grid format
                max_x = max(page['x'] + page['width'] for page in tile_grid)
                max_y = max(page['y'] + page['height'] for page in tile_grid)

                scale_x = preview_width / max_x if max_x > 0 else 1
                scale_y = preview_height / max_y if max_y > 0 else 1

                # Draw each page rectangle
                for i, page in enumerate(tile_grid):
                    x, y = page['x'], page['y']
                    width, height = page['width'], page['height']
                    gutter = page.get('gutter', 0)

                    # Scale to preview coordinates
                    preview_x = x * scale_x
                    preview_y = y * scale_y
                    preview_w = width * scale_x
                    preview_h = height * scale_y
                    preview_gutter = gutter * scale_x

                    # Draw red page boundary
                    painter.setPen(QPen(QColor(255, 0, 0), 1))
                    painter.drawRect(int(preview_x), int(preview_y), int(preview_w), int(preview_h))

                    # Draw blue gutter lines
                    if preview_gutter > 1:  # Only if gutter is visible
                        painter.setPen(QPen(QColor(0, 100, 255), 1))
                        gutter_x = preview_x + preview_gutter
                        gutter_y = preview_y + preview_gutter
                        gutter_w = preview_w - (2 * preview_gutter)
                        gutter_h = preview_h - (2 * preview_gutter)
                        if gutter_w > 0 and gutter_h > 0:
                            painter.drawRect(int(gutter_x), int(gutter_y), int(gutter_w), int(gutter_h))

                    # Draw page number
                    if preview_w > 15 and preview_h > 15:
                        painter.setPen(QPen(QColor(0, 0, 0), 1))
                        center_x = preview_x + preview_w / 2
                        center_y = preview_y + preview_h / 2
                        painter.drawText(int(center_x - 5), int(center_y), f"P{i + 1}")

            else:
                # Old tile grid format (tuples)
                max_x = max(x + w for x, y, w, h in tile_grid)
                max_y = max(y + h for x, y, w, h in tile_grid)

                scale_x = preview_width / max_x if max_x > 0 else 1
                scale_y = preview_height / max_y if max_y > 0 else 1

                # Draw each tile rectangle
                for i, (x, y, width, height) in enumerate(tile_grid):
                    # Scale to preview coordinates
                    preview_x = x * scale_x
                    preview_y = y * scale_y
                    preview_w = width * scale_x
                    preview_h = height * scale_y

                    # Draw tile boundary
                    painter.drawRect(int(preview_x), int(preview_y), int(preview_w), int(preview_h))

                    # Draw tile number (smaller for preview)
                    if preview_w > 20 and preview_h > 20:  # Only if tile is large enough
                        center_x = preview_x + preview_w / 2
                        center_y = preview_y + preview_h / 2
                        painter.drawText(int(center_x - 5), int(center_y), f"{i + 1}")

        painter.end()
        return result
