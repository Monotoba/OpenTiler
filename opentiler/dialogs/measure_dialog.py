"""
Measure dialog for OpenTiler: select two points and read scaled distance.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDialog, QFormLayout, QHBoxLayout,
                               QLabel, QMessageBox, QPushButton, QVBoxLayout)


class MeasureDialog(QDialog):
    """Dialog for measuring distance between two points on the scaled drawing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.point1 = None
        self.point2 = None
        self.point_count = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Measure Tool")
        self.setModal(False)
        self.resize(360, 240)

        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "1) Click two points on the drawing\n"
            "2) Read the measured distance (uses current scale)"
        )
        instructions.setStyleSheet(
            "background-color: #eef8e6; color: #2c3e50; padding: 10px; "
            "border: 1px solid #6aa84f; border-radius: 4px; font-weight: bold; font-size: 11px;"
        )
        layout.addWidget(instructions)

        # Readouts
        form = QFormLayout()
        self.p1_label = QLabel("Not selected")
        self.p2_label = QLabel("Not selected")
        self.px_dist_label = QLabel("0.0 px")
        self.mm_dist_label = QLabel("0.0 mm")
        self.in_dist_label = QLabel("0.000 in")
        form.addRow("Point 1 (x, y):", self.p1_label)
        form.addRow("Point 2 (x, y):", self.p2_label)
        form.addRow("Pixel Distance:", self.px_dist_label)
        form.addRow("Distance (mm):", self.mm_dist_label)
        form.addRow("Distance (in):", self.in_dist_label)
        layout.addLayout(form)

        # Units display (read-only) for clarity
        units_row = QHBoxLayout()
        units_row.addWidget(QLabel("Units:"))
        self.units_combo = QComboBox()
        self.units_combo.addItems(
            ["mm", "inches"]
        )  # display only; measured values shown in both
        self.units_combo.setEnabled(False)
        units_row.addWidget(self.units_combo)
        units_row.addStretch()
        layout.addLayout(units_row)

        # Buttons
        buttons = QHBoxLayout()
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_points)
        buttons.addWidget(self.clear_btn)

        buttons.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def _recompute(self):
        if not (self.point1 and self.point2):
            self.px_dist_label.setText("0.0 px")
            self.mm_dist_label.setText("0.0 mm")
            self.in_dist_label.setText("0.000 in")
            # Clear overlay text in viewer
            if hasattr(self.parent(), "document_viewer"):
                self.parent().document_viewer.set_measurement_text("")
            return
        dx = self.point2[0] - self.point1[0]
        dy = self.point2[1] - self.point1[1]
        px_dist = (dx * dx + dy * dy) ** 0.5
        self.px_dist_label.setText(f"{px_dist:.2f} px")

        # Scale factor is mm/px (stored on document viewer)
        scale = (
            getattr(self.parent().document_viewer, "scale_factor", 1.0)
            if self.parent()
            else 1.0
        )
        if scale and scale > 0:
            mm = px_dist * float(scale)
            inches = mm / 25.4
            self.mm_dist_label.setText(f"{mm:.3f} mm")
            self.in_dist_label.setText(f"{inches:.4f} in")
            # Update overlay text on the viewer (drawn above the line)
            if hasattr(self.parent(), "document_viewer"):
                self.parent().document_viewer.set_measurement_text(
                    f"{mm:.2f} mm ({inches:.3f} in)"
                )
        else:
            # No scale set — warn user once
            self.mm_dist_label.setText("(set scale)")
            self.in_dist_label.setText("(set scale)")
            if hasattr(self.parent(), "document_viewer"):
                # Fall back to pixels if desired; for now clear to avoid implying scale
                self.parent().document_viewer.set_measurement_text("")

    def on_point_selected(self, x, y):
        if self.point_count == 0:
            self.point1 = (x, y)
            self.p1_label.setText(f"({x:.1f}, {y:.1f})")
            self.point_count = 1
        elif self.point_count == 1:
            self.point2 = (x, y)
            self.p2_label.setText(f"({x:.1f}, {y:.1f})")
            self.point_count = 2
        else:
            self.clear_points()
            self.point1 = (x, y)
            self.p1_label.setText(f"({x:.1f}, {y:.1f})")
            self.point_count = 1
        self._recompute()

    def on_point_moved(self, x, y, index):
        if index == 0 and self.point1:
            self.point1 = (x, y)
            self.p1_label.setText(f"({x:.1f}, {y:.1f})")
        elif index == 1 and self.point2:
            self.point2 = (x, y)
            self.p2_label.setText(f"({x:.1f}, {y:.1f})")
        self._recompute()

    def clear_points(self):
        self.point1 = None
        self.point2 = None
        self.point_count = 0
        self.p1_label.setText("Not selected")
        self.p2_label.setText("Not selected")
        self.px_dist_label.setText("0.0 px")
        self.mm_dist_label.setText("0.0 mm")
        self.in_dist_label.setText("0.000 in")
        # Clear viewer points if available
        if hasattr(self.parent(), "document_viewer"):
            self.parent().document_viewer.selected_points.clear()
            self.parent().document_viewer._update_display()

    def showEvent(self, event):
        # Enable point selection in viewer
        if hasattr(self.parent(), "document_viewer"):
            self.parent().document_viewer.set_point_selection_mode(True)
        super().showEvent(event)

    def closeEvent(self, event):
        # Disable point selection when closing
        if hasattr(self.parent(), "document_viewer"):
            self.parent().document_viewer.set_point_selection_mode(False)
        super().closeEvent(event)
