#!/usr/bin/env python3
"""
OpenTiler Plugin System and Automation Demo

This script demonstrates the OpenTiler Plugin System and Automation capabilities:
1. Shows plugin system functionality
2. Demonstrates automation plugin features
3. Provides examples of real-world usage

Usage:
    python demo_plugin_automation.py                    # Full demonstration
    python demo_plugin_automation.py --plugin-only      # Plugin system only
    python demo_plugin_automation.py --automation-only  # Automation features only
"""

import sys
import time
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def demonstrate_plugin_system():
    """Demonstrate the plugin system functionality."""
    print("🔌 OpenTiler Plugin System Demonstration")
    print("=" * 45)
    
    try:
        # Test basic imports
        print("📦 Testing plugin system imports...")
        from plugins.hook_system import HookType, HookManager
        from plugins.plugin_manager import PluginManager
        from plugins.content_access import AccessLevel, ContentAccessManager
        from plugins.base_plugin import PluginInfo
        print("✅ All plugin system components imported successfully")
        
        # Test hook types
        print(f"\n🔗 Hook System:")
        print(f"   ✅ Found {len(list(HookType))} hook types")
        sample_hooks = list(HookType)[:5]
        for hook in sample_hooks:
            print(f"      - {hook.name}: {hook.value}")
        print(f"      ... and {len(list(HookType)) - 5} more")
        
        # Test hook manager
        print(f"\n🔧 Hook Manager:")
        hook_manager = HookManager()
        print(f"   ✅ Hook manager created with {len(hook_manager.handlers)} hook type handlers")
        
        # Test hook execution
        context = hook_manager.execute_hook(
            HookType.DOCUMENT_AFTER_LOAD,
            {'document_path': 'demo_document.pdf', 'page_count': 3}
        )
        print(f"   ✅ Hook execution successful")
        print(f"      Hook type: {context.hook_type.value}")
        print(f"      Context data: {context.data}")
        
        # Test access levels
        print(f"\n🔐 Content Access System:")
        levels = [level.value for level in AccessLevel]
        print(f"   ✅ Access levels: {levels}")
        
        # Test plugin info
        print(f"\n📋 Plugin Info Structure:")
        info = PluginInfo(
            name="Demo Plugin",
            version="1.0.0",
            description="Demonstration plugin for testing",
            author="OpenTiler Team"
        )
        print(f"   ✅ Plugin info: {info.name} v{info.version}")
        print(f"      Author: {info.author}")
        print(f"      Description: {info.description}")
        
        print(f"\n🎉 Plugin system demonstration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Plugin system demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demonstrate_automation_plugin():
    """Demonstrate the automation plugin functionality."""
    print("🤖 Automation Plugin Demonstration")
    print("=" * 40)
    
    try:
        # Import automation plugin
        print("📦 Importing automation plugin...")
        from plugins.builtin.automation_plugin import AutomationPlugin
        from unittest.mock import Mock
        print("✅ Automation plugin imported successfully")
        
        # Create mock main window
        print("\n🖥️  Creating mock OpenTiler window...")
        mock_window = Mock()
        mock_window.current_document = Mock()
        mock_window.current_document.file_path = "demo_document.pdf"
        mock_window.plan_view = Mock()
        mock_window.tile_preview = Mock()
        mock_window.measurement_system = Mock()
        print("✅ Mock OpenTiler window created")
        
        # Create automation plugin
        print("\n🔌 Creating automation plugin...")
        automation_plugin = AutomationPlugin(mock_window)
        print("✅ Automation plugin created")
        
        # Get plugin info
        info = automation_plugin.plugin_info
        print(f"\n📋 Plugin Information:")
        print(f"   Name: {info.name}")
        print(f"   Version: {info.version}")
        print(f"   Description: {info.description}")
        print(f"   Author: {info.author}")
        
        # Get automation actions
        automation_plugin._setup_automation_actions()
        actions = list(automation_plugin.automation_actions.keys())
        print(f"\n⚡ Automation Actions ({len(actions)} available):")
        for i, action in enumerate(actions[:10], 1):  # Show first 10
            print(f"   {i:2d}. {action}")
        if len(actions) > 10:
            print(f"   ... and {len(actions) - 10} more actions")
        
        # Get hook handlers
        handlers = automation_plugin.get_hook_handlers()
        print(f"\n🔗 Hook Handlers:")
        print(f"   ✅ Plugin provides {len(handlers)} hook handlers")
        
        handler = handlers[0]
        supported_hooks = handler.supported_hooks
        print(f"   ✅ Supports {len(supported_hooks)} hook types:")
        for hook in supported_hooks[:5]:
            print(f"      - {hook.name}")
        if len(supported_hooks) > 5:
            print(f"      ... and {len(supported_hooks) - 5} more")
        
        print(f"   ✅ Handler priority: {handler.priority}")
        
        # Get content access requirements
        requirements = automation_plugin.get_document_access_requirements()
        required_access = [key for key, value in requirements.items() if value]
        print(f"\n🔐 Content Access Requirements:")
        print(f"   ✅ Requires access to: {required_access}")
        
        # Test configuration
        config = automation_plugin.get_config()
        print(f"\n⚙️  Plugin Configuration:")
        for key, value in config.items():
            print(f"   {key}: {value}")
        
        print(f"\n🎉 Automation plugin demonstration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Automation plugin demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demonstrate_plugin_integration():
    """Demonstrate plugin system integration."""
    print("🔗 Plugin System Integration Demonstration")
    print("=" * 50)
    
    try:
        # Import components
        from plugins.plugin_manager import PluginManager
        from plugins.builtin.automation_plugin import AutomationPlugin
        from plugins.hook_system import get_hook_manager, HookType
        from unittest.mock import Mock
        
        print("📦 Creating integrated plugin environment...")
        
        # Create mock main window
        mock_window = Mock()
        mock_window.content_access_manager = Mock()
        mock_window.content_access_manager.grant_access.return_value = {
            'plan_view': Mock(),
            'tile_preview': Mock(),
            'measurements': Mock()
        }
        
        # Create plugin manager
        plugin_manager = PluginManager(mock_window)
        print("✅ Plugin manager created")
        
        # Create automation plugin
        automation_plugin = AutomationPlugin(mock_window)
        plugin_manager.plugins["automation"] = automation_plugin
        print("✅ Automation plugin loaded into manager")
        
        # Initialize plugin
        success = plugin_manager.initialize_plugin("automation")
        print(f"✅ Plugin initialization: {'Success' if success else 'Failed'}")
        
        # Get plugin info through manager
        info = plugin_manager.get_plugin_info("automation")
        print(f"✅ Plugin info retrieved: {info.name} v{info.version}")
        
        # Test hook system integration
        hook_manager = get_hook_manager()
        
        # Register plugin's hook handler
        handlers = automation_plugin.get_hook_handlers()
        for handler in handlers:
            hook_manager.register_handler(handler, "automation")
        print(f"✅ {len(handlers)} hook handlers registered")
        
        # Test hook execution with plugin
        context = hook_manager.execute_hook(
            HookType.DOCUMENT_AFTER_LOAD,
            {'document_path': 'integration_test.pdf'}
        )
        print(f"✅ Hook execution with plugin successful")
        print(f"   Hook type: {context.hook_type.value}")
        print(f"   Context data: {context.data}")
        
        # Test plugin management
        enabled_plugins = plugin_manager.get_enabled_plugins()
        print(f"✅ Enabled plugins: {enabled_plugins}")
        
        # Test plugin statistics
        stats = plugin_manager.registry.get_statistics()
        print(f"✅ Plugin registry statistics: {stats}")
        
        print(f"\n🎉 Plugin system integration demonstration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Plugin integration demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demonstrate_automation_workflow():
    """Demonstrate a complete automation workflow."""
    print("🎬 Automation Workflow Demonstration")
    print("=" * 40)
    
    try:
        # Import automation client
        sys.path.insert(0, str(project_root / "tools"))
        from automation_client import OpenTilerAutomationClient
        
        print("📦 Automation client imported successfully")
        
        # Show available sequences
        client = OpenTilerAutomationClient()
        print(f"\n📋 Available automation sequences:")
        for name, sequence in client.sequences.items():
            print(f"   {name:20} - {len(sequence)} steps")
            
            # Show first few steps
            print(f"      Steps preview:")
            for i, step in enumerate(sequence[:3], 1):
                description = step.get('description', step['action'])
                print(f"         {i}. {description}")
            if len(sequence) > 3:
                print(f"         ... and {len(sequence) - 3} more steps")
            print()
        
        print("💡 To run automation sequences:")
        print("   1. Launch OpenTiler with: python main.py")
        print("   2. Run automation client with: python tools/automation_client.py --generate-docs")
        print("   3. Or use interactive mode: python tools/automation_client.py --interactive")
        
        print(f"\n🎉 Automation workflow demonstration completed!")
        return True
        
    except Exception as e:
        print(f"❌ Automation workflow demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Demonstrate OpenTiler Plugin System and Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script demonstrates the comprehensive plugin system and automation
capabilities of OpenTiler, showing how plugins integrate with the core
application to provide powerful automation features.

Examples:
  %(prog)s                        # Full demonstration
  %(prog)s --plugin-only          # Plugin system only
  %(prog)s --automation-only      # Automation features only
  %(prog)s --integration-only     # Integration demonstration only
        """
    )
    
    parser.add_argument(
        '--plugin-only',
        action='store_true',
        help='Demonstrate plugin system only'
    )
    
    parser.add_argument(
        '--automation-only',
        action='store_true',
        help='Demonstrate automation plugin only'
    )
    
    parser.add_argument(
        '--integration-only',
        action='store_true',
        help='Demonstrate plugin integration only'
    )
    
    parser.add_argument(
        '--workflow-only',
        action='store_true',
        help='Demonstrate automation workflow only'
    )
    
    args = parser.parse_args()
    
    try:
        print("🎯 OpenTiler Plugin System and Automation Demo")
        print("=" * 50)
        print("This demonstration shows the plugin system in action!")
        print()
        
        success_count = 0
        total_count = 0
        
        # Run specific demonstrations based on arguments
        if args.plugin_only:
            total_count = 1
            if demonstrate_plugin_system():
                success_count += 1
        elif args.automation_only:
            total_count = 1
            if demonstrate_automation_plugin():
                success_count += 1
        elif args.integration_only:
            total_count = 1
            if demonstrate_plugin_integration():
                success_count += 1
        elif args.workflow_only:
            total_count = 1
            if demonstrate_automation_workflow():
                success_count += 1
        else:
            # Run all demonstrations
            demonstrations = [
                ("Plugin System", demonstrate_plugin_system),
                ("Automation Plugin", demonstrate_automation_plugin),
                ("Plugin Integration", demonstrate_plugin_integration),
                ("Automation Workflow", demonstrate_automation_workflow),
            ]
            
            total_count = len(demonstrations)
            
            for name, demo_func in demonstrations:
                print(f"\n{'='*60}")
                print(f"🎬 Running {name} Demonstration")
                print(f"{'='*60}")
                
                if demo_func():
                    success_count += 1
                    print(f"✅ {name} demonstration completed successfully")
                else:
                    print(f"❌ {name} demonstration failed")
                
                time.sleep(1)  # Brief pause between demonstrations
        
        # Final summary
        print(f"\n{'='*60}")
        print(f"📊 Demonstration Summary")
        print(f"{'='*60}")
        print(f"✅ Successful: {success_count}/{total_count}")
        print(f"📈 Success Rate: {success_count/total_count*100:.1f}%")
        
        if success_count == total_count:
            print(f"\n🎉 All demonstrations completed successfully!")
            print(f"🚀 The OpenTiler Plugin System is working perfectly!")
            print(f"\n💡 Next steps:")
            print(f"   1. Launch OpenTiler: python main.py")
            print(f"   2. Generate docs: python tools/automation_client.py --generate-docs")
            print(f"   3. Try interactive: python tools/automation_client.py --interactive")
            return 0
        else:
            print(f"\n⚠️  {total_count - success_count} demonstration(s) had issues")
            return 1
        
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
