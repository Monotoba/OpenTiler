#!/usr/bin/env python3
"""
OpenTiler Plugin Manager UI

This module provides a comprehensive UI for managing plugins within OpenTiler's
settings dialog, including plugin discovery, configuration, and status management.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, QThread, QTimer, Signal, pyqtSignal
from PySide6.QtGui import QAction, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox,
                               QDialog, QDialogButtonBox, QFrame, QGridLayout,
                               QGroupBox, QHBoxLayout, QHeaderView, QLabel,
                               QLineEdit, QListWidget, QListWidgetItem,
                               QMessageBox, QProgressBar, QPushButton,
                               QScrollArea, QSpinBox, QSplitter, QTableWidget,
                               QTableWidgetItem, QTabWidget, QTextEdit,
                               QVBoxLayout, QWidget)

from .base_plugin import BasePlugin, PluginInfo
from .hook_system import HookType, get_hook_manager
from .plugin_manager import PluginManager


class PluginDiscoveryThread(QThread):
    """Thread for discovering plugins without blocking the UI."""

    plugins_discovered = pyqtSignal(list)  # List of plugin names
    discovery_finished = pyqtSignal()

    def __init__(self, plugin_manager: PluginManager):
        super().__init__()
        self.plugin_manager = plugin_manager

    def run(self):
        """Run plugin discovery."""
        try:
            discovered = self.plugin_manager.discover_plugins()
            self.plugins_discovered.emit(discovered)
        except Exception as e:
            print(f"Plugin discovery error: {e}")
        finally:
            self.discovery_finished.emit()


class PluginInfoWidget(QWidget):
    """Widget displaying detailed information about a plugin."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_plugin = None

    def setup_ui(self):
        """Set up the plugin info UI."""
        layout = QVBoxLayout(self)

        # Plugin header
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)

        # Plugin icon (placeholder)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setStyleSheet("border: 1px solid gray; background: lightgray;")
        header_layout.addWidget(self.icon_label)

        # Plugin name and version
        info_layout = QVBoxLayout()
        self.name_label = QLabel("No plugin selected")
        self.name_label.setFont(QFont("", 12, QFont.Bold))
        self.version_label = QLabel("")
        self.author_label = QLabel("")

        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.version_label)
        info_layout.addWidget(self.author_label)
        info_layout.addStretch()

        header_layout.addLayout(info_layout)
        header_layout.addStretch()

        # Plugin status and controls
        controls_layout = QVBoxLayout()
        self.status_label = QLabel("Status: Unknown")
        self.enable_checkbox = QCheckBox("Enabled")
        self.enable_checkbox.stateChanged.connect(self.on_enable_changed)

        controls_layout.addWidget(self.status_label)
        controls_layout.addWidget(self.enable_checkbox)

        header_layout.addLayout(controls_layout)
        layout.addWidget(header_frame)

        # Plugin details tabs
        self.tabs = QTabWidget()

        # Description tab
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.tabs.addTab(self.description_text, "Description")

        # Dependencies tab
        self.dependencies_list = QListWidget()
        self.tabs.addTab(self.dependencies_list, "Dependencies")

        # Hooks tab
        self.hooks_table = QTableWidget()
        self.hooks_table.setColumnCount(2)
        self.hooks_table.setHorizontalHeaderLabels(["Hook Type", "Priority"])
        self.hooks_table.horizontalHeader().setStretchLastSection(True)
        self.tabs.addTab(self.hooks_table, "Hooks")

        # Settings tab
        self.settings_scroll = QScrollArea()
        self.settings_widget = QWidget()
        self.settings_scroll.setWidget(self.settings_widget)
        self.settings_scroll.setWidgetResizable(True)
        self.tabs.addTab(self.settings_scroll, "Settings")

        layout.addWidget(self.tabs)

    def set_plugin(
        self, plugin_name: str, plugin: BasePlugin, plugin_manager: PluginManager
    ):
        """Set the plugin to display information for."""
        self.current_plugin = plugin_name
        self.plugin = plugin
        self.plugin_manager = plugin_manager

        # Update header information
        info = plugin.plugin_info
        self.name_label.setText(info.name)
        self.version_label.setText(f"Version: {info.version}")
        self.author_label.setText(f"Author: {info.author}")

        # Update status
        status = plugin.get_status()
        self.status_label.setText(f"Status: {status}")
        self.enable_checkbox.setChecked(plugin.enabled)

        # Update description
        self.description_text.setPlainText(info.description)

        # Update dependencies
        self.dependencies_list.clear()
        if info.dependencies:
            for dep in info.dependencies:
                self.dependencies_list.addItem(dep)
        else:
            item = QListWidgetItem("No dependencies")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.dependencies_list.addItem(item)

        # Update hooks
        self.update_hooks_table()

        # Update settings
        self.update_settings_widget()

    def update_hooks_table(self):
        """Update the hooks table with plugin hook information."""
        self.hooks_table.setRowCount(0)

        if not self.plugin:
            return

        hook_handlers = self.plugin.get_hook_handlers()
        if not hook_handlers:
            self.hooks_table.setRowCount(1)
            item = QTableWidgetItem("No hooks registered")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.hooks_table.setItem(0, 0, item)
            self.hooks_table.setSpan(0, 0, 1, 2)
            return

        # Get hook manager to check registered hooks
        hook_manager = get_hook_manager()

        row = 0
        for handler in hook_handlers:
            for hook_type in handler.supported_hooks:
                self.hooks_table.setRowCount(row + 1)

                # Hook type
                type_item = QTableWidgetItem(hook_type.value)
                self.hooks_table.setItem(row, 0, type_item)

                # Priority
                priority_item = QTableWidgetItem(str(handler.priority))
                self.hooks_table.setItem(row, 1, priority_item)

                row += 1

    def update_settings_widget(self):
        """Update the settings widget with plugin-specific settings."""
        # Clear existing settings
        if self.settings_widget.layout():
            while self.settings_widget.layout().count():
                child = self.settings_widget.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            layout = QVBoxLayout(self.settings_widget)

        if not self.plugin:
            return

        # Get plugin settings widget
        plugin_settings = self.plugin.get_settings_widget()
        if plugin_settings:
            self.settings_widget.layout().addWidget(plugin_settings)
        else:
            no_settings_label = QLabel("No settings available for this plugin")
            no_settings_label.setAlignment(Qt.AlignCenter)
            self.settings_widget.layout().addWidget(no_settings_label)

        self.settings_widget.layout().addStretch()

    def on_enable_changed(self, state):
        """Handle plugin enable/disable."""
        if not self.current_plugin or not self.plugin_manager:
            return

        if state == Qt.Checked:
            success = self.plugin_manager.enable_plugin(self.current_plugin)
            if not success:
                self.enable_checkbox.setChecked(False)
                QMessageBox.warning(
                    self,
                    "Plugin Error",
                    f"Failed to enable plugin '{self.current_plugin}'",
                )
        else:
            success = self.plugin_manager.disable_plugin(self.current_plugin)
            if not success:
                self.enable_checkbox.setChecked(True)
                QMessageBox.warning(
                    self,
                    "Plugin Error",
                    f"Failed to disable plugin '{self.current_plugin}'",
                )

        # Update status
        if self.plugin:
            status = self.plugin.get_status()
            self.status_label.setText(f"Status: {status}")


