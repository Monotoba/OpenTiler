#!/usr/bin/env python3
"""
Test script to verify OpenTiler GUI functionality with a real document.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Add the opentiler package to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'opentiler'))

from opentiler.main_window import MainWindow


def test_document_loading():
    """Test loading a document from the plans folder."""
    app = QApplication(sys.argv)

    # Create main window
    main_window = MainWindow()
    main_window.show()

    # Test document path
    test_doc = "plans/original_plans/1147 Sky Skanner_2.pdf"

    if os.path.exists(test_doc):
        print(f"Loading test document: {test_doc}")

        # Load the document
        success = main_window.document_viewer.load_document(test_doc)

        if success:
            print("✅ Document loaded successfully!")
            print(f"Document path: {main_window.document_viewer.current_document}")
            print(f"Zoom factor: {main_window.document_viewer.zoom_factor}")
            print(f"Scale factor: {main_window.document_viewer.scale_factor}")

            # Test zoom functionality
            print("\n🔍 Testing zoom functionality...")
            original_zoom = main_window.document_viewer.zoom_factor
            main_window.document_viewer.zoom_in()
            print(f"After zoom in: {main_window.document_viewer.zoom_factor}")
            main_window.document_viewer.zoom_out()
            print(f"After zoom out: {main_window.document_viewer.zoom_factor}")
            main_window.document_viewer.zoom_fit()
            print(f"After zoom fit: {main_window.document_viewer.zoom_factor}")

            # Set zoom to a large value to ensure panning is possible
            print("\n🔍 Setting large zoom for panning test...")
            main_window.document_viewer.zoom_factor = 3.0  # Set to 300%
            main_window.document_viewer._update_display()
            print(f"Set zoom factor to: {main_window.document_viewer.zoom_factor}")

            # Check scroll bar ranges
            h_bar = main_window.document_viewer.scroll_area.horizontalScrollBar()
            v_bar = main_window.document_viewer.scroll_area.verticalScrollBar()
            print(f"Scroll bar ranges: H={h_bar.minimum()}-{h_bar.maximum()}, V={v_bar.minimum()}-{v_bar.maximum()}")

            if h_bar.maximum() > 0 or v_bar.maximum() > 0:
                print("✅ Scroll bars have range - panning should work!")
            else:
                print("❌ Scroll bars still have no range - panning won't work")

            # Test scaling dialog
            print("\n📏 Testing scaling dialog...")
            main_window.show_scaling_dialog()
            if main_window.scaling_dialog:
                print("✅ Scaling dialog created successfully!")
                print(f"Point selection mode: {main_window.document_viewer.point_selection_mode}")

            print("\n🎯 GUI is ready for manual testing!")
            print("You can now:")
            print("- Use middle mouse button to pan")
            print("- Use mouse wheel to zoom")
            print("- Click points in scaling mode")
            print("- Test all the controls")

        else:
            print("❌ Failed to load document")

    else:
        print(f"❌ Test document not found: {test_doc}")
        print("Available files in plans/original_plans/:")
        plans_dir = "plans/original_plans"
        if os.path.exists(plans_dir):
            files = os.listdir(plans_dir)[:10]  # Show first 10 files
            for f in files:
                print(f"  - {f}")

    # Keep the application running for manual testing
    print("\n🖱️  Application is running - test the mouse controls!")
    print("Press Ctrl+C in terminal to exit")

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    test_document_loading()
