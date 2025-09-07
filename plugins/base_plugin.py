#!/usr/bin/env python3
"""
Base Plugin Class for OpenTiler Plugin System

This module defines the base plugin interface that all OpenTiler plugins must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWidget

from .hook_system import HookContext, HookHandler, HookType, get_hook_manager


@dataclass
class PluginInfo:
    """Plugin metadata information."""

    name: str
    version: str
    description: str
    author: str
    website: Optional[str] = None
    license: Optional[str] = None
    dependencies: Optional[List[str]] = None
    min_opentiler_version: Optional[str] = None
    max_opentiler_version: Optional[str] = None


class BasePlugin(QObject):
    """
    Base class for all OpenTiler plugins.

    All plugins must inherit from this class and implement the required methods.
    """

    # Signals
    status_changed = Signal(str)  # Plugin status messages
    error_occurred = Signal(str)  # Plugin error messages

    def __init__(self, main_window=None):
        """
        Initialize the plugin.

        Args:
            main_window: Reference to OpenTiler's main window
        """
        super().__init__()
        self.main_window = main_window
        self._enabled = False
        self._initialized = False

    @property
    @abstractmethod
    def plugin_info(self) -> PluginInfo:
        """Return plugin information."""
        pass

    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled

    @property
    def initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self._initialized

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin.

        Called when the plugin is first loaded.

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    def enable(self) -> bool:
        """
        Enable the plugin.

        Called when the plugin should become active.

        Returns:
            True if enabled successfully, False otherwise
        """
        pass

    @abstractmethod
    def disable(self) -> bool:
        """
        Disable the plugin.

        Called when the plugin should become inactive.

        Returns:
            True if disabled successfully, False otherwise
        """
        pass

    @abstractmethod
    def cleanup(self) -> bool:
        """
        Clean up plugin resources.

        Called when the plugin is being unloaded.

        Returns:
            True if cleanup successful, False otherwise
        """
        pass

    def get_menu_actions(self) -> List[QAction]:
        """
        Get menu actions to add to OpenTiler's menu system.

        Returns:
            List of QAction objects to add to menus
        """
        return []

    def get_toolbar_actions(self) -> List[QAction]:
        """
        Get toolbar actions to add to OpenTiler's toolbar.

        Returns:
            List of QAction objects to add to toolbar
        """
        return []

    def get_settings_widget(self) -> Optional[QWidget]:
        """
        Get settings widget for plugin configuration.

        Returns:
            QWidget for plugin settings, or None if no settings
        """
        return None

    def get_keyboard_shortcuts(self) -> Dict[str, callable]:
        """
        Get keyboard shortcuts provided by this plugin.

        Returns:
            Dictionary mapping shortcut strings to callable functions
        """
        return {}

    def get_hook_handlers(self) -> List[HookHandler]:
        """
        Get hook handlers provided by this plugin.

        Returns:
            List of HookHandler instances
        """
        return []

    def get_document_access_requirements(self) -> Dict[str, bool]:
        """
        Get document access requirements for this plugin.

        Returns:
            Dictionary specifying required access levels:
            - 'plan_view': Access to plan view content
            - 'tile_preview': Access to tile preview content
            - 'document_data': Access to raw document data
            - 'metadata': Access to document metadata
            - 'measurements': Access to measurement data
            - 'transformations': Access to transformation data
        """
        return {
            "plan_view": False,
            "tile_preview": False,
            "document_data": False,
            "metadata": False,
            "measurements": False,
            "transformations": False,
        }

    def handle_document_loaded(self, document_path: str) -> None:
        """
        Handle document loaded event.

        Args:
            document_path: Path to the loaded document
        """
        pass

    def handle_document_closed(self) -> None:
        """Handle document closed event."""
        pass

    def handle_export_started(self, export_settings: Dict[str, Any]) -> None:
        """
        Handle export started event.

        Args:
            export_settings: Export configuration settings
        """
        pass

    def handle_export_finished(self, success: bool, output_path: str) -> None:
        """
        Handle export finished event.

        Args:
            success: Whether export was successful
            output_path: Path to exported files
        """
        pass

    def get_config(self) -> Dict[str, Any]:
        """
        Get plugin configuration.

        Returns:
            Dictionary of configuration settings
        """
        return {}

    def set_config(self, config: Dict[str, Any]) -> bool:
        """
        Set plugin configuration.

        Args:
            config: Dictionary of configuration settings

        Returns:
            True if configuration was applied successfully
        """
        return True

    def get_status(self) -> str:
        """
        Get current plugin status.

        Returns:
            Human-readable status string
        """
        if not self._initialized:
            return "Not initialized"
        elif self._enabled:
            return "Enabled"
        else:
            return "Disabled"

    def log_info(self, message: str) -> None:
        """Log info message."""
        self.status_changed.emit(f"[{self.plugin_info.name}] {message}")

    def log_error(self, message: str) -> None:
        """Log error message."""
        self.error_occurred.emit(f"[{self.plugin_info.name}] ERROR: {message}")


class PluginException(Exception):
    """Exception raised by plugins."""

    def __init__(self, plugin_name: str, message: str):
        self.plugin_name = plugin_name
        self.message = message
        super().__init__(f"Plugin '{plugin_name}': {message}")


class PluginLoadError(PluginException):
    """Exception raised when plugin fails to load."""

    pass


class PluginInitError(PluginException):
    """Exception raised when plugin fails to initialize."""

    pass
