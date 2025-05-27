"""
Settings dialog for OpenTiler application.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QPushButton, QColorDialog, QSlider, QGroupBox, QFormLayout,
    QDialogButtonBox, QLineEdit, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
import os

from ..settings.config import config


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    # Signal emitted when settings change
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 600)

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Add tabs
        self.tab_widget.addTab(self.create_general_tab(), "General")
        self.tab_widget.addTab(self.create_tiling_tab(), "Tiling")
        self.tab_widget.addTab(self.create_display_tab(), "Display")
        self.tab_widget.addTab(self.create_page_indicators_tab(), "Page Indicators")
        self.tab_widget.addTab(self.create_export_tab(), "Export")

        layout.addWidget(self.tab_widget)

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def create_general_tab(self):
        """Create the general settings tab."""
        widget = QWidget()
        layout = QFormLayout()

        # Default units
        self.units_combo = QComboBox()
        self.units_combo.addItems(["mm", "inches"])
        layout.addRow("Default Units:", self.units_combo)

        # Default DPI
        self.dpi_combo = QComboBox()
        available_dpi = config.get_available_dpi_options()
        for dpi in available_dpi:
            self.dpi_combo.addItem(f"{dpi} DPI", dpi)
        layout.addRow("Default DPI:", self.dpi_combo)

        # Default page size
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["A4", "A3", "A2", "A1", "A0", "Letter", "Legal", "Tabloid"])
        layout.addRow("Default Page Size:", self.page_size_combo)

        # Max recent files
        self.max_recent_spin = QSpinBox()
        self.max_recent_spin.setRange(1, 20)
        self.max_recent_spin.setSuffix(" files")
        layout.addRow("Max Recent Files:", self.max_recent_spin)

        # Default input directory
        input_dir_layout = QHBoxLayout()
        self.input_dir_edit = QLineEdit()
        self.input_dir_edit.setPlaceholderText("Enter path or use Browse button...")
        self.input_dir_edit.setToolTip("Enter directory path manually or use Browse button")
        input_dir_layout.addWidget(self.input_dir_edit)

        input_dir_button = QPushButton("Browse...")
        input_dir_button.clicked.connect(self.browse_input_dir)
        input_dir_layout.addWidget(input_dir_button)

        layout.addRow("Default Input Directory:", input_dir_layout)

        # Default output directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("Enter path or use Browse button...")
        self.output_dir_edit.setToolTip("Enter directory path manually or use Browse button")
        output_dir_layout.addWidget(self.output_dir_edit)

        output_dir_button = QPushButton("Browse...")
        output_dir_button.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(output_dir_button)

        layout.addRow("Default Output Directory:", output_dir_layout)

        widget.setLayout(layout)
        return widget

    def create_tiling_tab(self):
        """Create the tiling settings tab."""
        widget = QWidget()
        layout = QFormLayout()

        # Gutter size
        self.gutter_size_spin = QDoubleSpinBox()
        self.gutter_size_spin.setRange(0.0, 50.0)
        self.gutter_size_spin.setSuffix(" mm")
        self.gutter_size_spin.setDecimals(1)
        layout.addRow("Gutter Size:", self.gutter_size_spin)

        # Page orientation
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["auto", "landscape", "portrait"])
        layout.addRow("Page Orientation:", self.orientation_combo)

        widget.setLayout(layout)
        return widget

    def create_display_tab(self):
        """Create the display settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Gutter lines group
        gutter_group = QGroupBox("Gutter Lines (Blue)")
        gutter_layout = QFormLayout()

        self.gutter_display_check = QCheckBox("Show on screen")
        gutter_layout.addRow(self.gutter_display_check)

        self.gutter_print_check = QCheckBox("Include when printing")
        gutter_layout.addRow(self.gutter_print_check)

        gutter_group.setLayout(gutter_layout)
        layout.addWidget(gutter_group)

        # Crop marks group
        crop_group = QGroupBox("Crop Marks")
        crop_layout = QFormLayout()

        self.crop_display_check = QCheckBox("Show on screen")
        crop_layout.addRow(self.crop_display_check)

        self.crop_print_check = QCheckBox("Include when printing")
        crop_layout.addRow(self.crop_print_check)

        crop_group.setLayout(crop_layout)
        layout.addWidget(crop_group)

        # Scale line and text group
        scale_group = QGroupBox("Scale Line and Text (Red)")
        scale_layout = QFormLayout()

        self.scale_line_display_check = QCheckBox("Show scale line on screen")
        scale_layout.addRow(self.scale_line_display_check)

        self.scale_line_print_check = QCheckBox("Include scale line when printing")
        scale_layout.addRow(self.scale_line_print_check)

        self.scale_text_display_check = QCheckBox("Show scale text on screen")
        scale_layout.addRow(self.scale_text_display_check)

        self.scale_text_print_check = QCheckBox("Include scale text when printing")
        scale_layout.addRow(self.scale_text_print_check)

        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_page_indicators_tab(self):
        """Create the page indicators settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Display options
        display_group = QGroupBox("Display Options")
        display_layout = QFormLayout()

        self.indicator_display_check = QCheckBox("Show on screen")
        display_layout.addRow(self.indicator_display_check)

        self.indicator_print_check = QCheckBox("Include when printing")
        display_layout.addRow(self.indicator_print_check)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # Position and style
        style_group = QGroupBox("Position and Style")
        style_layout = QFormLayout()

        # Position
        self.position_combo = QComboBox()
        self.position_combo.addItems([
            "upper-left", "upper-right", "bottom-left", "bottom-right", "center-page"
        ])
        style_layout.addRow("Position:", self.position_combo)

        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setSuffix(" pt")
        style_layout.addRow("Font Size:", self.font_size_spin)

        # Font style
        self.font_style_combo = QComboBox()
        self.font_style_combo.addItems(["normal", "bold", "italic"])
        style_layout.addRow("Font Style:", self.font_style_combo)

        # Font color
        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 30)
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        style_layout.addRow("Font Color:", color_layout)

        # Alpha (transparency)
        alpha_layout = QHBoxLayout()
        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setRange(0, 255)
        self.alpha_label = QLabel("255")
        self.alpha_slider.valueChanged.connect(lambda v: self.alpha_label.setText(str(v)))
        alpha_layout.addWidget(self.alpha_slider)
        alpha_layout.addWidget(self.alpha_label)
        style_layout.addRow("Opacity:", alpha_layout)

        style_group.setLayout(style_layout)
        layout.addWidget(style_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_export_tab(self):
        """Create the export settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Metadata page group
        metadata_group = QGroupBox("Metadata Summary Page")
        metadata_layout = QFormLayout()

        self.metadata_include_check = QCheckBox("Include metadata page in tile exports")
        self.metadata_include_check.setToolTip("Add a summary page with scale, DPI, timestamp, and document information")
        metadata_layout.addRow(self.metadata_include_check)

        # Position
        self.metadata_position_combo = QComboBox()
        self.metadata_position_combo.addItems(["first", "last"])
        self.metadata_position_combo.setToolTip("Position of metadata page in the exported tile set")
        metadata_layout.addRow("Position:", self.metadata_position_combo)

        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def choose_color(self):
        """Open color chooser dialog."""
        color = QColorDialog.getColor(self.current_color, self, "Choose Font Color")
        if color.isValid():
            self.current_color = color
            self.update_color_button()

    def update_color_button(self):
        """Update the color button appearance."""
        self.color_button.setStyleSheet(
            f"background-color: {self.current_color.name()}; border: 1px solid black;"
        )

    def load_settings(self):
        """Load current settings into the dialog."""
        # General settings
        self.units_combo.setCurrentText(config.get_default_units())

        # Set DPI combo to current value
        current_dpi = config.get_default_dpi()
        for i in range(self.dpi_combo.count()):
            if self.dpi_combo.itemData(i) == current_dpi:
                self.dpi_combo.setCurrentIndex(i)
                break

        self.page_size_combo.setCurrentText(config.get_default_page_size())
        self.max_recent_spin.setValue(config.get_max_recent_files())

        # Tiling settings
        self.gutter_size_spin.setValue(config.get_gutter_size_mm())
        self.orientation_combo.setCurrentText(config.get_page_orientation())

        # Display settings
        self.gutter_display_check.setChecked(config.get_gutter_lines_display())
        self.gutter_print_check.setChecked(config.get_gutter_lines_print())
        self.crop_display_check.setChecked(config.get_crop_marks_display())
        self.crop_print_check.setChecked(config.get_crop_marks_print())

        # Scale line and text settings
        self.scale_line_display_check.setChecked(config.get_scale_line_display())
        self.scale_line_print_check.setChecked(config.get_scale_line_print())
        self.scale_text_display_check.setChecked(config.get_scale_text_display())
        self.scale_text_print_check.setChecked(config.get_scale_text_print())

        # Page indicator settings
        self.indicator_display_check.setChecked(config.get_page_indicator_display())
        self.indicator_print_check.setChecked(config.get_page_indicator_print())
        self.position_combo.setCurrentText(config.get_page_indicator_position())
        self.font_size_spin.setValue(config.get_page_indicator_font_size())
        self.font_style_combo.setCurrentText(config.get_page_indicator_font_style())

        # Color
        color_hex = config.get_page_indicator_font_color()
        self.current_color = QColor(color_hex)
        self.update_color_button()

        # Alpha
        self.alpha_slider.setValue(config.get_page_indicator_alpha())

        # Directory settings
        self.input_dir_edit.setText(config.get_last_input_dir())
        self.output_dir_edit.setText(config.get_last_output_dir())

        # Metadata page settings
        self.metadata_include_check.setChecked(config.get_include_metadata_page())
        self.metadata_position_combo.setCurrentText(config.get_metadata_page_position())

    def apply_settings(self):
        """Apply settings without closing dialog."""
        self.save_settings()
        self.settings_changed.emit()

    def accept_settings(self):
        """Accept and apply settings."""
        self.save_settings()
        self.settings_changed.emit()
        self.accept()

    def save_settings(self):
        """Save settings to configuration."""
        # General settings
        config.set_default_units(self.units_combo.currentText())
        config.set_default_dpi(self.dpi_combo.currentData())
        config.set_default_page_size(self.page_size_combo.currentText())
        config.set_max_recent_files(self.max_recent_spin.value())

        # Tiling settings
        config.set_gutter_size_mm(self.gutter_size_spin.value())
        config.set_page_orientation(self.orientation_combo.currentText())

        # Display settings
        config.set_gutter_lines_display(self.gutter_display_check.isChecked())
        config.set_gutter_lines_print(self.gutter_print_check.isChecked())
        config.set_crop_marks_display(self.crop_display_check.isChecked())
        config.set_crop_marks_print(self.crop_print_check.isChecked())

        # Scale line and text settings
        config.set_scale_line_display(self.scale_line_display_check.isChecked())
        config.set_scale_line_print(self.scale_line_print_check.isChecked())
        config.set_scale_text_display(self.scale_text_display_check.isChecked())
        config.set_scale_text_print(self.scale_text_print_check.isChecked())

        # Page indicator settings
        config.set_page_indicator_display(self.indicator_display_check.isChecked())
        config.set_page_indicator_print(self.indicator_print_check.isChecked())
        config.set_page_indicator_position(self.position_combo.currentText())
        config.set_page_indicator_font_size(self.font_size_spin.value())
        config.set_page_indicator_font_style(self.font_style_combo.currentText())
        config.set_page_indicator_font_color(self.current_color.name())
        config.set_page_indicator_alpha(self.alpha_slider.value())

        # Directory settings
        config.set_last_input_dir(self.input_dir_edit.text())
        config.set_last_output_dir(self.output_dir_edit.text())

        # Metadata page settings
        config.set_include_metadata_page(self.metadata_include_check.isChecked())
        config.set_metadata_page_position(self.metadata_position_combo.currentText())

        # Sync to disk
        config.sync()

    def browse_input_dir(self):
        """Browse for default input directory."""
        current_dir = self.input_dir_edit.text() or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Default Input Directory",
            current_dir
        )
        if directory:
            self.input_dir_edit.setText(directory)

    def browse_output_dir(self):
        """Browse for default output directory."""
        current_dir = self.output_dir_edit.text() or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Default Output Directory",
            current_dir
        )
        if directory:
            self.output_dir_edit.setText(directory)
