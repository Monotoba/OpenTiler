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
        pen = QPen(QColor(255, 0, 0), 1)  # Red lines for tile boundaries
        painter.setPen(pen)

        # Calculate scale factor for preview
        preview_width = result.width()
        preview_height = result.height()

        # Assume tile_grid contains (x, y, width, height) tuples in original image coordinates
        # We need to scale these to the preview size
        if tile_grid:
            # Get original image dimensions from first tile calculation
            # For now, estimate from the tile grid bounds
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
