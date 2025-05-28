#!/usr/bin/env python3
"""
OpenTiler Plugin System Integration

This module integrates the plugin system into OpenTiler's main application.
Add this to your main.py or create a separate module for plugin integration.
"""

import sys
import logging
import argparse
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QMessageBox
from PySide6.QtCore import QTimer

# Import plugin system
from plugins import PluginManager, BasePlugin


class OpenTilerWithPlugins:
    """
    OpenTiler application with plugin system integration.
    
    This class shows how to integrate the plugin system into OpenTiler.
    """
    
    def __init__(self, main_window: QMainWindow):
        """
        Initialize OpenTiler with plugin support.
        
        Args:
            main_window: OpenTiler's main window
        """
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Plugin system
        self.plugin_manager = None
        self.automation_mode = False
        
        # Plugin menu
        self.plugins_menu = None
        
    def initialize_plugin_system(self, automation_mode: bool = False) -> bool:
        """
        Initialize the plugin system.
        
        Args:
            automation_mode: Enable automation mode for documentation
            
        Returns:
            True if initialized successfully
        """
        try:
            self.automation_mode = automation_mode
            
            # Create plugin manager
            self.plugin_manager = PluginManager(
                main_window=self.main_window,
                config_dir="config/plugins"
            )
            
            # Connect plugin manager signals
            self.plugin_manager.plugin_loaded.connect(self._on_plugin_loaded)
            self.plugin_manager.plugin_enabled.connect(self._on_plugin_enabled)
            self.plugin_manager.plugin_disabled.connect(self._on_plugin_disabled)
            self.plugin_manager.plugin_error.connect(self._on_plugin_error)
            
            # Create plugins menu
            self._create_plugins_menu()
            
            # Discover and load plugins
            self._discover_and_load_plugins()
            
            # Auto-enable automation plugin if in automation mode
            if automation_mode:
                self._enable_automation_mode()
            
            self.logger.info("Plugin system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize plugin system: {e}")
            return False
    
    def _discover_and_load_plugins(self):
        """Discover and load available plugins."""
        try:
            # Discover plugins
            discovered_plugins = self.plugin_manager.discover_plugins()
            self.logger.info(f"Discovered {len(discovered_plugins)} plugins: {discovered_plugins}")
            
            # Load plugins
            for plugin_name in discovered_plugins:
                success = self.plugin_manager.load_plugin(plugin_name)
                if success:
                    self.logger.info(f"Loaded plugin: {plugin_name}")
                else:
                    self.logger.warning(f"Failed to load plugin: {plugin_name}")
            
            # Initialize and enable plugins based on configuration
            self._initialize_enabled_plugins()
            
        except Exception as e:
            self.logger.error(f"Error during plugin discovery: {e}")
    
    def _initialize_enabled_plugins(self):
        """Initialize and enable plugins based on configuration."""
        # For now, enable all loaded plugins
        # In a real implementation, this would check user preferences
        
        for plugin_name in self.plugin_manager.plugins.keys():
            try:
                # Initialize plugin
                if self.plugin_manager.initialize_plugin(plugin_name):
                    # Enable plugin
                    self.plugin_manager.enable_plugin(plugin_name)
                    self.logger.info(f"Enabled plugin: {plugin_name}")
                else:
                    self.logger.warning(f"Failed to initialize plugin: {plugin_name}")
                    
            except Exception as e:
                self.logger.error(f"Error enabling plugin {plugin_name}: {e}")
    
    def _enable_automation_mode(self):
        """Enable automation mode for documentation generation."""
        automation_plugin = self.plugin_manager.get_plugin("automation")
        if automation_plugin:
            self.logger.info("Automation mode enabled - documentation features active")
            
            # Show automation status in status bar if available
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("Automation Mode: Documentation features enabled", 5000)
        else:
            self.logger.warning("Automation plugin not available")
    
    def _create_plugins_menu(self):
        """Create the plugins menu in the menu bar."""
        if not hasattr(self.main_window, 'menuBar'):
            return
        
        menu_bar = self.main_window.menuBar()
        
        # Create Plugins menu
        self.plugins_menu = menu_bar.addMenu("&Plugins")
        
        # Add plugin management actions
        self._add_plugin_management_actions()
    
    def _add_plugin_management_actions(self):
        """Add plugin management actions to the plugins menu."""
        if not self.plugins_menu:
            return
        
        # Plugin Manager action
        manager_action = QAction("Plugin &Manager", self.main_window)
        manager_action.setStatusTip("Open plugin manager")
        manager_action.triggered.connect(self._show_plugin_manager)
        self.plugins_menu.addAction(manager_action)
        
        # Reload Plugins action
        reload_action = QAction("&Reload Plugins", self.main_window)
        reload_action.setStatusTip("Reload all plugins")
        reload_action.triggered.connect(self._reload_plugins)
        self.plugins_menu.addAction(reload_action)
        
        self.plugins_menu.addSeparator()
        
        # Plugin-specific actions will be added here
        self._update_plugin_menu()
    
    def _update_plugin_menu(self):
        """Update the plugins menu with plugin-specific actions."""
        if not self.plugins_menu or not self.plugin_manager:
            return
        
        # Remove existing plugin actions (keep management actions)
        actions = self.plugins_menu.actions()
        for action in actions[3:]:  # Skip first 3 (manager, reload, separator)
            self.plugins_menu.removeAction(action)
        
        # Add actions from enabled plugins
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            if plugin.enabled:
                # Add plugin menu actions
                plugin_actions = plugin.get_menu_actions()
                if plugin_actions:
                    plugin_submenu = self.plugins_menu.addMenu(plugin.plugin_info.name)
                    for action in plugin_actions:
                        plugin_submenu.addAction(action)
    
    def _show_plugin_manager(self):
        """Show the plugin manager dialog."""
        # This would open a plugin manager dialog
        # For now, show a simple message box with plugin status
        
        if not self.plugin_manager:
            QMessageBox.warning(self.main_window, "Plugin Manager", "Plugin system not initialized")
            return
        
        plugin_info = []
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            status = "Enabled" if plugin.enabled else "Disabled"
            info = plugin.plugin_info
            plugin_info.append(f"{info.name} v{info.version} - {status}")
        
        if plugin_info:
            message = "Loaded Plugins:\n\n" + "\n".join(plugin_info)
        else:
            message = "No plugins loaded"
        
        QMessageBox.information(self.main_window, "Plugin Manager", message)
    
    def _reload_plugins(self):
        """Reload all plugins."""
        if not self.plugin_manager:
            return
        
        try:
            # Disable all plugins
            for plugin_name in list(self.plugin_manager.plugins.keys()):
                self.plugin_manager.disable_plugin(plugin_name)
            
            # Clear plugins
            self.plugin_manager.plugins.clear()
            self.plugin_manager.plugin_classes.clear()
            
            # Rediscover and load plugins
            self._discover_and_load_plugins()
            
            # Update menu
            self._update_plugin_menu()
            
            self.logger.info("Plugins reloaded successfully")
            
            if hasattr(self.main_window, 'statusBar'):
                self.main_window.statusBar().showMessage("Plugins reloaded", 3000)
                
        except Exception as e:
            self.logger.error(f"Failed to reload plugins: {e}")
            QMessageBox.critical(self.main_window, "Error", f"Failed to reload plugins: {e}")
    
    def _on_plugin_loaded(self, plugin_name: str):
        """Handle plugin loaded signal."""
        self.logger.info(f"Plugin loaded: {plugin_name}")
        self._update_plugin_menu()
    
    def _on_plugin_enabled(self, plugin_name: str):
        """Handle plugin enabled signal."""
        self.logger.info(f"Plugin enabled: {plugin_name}")
        self._update_plugin_menu()
        
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(f"Plugin enabled: {plugin_name}", 2000)
    
    def _on_plugin_disabled(self, plugin_name: str):
        """Handle plugin disabled signal."""
        self.logger.info(f"Plugin disabled: {plugin_name}")
        self._update_plugin_menu()
        
        if hasattr(self.main_window, 'statusBar'):
            self.main_window.statusBar().showMessage(f"Plugin disabled: {plugin_name}", 2000)
    
    def _on_plugin_error(self, plugin_name: str, error_message: str):
        """Handle plugin error signal."""
        self.logger.error(f"Plugin error in {plugin_name}: {error_message}")
        
        # Show error to user
        QMessageBox.warning(
            self.main_window,
            "Plugin Error",
            f"Error in plugin '{plugin_name}':\n{error_message}"
        )
    
    def shutdown_plugin_system(self):
        """Shutdown the plugin system."""
        if self.plugin_manager:
            self.plugin_manager.shutdown()
            self.logger.info("Plugin system shutdown complete")


