#!/usr/bin/env python3
"""
OpenTiler Automation Plugin

This plugin provides automation capabilities for OpenTiler, including:
- Keyboard shortcuts for all major functions
- Socket-based automation API
- Documentation screenshot generation
- Automated testing support
"""

import sys
import time
import socket
import threading
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from PySide6.QtCore import QTimer, QThread, Signal, QObject
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton, QTextEdit, QGroupBox
from PySide6.QtGui import QKeySequence, QShortcut, QAction

# Add screen capture tool to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "screen_capture"))

try:
    from screen_capture import ScreenCapture
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    SCREEN_CAPTURE_AVAILABLE = False

from ..base_plugin import BasePlugin, PluginInfo
from ..hook_system import HookHandler, HookType, HookContext, get_hook_manager
from ..content_access import ContentAccessManager, AccessLevel


class AutomationServer(QThread):
    """Socket server for automation commands."""

    command_received = Signal(dict)

    def __init__(self, port: int = 8888):
        super().__init__()
        self.port = port
        self.server_socket = None
        self.running = False
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Run the automation server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(5)
            self.running = True

            self.logger.info(f"Automation server listening on port {self.port}")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    self.logger.info(f"Client connected from {address}")

                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket,),
                        daemon=True
                    )
                    client_thread.start()

                except Exception as e:
                    if self.running:
                        self.logger.error(f"Server error: {e}")

        except Exception as e:
            self.logger.error(f"Failed to start automation server: {e}")

    def _handle_client(self, client_socket):
        """Handle client connection."""
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break

                try:
                    command = json.loads(data.decode('utf-8'))
                    self.command_received.emit(command)

                    # Send response
                    response = {'status': 'received', 'command': command.get('action', 'unknown')}
                    client_socket.send(json.dumps(response).encode('utf-8'))

                except json.JSONDecodeError:
                    error_response = {'status': 'error', 'message': 'Invalid JSON'}
                    client_socket.send(json.dumps(error_response).encode('utf-8'))

        except Exception as e:
            self.logger.error(f"Client handling error: {e}")
        finally:
            client_socket.close()

    def stop(self):
        """Stop the automation server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()


class AutomationHookHandler(HookHandler):
    """Hook handler for automation plugin."""

    def __init__(self, automation_plugin):
        self.automation_plugin = automation_plugin

    @property
    def supported_hooks(self) -> List[HookType]:
        return [
            HookType.DOCUMENT_AFTER_LOAD,
            HookType.RENDER_BEFORE_DRAW,
            HookType.RENDER_AFTER_DRAW,
            HookType.MEASUREMENT_AFTER_FINISH,
            HookType.EXPORT_BEFORE_START,
            HookType.EXPORT_AFTER_SAVE
        ]

    @property
    def priority(self) -> int:
        return 100  # High priority for automation

    def handle_hook(self, context: HookContext) -> bool:
        """Handle hook events for automation."""
        try:
            if context.hook_type == HookType.DOCUMENT_AFTER_LOAD:
                return self._handle_document_loaded(context)
            elif context.hook_type == HookType.RENDER_BEFORE_DRAW:
                return self._handle_render_before_draw(context)
            elif context.hook_type == HookType.RENDER_AFTER_DRAW:
                return self._handle_render_after_draw(context)
            elif context.hook_type == HookType.MEASUREMENT_AFTER_FINISH:
                return self._handle_measurement_finished(context)
            elif context.hook_type == HookType.EXPORT_BEFORE_START:
                return self._handle_export_start(context)
            elif context.hook_type == HookType.EXPORT_AFTER_SAVE:
                return self._handle_export_finished(context)

            return True

        except Exception as e:
            self.automation_plugin.log_error(f"Hook handling error: {e}")
            return False

    def _handle_document_loaded(self, context: HookContext) -> bool:
        """Handle document loaded event."""
        document_path = context.data.get('document_path', '')
        self.automation_plugin.log_info(f"Document loaded: {document_path}")

        # Auto-capture screenshot if in documentation mode
        if self.automation_plugin.config.get('auto_capture_on_load', False):
            self.automation_plugin._action_capture_screenshot({
                'filename': 'auto-document-loaded.png'
            })

        return True

    def _handle_render_before_draw(self, context: HookContext) -> bool:
        """Handle before render event."""
        # Could add custom overlays or modifications here
        return True

    def _handle_render_after_draw(self, context: HookContext) -> bool:
        """Handle after render event."""
        # Could capture render statistics or add post-processing
        return True

    def _handle_measurement_finished(self, context: HookContext) -> bool:
        """Handle measurement completion."""
        measurement_data = context.data
        self.automation_plugin.log_info(f"Measurement completed: {measurement_data.get('distance', 0)} {measurement_data.get('units', 'mm')}")
        return True

    def _handle_export_start(self, context: HookContext) -> bool:
        """Handle export start."""
        export_settings = context.data.get('export_settings', {})
        self.automation_plugin.log_info(f"Export started: {export_settings.get('format', 'unknown')} format")
        return True

    def _handle_export_finished(self, context: HookContext) -> bool:
        """Handle export completion."""
        success = context.data.get('success', False)
        output_path = context.data.get('output_path', '')

        if success:
            self.automation_plugin.log_info(f"Export completed: {output_path}")

            # Auto-capture screenshot of completed export if enabled
            if self.automation_plugin.config.get('auto_capture_on_export', False):
                self.automation_plugin._action_capture_screenshot({
                    'filename': 'auto-export-completed.png'
                })
        else:
            self.automation_plugin.log_error("Export failed")

        return True


class AutomationPlugin(BasePlugin):
    """
    OpenTiler Automation Plugin.

    Provides comprehensive automation capabilities including keyboard shortcuts,
    socket API, and screenshot generation for documentation.
    """

    @property
    def plugin_info(self) -> PluginInfo:
        """Return plugin information."""
        return PluginInfo(
            name="Automation",
            version="1.0.0",
            description="Comprehensive automation and documentation tools for OpenTiler",
            author="OpenTiler Development Team",
            website="https://github.com/opentiler/opentiler",
            license="MIT",
            dependencies=[],
            min_opentiler_version="1.0.0"
        )

    def __init__(self, main_window=None):
        """Initialize the automation plugin."""
        super().__init__(main_window)

        self.logger = logging.getLogger(__name__)

        # Automation components
        self.automation_server = None
        self.screen_capture = None
        self.shortcuts = {}
        self.automation_actions = {}

        # Hook system
        self.hook_handler = AutomationHookHandler(self)
        self.hook_manager = get_hook_manager()

        # Content access
        self.content_access = None
        self.plan_view_access = None
        self.tile_preview_access = None
        self.measurement_access = None

        # Configuration
        self.config = {
            'enable_server': True,
            'server_port': 8888,
            'enable_shortcuts': True,
            'enable_screen_capture': SCREEN_CAPTURE_AVAILABLE,
            'screenshot_delay': 1.0,
            'demo_document_path': 'plans/original_plans/1147 Sky Skanner_2.pdf'
        }

        # Demo document path
        self.demo_document_path = None

        # Screenshot capture
        if SCREEN_CAPTURE_AVAILABLE:
            self.screen_capture = ScreenCapture()

    def initialize(self) -> bool:
        """Initialize the automation plugin."""
        try:
            self.logger.info("Initializing Automation Plugin")

            # Find demo document
            self._find_demo_document()

            # Setup automation actions
            self._setup_automation_actions()

            # Register hook handlers
            self.hook_manager.register_handler(self.hook_handler, "automation")

            # Setup content access
            self._setup_content_access()

            self._initialized = True
            self.log_info("Automation plugin initialized successfully")
            return True

        except Exception as e:
            self.log_error(f"Failed to initialize: {e}")
            return False

    def enable(self) -> bool:
        """Enable the automation plugin."""
        try:
            self.logger.info("Enabling Automation Plugin")

            # Setup keyboard shortcuts
            if self.config.get('enable_shortcuts', True):
                self._setup_keyboard_shortcuts()

            # Start automation server
            if self.config.get('enable_server', True):
                self._start_automation_server()

            self._enabled = True
            self.log_info("Automation plugin enabled")
            return True

        except Exception as e:
            self.log_error(f"Failed to enable: {e}")
            return False

    def disable(self) -> bool:
        """Disable the automation plugin."""
        try:
            self.logger.info("Disabling Automation Plugin")

            # Stop automation server
            if self.automation_server:
                self.automation_server.stop()
                self.automation_server.wait(3000)  # Wait up to 3 seconds
                self.automation_server = None

            # Remove keyboard shortcuts
            for shortcut in self.shortcuts.values():
                shortcut.setEnabled(False)
            self.shortcuts.clear()

            # Unregister hook handlers
            self.hook_manager.unregister_handler(self.hook_handler, "automation")

            self._enabled = False
            self.log_info("Automation plugin disabled")
            return True

        except Exception as e:
            self.log_error(f"Failed to disable: {e}")
            return False

    def cleanup(self) -> bool:
        """Clean up plugin resources."""
        try:
            if self.enabled:
                self.disable()

            self.log_info("Automation plugin cleaned up")
            return True

        except Exception as e:
            self.log_error(f"Failed to cleanup: {e}")
            return False

    def _find_demo_document(self):
        """Find the demo document for automation."""
        demo_path = self.config.get('demo_document_path', '')

        # Try relative to current directory
        if demo_path and Path(demo_path).exists():
            self.demo_document_path = str(Path(demo_path).resolve())
            self.log_info(f"Found demo document: {self.demo_document_path}")
            return

        # Try common locations
        common_paths = [
            'plans/original_plans/1147 Sky Skanner_2.pdf',
            '../plans/original_plans/1147 Sky Skanner_2.pdf',
            'docs/examples/1147 Sky Skanner_2.pdf'
        ]

        for path in common_paths:
            if Path(path).exists():
                self.demo_document_path = str(Path(path).resolve())
                self.log_info(f"Found demo document: {self.demo_document_path}")
                return

        self.log_info("Demo document not found - some automation features may be limited")

    def _setup_automation_actions(self):
        """Setup automation action handlers."""
        self.automation_actions = {
            'load_demo_document': self._action_load_demo_document,
            'open_file_menu': self._action_open_file_menu,
            'open_edit_menu': self._action_open_edit_menu,
            'open_view_menu': self._action_open_view_menu,
            'open_tools_menu': self._action_open_tools_menu,
            'open_help_menu': self._action_open_help_menu,
            'open_file_dialog': self._action_open_file_dialog,
            'open_export_dialog': self._action_open_export_dialog,
            'open_settings_dialog': self._action_open_settings_dialog,
            'open_scale_tool': self._action_open_scale_tool,
            'open_about_dialog': self._action_open_about_dialog,
            'zoom_in': self._action_zoom_in,
            'zoom_out': self._action_zoom_out,
            'fit_to_window': self._action_fit_to_window,
            'rotate_left': self._action_rotate_left,
            'rotate_right': self._action_rotate_right,
            'capture_screenshot': self._action_capture_screenshot,
        }

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for automation."""
        if not self.main_window:
            return

        shortcut_mappings = {
            'Ctrl+Shift+F1': 'load_demo_document',
            'Ctrl+Shift+F2': 'open_file_dialog',
            'Ctrl+Shift+F3': 'open_export_dialog',
            'Ctrl+Shift+F4': 'open_settings_dialog',
            'Ctrl+Shift+F5': 'open_scale_tool',
            'Ctrl+Shift+F6': 'open_about_dialog',
            'Ctrl+Shift+F7': 'capture_screenshot',
            'Ctrl+Shift+F8': 'open_file_menu',
            'Ctrl+Shift+F9': 'open_tools_menu',
            'Ctrl+Shift+F10': 'open_help_menu',
        }

        for key_sequence, action_name in shortcut_mappings.items():
            if action_name in self.automation_actions:
                shortcut = QShortcut(QKeySequence(key_sequence), self.main_window)
                shortcut.activated.connect(
                    lambda action=action_name: self._execute_action(action)
                )
                self.shortcuts[key_sequence] = shortcut
                self.log_info(f"Registered shortcut: {key_sequence} -> {action_name}")

    def _start_automation_server(self):
        """Start the automation server."""
        try:
            port = self.config.get('server_port', 8888)
            self.automation_server = AutomationServer(port)
            self.automation_server.command_received.connect(self._handle_automation_command)
            self.automation_server.start()

            self.log_info(f"Automation server started on port {port}")

        except Exception as e:
            self.log_error(f"Failed to start automation server: {e}")

    def _handle_automation_command(self, command: Dict[str, Any]):
        """Handle automation command from server."""
        action = command.get('action')
        if action in self.automation_actions:
            try:
                self.automation_actions[action](command.get('params', {}))
                self.log_info(f"Executed automation action: {action}")
            except Exception as e:
                self.log_error(f"Failed to execute action {action}: {e}")
        else:
            self.log_error(f"Unknown automation action: {action}")

    def _execute_action(self, action_name: str, params: Dict[str, Any] = None):
        """Execute an automation action."""
        if action_name in self.automation_actions:
            try:
                self.automation_actions[action_name](params or {})
                self.log_info(f"Executed action: {action_name}")
            except Exception as e:
                self.log_error(f"Failed to execute action {action_name}: {e}")

    # Automation action implementations
    def _action_load_demo_document(self, params: Dict[str, Any]):
        """Load the demo document."""
        if self.demo_document_path and self.main_window:
            # Call OpenTiler's load document method
            if hasattr(self.main_window, 'load_document'):
                self.main_window.load_document(self.demo_document_path)
            elif hasattr(self.main_window, 'open_file'):
                self.main_window.open_file(self.demo_document_path)

    def _action_open_file_menu(self, params: Dict[str, Any]):
        """Open the File menu."""
        if self.main_window and hasattr(self.main_window, 'menuBar'):
            file_menu = self.main_window.menuBar().findChild(object, 'fileMenu')
            if file_menu:
                file_menu.exec()

    def _action_open_edit_menu(self, params: Dict[str, Any]):
        """Open the Edit menu."""
        if self.main_window and hasattr(self.main_window, 'menuBar'):
            edit_menu = self.main_window.menuBar().findChild(object, 'editMenu')
            if edit_menu:
                edit_menu.exec()

    def _action_open_view_menu(self, params: Dict[str, Any]):
        """Open the View menu."""
        if self.main_window and hasattr(self.main_window, 'menuBar'):
            view_menu = self.main_window.menuBar().findChild(object, 'viewMenu')
            if view_menu:
                view_menu.exec()

    def _action_open_tools_menu(self, params: Dict[str, Any]):
        """Open the Tools menu."""
        if self.main_window and hasattr(self.main_window, 'menuBar'):
            tools_menu = self.main_window.menuBar().findChild(object, 'toolsMenu')
            if tools_menu:
                tools_menu.exec()

    def _action_open_help_menu(self, params: Dict[str, Any]):
        """Open the Help menu."""
        if self.main_window and hasattr(self.main_window, 'menuBar'):
            help_menu = self.main_window.menuBar().findChild(object, 'helpMenu')
            if help_menu:
                help_menu.exec()

    def _action_open_file_dialog(self, params: Dict[str, Any]):
        """Open the file dialog."""
        if self.main_window and hasattr(self.main_window, 'open_file_dialog'):
            self.main_window.open_file_dialog()

    def _action_open_export_dialog(self, params: Dict[str, Any]):
        """Open the export dialog."""
        if self.main_window and hasattr(self.main_window, 'open_export_dialog'):
            self.main_window.open_export_dialog()

    def _action_open_settings_dialog(self, params: Dict[str, Any]):
        """Open the settings dialog."""
        if self.main_window and hasattr(self.main_window, 'open_settings'):
            self.main_window.open_settings()

    def _action_open_scale_tool(self, params: Dict[str, Any]):
        """Open the scale tool."""
        if self.main_window and hasattr(self.main_window, 'open_scale_tool'):
            self.main_window.open_scale_tool()

    def _action_open_about_dialog(self, params: Dict[str, Any]):
        """Open the about dialog."""
        if self.main_window and hasattr(self.main_window, 'show_about'):
            self.main_window.show_about()

    def _action_zoom_in(self, params: Dict[str, Any]):
        """Zoom in."""
        if self.main_window and hasattr(self.main_window, 'zoom_in'):
            self.main_window.zoom_in()

    def _action_zoom_out(self, params: Dict[str, Any]):
        """Zoom out."""
        if self.main_window and hasattr(self.main_window, 'zoom_out'):
            self.main_window.zoom_out()

    def _action_fit_to_window(self, params: Dict[str, Any]):
        """Fit to window."""
        if self.main_window and hasattr(self.main_window, 'fit_to_window'):
            self.main_window.fit_to_window()

    def _action_rotate_left(self, params: Dict[str, Any]):
        """Rotate left."""
        if self.main_window and hasattr(self.main_window, 'rotate_left'):
            self.main_window.rotate_left()

    def _action_rotate_right(self, params: Dict[str, Any]):
        """Rotate right."""
        if self.main_window and hasattr(self.main_window, 'rotate_right'):
            self.main_window.rotate_right()

    def _action_capture_screenshot(self, params: Dict[str, Any]):
        """Capture screenshot of OpenTiler."""
        if not SCREEN_CAPTURE_AVAILABLE:
            self.log_error("Screen capture not available")
            return

        try:
            # Find OpenTiler window
            windows = self.screen_capture.list_windows()
            opentiler_window = None

            for window in windows:
                if ('OpenTiler' in window.title and
                    'Visual Studio Code' not in window.title):
                    opentiler_window = window
                    break

            if not opentiler_window:
                self.log_error("OpenTiler window not found for screenshot")
                return

            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = params.get('filename', f'opentiler_screenshot_{timestamp}.png')
            output_path = Path('docs/images') / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Capture screenshot
            success = self.screen_capture.capture_window(
                opentiler_window,
                str(output_path),
                target_size=params.get('size', (1600, 1000)),
                format_type=params.get('format', 'png'),
                quality=params.get('quality', 95)
            )

            if success:
                self.log_info(f"Screenshot captured: {output_path}")
            else:
                self.log_error("Failed to capture screenshot")

        except Exception as e:
            self.log_error(f"Screenshot capture error: {e}")

    def get_menu_actions(self) -> List[QAction]:
        """Get menu actions for the automation plugin."""
        actions = []

        # Add automation menu action
        automation_action = QAction("Automation Control", self.main_window)
        automation_action.setStatusTip("Open automation control panel")
        automation_action.triggered.connect(self._show_automation_control)
        actions.append(automation_action)

        return actions

    def _show_automation_control(self):
        """Show automation control panel."""
        # This would open a control panel for automation
        # For now, just log the action
        self.log_info("Automation control panel requested")

    def get_settings_widget(self) -> Optional[QWidget]:
        """Get settings widget for automation configuration."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Server settings
        server_group = QGroupBox("Automation Server")
        server_layout = QVBoxLayout(server_group)

        self.enable_server_cb = QCheckBox("Enable automation server")
        self.enable_server_cb.setChecked(self.config.get('enable_server', True))
        server_layout.addWidget(self.enable_server_cb)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_spinbox = QSpinBox()
        self.port_spinbox.setRange(1024, 65535)
        self.port_spinbox.setValue(self.config.get('server_port', 8888))
        port_layout.addWidget(self.port_spinbox)
        server_layout.addLayout(port_layout)

        layout.addWidget(server_group)

        # Shortcut settings
        shortcut_group = QGroupBox("Keyboard Shortcuts")
        shortcut_layout = QVBoxLayout(shortcut_group)

        self.enable_shortcuts_cb = QCheckBox("Enable automation shortcuts")
        self.enable_shortcuts_cb.setChecked(self.config.get('enable_shortcuts', True))
        shortcut_layout.addWidget(self.enable_shortcuts_cb)

        layout.addWidget(shortcut_group)

        # Screenshot settings
        if SCREEN_CAPTURE_AVAILABLE:
            screenshot_group = QGroupBox("Screenshot Capture")
            screenshot_layout = QVBoxLayout(screenshot_group)

            self.enable_capture_cb = QCheckBox("Enable screenshot capture")
            self.enable_capture_cb.setChecked(self.config.get('enable_screen_capture', True))
            screenshot_layout.addWidget(self.enable_capture_cb)

            layout.addWidget(screenshot_group)

        return widget

    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration."""
        return self.config.copy()

    def set_config(self, config: Dict[str, Any]) -> bool:
        """Set plugin configuration."""
        try:
            self.config.update(config)
            return True
        except Exception:
            return False

    def get_hook_handlers(self) -> List[HookHandler]:
        """Get hook handlers provided by this plugin."""
        return [self.hook_handler]

    def get_document_access_requirements(self) -> Dict[str, bool]:
        """Get document access requirements for this plugin."""
        return {
            'plan_view': True,
            'tile_preview': True,
            'document_data': True,
            'metadata': True,
            'measurements': True,
            'transformations': True
        }

    def _setup_content_access(self):
        """Setup content access for the plugin."""
        if self.main_window and hasattr(self.main_window, 'content_access_manager'):
            access_manager = self.main_window.content_access_manager

            # Request content access
            requirements = self.get_document_access_requirements()
            access_objects = access_manager.grant_access(
                "automation",
                requirements,
                AccessLevel.FULL_CONTROL
            )

            # Store access objects
            self.plan_view_access = access_objects.get('plan_view')
            self.tile_preview_access = access_objects.get('tile_preview')
            self.measurement_access = access_objects.get('measurements')

            self.log_info("Content access configured")
        else:
            self.log_info("Content access manager not available")
