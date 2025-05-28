#!/usr/bin/env python3
"""
OpenTiler Documentation Generation - Complete Workflow

This script demonstrates the complete workflow for generating OpenTiler
documentation images using the Sky Skanner test plan.

Usage:
    python run_documentation_generation.py                    # Complete workflow
    python run_documentation_generation.py --test-only        # Test components only
    python run_documentation_generation.py --show-commands    # Show commands only
"""

import sys
import time
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_system_components():
    """Test all system components before running automation."""
    print("🧪 Testing OpenTiler Documentation System Components")
    print("=" * 55)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Plugin System
    print("\n1️⃣  Testing Plugin System...")
    try:
        from plugins.hook_system import HookType, HookManager
        from plugins.plugin_manager import PluginManager
        from plugins.content_access import AccessLevel
        from plugins.builtin.automation_plugin import AutomationPlugin
        
        print("   ✅ Plugin system imports successful")
        
        # Test hook manager
        hook_manager = HookManager()
        print(f"   ✅ Hook manager: {len(hook_manager.handlers)} hook types")
        
        # Test automation plugin
        from unittest.mock import Mock
        mock_window = Mock()
        automation_plugin = AutomationPlugin(mock_window)
        automation_plugin._setup_automation_actions()
        
        actions = list(automation_plugin.automation_actions.keys())
        print(f"   ✅ Automation plugin: {len(actions)} actions available")
        
        success_count += 1
        
    except Exception as e:
        print(f"   ❌ Plugin system test failed: {e}")
    
    total_tests += 1
    
    # Test 2: Automation Client
    print("\n2️⃣  Testing Automation Client...")
    try:
        sys.path.insert(0, str(project_root / "tools"))
        from automation_client import OpenTilerAutomationClient
        
        client = OpenTilerAutomationClient()
        print(f"   ✅ Automation client created")
        print(f"   ✅ Available sequences: {list(client.sequences.keys())}")
        
        # Show sequence details
        doc_sequence = client.sequences.get('documentation_full', [])
        print(f"   ✅ Documentation sequence: {len(doc_sequence)} steps")
        
        success_count += 1
        
    except Exception as e:
        print(f"   ❌ Automation client test failed: {e}")
    
    total_tests += 1
    
    # Test 3: Screen Capture Tool
    print("\n3️⃣  Testing Screen Capture Tool...")
    try:
        sys.path.insert(0, str(project_root / "tools" / "screen_capture"))
        from screen_capture import ScreenCapture
        
        screen_capture = ScreenCapture()
        print("   ✅ Screen capture tool imported")
        
        # Test window listing (this should work even in headless)
        try:
            windows = screen_capture.list_windows()
            print(f"   ✅ Window detection: {len(windows)} windows found")
        except Exception:
            print("   ⚠️  Window detection not available (headless environment)")
        
        success_count += 1
        
    except Exception as e:
        print(f"   ❌ Screen capture test failed: {e}")
    
    total_tests += 1
    
    # Test 4: Test Plan File
    print("\n4️⃣  Testing Sky Skanner Test Plan...")
    try:
        test_plan_path = project_root / "plans" / "original_plans" / "1147 Sky Skanner_2.pdf"
        
        if test_plan_path.exists():
            file_size = test_plan_path.stat().st_size
            print(f"   ✅ Test plan found: {test_plan_path.name}")
            print(f"   ✅ File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
            success_count += 1
        else:
            print(f"   ❌ Test plan not found: {test_plan_path}")
        
    except Exception as e:
        print(f"   ❌ Test plan check failed: {e}")
    
    total_tests += 1
    
    # Test 5: Output Directory
    print("\n5️⃣  Testing Output Directory...")
    try:
        output_dir = project_root / "docs" / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"   ✅ Output directory ready: {output_dir}")
        
        # Check if writable
        test_file = output_dir / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        print("   ✅ Directory is writable")
        
        success_count += 1
        
    except Exception as e:
        print(f"   ❌ Output directory test failed: {e}")
    
    total_tests += 1
    
    # Summary
    print(f"\n📊 Component Test Results:")
    print(f"   ✅ Passed: {success_count}/{total_tests}")
    print(f"   📈 Success Rate: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print(f"\n🎉 All components are ready for documentation generation!")
        return True
    else:
        print(f"\n⚠️  {total_tests - success_count} component(s) need attention")
        return False


def show_documentation_commands():
    """Show the complete command sequence for documentation generation."""
    print("📋 OpenTiler Documentation Generation Commands")
    print("=" * 50)
    
    print("\n🎯 Complete Workflow Commands:")
    print()
    
    print("1️⃣  Launch OpenTiler with Sky Skanner Test Plan:")
    print("   cd /home/randy/projects/python-3/OpenTiler")
    print("   source venv/bin/activate")
    print('   python main.py "plans/original_plans/1147 Sky Skanner_2.pdf"')
    print()
    
    print("2️⃣  Generate Complete Documentation (in separate terminal):")
    print("   cd /home/randy/projects/python-3/OpenTiler")
    print("   source venv/bin/activate")
    print("   python tools/automation_client.py --generate-docs")
    print()
    
    print("3️⃣  Alternative: Generate Specific Sequences:")
    print("   # Basic workflow (4 screenshots)")
    print("   python tools/automation_client.py --sequence basic_workflow")
    print()
    print("   # Menu tour (5 screenshots)")
    print("   python tools/automation_client.py --sequence menu_tour")
    print()
    print("   # Full documentation (20+ screenshots)")
    print("   python tools/automation_client.py --sequence documentation_full")
    print()
    
    print("4️⃣  Interactive Mode for Manual Control:")
    print("   python tools/automation_client.py --interactive")
    print("   # Then use commands like:")
    print("   automation> action load_demo_document")
    print("   automation> screenshot sky_skanner_loaded.png")
    print("   automation> sequence basic_workflow")
    print("   automation> quit")
    print()
    
    print("5️⃣  Single Actions for Testing:")
    print("   python tools/automation_client.py --action load_demo_document")
    print("   python tools/automation_client.py --action capture_screenshot")
    print("   python tools/automation_client.py --action zoom_in")
    print("   python tools/automation_client.py --action open_settings_dialog")
    print()
    
    print("6️⃣  Check Generated Images:")
    print("   ls -la docs/images/")
    print("   # Images will be named like:")
    print("   #   opentiler-empty-interface.png")
    print("   #   opentiler-with-document.png")
    print("   #   opentiler-file-menu.png")
    print("   #   opentiler-settings-dialog.png")
    print("   #   ... and many more")
    print()
    
    print("🎯 Expected Results:")
    print("   ✅ 20+ high-quality PNG screenshots (1600x1000)")
    print("   ✅ Complete UI coverage (menus, dialogs, workflows)")
    print("   ✅ Consistent naming and organization")
    print("   ✅ Metadata file with generation details")
    print()
    
    print("💡 Automation Sequences Available:")
    try:
        sys.path.insert(0, str(project_root / "tools"))
        from automation_client import OpenTilerAutomationClient
        
        client = OpenTilerAutomationClient()
        
        for name, sequence in client.sequences.items():
            print(f"   📋 {name:20} - {len(sequence):2d} steps")
            
            # Show first few steps
            for i, step in enumerate(sequence[:3], 1):
                description = step.get('description', step['action'])
                print(f"      {i}. {description}")
            if len(sequence) > 3:
                print(f"      ... and {len(sequence) - 3} more steps")
            print()
        
    except Exception as e:
        print(f"   ❌ Could not load sequences: {e}")


def simulate_documentation_generation():
    """Simulate the documentation generation process."""
    print("🎬 Simulating OpenTiler Documentation Generation")
    print("=" * 50)
    
    print("\n📄 Using Test Plan: 1147 Sky Skanner_2.pdf")
    print("📁 Output Directory: docs/images/")
    print()
    
    # Simulate the automation sequence
    try:
        sys.path.insert(0, str(project_root / "tools"))
        from automation_client import OpenTilerAutomationClient
        
        client = OpenTilerAutomationClient()
        doc_sequence = client.sequences.get('documentation_full', [])
        
        print(f"🎬 Simulating 'documentation_full' sequence ({len(doc_sequence)} steps):")
        print()
        
        for i, step in enumerate(doc_sequence, 1):
            action = step['action']
            description = step.get('description', action)
            delay = step.get('delay', 1)
            params = step.get('params', {})
            
            print(f"Step {i:2d}/{len(doc_sequence)}: {description}")
            
            if action == 'capture_screenshot':
                filename = params.get('filename', 'screenshot.png')
                print(f"         📸 Would capture: {filename}")
            elif action == 'load_demo_document':
                print(f"         📄 Would load: Sky Skanner_2.pdf")
            elif 'menu' in action:
                menu_name = action.replace('open_', '').replace('_menu', '').title()
                print(f"         📋 Would open: {menu_name} menu")
            elif 'dialog' in action:
                dialog_name = action.replace('open_', '').replace('_dialog', '').replace('_', ' ').title()
                print(f"         🔧 Would open: {dialog_name} dialog")
            elif action in ['zoom_in', 'zoom_out', 'fit_to_window', 'rotate_left', 'rotate_right']:
                print(f"         🔍 Would execute: {action.replace('_', ' ').title()}")
            
            print(f"         ⏱️  Delay: {delay}s")
            print()
            
            # Simulate delay
            time.sleep(0.1)  # Very short delay for simulation
        
        print("🎉 Simulation completed!")
        print()
        print("📊 Expected Results:")
        print(f"   ✅ {len([s for s in doc_sequence if s['action'] == 'capture_screenshot'])} screenshots generated")
        print("   ✅ Complete UI documentation coverage")
        print("   ✅ High-quality PNG images (1600x1000)")
        print("   ✅ Consistent naming and organization")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="OpenTiler Documentation Generation Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script demonstrates the complete workflow for generating OpenTiler
documentation using the Sky Skanner test plan and automation system.

Examples:
  %(prog)s                        # Complete workflow demonstration
  %(prog)s --test-only            # Test system components only
  %(prog)s --show-commands        # Show command sequence only
  %(prog)s --simulate             # Simulate documentation generation
        """
    )
    
    parser.add_argument(
        '--test-only',
        action='store_true',
        help='Test system components only'
    )
    
    parser.add_argument(
        '--show-commands',
        action='store_true',
        help='Show documentation generation commands'
    )
    
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Simulate documentation generation process'
    )
    
    args = parser.parse_args()
    
    try:
        if args.test_only:
            return 0 if test_system_components() else 1
        elif args.show_commands:
            show_documentation_commands()
            return 0
        elif args.simulate:
            return 0 if simulate_documentation_generation() else 1
        else:
            # Complete workflow demonstration
            print("🎯 OpenTiler Documentation Generation - Complete Workflow")
            print("=" * 60)
            
            # Step 1: Test components
            print("\n" + "="*60)
            print("🧪 STEP 1: Testing System Components")
            print("="*60)
            
            if not test_system_components():
                print("❌ Component tests failed - cannot proceed")
                return 1
            
            # Step 2: Show commands
            print("\n" + "="*60)
            print("📋 STEP 2: Documentation Generation Commands")
            print("="*60)
            
            show_documentation_commands()
            
            # Step 3: Simulate process
            print("\n" + "="*60)
            print("🎬 STEP 3: Simulating Documentation Generation")
            print("="*60)
            
            if not simulate_documentation_generation():
                print("❌ Simulation failed")
                return 1
            
            # Final summary
            print("\n" + "="*60)
            print("🎉 DOCUMENTATION WORKFLOW READY")
            print("="*60)
            
            print("✅ All system components tested and working")
            print("✅ Automation sequences ready for execution")
            print("✅ Sky Skanner test plan available")
            print("✅ Output directory prepared")
            print()
            print("🚀 Ready to generate OpenTiler documentation!")
            print("   Run the commands shown above to generate actual screenshots")
            
            return 0
            
    except KeyboardInterrupt:
        print("\n⚠️  Workflow interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