class PluginManagerWidget(QWidget):
    """Main plugin manager widget for the settings dialog."""

    plugin_status_changed = Signal(str, bool)  # plugin_name, enabled

    def __init__(self, plugin_manager: PluginManager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setup_ui()
        self.refresh_plugins()

        # Connect plugin manager signals
        self.plugin_manager.plugin_loaded.connect(self.on_plugin_loaded)
        self.plugin_manager.plugin_enabled.connect(self.on_plugin_enabled)
        self.plugin_manager.plugin_disabled.connect(self.on_plugin_disabled)
        self.plugin_manager.plugin_error.connect(self.on_plugin_error)

    def setup_ui(self):
        """Set up the plugin manager UI."""
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_plugins)
        toolbar_layout.addWidget(self.refresh_button)

        self.discover_button = QPushButton("Discover Plugins")
        self.discover_button.clicked.connect(self.discover_plugins)
        toolbar_layout.addWidget(self.discover_button)

        toolbar_layout.addStretch()

        self.status_label = QLabel("Ready")
        toolbar_layout.addWidget(self.status_label)

        layout.addLayout(toolbar_layout)

        # Main content
        splitter = QSplitter(Qt.Horizontal)

        # Plugin list
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)

        list_layout.addWidget(QLabel("Available Plugins:"))
        self.plugin_list = QListWidget()
        self.plugin_list.currentItemChanged.connect(self.on_plugin_selected)
        list_layout.addWidget(self.plugin_list)

        # Plugin statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QGridLayout(stats_group)

        self.total_plugins_label = QLabel("0")
        self.enabled_plugins_label = QLabel("0")
        self.disabled_plugins_label = QLabel("0")

        stats_layout.addWidget(QLabel("Total:"), 0, 0)
        stats_layout.addWidget(self.total_plugins_label, 0, 1)
        stats_layout.addWidget(QLabel("Enabled:"), 1, 0)
        stats_layout.addWidget(self.enabled_plugins_label, 1, 1)
        stats_layout.addWidget(QLabel("Disabled:"), 2, 0)
        stats_layout.addWidget(self.disabled_plugins_label, 2, 1)

        list_layout.addWidget(stats_group)

        splitter.addWidget(list_widget)

        # Plugin details
        self.plugin_info = PluginInfoWidget()
        splitter.addWidget(self.plugin_info)

        # Set splitter proportions
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)

    def refresh_plugins(self):
        """Refresh the plugin list."""
        self.plugin_list.clear()

        # Add loaded plugins
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            item = QListWidgetItem(plugin_name)

            # Set icon based on status
            if plugin.enabled:
                item.setIcon(
                    self.style().standardIcon(self.style().SP_DialogApplyButton)
                )
            else:
                item.setIcon(
                    self.style().standardIcon(self.style().SP_DialogCancelButton)
                )

            # Set tooltip with plugin info
            info = plugin.plugin_info
            tooltip = f"{info.name} v{info.version}\n{info.description}\nAuthor: {info.author}"
            item.setToolTip(tooltip)

            self.plugin_list.addItem(item)

        self.update_statistics()

    def update_statistics(self):
        """Update plugin statistics."""
        total = len(self.plugin_manager.plugins)
        enabled = len(self.plugin_manager.get_enabled_plugins())
        disabled = total - enabled

        self.total_plugins_label.setText(str(total))
        self.enabled_plugins_label.setText(str(enabled))
        self.disabled_plugins_label.setText(str(disabled))

    def discover_plugins(self):
        """Discover new plugins."""
        self.status_label.setText("Discovering plugins...")
        self.discover_button.setEnabled(False)

        # Start discovery in background thread
        self.discovery_thread = PluginDiscoveryThread(self.plugin_manager)
        self.discovery_thread.plugins_discovered.connect(self.on_plugins_discovered)
        self.discovery_thread.discovery_finished.connect(self.on_discovery_finished)
        self.discovery_thread.start()

    def on_plugins_discovered(self, plugin_names: List[str]):
        """Handle discovered plugins."""
        new_plugins = []
        for plugin_name in plugin_names:
            if plugin_name not in self.plugin_manager.plugins:
                # Load new plugin
                if self.plugin_manager.load_plugin(plugin_name):
                    new_plugins.append(plugin_name)

        if new_plugins:
            self.status_label.setText(f"Discovered {len(new_plugins)} new plugins")
            self.refresh_plugins()
        else:
            self.status_label.setText("No new plugins found")

    def on_discovery_finished(self):
        """Handle discovery completion."""
        self.discover_button.setEnabled(True)

        # Reset status after delay
        QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))

    def on_plugin_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle plugin selection."""
        if not current:
            return

        plugin_name = current.text()
        plugin = self.plugin_manager.get_plugin(plugin_name)

        if plugin:
            self.plugin_info.set_plugin(plugin_name, plugin, self.plugin_manager)

    def on_plugin_loaded(self, plugin_name: str):
        """Handle plugin loaded signal."""
        self.refresh_plugins()

    def on_plugin_enabled(self, plugin_name: str):
        """Handle plugin enabled signal."""
        self.refresh_plugins()
        self.update_statistics()
        self.plugin_status_changed.emit(plugin_name, True)

    def on_plugin_disabled(self, plugin_name: str):
        """Handle plugin disabled signal."""
        self.refresh_plugins()
        self.update_statistics()
        self.plugin_status_changed.emit(plugin_name, False)

    def on_plugin_error(self, plugin_name: str, error_message: str):
        """Handle plugin error signal."""
        QMessageBox.critical(
            self, "Plugin Error", f"Error in plugin '{plugin_name}':\n{error_message}"
        )


def create_plugin_manager_settings_widget(plugin_manager: PluginManager) -> QWidget:
    """
    Create a plugin manager widget for inclusion in OpenTiler's settings dialog.

    Args:
        plugin_manager: The plugin manager instance

    Returns:
        Widget for the settings dialog
    """
    return PluginManagerWidget(plugin_manager)
