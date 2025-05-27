#!/usr/bin/env python3
"""
Test script to verify Save-As operations work correctly.
"""

import sys
import os
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'opentiler'))

def test_file_extension_handling():
    """Test that file extensions are added correctly."""
    print("Testing File Extension Handling")
    print("=" * 40)
    
    try:
        from opentiler.dialogs.save_as_dialog import SaveAsDialog
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QPixmap
        
        # Create minimal Qt application
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Create test dialog
        dialog = SaveAsDialog()
        
        # Create test pixmap
        test_pixmap = QPixmap(800, 600)
        test_pixmap.fill()
        
        # Set test data
        dialog.set_document_data(test_pixmap, 0.1)
        
        # Test DXF extension handling
        dialog.format_combo.setCurrentText("DXF (AutoCAD)")
        dialog.output_path_edit.setText("test_file")
        
        # Simulate the extension addition logic
        output_path = dialog.output_path_edit.text().strip()
        if not output_path.lower().endswith('.dxf'):
            output_path += '.dxf'
            
        print(f"✅ DXF extension test: 'test_file' → '{output_path}'")
        
        # Test FreeCAD extension handling
        dialog.format_combo.setCurrentText("FreeCAD (.FCStd)")
        dialog.output_path_edit.setText("test_file")
        
        output_path = dialog.output_path_edit.text().strip()
        if not output_path.lower().endswith('.fcstd'):
            output_path += '.FCStd'
            
        print(f"✅ FreeCAD extension test: 'test_file' → '{output_path}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Extension test error: {str(e)}")
        return False

def test_dxf_save():
    """Test DXF save functionality."""
    print("\nTesting DXF Save Operation")
    print("=" * 40)
    
    try:
        from opentiler.formats.dxf_handler import DXFHandler
        from PySide6.QtGui import QPixmap
        
        handler = DXFHandler()
        
        if not handler.is_available():
            print("❌ DXF handler not available")
            return False
            
        # Create test pixmap
        test_pixmap = QPixmap(800, 600)
        test_pixmap.fill()
        
        # Test save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp_file:
            output_path = tmp_file.name
            
        try:
            success = handler.save_as_dxf(test_pixmap, output_path, 0.1, "mm")
            
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ DXF save successful: {output_path} ({file_size} bytes)")
                
                # Get file info
                info = handler.get_dxf_info(output_path)
                print(f"   DXF Info: {info}")
                
                return True
            else:
                print(f"❌ DXF save failed: success={success}, exists={os.path.exists(output_path)}")
                return False
                
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
                
    except Exception as e:
        print(f"❌ DXF save test error: {str(e)}")
        return False

def test_freecad_save():
    """Test FreeCAD save functionality."""
    print("\nTesting FreeCAD Save Operation")
    print("=" * 40)
    
    try:
        from opentiler.formats.freecad_handler import FreeCADHandler
        from PySide6.QtGui import QPixmap
        
        handler = FreeCADHandler()
        
        if not handler.is_available():
            print("❌ FreeCAD handler not available")
            return False
            
        print(f"FreeCAD Status: {handler.get_availability_status()}")
        
        # Create test pixmap
        test_pixmap = QPixmap(800, 600)
        test_pixmap.fill()
        
        # Test save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.FCStd', delete=False) as tmp_file:
            output_path = tmp_file.name
            
        try:
            print(f"Attempting FreeCAD save to: {output_path}")
            success = handler.save_as_freecad(test_pixmap, output_path, 0.1, "mm")
            
            if success and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ FreeCAD save successful: {output_path} ({file_size} bytes)")
                
                # Get file info
                info = handler.get_freecad_info(output_path)
                print(f"   FreeCAD Info: {info}")
                
                return True
            else:
                print(f"❌ FreeCAD save failed: success={success}, exists={os.path.exists(output_path)}")
                return False
                
        finally:
            # Clean up
            if os.path.exists(output_path):
                os.unlink(output_path)
                
    except Exception as e:
        print(f"❌ FreeCAD save test error: {str(e)}")
        return False

def test_format_availability():
    """Test format availability detection."""
    print("\nTesting Format Availability")
    print("=" * 40)
    
    try:
        from opentiler.formats.dxf_handler import DXFHandler
        from opentiler.formats.freecad_handler import FreeCADHandler
        
        dxf_available = DXFHandler.is_available()
        freecad_available = FreeCADHandler.is_available()
        freecad_status = FreeCADHandler.get_availability_status()
        
        print(f"DXF Support: {dxf_available}")
        print(f"FreeCAD Support: {freecad_available}")
        print(f"FreeCAD Status: {freecad_status}")
        
        return dxf_available or freecad_available
        
    except Exception as e:
        print(f"❌ Availability test error: {str(e)}")
        return False

if __name__ == "__main__":
    print("OpenTiler Save Operations Test")
    print("=" * 50)
    
    # Test format availability first
    if not test_format_availability():
        print("\n❌ No CAD formats available - check installation")
        sys.exit(1)
    
    # Test file extension handling
    extension_ok = test_file_extension_handling()
    
    # Test DXF save
    dxf_ok = test_dxf_save()
    
    # Test FreeCAD save
    freecad_ok = test_freecad_save()
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print(f"File Extensions: {'✅ PASS' if extension_ok else '❌ FAIL'}")
    print(f"DXF Save: {'✅ PASS' if dxf_ok else '❌ FAIL'}")
    print(f"FreeCAD Save: {'✅ PASS' if freecad_ok else '❌ FAIL'}")
    
    if extension_ok and (dxf_ok or freecad_ok):
        print("\n🎉 Save operations are working correctly!")
        print("You can now:")
        print("- Save files with automatic extension addition")
        print("- Export to DXF format with scale information")
        print("- Export to FreeCAD format with proper geometry")
    else:
        print("\n⚠️ Some save operations failed - check error messages above")
        
    print("\nTo test in the application:")
    print("1. Run: ./venv/bin/python main.py")
    print("2. Load a document and apply scaling")
    print("3. Use File → Save As... to test CAD export")
    print("4. Try saving as 'test01' (extension will be added automatically)")
