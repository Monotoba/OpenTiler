"""
Floating page viewer dialog for inspecting individual tiles.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QPoint, QRect
from PySide6.QtGui import QPixmap, QPainter, QCursor, QKeySequence, QShortcut

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
            "background-color: #f0f0f0; border-bottom: 1px solid #ccc;"
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

    def show_page(self, page_pixmap, page_number, page_info=None):
        """Show a specific page in the viewer."""
        self.current_page_pixmap = page_pixmap.copy()
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

        # Apply zoom
        if self.zoom_factor != 1.0:
            size = self.current_page_pixmap.size() * self.zoom_factor
            scaled = self.current_page_pixmap.scaled(
                size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        else:
            scaled = self.current_page_pixmap

        self.image_label.setPixmap(scaled)
        self.image_label.resize(scaled.size())

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

    def __init__(self, page_pixmap, page_number, page_info, parent=None):
        super().__init__(parent)
        self.page_pixmap = page_pixmap
        self.page_number = page_number
        self.page_info = page_info
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

        self.page_viewer.show_page(self.page_pixmap, self.page_number, self.page_info)
        self.page_viewer.raise_()
        self.page_viewer.activateWindow()
