#!/usr/bin/env python3
"""
Simple test for FreeCAD detection without Qt dependencies.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'opentiler'))

def test_freecad_detection_simple():
    """Test FreeCAD detection without importing Qt components."""
    print("Testing FreeCAD Detection (No Qt)")
    print("=" * 40)
    
    try:
        # Test command detection directly
        import shutil
        freecad_commands = ['freecad', 'FreeCAD', '/snap/bin/freecad']
        
        found_command = None
        for cmd in freecad_commands:
            if shutil.which(cmd):
                found_command = cmd
                print(f"✅ Found FreeCAD command: {cmd}")
                break
        
        if not found_command:
            print("❌ No FreeCAD command found")
            return False
            
        # Test the detection function
        from opentiler.formats.freecad_handler import _detect_freecad, FREECAD_AVAILABLE, FREECAD_COMMAND
        
        print("\nRunning detection...")
        _detect_freecad()
        
        print(f"FREECAD_AVAILABLE: {FREECAD_AVAILABLE}")
        print(f"FREECAD_COMMAND: {FREECAD_COMMAND}")
        
        # Test the handler methods
        from opentiler.formats.freecad_handler import FreeCADHandler
        
        handler = FreeCADHandler()
        available = handler.is_available()
        status = handler.get_availability_status()
        
        print(f"Handler.is_available(): {available}")
        print(f"Handler.get_availability_status(): {status}")
        
        return available
        
    except Exception as e:
        print(f"❌ Error during detection: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("FreeCAD Detection Test")
    print("=" * 50)
    
    success = test_freecad_detection_simple()
    
    if success:
        print("\n✅ FreeCAD detection working!")
        print("The Save-As dialog should now show FreeCAD as available.")
    else:
        print("\n❌ FreeCAD detection failed.")
        print("Check FreeCAD installation and PATH.")
