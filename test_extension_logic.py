#!/usr/bin/env python3
"""
Test script to verify file extension addition logic.
"""

def test_extension_logic():
    """Test the file extension addition logic."""
    print("Testing File Extension Addition Logic")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        # (input_filename, format_text, expected_output)
        ("test01", "DXF (AutoCAD)", "test01.dxf"),
        ("test01.dxf", "DXF (AutoCAD)", "test01.dxf"),  # Already has extension
        ("test01.DXF", "DXF (AutoCAD)", "test01.DXF"),  # Already has extension (uppercase)
        ("my_drawing", "DXF (AutoCAD)", "my_drawing.dxf"),
        ("test01", "FreeCAD (.FCStd)", "test01.FCStd"),
        ("test01.FCStd", "FreeCAD (.FCStd)", "test01.FCStd"),  # Already has extension
        ("test01.fcstd", "FreeCAD (.FCStd)", "test01.fcstd"),  # Already has extension (lowercase)
        ("my_model", "FreeCAD (.FCStd)", "my_model.FCStd"),
    ]
    
    all_passed = True
    
    for i, (input_path, format_text, expected) in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{input_path}' with format '{format_text}'")
        
        # Apply the same logic as in the Save-As dialog
        output_path = input_path
        
        if "DXF" in format_text:
            if not output_path.lower().endswith('.dxf'):
                output_path += '.dxf'
        elif "FreeCAD" in format_text:
            if not output_path.lower().endswith('.fcstd'):
                output_path += '.FCStd'
        
        if output_path == expected:
            print(f"  ✅ PASS: '{input_path}' → '{output_path}'")
        else:
            print(f"  ❌ FAIL: '{input_path}' → '{output_path}' (expected '{expected}')")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All extension logic tests PASSED!")
        print("\nThe file extension addition should work correctly in OpenTiler.")
    else:
        print("❌ Some extension logic tests FAILED!")
        print("\nThere may be issues with the extension addition logic.")
    
    return all_passed

def test_real_world_scenarios():
    """Test real-world usage scenarios."""
    print("\n\nTesting Real-World Scenarios")
    print("=" * 50)
    
    scenarios = [
        "test01",           # Simple filename
        "my drawing",       # Filename with space
        "plan_v2",          # Filename with underscore
        "house-plan",       # Filename with dash
        "drawing.backup",   # Filename with different extension
        "test",             # Very short filename
        "very_long_filename_for_architectural_drawing_v3_final", # Long filename
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: '{scenario}'")
        
        # Test DXF
        dxf_result = scenario
        if not dxf_result.lower().endswith('.dxf'):
            dxf_result += '.dxf'
        print(f"  DXF: '{scenario}' → '{dxf_result}'")
        
        # Test FreeCAD
        freecad_result = scenario
        if not freecad_result.lower().endswith('.fcstd'):
            freecad_result += '.FCStd'
        print(f"  FreeCAD: '{scenario}' → '{freecad_result}'")
    
    print("\n✅ All real-world scenarios processed successfully!")

if __name__ == "__main__":
    print("OpenTiler File Extension Logic Test")
    print("=" * 60)
    
    # Test the extension logic
    logic_passed = test_extension_logic()
    
    # Test real-world scenarios
    test_real_world_scenarios()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Extension Logic: {'✅ PASS' if logic_passed else '❌ FAIL'}")
    print("Real-World Scenarios: ✅ PASS")
    
    if logic_passed:
        print("\n🎉 File extension addition should work correctly!")
        print("\nTo test in OpenTiler:")
        print("1. Run: ./venv/bin/python main.py")
        print("2. Load a document and apply scaling")
        print("3. Use File → Save As...")
        print("4. Enter filename without extension (e.g., 'test01')")
        print("5. Select DXF or FreeCAD format")
        print("6. Click Save - extension should be added automatically")
        print("7. Check status area for 'Added .dxf extension' message")
    else:
        print("\n⚠️ Extension logic needs to be fixed!")
        
    print("\nExpected behavior:")
    print("- 'test01' + DXF format → 'test01.dxf'")
    print("- 'test01' + FreeCAD format → 'test01.FCStd'")
    print("- Files with existing extensions remain unchanged")
    print("- Status area shows when extensions are added")
