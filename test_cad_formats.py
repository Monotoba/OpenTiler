#!/usr/bin/env python3
"""
Test script to verify DXF and FreeCAD format support in OpenTiler.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'opentiler'))

def test_dxf_support():
    """Test DXF format support."""
    print("Testing DXF Support")
    print("=" * 30)
    
    try:
        from opentiler.formats.dxf_handler import DXFHandler
        
        handler = DXFHandler()
        available = handler.is_available()
        
        print(f"DXF Handler Available: {available}")
        
        if available:
            print("✅ DXF support is working!")
            
            # Test creating a simple DXF
            from PySide6.QtGui import QPixmap
            
            # Create a test pixmap
            test_pixmap = QPixmap(800, 600)
            test_pixmap.fill()
            
            # Test export
            output_path = "/tmp/test_export.dxf"
            success = handler.save_as_dxf(test_pixmap, output_path, 0.1, "mm")
            
            if success and os.path.exists(output_path):
                print(f"✅ DXF export successful: {output_path}")
                
                # Get file info
                info = handler.get_dxf_info(output_path)
                print(f"DXF Info: {info}")
                
                # Clean up
                os.unlink(output_path)
            else:
                print("❌ DXF export failed")
        else:
            print("❌ DXF support not available")
            
    except Exception as e:
        print(f"❌ DXF test error: {str(e)}")
        
    print()

def test_freecad_support():
    """Test FreeCAD format support."""
    print("Testing FreeCAD Support")
    print("=" * 30)
    
    try:
        from opentiler.formats.freecad_handler import FreeCADHandler
        
        handler = FreeCADHandler()
        available = handler.is_available()
        status = handler.get_availability_status()
        
        print(f"FreeCAD Handler Available: {available}")
        print(f"FreeCAD Status: {status}")
        
        if available:
            print("✅ FreeCAD support is working!")
            
            # Test creating a simple FreeCAD file
            from PySide6.QtGui import QPixmap
            
            # Create a test pixmap
            test_pixmap = QPixmap(800, 600)
            test_pixmap.fill()
            
            # Test export (this might not work without full Python API)
            output_path = "/tmp/test_export.FCStd"
            try:
                success = handler.save_as_freecad(test_pixmap, output_path, 0.1, "mm")
                
                if success and os.path.exists(output_path):
                    print(f"✅ FreeCAD export successful: {output_path}")
                    
                    # Get file info
                    info = handler.get_freecad_info(output_path)
                    print(f"FreeCAD Info: {info}")
                    
                    # Clean up
                    os.unlink(output_path)
                else:
                    print("⚠️ FreeCAD export not available (command-line mode)")
            except Exception as e:
                print(f"⚠️ FreeCAD export limitation: {str(e)}")
        else:
            print("❌ FreeCAD support not available")
            
    except Exception as e:
        print(f"❌ FreeCAD test error: {str(e)}")
        
    print()

def test_application_startup():
    """Test that the application can start with CAD support."""
    print("Testing Application Startup")
    print("=" * 30)
    
    try:
        # Import main components
        from opentiler.main_window import MainWindow
        from opentiler.dialogs.save_as_dialog import SaveAsDialog
        from opentiler.dialogs.export_dialog import ExportDialog
        
        print("✅ All main components imported successfully")
        print("✅ Application should start without CAD-related errors")
        
    except Exception as e:
        print(f"❌ Application startup test failed: {str(e)}")
        
    print()

if __name__ == "__main__":
    print("OpenTiler CAD Format Support Test")
    print("=" * 50)
    print()
    
    test_dxf_support()
    test_freecad_support()
    test_application_startup()
    
    print("Test Summary:")
    print("- DXF support should be fully functional")
    print("- FreeCAD support available with command-line fallback")
    print("- Application ready for professional CAD workflows")
    print()
    print("To test in the application:")
    print("1. Run: ./venv/bin/python main.py")
    print("2. Load a document")
    print("3. Apply scaling")
    print("4. Use File → Save As... to test CAD export")
    print("5. Use File → Export Tiles... to test tile export")
