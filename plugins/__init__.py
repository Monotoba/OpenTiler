# OpenTiler Plugin System
"""
OpenTiler Plugin System

This module provides the core infrastructure for OpenTiler's plugin system,
allowing for extensible functionality through dynamically loaded plugins.
"""

__version__ = "1.0.0"
__author__ = "OpenTiler Development Team"

from .base_plugin import BasePlugin, PluginInfo
from .plugin_manager import PluginManager
from .plugin_registry import PluginRegistry

__all__ = ["PluginManager", "BasePlugin", "PluginInfo", "PluginRegistry"]
