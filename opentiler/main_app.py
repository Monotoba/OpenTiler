"""
Main application entry point for OpenTiler.
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from .main_window import MainWindow


def main():
    """Main application entry point."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("OpenTiler")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Randall Morgan")
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start the event loop
    sys.exit(app.exec())
