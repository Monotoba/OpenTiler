"""
Main application entry point for OpenTiler.
"""

import sys
import argparse
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from .main_window import MainWindow


def main():
    """Main application entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="OpenTiler - Architectural Drawing Tiler")
    parser.add_argument('document', nargs='?', help='Document file to load')
    parser.add_argument('--automation-mode', action='store_true', help='Enable automation mode')
    parser.add_argument('--enable-plugins', action='store_true', help='Enable plugin system')
    parser.add_argument('--plugin', action='append', help='Load specific plugin')

    args = parser.parse_args()

    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("OpenTiler")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Randall Morgan")

    # Create and show main window
    main_window = MainWindow()

    # Enable automation mode if requested
    if args.automation_mode or args.enable_plugins or args.plugin:
        try:
            # Import and initialize plugin system
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from plugins.plugin_manager import PluginManager
            from plugins.builtin.automation_plugin import AutomationPlugin

            # Create plugin manager
            plugin_manager = PluginManager(main_window)
            main_window.plugin_manager = plugin_manager

            # Load automation plugin if requested
            if args.automation_mode or (args.plugin and 'automation' in args.plugin):
                automation_plugin = AutomationPlugin(main_window)
                plugin_manager.plugins["automation"] = automation_plugin

                # Initialize and enable automation plugin
                if plugin_manager.initialize_plugin("automation"):
                    if plugin_manager.enable_plugin("automation"):
                        print("✅ Automation plugin enabled - server running on port 8888")
                    else:
                        print("❌ Failed to enable automation plugin")
                else:
                    print("❌ Failed to initialize automation plugin")

            # Load other specified plugins
            if args.plugin:
                for plugin_name in args.plugin:
                    if plugin_name != 'automation':  # Already handled above
                        if plugin_manager.load_plugin(plugin_name):
                            plugin_manager.initialize_plugin(plugin_name)
                            plugin_manager.enable_plugin(plugin_name)
                            print(f"✅ Plugin '{plugin_name}' loaded and enabled")
                        else:
                            print(f"❌ Failed to load plugin '{plugin_name}'")

        except Exception as e:
            print(f"❌ Plugin system error: {e}")

    # Load document if specified
    if args.document:
        document_path = Path(args.document)
        if document_path.exists():
            # Load document after window is shown
            def load_document():
                try:
                    main_window.load_document(str(document_path))
                    print(f"✅ Loaded document: {document_path.name}")
                except Exception as e:
                    print(f"❌ Failed to load document: {e}")

            # Use QTimer to load document after window is shown
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1000, load_document)
        else:
            print(f"❌ Document not found: {args.document}")

    main_window.show()

    # Start the event loop
    sys.exit(app.exec())
