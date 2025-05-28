# OpenTiler Plugin System

![Plugin System Architecture](../docs/images/plugin-system-architecture.png)

The OpenTiler Plugin System provides a powerful, extensible architecture for adding functionality to OpenTiler without modifying the core application.

## 🎯 Overview

### What is the Plugin System?

The plugin system allows developers to:
- **Extend OpenTiler functionality** without modifying core code
- **Add new features** through modular plugins
- **Customize behavior** for specific workflows
- **Integrate external tools** and services
- **Automate complex tasks** and documentation generation

### Key Features

- ✅ **Dynamic Loading** - Plugins loaded at runtime
- ✅ **Dependency Management** - Automatic dependency resolution
- ✅ **Comprehensive Hook System** - Deep integration with OpenTiler's core functions
- ✅ **Content Access Control** - Secure access to plan views, tiles, and measurements
- ✅ **Before/After Hooks** - Intercept and modify drawing and transformation operations
- ✅ **Menu Integration** - Add custom menu items and toolbars
- ✅ **Settings Integration** - Plugin-specific configuration with UI
- ✅ **Plugin Manager UI** - Complete management interface in settings dialog
- ✅ **Error Handling** - Robust error management and recovery
- ✅ **Hot Reload** - Reload plugins without restarting OpenTiler

## 🏗️ Architecture

### Core Components

#### **Plugin Manager** (`plugin_manager.py`)
- Discovers and loads plugins
- Manages plugin lifecycle (initialize, enable, disable, cleanup)
- Handles dependencies and load order
- Provides plugin communication

#### **Base Plugin** (`base_plugin.py`)
- Abstract base class for all plugins
- Defines plugin interface and lifecycle methods
- Provides event handling and configuration support
- Includes error handling and logging

#### **Plugin Registry** (`plugin_registry.py`)
- Maintains registry of available plugins
- Tracks dependencies and relationships
- Provides plugin discovery and metadata

#### **Hook System** (`hook_system.py`)
- Comprehensive before/after hooks for all OpenTiler operations
- Document lifecycle, rendering, measurements, exports, and UI events
- Priority-based hook execution with cancellation support
- Context-rich event data for plugin decision making

#### **Content Access** (`content_access.py`)
- Controlled access to plan views, tile previews, and measurements
- Read-only, read-write, and full-control access levels
- Secure plugin sandboxing with permission-based access
- Real-time document content and transformation access

#### **Plugin Manager UI** (`plugin_manager_ui.py`)
- Complete plugin management interface for settings dialog
- Plugin discovery, enable/disable, and configuration
- Hook registration status and execution statistics
- Real-time plugin status monitoring and error reporting

### Plugin Types

#### **Built-in Plugins** (`builtin/`)
- Core plugins shipped with OpenTiler
- Essential functionality and automation tools
- Examples: Automation Plugin, Export Enhancer

#### **External Plugins** (`external/`)
- Third-party plugins
- Community-contributed functionality
- Downloaded or installed separately

#### **User Plugins** (`user/`)
- User-created custom plugins
- Personal automation and customization
- Local development and testing

## 🚀 Getting Started

### Enabling the Plugin System

Add to your OpenTiler `main.py`:

```python
from opentiler_plugin_integration import integrate_plugins_with_main_window, add_plugin_arguments

def main():
    # Parse arguments with plugin support
    parser = argparse.ArgumentParser()
    add_plugin_arguments(parser)
    args = parser.parse_args()

    # Create main window
    main_window = OpenTilerMainWindow()

    # Integrate plugin system
    plugin_integration = integrate_plugins_with_main_window(main_window, args)

    # Run application
    main_window.show()
    return app.exec()
```

### Command Line Options

```bash
# Enable automation mode for documentation
python main.py --automation-mode

# Disable all plugins
python main.py --disable-plugins

# Custom plugin configuration directory
python main.py --plugin-config-dir /path/to/config
```

## 🔌 Built-in Plugins

### Automation Plugin

The **Automation Plugin** provides comprehensive automation capabilities:

#### **Features:**
- **Keyboard Shortcuts** - Quick access to all OpenTiler functions
- **Socket API** - Remote control via network commands
- **Screenshot Generation** - Automated documentation capture
- **Menu Automation** - Programmatic menu and dialog control

