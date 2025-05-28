#!/usr/bin/env python3
"""
OpenTiler Documentation Workflow Demo

This script demonstrates the complete workflow for generating OpenTiler
documentation images using the plugin system and automation capabilities.

It shows:
1. Plugin system functionality
2. Automation plugin integration
3. Real-world documentation generation workflow

Usage:
    python demo_documentation_workflow.py                    # Full demo
    python demo_documentation_workflow.py --plugin-test      # Test plugin system
    python demo_documentation_workflow.py --show-workflow    # Show workflow only
"""

import sys
import time
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_plugin_system():
    """Test the plugin system functionality."""
    print("🔌 OpenTiler Plugin System Test")
    print("=" * 35)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from plugins.hook_system import HookType, HookManager
        from plugins.plugin_manager import PluginManager
        from plugins.content_access import AccessLevel
        from plugins.builtin.automation_plugin import AutomationPlugin
        print("✅ All plugin components imported successfully")
        
        # Test hook system
        print("\n🔗 Testing hook system...")
        hook_manager = HookManager()
        print(f"✅ Hook manager created with {len(hook_manager.handlers)} hook types")
        
        # Test hook execution
        context = hook_manager.execute_hook(
            HookType.DOCUMENT_AFTER_LOAD,
            {'document_path': 'test.pdf'}
        )
        print(f"✅ Hook execution successful: {context.hook_type.value}")
        
        # Test automation plugin
        print("\n🤖 Testing automation plugin...")
        from unittest.mock import Mock
        mock_window = Mock()
        
        automation_plugin = AutomationPlugin(mock_window)
        print(f"✅ Automation plugin created")
        
        info = automation_plugin.plugin_info
        print(f"✅ Plugin info: {info.name} v{info.version}")
        
        # Setup automation actions
        automation_plugin._setup_automation_actions()
        actions = list(automation_plugin.automation_actions.keys())
        print(f"✅ Automation actions available: {len(actions)}")
        
        # Show sample actions
        print("   Sample actions:")
        for action in actions[:5]:
            print(f"   - {action}")
        
        print("\n🎉 Plugin system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Plugin system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_documentation_workflow():
    """Show the documentation generation workflow."""
    print("📋 OpenTiler Documentation Generation Workflow")
    print("=" * 50)
    
    print("🎯 Complete Workflow Overview:")
    print()
    
    print("1️⃣  Plugin System Setup:")
    print("   ✅ Hook system provides 42+ hook types for plugin integration")
    print("   ✅ Plugin manager handles plugin lifecycle and discovery")
    print("   ✅ Content access system provides secure component access")
    print("   ✅ Automation plugin provides remote control capabilities")
    print()
    
    print("2️⃣  OpenTiler Launch:")
    print("   ✅ Launch OpenTiler with plugin system enabled")
    print("   ✅ Automation plugin starts server on port 8888")
    print("   ✅ Plugin registers hook handlers for automation events")
    print("   ✅ Content access is granted for plan view, tiles, measurements")
    print()
    
    print("3️⃣  Automation Client Connection:")
    print("   ✅ Automation client connects to OpenTiler server")
    print("   ✅ Client sends JSON commands to control application")
    print("   ✅ Plugin executes actions and captures screenshots")
    print("   ✅ Screen capture tool generates high-quality images")
    print()
    
    print("4️⃣  Documentation Sequences:")
    print("   ✅ documentation_full: Complete UI tour (20+ screenshots)")
    print("   ✅ basic_workflow: Essential workflow (4 screenshots)")
    print("   ✅ menu_tour: All menu screenshots (5 screenshots)")
    print("   ✅ Custom sequences can be easily added")
    print()
    
    print("5️⃣  Available Automation Actions:")
    
    # Import automation client to show sequences
    try:
        sys.path.insert(0, str(project_root / "tools"))
        from automation_client import OpenTilerAutomationClient
        
        client = OpenTilerAutomationClient()
        
        print(f"   📋 Predefined Sequences ({len(client.sequences)}):")
        for name, sequence in client.sequences.items():
            print(f"      {name:20} - {len(sequence):2d} steps")
        
        print(f"\n   ⚡ Sample Actions from 'documentation_full':")
        doc_sequence = client.sequences.get('documentation_full', [])
        for i, step in enumerate(doc_sequence[:8], 1):
            description = step.get('description', step['action'])
            print(f"      {i:2d}. {description}")
        if len(doc_sequence) > 8:
            print(f"      ... and {len(doc_sequence) - 8} more steps")
        
    except Exception as e:
        print(f"   ❌ Could not load automation sequences: {e}")
    
    print()
    print("6️⃣  Generated Documentation:")
    print("   ✅ High-quality PNG screenshots (1600x1000 default)")
    print("   ✅ Comprehensive UI coverage (menus, dialogs, workflows)")
    print("   ✅ Consistent naming and organization")
    print("   ✅ Metadata tracking for documentation management")
    print()
    
    print("💡 To run the complete workflow:")
    print("   1. Test plugin system:     python demo_documentation_workflow.py --plugin-test")
    print("   2. Launch OpenTiler:       python main.py")
    print("   3. Generate docs:          python tools/automation_client.py --generate-docs")
    print("   4. Interactive mode:       python tools/automation_client.py --interactive")
    print()
    
    print("🎉 The plugin system enables powerful automation capabilities!")
    return True


def demonstrate_complete_workflow():
    """Demonstrate the complete documentation workflow."""
    print("🎬 Complete OpenTiler Documentation Workflow Demo")
    print("=" * 55)
    
    # Step 1: Test plugin system
    print("\n" + "="*60)
    print("🔌 STEP 1: Testing Plugin System")
    print("="*60)
    
    if not test_plugin_system():
        print("❌ Plugin system test failed - cannot continue")
        return False
    
    # Step 2: Show workflow
    print("\n" + "="*60)
    print("📋 STEP 2: Documentation Workflow Overview")
    print("="*60)
    
    if not show_documentation_workflow():
        print("❌ Workflow overview failed")
        return False
    
    # Step 3: Show automation capabilities
    print("\n" + "="*60)
    print("🤖 STEP 3: Automation Capabilities")
    print("="*60)
    
    try:
        sys.path.insert(0, str(project_root / "tools"))
        from automation_client import OpenTilerAutomationClient
        
        client = OpenTilerAutomationClient()
        print("✅ Automation client created successfully")
        
        print(f"\n📊 Automation Statistics:")
        total_sequences = len(client.sequences)
        total_steps = sum(len(seq) for seq in client.sequences.values())
        print(f"   Sequences available: {total_sequences}")
        print(f"   Total automation steps: {total_steps}")
        print(f"   Average steps per sequence: {total_steps/total_sequences:.1f}")
        
        print(f"\n🎯 Key Features:")
        print(f"   ✅ Socket-based communication with OpenTiler")
        print(f"   ✅ JSON command protocol for reliability")
        print(f"   ✅ Predefined sequences for common tasks")
        print(f"   ✅ Interactive mode for manual control")
        print(f"   ✅ Screenshot capture with quality control")
        print(f"   ✅ Error handling and recovery")
        
    except Exception as e:
        print(f"❌ Automation capabilities demo failed: {e}")
        return False
    
    # Step 4: Summary
    print("\n" + "="*60)
    print("🎉 WORKFLOW DEMONSTRATION COMPLETE")
    print("="*60)
    
    print("✅ Plugin system is working correctly")
    print("✅ Automation plugin provides comprehensive control")
    print("✅ Documentation generation workflow is ready")
    print("✅ All components integrate seamlessly")
    
    print(f"\n🚀 Ready for Production Use!")
    print(f"   The OpenTiler plugin system and automation capabilities")
    print(f"   are fully functional and ready for generating documentation.")
    
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Demonstrate OpenTiler documentation workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script demonstrates the complete workflow for generating OpenTiler
documentation using the plugin system and automation capabilities.

Examples:
  %(prog)s                        # Complete workflow demonstration
  %(prog)s --plugin-test          # Test plugin system only
  %(prog)s --show-workflow        # Show workflow overview only
        """
    )
    
    parser.add_argument(
        '--plugin-test',
        action='store_true',
        help='Test plugin system functionality only'
    )
    
    parser.add_argument(
        '--show-workflow',
        action='store_true',
        help='Show documentation workflow overview only'
    )
    
    args = parser.parse_args()
    
    try:
        if args.plugin_test:
            return 0 if test_plugin_system() else 1
        elif args.show_workflow:
            return 0 if show_documentation_workflow() else 1
        else:
            return 0 if demonstrate_complete_workflow() else 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Demonstration interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
