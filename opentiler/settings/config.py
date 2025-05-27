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

        # Crop mark settings
        if not self.settings.contains("crop_marks_display"):
            self.settings.setValue("crop_marks_display", True)

        if not self.settings.contains("crop_marks_print"):
            self.settings.setValue("crop_marks_print", True)

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
        return self.get("page_indicator_display", True) == True

    def set_page_indicator_display(self, display):
        """Set whether to display page indicators."""
        self.set("page_indicator_display", bool(display))

    def get_page_indicator_print(self):
        """Get whether to print page indicators."""
        return self.get("page_indicator_print", True) == True

    def set_page_indicator_print(self, print_enabled):
        """Set whether to print page indicators."""
        self.set("page_indicator_print", bool(print_enabled))

    # Crop mark settings
    def get_crop_marks_display(self):
        """Get whether to display crop marks."""
        return self.get("crop_marks_display", True) == True

    def set_crop_marks_display(self, display):
        """Set whether to display crop marks."""
        self.set("crop_marks_display", bool(display))

    def get_crop_marks_print(self):
        """Get whether to print crop marks."""
        return self.get("crop_marks_print", True) == True

    def set_crop_marks_print(self, print_enabled):
        """Set whether to print crop marks."""
        self.set("crop_marks_print", bool(print_enabled))


# Global configuration instance
config = Config()