#### **Keyboard Shortcuts:**
| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+F1` | Load demo document |
| `Ctrl+Shift+F2` | Open file dialog |
| `Ctrl+Shift+F3` | Open export dialog |
| `Ctrl+Shift+F4` | Open settings dialog |
| `Ctrl+Shift+F5` | Open scale tool |
| `Ctrl+Shift+F6` | Open about dialog |
| `Ctrl+Shift+F7` | Capture screenshot |
| `Ctrl+Shift+F8` | Open file menu |
| `Ctrl+Shift+F9` | Open tools menu |
| `Ctrl+Shift+F10` | Open help menu |

#### **Socket API:**
```python
import socket
import json

# Connect to automation server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8888))

# Send command
command = {
    'action': 'load_demo_document',
    'params': {}
}
sock.send(json.dumps(command).encode('utf-8'))

# Receive response
response = json.loads(sock.recv(1024).decode('utf-8'))
```

#### **Available Actions:**
- `load_demo_document` - Load the Sky Skanner demo file
- `open_file_menu` - Open File menu
- `open_edit_menu` - Open Edit menu
- `open_view_menu` - Open View menu
- `open_tools_menu` - Open Tools menu
- `open_help_menu` - Open Help menu
- `open_file_dialog` - Open file selection dialog
- `open_export_dialog` - Open export configuration dialog
- `open_settings_dialog` - Open application settings
- `open_scale_tool` - Open scale measurement tool
- `open_about_dialog` - Open about dialog
- `zoom_in` - Increase zoom level
- `zoom_out` - Decrease zoom level
- `fit_to_window` - Fit document to window
- `rotate_left` - Rotate document counter-clockwise
- `rotate_right` - Rotate document clockwise
- `capture_screenshot` - Capture screenshot of OpenTiler

### Snap Plugin

The **Snap Plugin** demonstrates the hook system with intelligent snap functionality:

#### **Features:**
- **Measurement Hooks** - Intercept measurement events for snap functionality
- **Content Analysis** - Analyze document content for snap points
- **Visual Indicators** - Render snap points as visual overlays
- **Grid Snap** - Snap to regular grid points
- **Content Snap** - Snap to document corners, edges, and intersections

#### **Hook Integration:**
```python
@property
def supported_hooks(self) -> List[HookType]:
    return [
        HookType.MEASUREMENT_BEFORE_START,
        HookType.MEASUREMENT_BEFORE_UPDATE,
        HookType.RENDER_AFTER_DRAW,
        HookType.DOCUMENT_AFTER_LOAD
    ]
```

## 🔗 Hook System

### Comprehensive Hook Types

The hook system provides **before** and **after** hooks for all major OpenTiler operations:

#### **Document Lifecycle Hooks:**
- `DOCUMENT_BEFORE_LOAD` / `DOCUMENT_AFTER_LOAD`
- `DOCUMENT_BEFORE_CLOSE` / `DOCUMENT_AFTER_CLOSE`

#### **Rendering Hooks:**
- `RENDER_BEFORE_DRAW` / `RENDER_AFTER_DRAW`
- `RENDER_BEFORE_TRANSFORM` / `RENDER_AFTER_TRANSFORM`

#### **Tile Processing Hooks:**
- `TILE_BEFORE_GENERATE` / `TILE_AFTER_GENERATE`
- `TILE_BEFORE_EXPORT` / `TILE_AFTER_EXPORT`

#### **Measurement Hooks:**
- `MEASUREMENT_BEFORE_START` / `MEASUREMENT_AFTER_START`
- `MEASUREMENT_BEFORE_UPDATE` / `MEASUREMENT_AFTER_UPDATE`
- `MEASUREMENT_BEFORE_FINISH` / `MEASUREMENT_AFTER_FINISH`

#### **Scale Hooks:**
- `SCALE_BEFORE_SET` / `SCALE_AFTER_SET`
- `SCALE_BEFORE_CALCULATE` / `SCALE_AFTER_CALCULATE`

#### **View Transformation Hooks:**
- `VIEW_BEFORE_ZOOM` / `VIEW_AFTER_ZOOM`
- `VIEW_BEFORE_PAN` / `VIEW_AFTER_PAN`
- `VIEW_BEFORE_ROTATE` / `VIEW_AFTER_ROTATE`

#### **Export Hooks:**
- `EXPORT_BEFORE_START` / `EXPORT_AFTER_START`
- `EXPORT_BEFORE_PROCESS` / `EXPORT_AFTER_PROCESS`
- `EXPORT_BEFORE_SAVE` / `EXPORT_AFTER_SAVE`

### Hook Handler Implementation

```python
class MyHookHandler(HookHandler):
    @property
    def supported_hooks(self) -> List[HookType]:
        return [HookType.RENDER_BEFORE_DRAW, HookType.MEASUREMENT_AFTER_FINISH]

    @property
    def priority(self) -> int:
        return 100  # Higher = executed first

    def handle_hook(self, context: HookContext) -> bool:
        if context.hook_type == HookType.RENDER_BEFORE_DRAW:
            # Modify rendering before it happens
            painter = context.data.get('painter')
            # Add custom overlays, modify transforms, etc.

        elif context.hook_type == HookType.MEASUREMENT_AFTER_FINISH:
            # React to completed measurements
            distance = context.data.get('distance', 0)
            units = context.data.get('units', 'mm')
            # Log, validate, or trigger other actions

        return True  # Success
