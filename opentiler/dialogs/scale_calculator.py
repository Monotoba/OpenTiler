"""
Scale calculator dialog for OpenTiler.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QGroupBox, QTabWidget, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator


class ScaleCalculatorDialog(QDialog):
    """Dialog for calculating scale factors."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Scale Calculator")
        self.setModal(True)
        self.resize(400, 350)

        layout = QVBoxLayout()

        # Create tab widget
        tab_widget = QTabWidget()

        # Tab 1: Calculate Scale
        calc_tab = QWidget()
        self.setup_calculate_tab(calc_tab)
        tab_widget.addTab(calc_tab, "Calculate Scale")

        # Tab 2: Use Scale
        use_tab = QWidget()
        self.setup_use_scale_tab(use_tab)
        tab_widget.addTab(use_tab, "Use Scale")

        layout.addWidget(tab_widget)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def setup_calculate_tab(self, tab):
        """Setup the calculate scale tab."""
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Enter the measured length on the document and the real-world length "
            "to calculate the scale factor."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #e8e8e8; color: #333; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(instructions)

        # Input group
        input_group = QGroupBox("Measurements")
        input_layout = QFormLayout()

        # Document length
        doc_layout = QHBoxLayout()
        self.doc_length = QLineEdit()
        self.doc_length.setValidator(QDoubleValidator(0.001, 999999.999, 6))
        self.doc_length.textChanged.connect(self.calculate_scale)
        doc_layout.addWidget(self.doc_length)

        self.doc_units = QComboBox()
        self.doc_units.addItems(["mm", "inches", "pixels"])
        self.doc_units.currentTextChanged.connect(self.calculate_scale)
        doc_layout.addWidget(self.doc_units)

        input_layout.addRow("Document Length:", doc_layout)

        # Real-world length
        real_layout = QHBoxLayout()
        self.real_length = QLineEdit()
        self.real_length.setValidator(QDoubleValidator(0.001, 999999.999, 6))
        self.real_length.textChanged.connect(self.calculate_scale)
        real_layout.addWidget(self.real_length)

        self.real_units = QComboBox()
        self.real_units.addItems(["mm", "inches"])
        self.real_units.currentTextChanged.connect(self.calculate_scale)
        real_layout.addWidget(self.real_units)

        input_layout.addRow("Real-World Length:", real_layout)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Results group
        results_group = QGroupBox("Calculated Scale")
        results_layout = QFormLayout()

        self.scale_factor_label = QLabel("Not calculated")
        self.scale_factor_label.setStyleSheet("font-weight: bold;")
        results_layout.addRow("Scale Factor:", self.scale_factor_label)

        self.scale_ratio_label = QLabel("Not calculated")
        results_layout.addRow("Scale Ratio:", self.scale_ratio_label)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        layout.addStretch()
        tab.setLayout(layout)

    def setup_use_scale_tab(self, tab):
        """Setup the use scale tab."""
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Enter a scale factor and one length to calculate the other length."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #e8e8e8; color: #333; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(instructions)

        # Scale input group
        scale_group = QGroupBox("Scale Factor")
        scale_layout = QFormLayout()

        self.scale_input = QLineEdit()
        self.scale_input.setValidator(QDoubleValidator(0.000001, 999999.999, 6))
        self.scale_input.textChanged.connect(self.use_scale_calculate)
        scale_layout.addRow("Scale Factor:", self.scale_input)

        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)

        # Conversion group
        conversion_group = QGroupBox("Length Conversion")
        conversion_layout = QFormLayout()

        # Known length
        known_layout = QHBoxLayout()
        self.known_length = QLineEdit()
        self.known_length.setValidator(QDoubleValidator(0.001, 999999.999, 6))
        self.known_length.textChanged.connect(self.use_scale_calculate)
        known_layout.addWidget(self.known_length)

        self.known_units = QComboBox()
        self.known_units.addItems(["mm", "inches"])
        self.known_units.currentTextChanged.connect(self.use_scale_calculate)
        known_layout.addWidget(self.known_units)

        conversion_layout.addRow("Known Length:", known_layout)

        # Calculated length
        calc_layout = QHBoxLayout()
        self.calc_length_label = QLabel("Not calculated")
        self.calc_length_label.setStyleSheet("font-weight: bold;")
        calc_layout.addWidget(self.calc_length_label)

        self.calc_units = QComboBox()
        self.calc_units.addItems(["inches", "mm"])
        self.calc_units.currentTextChanged.connect(self.use_scale_calculate)
        calc_layout.addWidget(self.calc_units)

        conversion_layout.addRow("Calculated Length:", calc_layout)

        conversion_group.setLayout(conversion_layout)
        layout.addWidget(conversion_group)

        layout.addStretch()
        tab.setLayout(layout)

    def calculate_scale(self):
        """Calculate scale factor from document and real-world measurements."""
        try:
            doc_text = self.doc_length.text()
            real_text = self.real_length.text()

            if not doc_text or not real_text:
                self.scale_factor_label.setText("Not calculated")
                self.scale_ratio_label.setText("Not calculated")
                return

            doc_val = float(doc_text)
            real_val = float(real_text)

            if doc_val <= 0 or real_val <= 0:
                self.scale_factor_label.setText("Invalid values")
                self.scale_ratio_label.setText("Invalid values")
                return

            # Convert to same units if necessary
            doc_units = self.doc_units.currentText()
            real_units = self.real_units.currentText()

            # Convert document units to mm for calculation
            if doc_units == "inches":
                doc_val_mm = doc_val * 25.4
            elif doc_units == "pixels":
                # Assume 300 DPI for pixel conversion
                doc_val_mm = doc_val * 25.4 / 300
            else:
                doc_val_mm = doc_val

            # Convert real-world units to mm
            if real_units == "inches":
                real_val_mm = real_val * 25.4
            else:
                real_val_mm = real_val

            # Calculate scale factor (real-world per document unit)
            scale_factor = real_val_mm / doc_val_mm

            self.scale_factor_label.setText(f"{scale_factor:.6f}")

            # Calculate ratio
            if scale_factor >= 1.0:
                ratio_text = f"{scale_factor:.2f}:1"
            else:
                ratio = 1.0 / scale_factor
                ratio_text = f"1:{ratio:.2f}"

            self.scale_ratio_label.setText(ratio_text)

        except ValueError:
            self.scale_factor_label.setText("Invalid input")
            self.scale_ratio_label.setText("Invalid input")

    def use_scale_calculate(self):
        """Calculate length using scale factor."""
        try:
            scale_text = self.scale_input.text()
            known_text = self.known_length.text()

            if not scale_text or not known_text:
                self.calc_length_label.setText("Not calculated")
                return

            scale_val = float(scale_text)
            known_val = float(known_text)

            if scale_val <= 0 or known_val <= 0:
                self.calc_length_label.setText("Invalid values")
                return

            # Convert known length to mm
            known_units = self.known_units.currentText()
            if known_units == "inches":
                known_val_mm = known_val * 25.4
            else:
                known_val_mm = known_val

            # Calculate other length using scale
            calc_val_mm = known_val_mm * scale_val

            # Convert to target units
            calc_units = self.calc_units.currentText()
            if calc_units == "inches":
                calc_val = calc_val_mm / 25.4
            else:
                calc_val = calc_val_mm

            self.calc_length_label.setText(f"{calc_val:.6f}")

        except ValueError:
            self.calc_length_label.setText("Invalid input")
