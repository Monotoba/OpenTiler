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


# Global configuration instance
config = Config()