```

## 🔐 Content Access System

### Access Levels

- **READ_ONLY** - View content and state information
- **READ_WRITE** - Modify view settings and add overlays
- **FULL_CONTROL** - Complete access to all content and transformations

### Plan View Access

```python
def get_document_access_requirements(self) -> Dict[str, bool]:
    return {
        'plan_view': True,        # Access to plan view content
        'tile_preview': True,     # Access to tile preview
        'document_data': True,    # Access to raw document data
        'metadata': True,         # Access to document metadata
        'measurements': True,     # Access to measurement data
        'transformations': True   # Access to transformation data
    }

# In plugin initialization:
plan_view = self.content_access_objects['plan_view']
document_info = plan_view.get_document_info()
content_image = plan_view.get_content_image()
plan_view.add_overlay('my_overlay', my_draw_function)
```

### Tile Preview Access

```python
tile_preview = self.content_access_objects['tile_preview']
tile_count = tile_preview.get_tile_count()
tile_info = tile_preview.get_tile_info(0)
tile_image = tile_preview.get_tile_image(0, (800, 600))
```

### Measurement Access

```python
measurement_access = self.content_access_objects['measurements']
measurements = measurement_access.get_measurements()
snap_points = measurement_access.get_snap_points(point, radius=10)
measurement_id = measurement_access.add_measurement(start, end)
```

## 🛠️ Creating Plugins

### Basic Plugin Structure

```python
from plugins.base_plugin import BasePlugin, PluginInfo

class MyPlugin(BasePlugin):
    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="My Plugin",
            version="1.0.0",
            description="Example plugin for OpenTiler",
            author="Your Name",
            dependencies=[]
        )

    def initialize(self) -> bool:
        self.log_info("Initializing My Plugin")
        return True

    def enable(self) -> bool:
        self.log_info("Enabling My Plugin")
        return True

    def disable(self) -> bool:
        self.log_info("Disabling My Plugin")
        return True

    def cleanup(self) -> bool:
        self.log_info("Cleaning up My Plugin")
        return True
```

### Plugin with Menu Actions

```python
from PySide6.QtWidgets import QAction

class MenuPlugin(BasePlugin):
    def get_menu_actions(self):
        action = QAction("My Action", self.main_window)
        action.triggered.connect(self.my_action)
        return [action]

    def my_action(self):
        self.log_info("My action executed!")
```

### Plugin with Settings

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox

class SettingsPlugin(BasePlugin):
    def get_settings_widget(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.enable_feature = QCheckBox("Enable Feature")
        layout.addWidget(self.enable_feature)

        return widget

    def get_config(self):
        return {'enable_feature': self.enable_feature.isChecked()}

    def set_config(self, config):
        self.enable_feature.setChecked(config.get('enable_feature', False))
        return True
```

