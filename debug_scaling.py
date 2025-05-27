#!/usr/bin/env python3
"""
Debug script to test scaling functionality.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Add the opentiler package to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from opentiler.main_window import MainWindow

def debug_scaling():
    """Debug the scaling functionality."""
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

            # Test scaling dialog
            print("\n🔧 Testing scaling dialog...")
            main_window.show_scaling_dialog()

            # Check if dialog was created
            if main_window.scaling_dialog:
                print("✅ Scaling dialog created")

                # Check point selection mode
                if main_window.document_viewer.point_selection_mode:
                    print("✅ Point selection mode enabled")
                else:
                    print("❌ Point selection mode NOT enabled")

                # Check signal connections
                print("\n🔗 Checking signal connections...")

                # Check if signals exist
                print(f"Point selected signal exists: {hasattr(main_window.document_viewer, 'point_selected')}")
                print(f"Scale applied signal exists: {hasattr(main_window.scaling_dialog, 'scale_applied')}")

                # Check if the connection was made in show_scaling_dialog
                print(f"Scaling dialog has parent: {main_window.scaling_dialog.parent() is not None}")

                # Test manual point selection
                print("\n🎯 Testing manual point selection...")
                try:
                    # Simulate point selection
                    main_window.scaling_dialog.on_point_selected(100, 100)
                    print("✅ First point set")

                    main_window.scaling_dialog.on_point_selected(200, 100)
                    print("✅ Second point set")

                    # Check if points were set
                    if main_window.scaling_dialog.point1 and main_window.scaling_dialog.point2:
                        print(f"Point 1: {main_window.scaling_dialog.point1}")
                        print(f"Point 2: {main_window.scaling_dialog.point2}")

                        # Set distance and test scale calculation
                        main_window.scaling_dialog.distance_input.setText("1000")
                        main_window.scaling_dialog.update_scale_preview()

                        if main_window.scaling_dialog.apply_button.isEnabled():
                            print("✅ Apply button enabled - scale calculation working")
                        else:
                            print("❌ Apply button disabled - scale calculation failed")
                    else:
                        print("❌ Points not set properly")

                except Exception as e:
                    print(f"❌ Error in manual point selection: {e}")

            else:
                print("❌ Scaling dialog NOT created")

        else:
            print("❌ Failed to load document")

    else:
        print(f"❌ Test document not found: {test_doc}")

    print("\n🖱️  Application is running - test the scaling tool manually!")
    print("1. Click Tools → Scaling Tool")
    print("2. Click two points on the document")
    print("3. Enter a distance and click Apply")
    print("Press Ctrl+C in terminal to exit")

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    debug_scaling()
