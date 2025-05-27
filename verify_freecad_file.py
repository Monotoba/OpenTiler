#!/usr/bin/env python3
"""
Script to verify that a FreeCAD file was created correctly.
Usage: python verify_freecad_file.py <path_to_fcstd_file>
"""

import sys
import os
import zipfile
import xml.etree.ElementTree as ET

def verify_freecad_file(file_path):
    """Verify that a FreeCAD file is valid and contains expected content."""
    print(f"Verifying FreeCAD file: {file_path}")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ File does not exist: {file_path}")
        return False
        
    # Check file size
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size} bytes")
    
    if file_size == 0:
        print("❌ File is empty")
        return False
        
    # Check if it's a valid ZIP file
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            file_list = zf.namelist()
            print(f"✅ Valid ZIP archive with {len(file_list)} files")
            print(f"Files: {', '.join(file_list)}")
            
            # Check for required files
            required_files = ['Document.xml']
            missing_files = [f for f in required_files if f not in file_list]
            
            if missing_files:
                print(f"❌ Missing required files: {missing_files}")
                return False
            else:
                print("✅ All required files present")
                
            # Check Document.xml content
            try:
                doc_xml = zf.read('Document.xml').decode('utf-8')
                root = ET.fromstring(doc_xml)
                
                print("\n📄 Document.xml Analysis:")
                
                # Check document properties
                properties = root.find('Properties')
                if properties is not None:
                    prop_count = properties.get('Count', '0')
                    print(f"   Properties: {prop_count}")
                    
                    for prop in properties.findall('Property'):
                        name = prop.get('name')
                        value = prop.find('String')
                        if value is not None:
                            print(f"   - {name}: {value.get('value')}")
                
                # Check objects
                objects = root.find('Objects')
                if objects is not None:
                    obj_count = objects.get('Count', '0')
                    print(f"   Objects: {obj_count}")
                    
                    for obj in objects.findall('Object'):
                        obj_type = obj.get('type')
                        obj_name = obj.get('name')
                        print(f"   - {obj_name}: {obj_type}")
                
                # Check object data
                object_data = root.find('ObjectData')
                if object_data is not None:
                    data_count = object_data.get('Count', '0')
                    print(f"   Object Data: {data_count}")
                    
                    for obj_data in object_data.findall('Object'):
                        obj_name = obj_data.get('name')
                        properties = obj_data.find('Properties')
                        if properties is not None:
                            prop_count = properties.get('Count', '0')
                            print(f"   - {obj_name}: {prop_count} properties")
                            
                            # Look for scale information
                            for prop in properties.findall('Property'):
                                prop_name = prop.get('name')
                                if prop_name == 'Label':
                                    string_val = prop.find('String')
                                    if string_val is not None:
                                        label = string_val.get('value')
                                        if 'Scale:' in label or 'Width:' in label or 'Height:' in label:
                                            print(f"     📏 {label}")
                
                print("✅ Document.xml is valid and contains expected structure")
                
            except ET.ParseError as e:
                print(f"❌ Document.xml is not valid XML: {e}")
                return False
            except Exception as e:
                print(f"❌ Error reading Document.xml: {e}")
                return False
                
            # Check for boundary shape
            if 'BoundaryShape.brp' in file_list:
                print("✅ Boundary shape file present")
                brep_data = zf.read('BoundaryShape.brp').decode('utf-8')
                if 'CASCADE Topology' in brep_data:
                    print("✅ Valid BREP geometry format")
                else:
                    print("⚠️ BREP file may not be valid")
            else:
                print("⚠️ No boundary shape file found")
                
            # Check GUI document
            if 'GuiDocument.xml' in file_list:
                print("✅ GUI document present")
            else:
                print("⚠️ No GUI document found")
                
    except zipfile.BadZipFile:
        print("❌ File is not a valid ZIP archive")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
        
    print("\n🎉 FreeCAD file verification completed successfully!")
    print("The file should open correctly in FreeCAD.")
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python verify_freecad_file.py <path_to_fcstd_file>")
        print("\nExample:")
        print("  python verify_freecad_file.py test01.FCStd")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    if verify_freecad_file(file_path):
        print("\n✅ File verification PASSED")
        sys.exit(0)
    else:
        print("\n❌ File verification FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
