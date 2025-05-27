"""
Configuration management for OpenTiler.
"""

import os
import json
from pathlib import Path
from PySide6.QtCore import QSettings


class Config:
    """Configuration manager for OpenTiler."""

    def __init__(self):
        self.settings = QSettings("RandallMorgan", "OpenTiler")
        self.load_defaults()

    def load_defaults(self):
        """Load default configuration values."""
        # Set defaults if not already set
        if not self.settings.contains("default_units"):
            self.settings.setValue("default_units", "mm")

        if not self.settings.contains("default_dpi"):
            self.settings.setValue("default_dpi", 300)

        if not self.settings.contains("default_page_size"):
            self.settings.setValue("default_page_size", "A4")

        if not self.settings.contains("last_input_dir"):
            self.settings.setValue("last_input_dir", str(Path.home()))

        if not self.settings.contains("last_output_dir"):
            self.settings.setValue("last_output_dir", str(Path.home()))

        if not self.settings.contains("window_geometry"):
            self.settings.setValue("window_geometry", "")

        if not self.settings.contains("window_state"):
            self.settings.setValue("window_state", "")

        # Tiling and display settings
        if not self.settings.contains("gutter_size_mm"):
            self.settings.setValue("gutter_size_mm", 10.0)

        if not self.settings.contains("page_orientation"):
            self.settings.setValue("page_orientation", "auto")  # auto, landscape, portrait

        # Page indicator settings
        if not self.settings.contains("page_indicator_position"):
            self.settings.setValue("page_indicator_position", "bottom-right")

        if not self.settings.contains("page_indicator_font_size"):
            self.settings.setValue("page_indicator_font_size", 12)

        if not self.settings.contains("page_indicator_font_color"):
            self.settings.setValue("page_indicator_font_color", "#FFFFFF")  # White

        if not self.settings.contains("page_indicator_font_style"):
            self.settings.setValue("page_indicator_font_style", "bold")

        if not self.settings.contains("page_indicator_alpha"):
            self.settings.setValue("page_indicator_alpha", 255)  # Fully opaque

        if not self.settings.contains("page_indicator_display"):
            self.settings.setValue("page_indicator_display", True)

        if not self.settings.contains("page_indicator_print"):
            self.settings.setValue("page_indicator_print", True)

        # Gutter line settings
        if not self.settings.contains("gutter_lines_display"):
            self.settings.setValue("gutter_lines_display", True)

        if not self.settings.contains("gutter_lines_print"):
            self.settings.setValue("gutter_lines_print", True)

        # Crop mark settings
        if not self.settings.contains("crop_marks_display"):
            self.settings.setValue("crop_marks_display", True)

        if not self.settings.contains("crop_marks_print"):
            self.settings.setValue("crop_marks_print", True)

        # Scale line and text settings
        if not self.settings.contains("scale_line_display"):
            self.settings.setValue("scale_line_display", True)

        if not self.settings.contains("scale_line_print"):
            self.settings.setValue("scale_line_print", True)

        if not self.settings.contains("scale_text_display"):
            self.settings.setValue("scale_text_display", True)

        if not self.settings.contains("scale_text_print"):
            self.settings.setValue("scale_text_print", True)

        # Recent files settings
        if not self.settings.contains("recent_files"):
            self.settings.setValue("recent_files", "[]")  # Store as JSON string

        if not self.settings.contains("max_recent_files"):
            self.settings.setValue("max_recent_files", 10)

        # Metadata page settings
        if not self.settings.contains("include_metadata_page"):
            self.settings.setValue("include_metadata_page", True)

        if not self.settings.contains("metadata_page_position"):
            self.settings.setValue("metadata_page_position", "first")  # first, last

    def get(self, key, default=None):
        """Get a configuration value."""
        return self.settings.value(key, default)

    def set(self, key, value):
        """Set a configuration value."""
        self.settings.setValue(key, value)

    def get_default_units(self):
        """Get default units (mm or inches)."""
        return self.get("default_units", "mm")

    def set_default_units(self, units):
        """Set default units."""
        self.set("default_units", units)

    def get_default_dpi(self):
        """Get default DPI."""
        return int(self.get("default_dpi", 300))

    def set_default_dpi(self, dpi):
        """Set default DPI."""
        self.set("default_dpi", dpi)

    def get_default_page_size(self):
        """Get default page size."""
        return self.get("default_page_size", "A4")

    def set_default_page_size(self, page_size):
        """Set default page size."""
        self.set("default_page_size", page_size)

    def get_last_input_dir(self):
        """Get last used input directory."""
        return self.get("last_input_dir", str(Path.home()))

    def set_last_input_dir(self, directory):
        """Set last used input directory."""
        self.set("last_input_dir", directory)

    def get_last_output_dir(self):
        """Get last used output directory."""
        return self.get("last_output_dir", str(Path.home()))

    def set_last_output_dir(self, directory):
        """Set last used output directory."""
        self.set("last_output_dir", directory)

    def get_window_geometry(self):
        """Get saved window geometry."""
        return self.get("window_geometry", "")

    def set_window_geometry(self, geometry):
        """Set window geometry."""
        self.set("window_geometry", geometry)

    def get_window_state(self):
        """Get saved window state."""
        return self.get("window_state", "")

    def set_window_state(self, state):
        """Set window state."""
        self.set("window_state", state)

    def sync(self):
        """Synchronize settings to disk."""
        self.settings.sync()

    # Tiling settings
    def get_gutter_size_mm(self):
        """Get gutter size in millimeters."""
        return float(self.get("gutter_size_mm", 10.0))

    def set_gutter_size_mm(self, size):
        """Set gutter size in millimeters."""
        self.set("gutter_size_mm", float(size))

    def get_page_orientation(self):
        """Get page orientation preference."""
        return self.get("page_orientation", "auto")

    def set_page_orientation(self, orientation):
        """Set page orientation preference."""
        self.set("page_orientation", orientation)

    # Page indicator settings
    def get_page_indicator_position(self):
        """Get page indicator position."""
        return self.get("page_indicator_position", "bottom-right")

    def set_page_indicator_position(self, position):
        """Set page indicator position."""
        self.set("page_indicator_position", position)

    def get_page_indicator_font_size(self):
        """Get page indicator font size."""
        return int(self.get("page_indicator_font_size", 12))

    def set_page_indicator_font_size(self, size):
        """Set page indicator font size."""
        self.set("page_indicator_font_size", int(size))

    def get_page_indicator_font_color(self):
        """Get page indicator font color."""
        return self.get("page_indicator_font_color", "#FFFFFF")

    def set_page_indicator_font_color(self, color):
        """Set page indicator font color."""
        self.set("page_indicator_font_color", color)

    def get_page_indicator_font_style(self):
        """Get page indicator font style."""
        return self.get("page_indicator_font_style", "bold")

    def set_page_indicator_font_style(self, style):
        """Set page indicator font style."""
        self.set("page_indicator_font_style", style)

    def get_page_indicator_alpha(self):
        """Get page indicator alpha (transparency)."""
        return int(self.get("page_indicator_alpha", 255))

    def set_page_indicator_alpha(self, alpha):
        """Set page indicator alpha (transparency)."""
        self.set("page_indicator_alpha", int(alpha))

    def get_page_indicator_display(self):
        """Get whether to display page indicators."""
        value = self.get("page_indicator_display", True)
        return str(value).lower() == 'true' if isinstance(value, str) else bool(value)

    def set_page_indicator_display(self, display):
        """Set whether to display page indicators."""
        self.set("page_indicator_display", bool(display))

    def get_page_indicator_print(self):
        """Get whether to print page indicators."""
        value = self.get("page_indicator_print", True)
        return str(value).lower() == 'true' if isinstance(value, str) else bool(value)

    def set_page_indicator_print(self, print_enabled):
        """Set whether to print page indicators."""
        self.set("page_indicator_print", bool(print_enabled))

    # Gutter line settings
    def get_gutter_lines_display(self):
        """Get whether to display gutter lines."""
        value = self.get("gutter_lines_display", True)
        return str(value).lower() == 'true' if isinstance(value, str) else bool(value)

    def set_gutter_lines_display(self, display):
        """Set whether to display gutter lines."""
        self.set("gutter_lines_display", bool(display))

    def get_gutter_lines_print(self):
        """Get whether to print gutter lines."""
        value = self.get("gutter_lines_print", True)
        return str(value).lower() == 'true' if isinstance(value, str) else bool(value)

    def set_gutter_lines_print(self, print_enabled):
        """Set whether to print gutter lines."""
        self.set("gutter_lines_print", bool(print_enabled))

    # Crop mark settings
    def get_crop_marks_display(self):
        """Get whether to display crop marks."""
        value = self.get("crop_marks_display", True)
        return str(value).lower() == 'true' if isinstance(value, str) else bool(value)

    def set_crop_marks_display(self, display):
        """Set whether to display crop marks."""
        self.set("crop_marks_display", bool(display))

    def get_crop_marks_print(self):
        """Get whether to print crop marks."""
        value = self.get("crop_marks_print", True)
        return str(value).lower() == 'true' if isinstance(value, str) else bool(value)

    def set_crop_marks_print(self, print_enabled):
        """Set whether to print crop marks."""
        self.set("crop_marks_print", bool(print_enabled))

    # Scale line and text settings
    def get_scale_line_display(self):
        """Get whether to display scale line."""
        value = self.get("scale_line_display", True)
        return str(value).lower() == 'true' if isinstance(value, str) else bool(value)

    def set_scale_line_display(self, display):
        """Set whether to display scale line."""
        self.set("scale_line_display", bool(display))

    def get_scale_line_print(self):
        """Get whether to print scale line."""
        value = self.get("scale_line_print", True)
        return str(value).lower() == 'true' if isinstance(value, str) else bool(value)

    def set_scale_line_print(self, print_enabled):
        """Set whether to print scale line."""
        self.set("scale_line_print", bool(print_enabled))

    def get_scale_text_display(self):
        """Get whether to display scale text."""
        value = self.get("scale_text_display", True)
        return str(value).lower() == 'true' if isinstance(value, str) else bool(value)

    def set_scale_text_display(self, display):
        """Set whether to display scale text."""
        self.set("scale_text_display", bool(display))

    def get_scale_text_print(self):
        """Get whether to print scale text."""
        value = self.get("scale_text_print", True)
        return str(value).lower() == 'true' if isinstance(value, str) else bool(value)

    def set_scale_text_print(self, print_enabled):
        """Set whether to print scale text."""
        self.set("scale_text_print", bool(print_enabled))

    # Recent files settings
    def get_recent_files(self):
        """Get list of recent files."""
        files_json = self.get("recent_files", "[]")
        try:
            # Parse JSON string to list
            files = json.loads(files_json)
            return files if isinstance(files, list) else []
        except (json.JSONDecodeError, TypeError):
            return []

    def add_recent_file(self, file_path):
        """Add a file to the recent files list."""
        recent_files = self.get_recent_files()

        # Remove if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)

        # Add to beginning
        recent_files.insert(0, file_path)

        # Limit to max recent files
        max_files = self.get_max_recent_files()
        recent_files = recent_files[:max_files]

        # Store as JSON string
        self.set("recent_files", json.dumps(recent_files))
        self.sync()

    def remove_recent_file(self, file_path):
        """Remove a file from the recent files list."""
        recent_files = self.get_recent_files()
        if file_path in recent_files:
            recent_files.remove(file_path)
            self.set("recent_files", json.dumps(recent_files))
            self.sync()

    def clear_recent_files(self):
        """Clear all recent files."""
        self.set("recent_files", "[]")
        self.sync()

    def get_max_recent_files(self):
        """Get maximum number of recent files to keep."""
        return int(self.get("max_recent_files", 10))

    def set_max_recent_files(self, max_files):
        """Set maximum number of recent files to keep."""
        self.set("max_recent_files", int(max_files))

    # Metadata page settings
    def get_include_metadata_page(self):
        """Get whether to include metadata page in exports."""
        return bool(self.get("include_metadata_page", True))

    def set_include_metadata_page(self, include):
        """Set whether to include metadata page in exports."""
        self.set("include_metadata_page", bool(include))

    def get_metadata_page_position(self):
        """Get metadata page position (first or last)."""
        return self.get("metadata_page_position", "first")

    def set_metadata_page_position(self, position):
        """Set metadata page position."""
        self.set("metadata_page_position", position)


# Global configuration instance
config = Config()
