#!/usr/bin/env python3
"""
Test the complete scaling and tiling process.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Add the opentiler package to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from opentiler.main_window import MainWindow

def test_scaling_process():
    """Test the scaling and tiling process."""
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

            # Simulate scaling process
            print("\n🔧 Simulating scaling process...")

            # Simulate two points being selected (example coordinates)
            point1 = (100, 100)
            point2 = (200, 100)  # 100 pixels apart horizontally

            # Calculate pixel distance
            dx = point2[0] - point1[0]
            dy = point2[1] - point1[1]
            pixel_distance = (dx**2 + dy**2)**0.5
            print(f"Pixel distance: {pixel_distance} pixels")

            # Assume this represents 10mm in real world (small scale for testing)
            real_distance = 10.0  # mm
            scale_factor = real_distance / pixel_distance
            print(f"Scale factor: {scale_factor} mm/pixel")

            # Manually trigger the scaling process
            print("\n🎯 Triggering tiling process...")
            main_window.on_scale_applied(scale_factor)

            print("\n✅ Test completed! Check the GUI for tiles.")

        else:
            print("❌ Failed to load document")

    else:
        print(f"❌ Test document not found: {test_doc}")

    # Keep the application running for manual inspection
    print("\n🖱️  Application is running - check for tiles!")
    print("Press Ctrl+C in terminal to exit")

    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    test_scaling_process()
