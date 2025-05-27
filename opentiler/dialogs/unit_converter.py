"""
Unit converter dialog for OpenTiler.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator


class UnitConverterDialog(QDialog):
    """Dialog for converting between units."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Unit Converter")
        self.setModal(True)
        self.resize(350, 200)

        layout = QVBoxLayout()

        # Converter group
        converter_group = QGroupBox("Length Converter")
        converter_layout = QFormLayout()

        # Input section
        input_layout = QHBoxLayout()
        self.input_value = QLineEdit()
        self.input_value.setValidator(QDoubleValidator(0.0, 999999.999, 6))
        self.input_value.textChanged.connect(self.convert_units)
        input_layout.addWidget(self.input_value)

        self.input_units = QComboBox()
        self.input_units.addItems(["mm", "inches"])
        self.input_units.currentTextChanged.connect(self.convert_units)
        input_layout.addWidget(self.input_units)

        converter_layout.addRow("Input:", input_layout)

        # Output section
        output_layout = QHBoxLayout()
        self.output_value = QLineEdit()
        self.output_value.setReadOnly(True)
        self.output_value.setStyleSheet("background-color: #f0f0f0;")
        output_layout.addWidget(self.output_value)

        self.output_units = QComboBox()
        self.output_units.addItems(["inches", "mm"])
        self.output_units.currentTextChanged.connect(self.convert_units)
        output_layout.addWidget(self.output_units)

        converter_layout.addRow("Output:", output_layout)

        converter_group.setLayout(converter_layout)
        layout.addWidget(converter_group)

        # Conversion reference
        reference_group = QGroupBox("Reference")
        reference_layout = QVBoxLayout()

        reference_text = QLabel(
            "1 inch = 25.4 mm\n"
            "1 mm = 0.0393701 inches"
        )
        reference_text.setStyleSheet("""
            font-family: monospace;
            background-color: #e8e8e8;
            color: #333;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 3px;
        """)
        reference_layout.addWidget(reference_text)

        reference_group.setLayout(reference_layout)
        layout.addWidget(reference_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.swap_button = QPushButton("Swap Units")
        self.swap_button.clicked.connect(self.swap_units)
        button_layout.addWidget(self.swap_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Set initial focus
        self.input_value.setFocus()

    def convert_units(self):
        """Convert between units."""
        try:
            input_text = self.input_value.text()
            if not input_text:
                self.output_value.clear()
                return

            input_val = float(input_text)
            input_unit = self.input_units.currentText()
            output_unit = self.output_units.currentText()

            # Conversion factors
            if input_unit == "mm" and output_unit == "inches":
                result = input_val * 0.0393701
            elif input_unit == "inches" and output_unit == "mm":
                result = input_val * 25.4
            else:
                # Same units
                result = input_val

            self.output_value.setText(f"{result:.6f}")

        except ValueError:
            self.output_value.clear()

    def swap_units(self):
        """Swap input and output units."""
        # Get current values
        input_unit = self.input_units.currentText()
        output_unit = self.output_units.currentText()
        output_value = self.output_value.text()

        # Swap units
        self.input_units.setCurrentText(output_unit)
        self.output_units.setCurrentText(input_unit)

        # Set input value to previous output
        if output_value:
            self.input_value.setText(output_value)
        else:
            self.input_value.clear()
