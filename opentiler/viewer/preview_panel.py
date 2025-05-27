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
        pen = QPen(QColor(255, 0, 0), 2)  # Red lines for tile boundaries
        painter.setPen(pen)
        
        # Draw tile boundaries (simplified for preview)
        # This is a placeholder - actual implementation would depend on tile_grid structure
        width = result.width()
        height = result.height()
        
        # Draw some example grid lines
        for i in range(1, 4):  # Draw 3 vertical lines
            x = (width * i) // 4
            painter.drawLine(x, 0, x, height)
            
        for i in range(1, 3):  # Draw 2 horizontal lines
            y = (height * i) // 3
            painter.drawLine(0, y, width, y)
            
        painter.end()
        return result