## 🔧 Automation Client

Use the automation client to control OpenTiler remotely:

### Generate Documentation Screenshots

```bash
# Generate complete documentation
python tools/automation_client.py --generate-docs

# Execute specific sequence
python tools/automation_client.py --sequence documentation_full

# Interactive mode
python tools/automation_client.py --interactive
```

### Automation Sequences

#### **documentation_full**
Complete documentation screenshot generation:
- Empty interface
- Document loaded (Sky Skanner)
- All menus (File, Edit, View, Tools, Help)
- All dialogs (File, Export, Settings, Scale, About)

#### **basic_workflow**
Basic user workflow demonstration:
- Empty interface → Load document → Zoom → Fit to window

#### **menu_tour**
Tour of all OpenTiler menus with screenshots

### Custom Automation

```python
from tools.automation_client import OpenTilerAutomationClient

client = OpenTilerAutomationClient()
if client.connect():
    # Load demo document
    client.send_command('load_demo_document')

    # Capture screenshot
    client.send_command('capture_screenshot', {
        'filename': 'my_screenshot.png',
        'size': (1600, 1000)
    })

    client.disconnect()
```

## 📁 Directory Structure

```
plugins/
├── __init__.py                 # Plugin system exports
├── base_plugin.py             # Base plugin class
├── plugin_manager.py          # Plugin manager
├── plugin_registry.py         # Plugin registry
├── README.md                  # This file
├── builtin/                   # Built-in plugins
│   ├── __init__.py
│   └── automation_plugin.py   # Automation plugin
├── external/                  # External plugins
│   └── (third-party plugins)
└── user/                      # User plugins
    └── (custom plugins)

config/
└── plugins/
    ├── plugins.json           # Plugin configuration
    └── user/                  # User plugin directory

tools/
└── automation_client.py       # Automation client
```

## 🔍 Plugin Development

### Plugin Lifecycle

1. **Discovery** - Plugin manager scans plugin directories
2. **Loading** - Plugin class is imported and instantiated
3. **Registration** - Plugin info is registered in registry
4. **Initialization** - Plugin's `initialize()` method is called
5. **Enabling** - Plugin's `enable()` method is called
6. **Runtime** - Plugin responds to events and provides functionality
7. **Disabling** - Plugin's `disable()` method is called
8. **Cleanup** - Plugin's `cleanup()` method is called

### Event Handling

Plugins can respond to OpenTiler events:

```python
def handle_document_loaded(self, document_path: str):
    self.log_info(f"Document loaded: {document_path}")

def handle_export_started(self, export_settings):
    self.log_info("Export started")

def handle_export_finished(self, success: bool, output_path: str):
    self.log_info(f"Export finished: {success}")
```

### Error Handling

```python
def enable(self) -> bool:
    try:
        # Plugin initialization code
        return True
    except Exception as e:
        self.log_error(f"Failed to enable: {e}")
        return False
```

## 🚀 Future Enhancements

### Planned Features

- **Plugin Marketplace** - Browse and install plugins
- **Visual Plugin Editor** - GUI for creating simple plugins
- **Plugin Templates** - Scaffolding for common plugin types
- **Advanced Event System** - More granular event handling
- **Plugin Sandboxing** - Security isolation for external plugins
- **Hot Reload** - Update plugins without restart
- **Plugin Dependencies** - Automatic dependency installation

### Plugin Ideas

- **Export Enhancers** - Additional export formats and options
- **Cloud Integration** - Upload to cloud services
- **CAD Integration** - Enhanced DXF and CAD file support
- **Measurement Tools** - Advanced measurement and annotation
- **Batch Processing** - Process multiple documents
- **Template System** - Document templates and presets
- **Collaboration** - Share and collaborate on documents
- **Version Control** - Git integration for document tracking

## 📚 Resources

- **Plugin API Reference** - Complete API documentation
- **Example Plugins** - Sample implementations
- **Development Guide** - Step-by-step plugin creation
- **Best Practices** - Plugin development guidelines
- **Community Forum** - Plugin development discussions

---

*The OpenTiler Plugin System enables unlimited extensibility while maintaining a clean, stable core application.*