def add_plugin_arguments(parser: argparse.ArgumentParser):
    """
    Add plugin-related command line arguments.
    
    Args:
        parser: ArgumentParser to add arguments to
    """
    plugin_group = parser.add_argument_group('Plugin Options')
    
    plugin_group.add_argument(
        '--automation-mode',
        action='store_true',
        help='Enable automation mode for documentation generation'
    )
    
    plugin_group.add_argument(
        '--disable-plugins',
        action='store_true',
        help='Disable all plugins'
    )
    
    plugin_group.add_argument(
        '--plugin-config-dir',
        type=str,
        default='config/plugins',
        help='Directory for plugin configuration files'
    )


def integrate_plugins_with_main_window(main_window: QMainWindow, args) -> Optional[OpenTilerWithPlugins]:
    """
    Integrate plugins with OpenTiler's main window.
    
    Args:
        main_window: OpenTiler's main window
        args: Command line arguments
        
    Returns:
        OpenTilerWithPlugins instance or None if disabled
    """
    if getattr(args, 'disable_plugins', False):
        logging.info("Plugins disabled by command line argument")
        return None
    
    try:
        # Create plugin integration
        plugin_integration = OpenTilerWithPlugins(main_window)
        
        # Initialize plugin system
        automation_mode = getattr(args, 'automation_mode', False)
        success = plugin_integration.initialize_plugin_system(automation_mode)
        
        if success:
            logging.info("Plugin system integration successful")
            return plugin_integration
        else:
            logging.error("Plugin system integration failed")
            return None
            
    except Exception as e:
        logging.error(f"Failed to integrate plugin system: {e}")
        return None


# Example usage in main.py:
"""
def main():
    app = QApplication(sys.argv)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="OpenTiler - Professional Document Scaling")
    add_plugin_arguments(parser)
    args = parser.parse_args()
    
    # Create main window
    main_window = OpenTilerMainWindow()
    
    # Integrate plugin system
    plugin_integration = integrate_plugins_with_main_window(main_window, args)
    
    # Show main window
    main_window.show()
    
    # Run application
    try:
        result = app.exec()
    finally:
        # Shutdown plugin system
        if plugin_integration:
            plugin_integration.shutdown_plugin_system()
    
    return result

if __name__ == "__main__":
    sys.exit(main())
"""
