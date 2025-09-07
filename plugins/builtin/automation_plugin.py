
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
    from screen_capture import ScreenCapture, HAS_DEPENDENCIES as _SC_DEPS
    SCREEN_CAPTURE_AVAILABLE = bool(_SC_DEPS)
except Exception:
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
            try:
                self.screen_capture = ScreenCapture()
            except Exception:
                # Dependencies may be unavailable at runtime
                self.screen_capture = None
                self.config['enable_screen_capture'] = False

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
            'close_scale_tool': self._action_close_scale_tool,
            'open_about_dialog': self._action_open_about_dialog,
            'zoom_in': self._action_zoom_in,
            'zoom_out': self._action_zoom_out,
            'fit_to_window': self._action_fit_to_window,
            'rotate_left': self._action_rotate_left,
            'rotate_right': self._action_rotate_right,
            'capture_screenshot': self._action_capture_screenshot,
            'set_scale_measurement': self._action_set_scale_measurement,
            'apply_scale': self._action_apply_scale,
            'send_keys': self._action_send_keys,
            'click_button': self._action_click_button,
            'dismiss_message_box': self._action_dismiss_message_box,
            'dismiss_any_dialog': self._action_dismiss_any_dialog,
            'click_menu_item': self._action_click_menu_item,
            'click_settings_tab': self._action_click_settings_tab,
            'change_setting': self._action_change_setting,
            'select_wing_tip_points': self._action_select_wing_tip_points,
            'set_scale_distance': self._action_set_scale_distance,
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
            menubar = self.main_window.menuBar()
            for action in menubar.actions():
                if action.text() == "&File":
                    action.menu().exec(menubar.mapToGlobal(menubar.rect().bottomLeft()))
                    break

    def _action_open_edit_menu(self, params: Dict[str, Any]):
        """Open the Edit menu."""
        if self.main_window and hasattr(self.main_window, 'menuBar'):
            menubar = self.main_window.menuBar()
            for action in menubar.actions():
                if action.text() == "&Edit":
                    action.menu().exec(menubar.mapToGlobal(menubar.rect().bottomLeft()))
                    break

    def _action_open_view_menu(self, params: Dict[str, Any]):
        """Open the View menu."""
        if self.main_window and hasattr(self.main_window, 'menuBar'):
            menubar = self.main_window.menuBar()
            for action in menubar.actions():
                if action.text() == "&View":
                    action.menu().exec(menubar.mapToGlobal(menubar.rect().bottomLeft()))
                    break

    def _action_open_tools_menu(self, params: Dict[str, Any]):
        """Open the Tools menu."""
        if self.main_window and hasattr(self.main_window, 'menuBar'):
            menubar = self.main_window.menuBar()
            for action in menubar.actions():
                if action.text() == "&Tools":
                    action.menu().exec(menubar.mapToGlobal(menubar.rect().bottomLeft()))
                    break

    def _action_open_help_menu(self, params: Dict[str, Any]):
        """Open the Help menu."""
        if self.main_window and hasattr(self.main_window, 'menuBar'):
            menubar = self.main_window.menuBar()
            for action in menubar.actions():
                if action.text() == "&Help":
                    action.menu().exec(menubar.mapToGlobal(menubar.rect().bottomLeft()))
                    break

    def _action_open_file_dialog(self, params: Dict[str, Any]):
        """Open the file dialog."""
        if self.main_window and hasattr(self.main_window, 'open_file'):
            self.main_window.open_file()

    def _action_open_export_dialog(self, params: Dict[str, Any]):
        """Open the export dialog."""
        if self.main_window and hasattr(self.main_window, 'export_document'):
            self.main_window.export_document()

    def _action_open_settings_dialog(self, params: Dict[str, Any]):
        """Open the settings dialog."""
        if self.main_window and hasattr(self.main_window, 'show_settings'):
            self.main_window.show_settings()

    def _action_open_scale_tool(self, params: Dict[str, Any]):
        """Open the scale tool."""
        if self.main_window and hasattr(self.main_window, 'show_scaling_dialog'):
            self.main_window.show_scaling_dialog()

    def _action_open_about_dialog(self, params: Dict[str, Any]):
        """Open the about dialog."""
        if self.main_window and hasattr(self.main_window, 'show_about'):
            self.main_window.show_about()

    def _action_zoom_in(self, params: Dict[str, Any]):
        """Zoom in."""
        if self.main_window and hasattr(self.main_window, 'document_viewer'):
            self.main_window.document_viewer.zoom_in()

    def _action_zoom_out(self, params: Dict[str, Any]):
        """Zoom out."""
        if self.main_window and hasattr(self.main_window, 'document_viewer'):
            self.main_window.document_viewer.zoom_out()

    def _action_fit_to_window(self, params: Dict[str, Any]):
        """Fit to window."""
        if self.main_window and hasattr(self.main_window, 'document_viewer'):
            self.main_window.document_viewer.zoom_fit()

    def _action_rotate_left(self, params: Dict[str, Any]):
        """Rotate left."""
        if self.main_window and hasattr(self.main_window, 'document_viewer'):
            self.main_window.document_viewer.rotate_counterclockwise()

    def _action_rotate_right(self, params: Dict[str, Any]):
        """Rotate right."""
        if self.main_window and hasattr(self.main_window, 'document_viewer'):
            self.main_window.document_viewer.rotate_clockwise()

    def _action_capture_screenshot(self, params: Dict[str, Any]):
        """Capture screenshot of OpenTiler."""
        if not SCREEN_CAPTURE_AVAILABLE:
            self.log_error("Screen capture not available")
            return

        try:
            # Find OpenTiler window
            windows = self.screen_capture.list_windows()
            opentiler_window = None

            self.log_info(f"Found {len(windows)} visible windows")

            # Log all windows for debugging
            for i, window in enumerate(windows):
                self.log_info(f"Window {i+1}: '{window.title}' at ({window.left},{window.top}) {window.width}x{window.height}")

            for window in windows:
                if ('OpenTiler' in window.title and
                    'Visual Studio Code' not in window.title and
                    window.width > 100 and window.height > 100):  # Ensure it's a real window
                    opentiler_window = window
                    self.log_info(f"Selected OpenTiler window: {window.title}")
                    break

            if not opentiler_window:
                self.log_error("OpenTiler window not found for screenshot")
                return

            # Ensure OpenTiler window is active and visible
            try:
                if hasattr(opentiler_window, 'activate'):
                    opentiler_window.activate()
                    self.log_info("Activated OpenTiler window")
                if hasattr(opentiler_window, 'isMinimized') and opentiler_window.isMinimized:
                    opentiler_window.restore()
                    self.log_info("Restored minimized OpenTiler window")

                import time
                time.sleep(0.5)  # Wait for window to be ready
            except Exception as e:
                self.log_warning(f"Could not activate window: {e}")

            # Generate filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = params.get('filename', f'opentiler_screenshot_{timestamp}.png')
            output_path = Path('docs/images') / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            self.log_info(f"Capturing to: {output_path}")

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

    def _action_set_scale_measurement(self, params: Dict[str, Any]):
        """Set scale measurement value in the scale tool dialog."""
        try:
            # Get the measurement value from parameters
            measurement = params.get('measurement', '460')
            unit = params.get('unit', 'mm')
            full_value = f"{measurement}{unit}"

            # Find the scale dialog
            if self.main_window and hasattr(self.main_window, 'scaling_dialog'):
                scaling_dialog = self.main_window.scaling_dialog
                if scaling_dialog and scaling_dialog.isVisible():
                    # Find the distance input field
                    distance_input = scaling_dialog.findChild(object, 'distance_input')
                    if not distance_input:
                        # Try alternative names
                        for name in ['distanceInput', 'distance_field', 'measurement_input']:
                            distance_input = scaling_dialog.findChild(object, name)
                            if distance_input:
                                break

                    if distance_input and hasattr(distance_input, 'setText'):
                        # Clear and set the new value
                        distance_input.clear()
                        distance_input.setText(full_value)
                        self.log_info(f"Set scale measurement to: {full_value}")
                    else:
                        self.log_error("Could not find distance input field in scale dialog")
                else:
                    self.log_error("Scale dialog not visible or not found")
            else:
                self.log_error("Main window or scaling dialog not available")

        except Exception as e:
            self.log_error(f"Failed to set scale measurement: {e}")

    def _action_apply_scale(self, params: Dict[str, Any]):
        """Apply the scale in the scale tool dialog."""
        try:
            # Find the scaling dialog
            scaling_dialog = None
            if self.main_window and hasattr(self.main_window, 'scaling_dialog'):
                scaling_dialog = self.main_window.scaling_dialog

            if scaling_dialog and scaling_dialog.isVisible():
                # Use the apply_button directly from the dialog
                apply_button = scaling_dialog.apply_button
                if apply_button and hasattr(apply_button, 'click') and apply_button.isEnabled():
                    apply_button.click()
                    self.log_info("Applied scale measurement")
                else:
                    self.log_error("Apply button not found or not enabled in scale dialog")
            else:
                self.log_error("Scale dialog not visible or not found")

        except Exception as e:
            self.log_error(f"Failed to apply scale: {e}")

    def _action_send_keys(self, params: Dict[str, Any]):
        """Send keyboard input to the focused widget."""
        try:
            from PySide6.QtGui import QKeySequence
            from PySide6.QtCore import QCoreApplication
            from PySide6.QtTest import QTest

            keys = params.get('keys', '')
            if not keys:
                self.log_error("No keys specified for send_keys action")
                return

            # Get the currently focused widget
            focused_widget = QCoreApplication.instance().focusWidget()
            if focused_widget:
                # Send the key sequence
                if hasattr(focused_widget, 'setText') and 'text' in params:
                    # Direct text input
                    focused_widget.setText(params['text'])
                    self.log_info(f"Set text: {params['text']}")
                else:
                    # Send individual keys
                    for char in keys:
                        QTest.keyClick(focused_widget, ord(char))
                    self.log_info(f"Sent keys: {keys}")
            else:
                self.log_error("No focused widget found for key input")

        except Exception as e:
            self.log_error(f"Failed to send keys: {e}")

    def _action_click_button(self, params: Dict[str, Any]):
        """Click a button by name or text."""
        try:
            from PySide6.QtWidgets import QPushButton, QApplication
            from PySide6.QtCore import QCoreApplication

            button_name = params.get('name', '')
            button_text = params.get('text', '')

            if not button_name and not button_text:
                self.log_error("No button name or text specified")
                return

            self.log_info(f"Looking for button: name='{button_name}' text='{button_text}'")

            # Find the button - search all visible widgets
            button = None

            # Get all top-level widgets (including modal dialogs)
            app = QApplication.instance()
            all_widgets = app.allWidgets()

            # Log all visible dialogs for debugging
            visible_dialogs = []
            for widget in all_widgets:
                if widget.isVisible() and hasattr(widget, 'windowTitle') and widget.windowTitle():
                    visible_dialogs.append(f"'{widget.windowTitle()}' ({type(widget).__name__})")

            self.log_info(f"Visible dialogs: {visible_dialogs}")

            # Search for button in all visible widgets
            for widget in all_widgets:
                if not widget.isVisible():
                    continue

                # Search for buttons in this widget
                if isinstance(widget, QPushButton):
                    if (button_name and widget.objectName() == button_name) or \
                       (button_text and widget.text() == button_text):
                        button = widget
                        self.log_info(f"Found button in widget: {type(widget.parent()).__name__ if widget.parent() else 'None'}")
                        break

                # Search for buttons as children of this widget
                buttons = widget.findChildren(QPushButton)
                for btn in buttons:
                    if not btn.isVisible():
                        continue
                    if (button_name and btn.objectName() == button_name) or \
                       (button_text and btn.text() == button_text):
                        button = btn
                        self.log_info(f"Found button '{btn.text()}' in {type(widget).__name__}")
                        break

                if button:
                    break

            if button and hasattr(button, 'click') and button.isEnabled():
                self.log_info(f"Clicking button: '{button.text()}' (enabled: {button.isEnabled()})")
                button.click()
                self.log_info(f"Successfully clicked button: {button_name or button_text}")
            else:
                if button:
                    self.log_error(f"Button found but not clickable: enabled={button.isEnabled() if button else 'N/A'}")
                else:
                    self.log_error(f"Button not found: {button_name or button_text}")
                    # Log all available buttons for debugging
                    all_buttons = []
                    for widget in all_widgets:
                        if widget.isVisible():
                            buttons = widget.findChildren(QPushButton)
                            for btn in buttons:
                                if btn.isVisible():
                                    all_buttons.append(f"'{btn.text()}' (name: '{btn.objectName()}')")
                    self.log_info(f"Available buttons: {all_buttons}")

        except Exception as e:
            self.log_error(f"Failed to click button: {e}")
            import traceback
            self.log_error(f"Traceback: {traceback.format_exc()}")

    def _action_dismiss_message_box(self, params: Dict[str, Any]):
        """Dismiss a QMessageBox by clicking OK or specified button."""
        try:
            from PySide6.QtWidgets import QMessageBox, QApplication
            from PySide6.QtCore import QTimer

            button_text = params.get('button', 'OK')
            self.log_info(f"Looking for QMessageBox with button: {button_text}")

            # Find all QMessageBox instances
            app = QApplication.instance()
            message_boxes = []

            for widget in app.allWidgets():
                if isinstance(widget, QMessageBox) and widget.isVisible():
                    message_boxes.append(widget)
                    self.log_info(f"Found QMessageBox: title='{widget.windowTitle()}' text='{widget.text()}'")

            if not message_boxes:
                self.log_error("No visible QMessageBox found")
                return

            # Use the first visible message box
            msg_box = message_boxes[0]

            # Try to click the specified button
            if button_text.upper() == 'OK':
                # Try standard OK button
                ok_button = msg_box.button(QMessageBox.Ok)
                if ok_button:
                    self.log_info("Clicking QMessageBox OK button")
                    ok_button.click()
                    self.log_info("Successfully clicked QMessageBox OK button")
                    return

            # Try to find button by text
            buttons = msg_box.buttons()
            for button in buttons:
                if button.text() == button_text:
                    self.log_info(f"Clicking QMessageBox button: {button.text()}")
                    button.click()
                    self.log_info(f"Successfully clicked QMessageBox button: {button.text()}")
                    return

            # If no specific button found, try the default button
            default_button = msg_box.defaultButton()
            if default_button:
                self.log_info(f"Clicking QMessageBox default button: {default_button.text()}")
                default_button.click()
                self.log_info("Successfully clicked QMessageBox default button")
            else:
                self.log_error(f"No button '{button_text}' found in QMessageBox")
                # Log available buttons
                available_buttons = [btn.text() for btn in buttons]
                self.log_info(f"Available buttons: {available_buttons}")

        except Exception as e:
            self.log_error(f"Failed to dismiss message box: {e}")
            import traceback
            self.log_error(f"Traceback: {traceback.format_exc()}")

    def _action_close_scale_tool(self, params: Dict[str, Any]):
        """Close the scale tool dialog by clicking its close button."""
        try:
            # Find the scaling dialog
            scaling_dialog = None
            if self.main_window and hasattr(self.main_window, 'scaling_dialog'):
                scaling_dialog = self.main_window.scaling_dialog

            if scaling_dialog and scaling_dialog.isVisible():
                self.log_info("Closing scale tool dialog")

                # Try to close the dialog properly
                if hasattr(scaling_dialog, 'close'):
                    scaling_dialog.close()
                    self.log_info("Scale tool dialog closed")
                elif hasattr(scaling_dialog, 'reject'):
                    scaling_dialog.reject()
                    self.log_info("Scale tool dialog rejected (closed)")
                else:
                    # Try to find and click the close button
                    from PySide6.QtWidgets import QPushButton

                    # Look for close button by common names
                    close_button = None
                    for button_name in ['close_button', 'closeButton', 'cancel_button', 'cancelButton']:
                        close_button = scaling_dialog.findChild(QPushButton, button_name)
                        if close_button:
                            break

                    if not close_button:
                        # Look for buttons with close-related text
                        buttons = scaling_dialog.findChildren(QPushButton)
                        for btn in buttons:
                            if btn.text().lower() in ['close', 'cancel', 'done', '&close', '&cancel']:
                                close_button = btn
                                break

                    if close_button and close_button.isEnabled():
                        self.log_info(f"Clicking close button: {close_button.text()}")
                        close_button.click()
                        self.log_info("Scale tool dialog closed via button click")
                    else:
                        self.log_error("Could not find close button in scale tool dialog")
            else:
                self.log_error("Scale tool dialog not visible or not found")

        except Exception as e:
            self.log_error(f"Failed to close scale tool: {e}")
            import traceback
            self.log_error(f"Traceback: {traceback.format_exc()}")

    def _action_dismiss_any_dialog(self, params: Dict[str, Any]):
        """Dismiss any open dialog by finding and clicking common close buttons."""
        try:
            from PySide6.QtWidgets import QApplication, QPushButton, QDialog, QMessageBox

            self.log_info("Looking for any open dialogs to dismiss...")

            # Get all widgets
            app = QApplication.instance()
            all_widgets = app.allWidgets()

            # Find all visible dialogs and message boxes
            open_dialogs = []
            for widget in all_widgets:
                if widget.isVisible() and widget != self.main_window:
                    if isinstance(widget, (QDialog, QMessageBox)) or \
                       (hasattr(widget, 'windowTitle') and widget.windowTitle() and
                        widget.isWindow()):
                        open_dialogs.append(widget)

            self.log_info(f"Found {len(open_dialogs)} open dialogs")

            # Log all open dialogs
            for dialog in open_dialogs:
                dialog_type = type(dialog).__name__
                title = getattr(dialog, 'windowTitle', lambda: 'No Title')()
                self.log_info(f"Open dialog: {dialog_type} - '{title}'")

            # Try to dismiss each dialog
            dismissed_count = 0
            for dialog in open_dialogs:
                if self._try_dismiss_dialog(dialog):
                    dismissed_count += 1

            self.log_info(f"Successfully dismissed {dismissed_count} dialogs")
            return dismissed_count > 0

        except Exception as e:
            self.log_error(f"Failed to dismiss dialogs: {e}")
            import traceback
            self.log_error(f"Traceback: {traceback.format_exc()}")
            return False

    def _try_dismiss_dialog(self, dialog):
        """Try to dismiss a specific dialog using various methods."""
        try:
            from PySide6.QtWidgets import QPushButton, QMessageBox

            dialog_type = type(dialog).__name__
            title = getattr(dialog, 'windowTitle', lambda: 'No Title')()
            self.log_info(f"Attempting to dismiss {dialog_type}: '{title}'")

            # Method 1: Handle QMessageBox specifically
            if isinstance(dialog, QMessageBox):
                self.log_info("Handling QMessageBox")

                # Try standard buttons first
                for std_button in [QMessageBox.Ok, QMessageBox.Close, QMessageBox.Cancel,
                                 QMessageBox.Yes, QMessageBox.No]:
                    button = dialog.button(std_button)
                    if button and button.isVisible() and button.isEnabled():
                        self.log_info(f"Clicking QMessageBox standard button: {button.text()}")
                        button.click()
                        return True

                # Try default button
                default_button = dialog.defaultButton()
                if default_button:
                    self.log_info(f"Clicking QMessageBox default button: {default_button.text()}")
                    default_button.click()
                    return True

            # Method 2: Look for common close buttons by text
            common_close_texts = [
                'OK', '&OK', 'ok',
                'Close', '&Close', 'close',
                'Cancel', '&Cancel', 'cancel',
                'Quit', '&Quit', 'quit',
                'Done', '&Done', 'done',
                'Exit', '&Exit', 'exit',
                'Dismiss', '&Dismiss', 'dismiss',
                'Apply', '&Apply', 'apply'  # Sometimes Apply closes dialogs
            ]

            buttons = dialog.findChildren(QPushButton)
            self.log_info(f"Found {len(buttons)} buttons in dialog")

            # Log all available buttons
            button_texts = [btn.text() for btn in buttons if btn.isVisible()]
            self.log_info(f"Available buttons: {button_texts}")

            for button in buttons:
                if button.isVisible() and button.isEnabled():
                    button_text = button.text().strip()
                    if button_text in common_close_texts:
                        self.log_info(f"Clicking button by text: '{button_text}'")
                        button.click()
                        return True

            # Method 3: Look for buttons by object name
            common_close_names = [
                'ok_button', 'okButton', 'OK_button',
                'close_button', 'closeButton', 'Close_button',
                'cancel_button', 'cancelButton', 'Cancel_button',
                'quit_button', 'quitButton', 'Quit_button',
                'done_button', 'doneButton', 'Done_button',
                'apply_button', 'applyButton', 'Apply_button'
            ]

            for name in common_close_names:
                button = dialog.findChild(QPushButton, name)
                if button and button.isVisible() and button.isEnabled():
                    self.log_info(f"Clicking button by name: '{name}' (text: '{button.text()}')")
                    button.click()
                    return True

            # Method 4: Try dialog's built-in close methods
            if hasattr(dialog, 'accept') and callable(dialog.accept):
                self.log_info("Calling dialog.accept()")
                dialog.accept()
                return True

            if hasattr(dialog, 'close') and callable(dialog.close):
                self.log_info("Calling dialog.close()")
                dialog.close()
                return True

            if hasattr(dialog, 'reject') and callable(dialog.reject):
                self.log_info("Calling dialog.reject()")
                dialog.reject()
                return True

            # Method 5: Send Escape key to dialog
            try:
                from PySide6.QtCore import Qt
                from PySide6.QtGui import QKeyEvent
                from PySide6.QtCore import QCoreApplication

                self.log_info("Sending Escape key to dialog")
                key_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)
                QCoreApplication.postEvent(dialog, key_event)
                return True
            except:
                pass

            self.log_warning(f"Could not dismiss dialog: {dialog_type} - '{title}'")
            return False

        except Exception as e:
            self.log_error(f"Error dismissing dialog: {e}")
            return False

    def _action_click_menu_item(self, params: Dict[str, Any]):
        """Click a specific menu item."""
        try:
            menu_name = params.get('menu', '')
            item_name = params.get('item', '')

            if not menu_name or not item_name:
                self.log_error("Menu name and item name required")
                return False

            self.log_info(f"Clicking menu item: {menu_name} → {item_name}")

            if not self.main_window or not hasattr(self.main_window, 'menuBar'):
                self.log_error("Main window or menu bar not available")
                return False

            menubar = self.main_window.menuBar()

            # Find the menu
            target_menu = None
            for action in menubar.actions():
                if action.text().replace('&', '') == menu_name:
                    target_menu = action.menu()
                    break

            if not target_menu:
                self.log_error(f"Menu '{menu_name}' not found")
                return False

            # Find the menu item
            target_action = None
            for action in target_menu.actions():
                if action.text().replace('&', '') == item_name:
                    target_action = action
                    break

            if not target_action:
                self.log_error(f"Menu item '{item_name}' not found in '{menu_name}' menu")
                # Log available items for debugging
                available_items = [action.text().replace('&', '') for action in target_menu.actions() if action.text()]
                self.log_info(f"Available items in {menu_name}: {available_items}")
                return False

            # Check if the action is enabled
            if not target_action.isEnabled():
                self.log_warning(f"Menu item '{menu_name} → {item_name}' is disabled")
                return False

            # Trigger the action
            target_action.trigger()
            self.log_info(f"Successfully clicked menu item: {menu_name} → {item_name}")
            return True

        except Exception as e:
            self.log_error(f"Failed to click menu item: {e}")
            import traceback
            self.log_error(f"Traceback: {traceback.format_exc()}")
            return False

    def _action_click_settings_tab(self, params: Dict[str, Any]):
        """Click a settings tab in the settings dialog."""
        try:
            from PySide6.QtWidgets import QTabWidget, QApplication

            tab_name = params.get('tab', '')
            if not tab_name:
                self.log_error("Tab name required")
                return False

            self.log_info(f"Clicking settings tab: {tab_name}")

            # Find settings dialog with tab widget
            app = QApplication.instance()
            all_widgets = app.allWidgets()

            tab_widget = None
            for widget in all_widgets:
                if widget.isVisible() and isinstance(widget, QTabWidget):
                    # Check if this tab widget is in a settings dialog
                    parent = widget.parent()
                    while parent:
                        if hasattr(parent, 'windowTitle') and 'settings' in parent.windowTitle().lower():
                            tab_widget = widget
                            break
                        parent = parent.parent()
                    if tab_widget:
                        break

            if not tab_widget:
                self.log_error("Settings tab widget not found")
                return False

            # Find the tab by name
            tab_index = -1
            for i in range(tab_widget.count()):
                if tab_widget.tabText(i).replace('&', '') == tab_name:
                    tab_index = i
                    break

            if tab_index == -1:
                self.log_error(f"Tab '{tab_name}' not found")
                # Log available tabs
                available_tabs = [tab_widget.tabText(i).replace('&', '') for i in range(tab_widget.count())]
                self.log_info(f"Available tabs: {available_tabs}")
                return False

            # Click the tab
            tab_widget.setCurrentIndex(tab_index)
            self.log_info(f"Successfully clicked settings tab: {tab_name}")
            return True

        except Exception as e:
            self.log_error(f"Failed to click settings tab: {e}")
            import traceback
            self.log_error(f"Traceback: {traceback.format_exc()}")
            return False

    def _action_change_setting(self, params: Dict[str, Any]):
        """Change a setting value in the settings dialog."""
        try:
            tab_name = params.get('tab', '')
            setting_name = params.get('setting', '')
            setting_value = params.get('value', '')

            if not tab_name or not setting_name:
                self.log_error("Tab name and setting name required")
                return False

            self.log_info(f"Changing setting: {tab_name}.{setting_name} = {setting_value}")

            # This is a placeholder implementation
            # In a real implementation, you would:
            # 1. Navigate to the correct tab
            # 2. Find the setting control (checkbox, textbox, combobox, etc.)
            # 3. Change its value

            # For now, just log the action
            self.log_info(f"Setting change simulated: {tab_name}.{setting_name} = {setting_value}")
            return True

        except Exception as e:
            self.log_error(f"Failed to change setting: {e}")
            import traceback
            self.log_error(f"Traceback: {traceback.format_exc()}")
            return False

    def _action_select_wing_tip_points(self, params: Dict[str, Any]):
        """Select wing tip points for scaling (simulates clicking on wing tips)."""
        try:
            # Get wing tip coordinates from parameters or use defaults for Sky Skanner
            point1_x = params.get('point1_x', 300)  # Left wing tip
            point1_y = params.get('point1_y', 400)
            point2_x = params.get('point2_x', 800)  # Right wing tip
            point2_y = params.get('point2_y', 400)

            # Find the scaling dialog and document viewer
            scaling_dialog = None
            document_viewer = None

            if self.main_window:
                if hasattr(self.main_window, 'scaling_dialog'):
                    scaling_dialog = self.main_window.scaling_dialog
                if hasattr(self.main_window, 'document_viewer'):
                    document_viewer = self.main_window.document_viewer

            if scaling_dialog and scaling_dialog.isVisible() and document_viewer:
                # Enable point selection mode in document viewer
                document_viewer.set_point_selection_mode(True)
                self.log_info("Enabled point selection mode in document viewer")

                # Simulate clicking on the document at wing tip locations
                # This should trigger the point_selected signal which is connected to scaling_dialog.on_point_selected

                # Simulate first wing tip click
                self.log_info(f"Simulating click on wing tip 1: ({point1_x}, {point1_y})")
                if hasattr(document_viewer, 'point_selected'):
                    document_viewer.point_selected.emit(point1_x, point1_y)
                else:
                    # Fallback: call scaling dialog directly
                    scaling_dialog.on_point_selected(point1_x, point1_y)

                # Simulate second wing tip click
                self.log_info(f"Simulating click on wing tip 2: ({point2_x}, {point2_y})")
                if hasattr(document_viewer, 'point_selected'):
                    document_viewer.point_selected.emit(point2_x, point2_y)
                else:
                    # Fallback: call scaling dialog directly
                    scaling_dialog.on_point_selected(point2_x, point2_y)

                self.log_info("Wing tip points selected for scaling")
            else:
                self.log_error("Scale dialog not visible or document viewer not available")

        except Exception as e:
            self.log_error(f"Failed to select wing tip points: {e}")

    def _action_set_scale_distance(self, params: Dict[str, Any]):
        """Set the distance value in the scale tool dialog."""
        try:
            # Get distance and unit from parameters
            distance = params.get('distance', '460')
            unit = params.get('unit', 'mm')

            # Find the scaling dialog
            scaling_dialog = None
            if self.main_window and hasattr(self.main_window, 'scaling_dialog'):
                scaling_dialog = self.main_window.scaling_dialog

            if scaling_dialog and scaling_dialog.isVisible():
                # Find the distance input field
                distance_input = scaling_dialog.distance_input
                if distance_input:
                    # Clear and set the distance value
                    distance_input.clear()
                    distance_input.setText(distance)
                    self.log_info(f"Set scale distance to: {distance}")

                    # Set the unit if units combo exists
                    units_combo = scaling_dialog.units_combo
                    if units_combo:
                        index = units_combo.findText(unit)
                        if index >= 0:
                            units_combo.setCurrentIndex(index)
                            self.log_info(f"Set scale unit to: {unit}")
                        else:
                            self.log_error(f"Unit '{unit}' not found in combo box")

                    # Trigger update to calculate scale
                    scaling_dialog.update_scale_preview()
                else:
                    self.log_error("Distance input field not found in scale dialog")
            else:
                self.log_error("Scale dialog not visible - cannot set distance")

        except Exception as e:
            self.log_error(f"Failed to set scale distance: {e}")

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
