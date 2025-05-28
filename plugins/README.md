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
- ✅ **Event System** - React to OpenTiler events
- ✅ **Menu Integration** - Add custom menu items and toolbars
- ✅ **Settings Integration** - Plugin-specific configuration
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
