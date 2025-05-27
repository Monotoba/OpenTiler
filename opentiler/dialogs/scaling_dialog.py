"""
Scaling dialog for OpenTiler.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDoubleValidator


class ScalingDialog(QDialog):
    """Dialog for setting document scale based on two points."""

    # Signals
    scale_applied = Signal(float)  # Emitted when scale is applied

    def __init__(self, parent=None):
        super().__init__(parent)
        self.point1 = None
        self.point2 = None
        self.point_count = 0
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Scaling Tool")
        self.setModal(False)  # Allow interaction with main window
        self.resize(400, 300)

        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "1. Click two points on the document\n"
            "2. Enter the real-world distance between them\n"
            "3. Click Apply to set the scale"
        )
        instructions.setStyleSheet(
            "background-color: #e8f4fd; "
            "color: #2c3e50; "
            "padding: 12px; "
            "border: 2px solid #3498db; "
            "border-radius: 5px; "
            "font-weight: bold; "
            "font-size: 11px;"
        )
        layout.addWidget(instructions)

        # Point coordinates group
        coords_group = QGroupBox("Point Coordinates")
        coords_layout = QFormLayout()

        self.point1_label = QLabel("Not selected")
        coords_layout.addRow("Point 1 (x, y):", self.point1_label)

        self.point2_label = QLabel("Not selected")
        coords_layout.addRow("Point 2 (x, y):", self.point2_label)

        self.distance_label = QLabel("0.0 pixels")
        coords_layout.addRow("Pixel Distance:", self.distance_label)

        coords_group.setLayout(coords_layout)
        layout.addWidget(coords_group)

        # Real-world distance group
        distance_group = QGroupBox("Real-World Distance")
        distance_layout = QFormLayout()

        # Distance input
        distance_input_layout = QHBoxLayout()
        self.distance_input = QLineEdit()
        self.distance_input.setValidator(QDoubleValidator(0.001, 999999.999, 3))
        self.distance_input.textChanged.connect(self.update_scale_preview)
        distance_input_layout.addWidget(self.distance_input)

        # Units combo
        self.units_combo = QComboBox()
        self.units_combo.addItems(["mm", "inches"])
        self.units_combo.currentTextChanged.connect(self.update_scale_preview)
        distance_input_layout.addWidget(self.units_combo)

        distance_layout.addRow("Distance:", distance_input_layout)

        # Scale preview
        self.scale_preview_label = QLabel("Scale: Not calculated")
        self.scale_preview_label.setStyleSheet("font-weight: bold;")
        distance_layout.addRow("Calculated Scale:", self.scale_preview_label)

        distance_group.setLayout(distance_layout)
        layout.addWidget(distance_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.clear_button = QPushButton("Clear Points")
        self.clear_button.clicked.connect(self.clear_points)
        button_layout.addWidget(self.clear_button)

        button_layout.addStretch()

        self.apply_button = QPushButton("Apply Scale")
        self.apply_button.clicked.connect(self.apply_scale)
        self.apply_button.setEnabled(False)
        button_layout.addWidget(self.apply_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def set_point1(self, x, y):
        """Set the first point coordinates."""
        self.point1 = (x, y)
        self.point1_label.setText(f"({x:.1f}, {y:.1f})")
        self.update_distance()

    def set_point2(self, x, y):
        """Set the second point coordinates."""
        self.point2 = (x, y)
        self.point2_label.setText(f"({x:.1f}, {y:.1f})")
        self.update_distance()

    def update_distance(self):
        """Update the pixel distance between points."""
        if self.point1 and self.point2:
            dx = self.point2[0] - self.point1[0]
            dy = self.point2[1] - self.point1[1]
            distance = (dx**2 + dy**2)**0.5
            self.distance_label.setText(f"{distance:.1f} pixels")
            self.update_scale_preview()
        else:
            self.distance_label.setText("0.0 pixels")

    def update_scale_preview(self):
        """Update the scale preview calculation."""
        if not (self.point1 and self.point2 and self.distance_input.text()):
            self.scale_preview_label.setText("Scale: Not calculated")
            self.apply_button.setEnabled(False)
            return

        try:
            # Calculate pixel distance
            dx = self.point2[0] - self.point1[0]
            dy = self.point2[1] - self.point1[1]
            pixel_distance = (dx**2 + dy**2)**0.5

            # Get real-world distance
            real_distance = float(self.distance_input.text())

            if pixel_distance > 0 and real_distance > 0:
                # Calculate scale (real-world units per pixel)
                scale = real_distance / pixel_distance
                units = self.units_combo.currentText()

                # Format scale display
                if scale >= 1.0:
                    scale_text = f"{scale:.3f} {units}/pixel"
                else:
                    ratio = 1.0 / scale
                    scale_text = f"1:{ratio:.1f} (pixel = {scale:.3f} {units})"

                self.scale_preview_label.setText(f"Scale: {scale_text}")
                self.apply_button.setEnabled(True)
            else:
                self.scale_preview_label.setText("Scale: Invalid values")
                self.apply_button.setEnabled(False)

        except ValueError:
            self.scale_preview_label.setText("Scale: Invalid distance")
            self.apply_button.setEnabled(False)

    def apply_scale(self):
        """Apply the calculated scale."""
        if not (self.point1 and self.point2 and self.distance_input.text()):
            QMessageBox.warning(self, "Warning", "Please select two points and enter a distance.")
            return

        try:
            # Calculate pixel distance
            dx = self.point2[0] - self.point1[0]
            dy = self.point2[1] - self.point1[1]
            pixel_distance = (dx**2 + dy**2)**0.5

            # Get real-world distance
            real_distance = float(self.distance_input.text())

            if pixel_distance > 0 and real_distance > 0:
                scale = real_distance / pixel_distance
                self.scale_applied.emit(scale)
                QMessageBox.information(self, "Success", f"Scale applied: {scale:.6f}")
            else:
                QMessageBox.warning(self, "Warning", "Invalid distance values.")

        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter a valid distance.")

    def on_point_selected(self, x, y):
        """Handle point selection from the document viewer."""
        if self.point_count == 0:
            self.set_point1(x, y)
            self.point_count = 1
        elif self.point_count == 1:
            self.set_point2(x, y)
            self.point_count = 2
        else:
            # Reset and start over with new first point
            self.clear_points()
            self.set_point1(x, y)
            self.point_count = 1

    def clear_points(self):
        """Clear the selected points."""
        self.point1 = None
        self.point2 = None
        self.point_count = 0
        self.point1_label.setText("Not selected")
        self.point2_label.setText("Not selected")
        self.distance_label.setText("0.0 pixels")
        self.scale_preview_label.setText("Scale: Not calculated")
        self.apply_button.setEnabled(False)

        # Clear points in the viewer if parent has document viewer
        if hasattr(self.parent(), 'document_viewer'):
            self.parent().document_viewer.selected_points.clear()
            self.parent().document_viewer._update_display()

    def closeEvent(self, event):
        """Handle dialog close event."""
        # Disable point selection mode when dialog is closed
        if hasattr(self.parent(), 'document_viewer'):
            self.parent().document_viewer.set_point_selection_mode(False)
        super().closeEvent(event)

    def hideEvent(self, event):
        """Handle dialog hide event."""
        # Disable point selection mode when dialog is hidden
        if hasattr(self.parent(), 'document_viewer'):
            self.parent().document_viewer.set_point_selection_mode(False)
        super().hideEvent(event)
