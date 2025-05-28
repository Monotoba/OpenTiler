#!/usr/bin/env python3
"""
Plugin Manager for OpenTiler Plugin System

This module manages the loading, initialization, and lifecycle of plugins.
"""

import os
import sys
import importlib
import importlib.util
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from PySide6.QtCore import QObject, Signal

from .base_plugin import BasePlugin, PluginInfo, PluginLoadError, PluginInitError
from .plugin_registry import PluginRegistry
from .hook_system import get_hook_manager
from .content_access import ContentAccessManager, AccessLevel


class PluginManager(QObject):
    """
    Manages OpenTiler plugins.

    Handles plugin discovery, loading, initialization, and lifecycle management.
    """

    # Signals
    plugin_loaded = Signal(str)      # Plugin name
    plugin_enabled = Signal(str)     # Plugin name
    plugin_disabled = Signal(str)    # Plugin name
    plugin_error = Signal(str, str)  # Plugin name, error message

    def __init__(self, main_window=None, config_dir: Optional[str] = None):
        """
        Initialize the plugin manager.

        Args:
            main_window: Reference to OpenTiler's main window
            config_dir: Directory for plugin configuration files
        """
        super().__init__()
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)

        # Plugin storage
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}

        # Plugin registry
        self.registry = PluginRegistry()

        # Hook system
        self.hook_manager = get_hook_manager()

        # Content access manager
        self.content_access_manager = ContentAccessManager(main_window)

        # Configuration
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / "config" / "plugins"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Plugin directories
        self.plugin_dirs = [
            Path(__file__).parent / "builtin",  # Built-in plugins
            Path.cwd() / "plugins" / "external",  # External plugins
            self.config_dir / "user"  # User plugins
        ]

        # Ensure plugin directories exist
        for plugin_dir in self.plugin_dirs:
            plugin_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self._load_config()

    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugin directories.

        Returns:
            List of discovered plugin names
        """
        discovered = []

        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue

            self.logger.info(f"Scanning plugin directory: {plugin_dir}")

            # Look for Python files and packages
            for item in plugin_dir.iterdir():
                if item.is_file() and item.suffix == '.py' and not item.name.startswith('_'):
                    # Single file plugin
                    plugin_name = item.stem
                    if self._is_valid_plugin(item):
                        discovered.append(plugin_name)
                        self.logger.info(f"Discovered plugin: {plugin_name}")

                elif item.is_dir() and not item.name.startswith('_'):
                    # Package plugin
                    init_file = item / "__init__.py"
                    if init_file.exists() and self._is_valid_plugin(init_file):
                        plugin_name = item.name
                        discovered.append(plugin_name)
                        self.logger.info(f"Discovered plugin package: {plugin_name}")

        return discovered

    def _is_valid_plugin(self, plugin_path: Path) -> bool:
        """
        Check if a file/package is a valid plugin.

        Args:
            plugin_path: Path to plugin file or __init__.py

        Returns:
            True if valid plugin
        """
        try:
            # Read file and check for BasePlugin inheritance
            with open(plugin_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return 'BasePlugin' in content and 'class' in content
        except Exception:
            return False

    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a specific plugin.

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            True if loaded successfully
        """
        if plugin_name in self.plugins:
            self.logger.warning(f"Plugin {plugin_name} already loaded")
            return True

        try:
            # Find plugin file
            plugin_path = self._find_plugin_path(plugin_name)
            if not plugin_path:
                raise PluginLoadError(plugin_name, f"Plugin file not found")

            # Load plugin module
            plugin_class = self._load_plugin_module(plugin_name, plugin_path)
            if not plugin_class:
                raise PluginLoadError(plugin_name, "No valid plugin class found")

            # Create plugin instance
            plugin_instance = plugin_class(self.main_window)

            # Validate plugin
            if not isinstance(plugin_instance, BasePlugin):
                raise PluginLoadError(plugin_name, "Plugin does not inherit from BasePlugin")

            # Store plugin
            self.plugin_classes[plugin_name] = plugin_class
            self.plugins[plugin_name] = plugin_instance

            # Register plugin
            self.registry.register_plugin(plugin_instance.plugin_info)

            # Connect signals
            plugin_instance.status_changed.connect(
                lambda msg: self.logger.info(f"Plugin {plugin_name}: {msg}")
            )
            plugin_instance.error_occurred.connect(
                lambda msg: self.plugin_error.emit(plugin_name, msg)
            )

            self.logger.info(f"Loaded plugin: {plugin_name}")
            self.plugin_loaded.emit(plugin_name)
            return True

        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            self.plugin_error.emit(plugin_name, str(e))
            return False

    def _find_plugin_path(self, plugin_name: str) -> Optional[Path]:
        """Find the path to a plugin file."""
        for plugin_dir in self.plugin_dirs:
            # Check for single file plugin
            plugin_file = plugin_dir / f"{plugin_name}.py"
            if plugin_file.exists():
                return plugin_file

            # Check for package plugin
            plugin_package = plugin_dir / plugin_name / "__init__.py"
            if plugin_package.exists():
                return plugin_package

        return None

    def _load_plugin_module(self, plugin_name: str, plugin_path: Path) -> Optional[Type[BasePlugin]]:
        """Load plugin module and return plugin class."""
        try:
            # Create module spec
            if plugin_path.name == "__init__.py":
                # Package plugin
                module_name = f"plugins.{plugin_path.parent.name}"
                spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            else:
                # Single file plugin
                module_name = f"plugins.{plugin_name}"
                spec = importlib.util.spec_from_file_location(module_name, plugin_path)

            if not spec or not spec.loader:
                return None

            # Load module
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, BasePlugin) and
                    attr != BasePlugin):
                    return attr

            return None

        except Exception as e:
            self.logger.error(f"Failed to load module for {plugin_name}: {e}")
            return None

    def initialize_plugin(self, plugin_name: str) -> bool:
        """
        Initialize a loaded plugin.

        Args:
            plugin_name: Name of the plugin to initialize

        Returns:
            True if initialized successfully
        """
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin {plugin_name} not loaded")
            return False

        plugin = self.plugins[plugin_name]

        try:
            # Load plugin configuration
            config = self.plugin_configs.get(plugin_name, {})
            plugin.set_config(config)

            # Initialize plugin
            if plugin.initialize():
                plugin._initialized = True

                # Register hook handlers
                hook_handlers = plugin.get_hook_handlers()
                for handler in hook_handlers:
                    self.hook_manager.register_handler(handler, plugin_name)

                # Setup content access
                requirements = plugin.get_document_access_requirements()
                if any(requirements.values()):
                    # Determine access level based on plugin requirements
                    access_level = AccessLevel.READ_ONLY
                    if requirements.get('transformations', False):
                        access_level = AccessLevel.FULL_CONTROL
                    elif any(requirements.get(key, False) for key in ['measurements', 'tile_preview']):
                        access_level = AccessLevel.READ_WRITE

                    # Grant access
                    access_objects = self.content_access_manager.grant_access(
                        plugin_name, requirements, access_level
                    )

                    # Store access reference in plugin if it has the attribute
                    if hasattr(plugin, 'content_access_objects'):
                        plugin.content_access_objects = access_objects

                self.logger.info(f"Initialized plugin: {plugin_name}")
                return True
            else:
                raise PluginInitError(plugin_name, "Plugin initialization returned False")

        except Exception as e:
            self.logger.error(f"Failed to initialize plugin {plugin_name}: {e}")
            self.plugin_error.emit(plugin_name, str(e))
            return False

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name not in self.plugins:
            return False

        plugin = self.plugins[plugin_name]

        if not plugin.initialized:
            if not self.initialize_plugin(plugin_name):
                return False

        try:
            if plugin.enable():
                plugin._enabled = True
                self.logger.info(f"Enabled plugin: {plugin_name}")
                self.plugin_enabled.emit(plugin_name)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to enable plugin {plugin_name}: {e}")
            return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name not in self.plugins:
            return False

        plugin = self.plugins[plugin_name]

        try:
            if plugin.disable():
                plugin._enabled = False
                self.logger.info(f"Disabled plugin: {plugin_name}")
                self.plugin_disabled.emit(plugin_name)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to disable plugin {plugin_name}: {e}")
            return False

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """Get a plugin instance by name."""
        return self.plugins.get(plugin_name)

    def get_enabled_plugins(self) -> List[str]:
        """Get list of enabled plugin names."""
        return [name for name, plugin in self.plugins.items() if plugin.enabled]

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get plugin information."""
        plugin = self.plugins.get(plugin_name)
        return plugin.plugin_info if plugin else None

    def _load_config(self) -> None:
        """Load plugin configurations."""
        config_file = self.config_dir / "plugins.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.plugin_configs = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load plugin config: {e}")

    def _save_config(self) -> None:
        """Save plugin configurations."""
        config_file = self.config_dir / "plugins.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(self.plugin_configs, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save plugin config: {e}")

    def shutdown(self) -> None:
        """Shutdown plugin manager and cleanup all plugins."""
        for plugin_name, plugin in self.plugins.items():
            try:
                if plugin.enabled:
                    plugin.disable()
                plugin.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up plugin {plugin_name}: {e}")

        self._save_config()
        self.plugins.clear()
        self.plugin_classes.clear()
