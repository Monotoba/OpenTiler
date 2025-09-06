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
        self.tab_widget.addTab(self.create_project_tab(), "Project")
        self.tab_widget.addTab(self.create_logging_tab(), "Logging")

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
        self.units_combo.setToolTip("Default measurement units used in scaling, gutters, and metadata.")
        layout.addRow("Default Units:", self.units_combo)

        # Default DPI
        self.dpi_combo = QComboBox()
        self.dpi_combo.setToolTip("Default DPI used for export/printing where applicable (e.g., PDF rendering).")
        available_dpi = config.get_available_dpi_options()
        for dpi in available_dpi:
            self.dpi_combo.addItem(f"{dpi} DPI", dpi)
        layout.addRow("Default DPI:", self.dpi_combo)

        # Default page size
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["A4", "A3", "A2", "A1", "A0", "Letter", "Legal", "Tabloid"])
        self.page_size_combo.setToolTip("Default target page size used when tiling documents.")
        layout.addRow("Default Page Size:", self.page_size_combo)

        # Max recent files
        self.max_recent_spin = QSpinBox()
        self.max_recent_spin.setRange(1, 20)
        self.max_recent_spin.setSuffix(" files")
        self.max_recent_spin.setToolTip("How many recent files to list in the menu.")
        layout.addRow("Max Recent Files:", self.max_recent_spin)

        # Max recent projects
        self.max_recent_projects_spin = QSpinBox()
        self.max_recent_projects_spin.setRange(1, 50)
        self.max_recent_projects_spin.setSuffix(" projects")
        self.max_recent_projects_spin.setToolTip("How many recent projects to list in the Project menu.")
        layout.addRow("Max Recent Projects:", self.max_recent_projects_spin)

        # Open last project on startup
        self.open_last_project_check = QCheckBox("Open last project on start up.")
        self.open_last_project_check.setToolTip("Load the most recently opened project automatically when the app starts.")
        layout.addRow(self.open_last_project_check)

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
        self.gutter_size_spin.setToolTip(
            "Width of the inner white margin inside each page tile; content is clipped to this area."
        )
        layout.addRow("Gutter Size:", self.gutter_size_spin)

        # Page orientation
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["auto", "landscape", "portrait"])
        self.orientation_combo.setToolTip(
            "Auto chooses orientation based on tile aspect ratio; or force landscape/portrait."
        )
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
        self.gutter_display_check.setToolTip("Show a blue outline indicating the printable area (inside the gutter) in the preview.")
        gutter_layout.addRow(self.gutter_display_check)

        self.gutter_print_check = QCheckBox("Include when printing")
        self.gutter_print_check.setToolTip("Include the blue gutter outline when printing/exporting (if enabled).")
        gutter_layout.addRow(self.gutter_print_check)

        gutter_group.setLayout(gutter_layout)
        layout.addWidget(gutter_group)

        # Crop marks group
        crop_group = QGroupBox("Crop Marks")
        crop_layout = QFormLayout()

        self.crop_display_check = QCheckBox("Show on screen")
        self.crop_display_check.setToolTip("Draw crop marks at gutter intersections in the preview.")
        crop_layout.addRow(self.crop_display_check)

        self.crop_print_check = QCheckBox("Include when printing")
        self.crop_print_check.setToolTip("Include crop marks at gutter intersections in printed/exported output.")
        crop_layout.addRow(self.crop_print_check)

        crop_group.setLayout(crop_layout)
        layout.addWidget(crop_group)

        # Registration marks group
        reg_group = QGroupBox("Registration Marks (Circle + Crosshair)")
        reg_layout = QFormLayout()

        self.reg_display_check = QCheckBox("Show on screen")
        self.reg_display_check.setToolTip("Display registration marks at printable-area corners in the preview.")
        reg_layout.addRow(self.reg_display_check)

        self.reg_print_check = QCheckBox("Include when printing")
        self.reg_print_check.setToolTip("Include registration marks on exported/printed tiles.")
        reg_layout.addRow(self.reg_print_check)

        self.reg_diameter_spin = QDoubleSpinBox()
        self.reg_diameter_spin.setRange(2.0, 50.0)
        self.reg_diameter_spin.setDecimals(1)
        self.reg_diameter_spin.setSuffix(" mm")
        self.reg_diameter_spin.setToolTip("Diameter of the registration circle.")
        reg_layout.addRow("Circle Diameter:", self.reg_diameter_spin)

        self.reg_crosshair_spin = QDoubleSpinBox()
        self.reg_crosshair_spin.setRange(2.0, 50.0)
        self.reg_crosshair_spin.setDecimals(1)
        self.reg_crosshair_spin.setSuffix(" mm")
        self.reg_crosshair_spin.setToolTip("Length of each crosshair axis from center.")
        reg_layout.addRow("Crosshair Length:", self.reg_crosshair_spin)

        reg_group.setLayout(reg_layout)
        layout.addWidget(reg_group)

        # Scale line and text group
        scale_group = QGroupBox("Scale Line and Text (Red)")
        scale_layout = QFormLayout()

        self.scale_line_display_check = QCheckBox("Show scale line on screen")
        self.scale_line_display_check.setToolTip("Draw the red measured scale line on pages that contain it in the preview.")
        scale_layout.addRow(self.scale_line_display_check)

        self.scale_line_print_check = QCheckBox("Include scale line when printing")
        self.scale_line_print_check.setToolTip("Include the red measured scale line when printing/exporting.")
        scale_layout.addRow(self.scale_line_print_check)

        self.scale_text_display_check = QCheckBox("Show scale text on screen")
        self.scale_text_display_check.setToolTip("Show the measured distance (text) alongside the scale line in the preview.")
        scale_layout.addRow(self.scale_text_display_check)

        self.scale_text_print_check = QCheckBox("Include scale text when printing")
        self.scale_text_print_check.setToolTip("Include the measured distance text when printing/exporting.")
        scale_layout.addRow(self.scale_text_print_check)

        # Convenience: single switch to print both line and text
        self.measure_print_check = QCheckBox("Print measurements (line + text)")
        self.measure_print_check.setToolTip("Convenience toggle to include both the measured line and its distance text when printing/exporting.")
        scale_layout.addRow(self.measure_print_check)

        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)

        # Datum line group
        datum_group = QGroupBox("Datum Line (Selected Points)")
        datum_layout = QFormLayout()

        self.datum_display_check = QCheckBox("Show datum line on screen")
        self.datum_display_check.setToolTip("Draw a line between the two selected scale points during preview.")
        datum_layout.addRow(self.datum_display_check)

        self.datum_print_check = QCheckBox("Include datum line when printing")
        self.datum_print_check.setToolTip("Include the datum line on printed/exported tiles.")
        datum_layout.addRow(self.datum_print_check)

        self.datum_style_combo = QComboBox()
        self.datum_style_combo.addItems(["solid", "dash", "dot", "dashdot", "dashdotdot", "dot-dash-dot"]) 
        datum_layout.addRow("Line Style:", self.datum_style_combo)

        self.datum_width_spin = QSpinBox()
        self.datum_width_spin.setRange(1, 8)
        self.datum_width_spin.setSuffix(" px")
        datum_layout.addRow("Line Width:", self.datum_width_spin)

        self.datum_color_button = QPushButton()
        self.datum_color_button.setFixedSize(50, 24)
        self.datum_color_button.clicked.connect(self.choose_datum_color)
        datum_layout.addRow("Line Color:", self.datum_color_button)

        datum_group.setLayout(datum_layout)
        layout.addWidget(datum_group)

        # Scale bar overlay group
        bar_group = QGroupBox("Scale Bar Overlay")
        bar_layout = QFormLayout()

        self.scale_bar_display_check = QCheckBox("Show on screen")
        self.scale_bar_display_check.setToolTip("Show the alternating light/dark scale bar overlay in the selected location.")
        bar_layout.addRow(self.scale_bar_display_check)

        self.scale_bar_print_check = QCheckBox("Include when printing")
        self.scale_bar_print_check.setToolTip("Include the scale bar in exported/printed output.")
        bar_layout.addRow(self.scale_bar_print_check)

        self.scale_bar_location_combo = QComboBox()
        locations = [
            "Page-N", "Page-NE", "Page-E", "Page-SE", "Page-S", "Page-SW", "Page-W", "Page-NW",
            "Gutter-N", "Gutter-NE", "Gutter-E", "Gutter-SE", "Gutter-S", "Gutter-SW", "Gutter-W", "Gutter-NW",
        ]
        self.scale_bar_location_combo.addItems(locations)
        bar_layout.addRow("Location:", self.scale_bar_location_combo)

        # Length slider + label (dynamic units)
        self.scale_bar_length_slider = QSlider(Qt.Horizontal)
        self.scale_bar_length_value = QLabel("")
        bar_layout.addRow("Length:", self.scale_bar_length_slider)
        bar_layout.addRow("", self.scale_bar_length_value)

        # Opacity slider
        self.scale_bar_opacity_slider = QSlider(Qt.Horizontal)
        self.scale_bar_opacity_slider.setRange(0, 100)
        self.scale_bar_opacity_value = QLabel("60%")
        self.scale_bar_opacity_slider.valueChanged.connect(lambda v: self.scale_bar_opacity_value.setText(f"{v}%"))
        bar_layout.addRow("Opacity:", self.scale_bar_opacity_slider)
        bar_layout.addRow("", self.scale_bar_opacity_value)

        bar_group.setLayout(bar_layout)
        layout.addWidget(bar_group)

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
        self.indicator_display_check.setToolTip("Display page indicator labels (e.g., P1) over each tile in the preview.")
        display_layout.addRow(self.indicator_display_check)

        self.indicator_print_check = QCheckBox("Include when printing")
        self.indicator_print_check.setToolTip("Include page indicator labels when printing/exporting.")
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
        self.position_combo.setToolTip("Where to place the page indicator label within the printable area.")
        style_layout.addRow("Position:", self.position_combo)

        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setSuffix(" pt")
        self.font_size_spin.setToolTip("Font size for the page indicator label.")
        style_layout.addRow("Font Size:", self.font_size_spin)

        # Font style
        self.font_style_combo = QComboBox()
        self.font_style_combo.addItems(["normal", "bold", "italic"])
        self.font_style_combo.setToolTip("Font style for the page indicator label.")
        style_layout.addRow("Font Style:", self.font_style_combo)

        # Font color
        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 30)
        self.color_button.clicked.connect(self.choose_color)
        self.color_button.setToolTip("Choose the font color for the page indicator label.")
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        style_layout.addRow("Font Color:", color_layout)

        # Alpha (transparency)
        alpha_layout = QHBoxLayout()
        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setRange(0, 255)
        self.alpha_label = QLabel("255")
        self.alpha_slider.valueChanged.connect(lambda v: self.alpha_label.setText(str(v)))
        self.alpha_slider.setToolTip("Opacity of the page indicator label (0 = transparent, 255 = opaque).")
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

    def create_project_tab(self):
        """Create the project settings tab."""
        widget = QWidget()
        layout = QFormLayout()

        self.project_storage_combo = QComboBox()
        self.project_storage_combo.addItems([
            "reference",  # .otproj references original on disk
            "sidecar",    # .otproj + <name>.dat holds compressed original
            "embedded",   # .otprjz embeds original
        ])
        self.project_storage_combo.setToolTip(
            "How to store the original file with a project: reference only, compressed sidecar, or embedded in a zip project."
        )
        layout.addRow("Original Storage:", self.project_storage_combo)

        widget.setLayout(layout)
        return widget

    def create_logging_tab(self):
        """Create the logging settings tab."""
        widget = QWidget()
        layout = QFormLayout()

        # Enable logging
        self.logging_enabled_check = QCheckBox("Enable logging")
        self.logging_enabled_check.setToolTip("Turn on application logging. Errors are always allowed; other levels honor per-component toggles.")
        layout.addRow(self.logging_enabled_check)

        # Level
        self.logging_level_combo = QComboBox()
        self.logging_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.logging_level_combo.setToolTip("Minimum log level to emit.")
        layout.addRow("Log Level:", self.logging_level_combo)

        # Components
        comp_box = QGroupBox("Components")
        comp_form = QFormLayout()
        self.log_printing_check = QCheckBox("Printing")
        self.log_projects_check = QCheckBox("Projects")
        self.log_preview_check = QCheckBox("Preview")
        self.log_viewer_check = QCheckBox("Viewer")
        self.log_export_check = QCheckBox("Export")
        self.log_metadata_check = QCheckBox("Metadata")
        self.log_settings_check = QCheckBox("Settings")
        comp_form.addRow(self.log_printing_check)
        comp_form.addRow(self.log_projects_check)
        comp_form.addRow(self.log_preview_check)
        comp_form.addRow(self.log_viewer_check)
        comp_form.addRow(self.log_export_check)
        comp_form.addRow(self.log_metadata_check)
        comp_form.addRow(self.log_settings_check)
        comp_box.setLayout(comp_form)
        layout.addRow(comp_box)

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
        self.max_recent_projects_spin.setValue(config.get_max_recent_projects())
        self.open_last_project_check.setChecked(config.get_open_last_project_on_startup())

        # Tiling settings
        self.gutter_size_spin.setValue(config.get_gutter_size_mm())
        self.orientation_combo.setCurrentText(config.get_page_orientation())

        # Display settings
        self.gutter_display_check.setChecked(config.get_gutter_lines_display())
        self.gutter_print_check.setChecked(config.get_gutter_lines_print())
        self.crop_display_check.setChecked(config.get_crop_marks_display())
        self.crop_print_check.setChecked(config.get_crop_marks_print())
        self.scale_bar_display_check.setChecked(config.get_scale_bar_display())
        self.scale_bar_print_check.setChecked(config.get_scale_bar_print())
        self.scale_bar_location_combo.setCurrentText(config.get_scale_bar_location())
        self.scale_bar_opacity_slider.setValue(config.get_scale_bar_opacity())

        # Configure length slider based on units
        self._configure_scale_bar_length_slider()
        self.reg_display_check.setChecked(config.get_reg_marks_display())
        self.reg_print_check.setChecked(config.get_reg_marks_print())
        self.reg_diameter_spin.setValue(config.get_reg_mark_diameter_mm())
        self.reg_crosshair_spin.setValue(config.get_reg_mark_crosshair_mm())

        # Scale line and text settings
        self.scale_line_display_check.setChecked(config.get_scale_line_display())
        self.scale_line_print_check.setChecked(config.get_scale_line_print())
        self.scale_text_display_check.setChecked(config.get_scale_text_display())
        self.scale_text_print_check.setChecked(config.get_scale_text_print())
        # Measurement convenience reflects both line+text print enabled
        self.measure_print_check.setChecked(bool(config.get_scale_line_print() and config.get_scale_text_print()))

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

        # Project settings
        self.project_storage_combo.setCurrentText(config.get_project_original_storage())

        # Logging settings
        self.logging_enabled_check.setChecked(config.get_logging_enabled())
        self.logging_level_combo.setCurrentText(config.get_logging_level())
        self.log_printing_check.setChecked(config.get_logging_component_enabled('printing'))
        self.log_projects_check.setChecked(config.get_logging_component_enabled('projects'))
        self.log_preview_check.setChecked(config.get_logging_component_enabled('preview'))
        self.log_viewer_check.setChecked(config.get_logging_component_enabled('viewer'))
        self.log_export_check.setChecked(config.get_logging_component_enabled('export'))
        self.log_metadata_check.setChecked(config.get_logging_component_enabled('metadata'))
        self.log_settings_check.setChecked(config.get_logging_component_enabled('settings'))

        # Datum line settings
        self.datum_display_check.setChecked(config.get_datum_line_display())
        self.datum_print_check.setChecked(config.get_datum_line_print())
        self.datum_style_combo.setCurrentText(config.get_datum_line_style())
        self.datum_width_spin.setValue(config.get_datum_line_width_px())
        # Color
        self.datum_color = QColor(config.get_datum_line_color())
        self.update_datum_color_button()

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
        config.set_max_recent_projects(self.max_recent_projects_spin.value())
        config.set_open_last_project_on_startup(self.open_last_project_check.isChecked())

        # Tiling settings
        config.set_gutter_size_mm(self.gutter_size_spin.value())
        config.set_page_orientation(self.orientation_combo.currentText())

        # Display settings
        config.set_gutter_lines_display(self.gutter_display_check.isChecked())
        config.set_gutter_lines_print(self.gutter_print_check.isChecked())
        config.set_crop_marks_display(self.crop_display_check.isChecked())
        config.set_crop_marks_print(self.crop_print_check.isChecked())
        # Registration marks
        config.set_reg_marks_display(self.reg_display_check.isChecked())
        config.set_reg_marks_print(self.reg_print_check.isChecked())
        config.set_reg_mark_diameter_mm(self.reg_diameter_spin.value())
        config.set_reg_mark_crosshair_mm(self.reg_crosshair_spin.value())
        config.set_scale_bar_display(self.scale_bar_display_check.isChecked())
        config.set_scale_bar_print(self.scale_bar_print_check.isChecked())
        config.set_scale_bar_location(self.scale_bar_location_combo.currentText())
        config.set_scale_bar_opacity(self.scale_bar_opacity_slider.value())

        # Save length according to units
        units = config.get_default_units()
        if units == 'inches':
            # Slider step = 0.5 inch; store as inches
            half_in = self.scale_bar_length_slider.value() / 2.0
            config.set_scale_bar_length_in(half_in)
        else:
            # Centimeters, step = 1 cm
            cm = self.scale_bar_length_slider.value()
            config.set_scale_bar_length_cm(cm)

        # Logging settings
        config.set_logging_enabled(self.logging_enabled_check.isChecked())
        config.set_logging_level(self.logging_level_combo.currentText())
        config.set_logging_component_enabled('printing', self.log_printing_check.isChecked())
        config.set_logging_component_enabled('projects', self.log_projects_check.isChecked())
        config.set_logging_component_enabled('preview', self.log_preview_check.isChecked())
        config.set_logging_component_enabled('viewer', self.log_viewer_check.isChecked())
        config.set_logging_component_enabled('export', self.log_export_check.isChecked())
        config.set_logging_component_enabled('metadata', self.log_metadata_check.isChecked())
        config.set_logging_component_enabled('settings', self.log_settings_check.isChecked())

        # Project settings
        config.set_project_original_storage(self.project_storage_combo.currentText())

        # Datum line settings
        config.set_datum_line_display(self.datum_display_check.isChecked())
        config.set_datum_line_print(self.datum_print_check.isChecked())
        config.set_datum_line_style(self.datum_style_combo.currentText())
        config.set_datum_line_width_px(self.datum_width_spin.value())
        config.set_datum_line_color(self.datum_color.name())

        # Measurement print convenience: if toggled, set both underlying options
        if hasattr(self, 'measure_print_check'):
            want = bool(self.measure_print_check.isChecked())
            config.set_scale_line_print(want)
            config.set_scale_text_print(want)

    def choose_datum_color(self):
        color = QColorDialog.getColor(self.datum_color, self, "Choose Datum Line Color")
        if color.isValid():
            self.datum_color = color
            self.update_datum_color_button()

    def update_datum_color_button(self):
        if hasattr(self, 'datum_color') and self.datum_color:
            self.datum_color_button.setStyleSheet(f"background-color: {self.datum_color.name()}; border: 1px solid #888;")

    def _configure_scale_bar_length_slider(self):
        """Configure the scale bar length slider according to current units."""
        units = config.get_default_units()
        if units == 'inches':
            # Range 1–24 inches, step 0.5; encode as halves
            self.scale_bar_length_slider.setRange(2, 48)
            self.scale_bar_length_slider.setSingleStep(1)
            val_in = config.get_scale_bar_length_in()
            slider_val = int(round(val_in * 2.0))
            self.scale_bar_length_slider.setValue(slider_val)
            self.scale_bar_length_value.setText(f"{val_in:.1f} in")
            self.scale_bar_length_slider.valueChanged.connect(
                lambda v: self.scale_bar_length_value.setText(f"{v/2.0:.1f} in")
            )
        else:
            # Range 1–50 cm, step 1
            self.scale_bar_length_slider.setRange(1, 50)
            self.scale_bar_length_slider.setSingleStep(1)
            val_cm = int(round(config.get_scale_bar_length_cm()))
            self.scale_bar_length_slider.setValue(val_cm)
            self.scale_bar_length_value.setText(f"{val_cm} cm")
            self.scale_bar_length_slider.valueChanged.connect(
                lambda v: self.scale_bar_length_value.setText(f"{v} cm")
            )

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
