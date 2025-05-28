#!/usr/bin/env python3
"""
OpenTiler Documentation Image Creator

This script demonstrates the OpenTiler Plugin System in action by:
1. Launching OpenTiler with the automation plugin enabled
2. Using the automation plugin to control the application
3. Generating comprehensive documentation screenshots
4. Showcasing the plugin system's real-world capabilities

Usage:
    python create_documentation_images.py                    # Full documentation generation
    python create_documentation_images.py --quick            # Quick demo screenshots
    python create_documentation_images.py --test-plugin      # Test plugin system only
    python create_documentation_images.py --interactive      # Interactive automation mode
"""

import sys
import time
import subprocess
import argparse
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_plugin_system():
    """Test the plugin system functionality."""
    print("🔌 Testing OpenTiler Plugin System")
    print("=" * 40)
    
    try:
        # Import plugin system components
        from plugins.plugin_manager import PluginManager
        from plugins.builtin.automation_plugin import AutomationPlugin
        from unittest.mock import Mock
        
        print("✅ Plugin system components imported")
        
        # Create mock main window
        mock_window = Mock()
        print("✅ Mock OpenTiler window created")
        
        # Create plugin manager
        plugin_manager = PluginManager(mock_window)
        print("✅ Plugin manager created")
        
        # Discover plugins
        discovered = plugin_manager.discover_plugins()
        print(f"✅ Plugin discovery found: {discovered}")
        
        # Create automation plugin
        automation_plugin = AutomationPlugin(mock_window)
        plugin_manager.plugins["automation"] = automation_plugin
        print("✅ Automation plugin loaded")
        
        # Initialize plugin
        if plugin_manager.initialize_plugin("automation"):
            print("✅ Automation plugin initialized")
        else:
            print("❌ Failed to initialize automation plugin")
            return False
        
        # Get plugin info
        info = plugin_manager.get_plugin_info("automation")
        print(f"✅ Plugin info: {info.name} v{info.version}")
        print(f"   Description: {info.description}")
        print(f"   Author: {info.author}")
        
        # Get automation actions
        actions = list(automation_plugin.automation_actions.keys())
        print(f"✅ Available automation actions ({len(actions)}):")
        for i, action in enumerate(actions[:8], 1):  # Show first 8
            print(f"   {i:2d}. {action}")
        if len(actions) > 8:
            print(f"   ... and {len(actions) - 8} more actions")
        
        # Get hook handlers
        handlers = automation_plugin.get_hook_handlers()
        print(f"✅ Plugin provides {len(handlers)} hook handlers")
        
        # Get content access requirements
        requirements = automation_plugin.get_document_access_requirements()
        required_access = [key for key, value in requirements.items() if value]
        print(f"✅ Plugin requires access to: {required_access}")
        
        # Test hook system integration
        from plugins.hook_system import get_hook_manager, HookType
        hook_manager = get_hook_manager()
        
        # Register plugin's hook handler
        hook_manager.register_handler(automation_plugin.hook_handler, "automation")
        print("✅ Hook handler registered")
        
        # Test hook execution
        context = hook_manager.execute_hook(
            HookType.DOCUMENT_AFTER_LOAD,
            {'document_path': 'test_document.pdf'}
        )
        print("✅ Hook execution successful")
        print(f"   Hook type: {context.hook_type.value}")
        print(f"   Context data: {context.data}")
        
        print("\n🎉 Plugin system test completed successfully!")
        print("   The automation plugin is ready for real-world use!")
        return True
        
    except Exception as e:
        print(f"❌ Plugin system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def launch_opentiler_with_automation(document_path: Optional[str] = None) -> subprocess.Popen:
    """Launch OpenTiler with automation plugin enabled.
    
    Args:
        document_path: Optional document to load
        
    Returns:
        OpenTiler process
    """
    print("🚀 Launching OpenTiler with Automation Plugin")
    print("=" * 45)
    
    # Build command
    cmd = [sys.executable, 'main.py']
    
    # Add document if specified
    if document_path and Path(document_path).exists():
        cmd.append(document_path)
        print(f"📄 Loading document: {document_path}")
    
    print(f"🔧 Command: {' '.join(cmd)}")
    print("⏳ Starting OpenTiler...")
    
    # Launch OpenTiler
    process = subprocess.Popen(
        cmd,
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for startup
    print("⏳ Waiting for OpenTiler to initialize...")
    time.sleep(8)  # Give time for plugin system to load
    
    print("✅ OpenTiler should now be running with automation plugin")
    print("🔌 Automation server should be available on port 8888")
    
    return process


def generate_documentation_images(sequence_type: str = "documentation_full"):
    """Generate documentation images using automation client.
    
    Args:
        sequence_type: Type of sequence to run
    """
    print(f"📸 Generating Documentation Images: {sequence_type}")
    print("=" * 50)
    
    # Import automation client
    sys.path.insert(0, str(project_root / "tools"))
    from automation_client import OpenTilerAutomationClient
    
    # Create automation client
    client = OpenTilerAutomationClient()
    
    try:
        # Connect to automation server
        print("🔌 Connecting to automation server...")
        if not client.connect():
            print("❌ Failed to connect to automation server")
            print("   Make sure OpenTiler is running with automation plugin")
            return False
        
        print("✅ Connected to automation server")
        
        # Execute documentation sequence
        print(f"🎬 Executing sequence: {sequence_type}")
        success = client.execute_sequence(sequence_type)
        
        if success:
            print("\n🎉 Documentation images generated successfully!")
            print("📁 Check docs/images/ for the generated screenshots")
        else:
            print("\n⚠️  Some images may have failed to generate")
        
        return success
        
    except Exception as e:
        print(f"❌ Error generating images: {e}")
        return False
    finally:
        client.disconnect()


def run_interactive_automation():
    """Run interactive automation mode."""
    print("🎮 Interactive Automation Mode")
    print("=" * 35)
    
    # Import automation client
    sys.path.insert(0, str(project_root / "tools"))
    from automation_client import OpenTilerAutomationClient
    
    # Create and run interactive client
    client = OpenTilerAutomationClient()
    client.interactive_mode()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Create OpenTiler documentation images using the automation plugin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script demonstrates the OpenTiler Plugin System in action by:
1. Testing the plugin system functionality
2. Launching OpenTiler with the automation plugin
3. Using the plugin to generate documentation screenshots

Examples:
  %(prog)s                        # Full documentation generation
  %(prog)s --quick                # Quick demo screenshots  
  %(prog)s --test-plugin          # Test plugin system only
  %(prog)s --interactive          # Interactive automation mode
  %(prog)s --document path.pdf    # Use specific document
        """
    )
    
    parser.add_argument(
        '--document', '-d',
        help='Path to document to load in OpenTiler'
    )
    
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Generate quick demo screenshots (basic_workflow sequence)'
    )
    
    parser.add_argument(
        '--test-plugin', '-t',
        action='store_true',
        help='Test plugin system functionality only'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive automation mode'
    )
    
    parser.add_argument(
        '--no-launch',
        action='store_true',
        help='Skip launching OpenTiler (assume already running)'
    )
    
    args = parser.parse_args()
    
    try:
        # Test plugin system if requested
        if args.test_plugin:
            return 0 if test_plugin_system() else 1
        
        # Run interactive mode if requested
        if args.interactive:
            if not args.no_launch:
                print("⚠️  Interactive mode requires OpenTiler to be already running")
                print("   Launch OpenTiler first, then use --no-launch flag")
                return 1
            run_interactive_automation()
            return 0
        
        # Determine document path
        document_path = args.document
        if not document_path:
            # Use default demo document
            demo_path = "plans/original_plans/1147 Sky Skanner_2.pdf"
            if Path(demo_path).exists():
                document_path = demo_path
            else:
                print(f"⚠️  Demo document not found: {demo_path}")
                print("   Continuing without document...")
        
        # Launch OpenTiler unless skipped
        opentiler_process = None
        if not args.no_launch:
            opentiler_process = launch_opentiler_with_automation(document_path)
        
        try:
            # Determine sequence type
            sequence_type = "basic_workflow" if args.quick else "documentation_full"
            
            # Generate documentation images
            success = generate_documentation_images(sequence_type)
            
            if success:
                print(f"\n🎉 Documentation image creation completed successfully!")
                print("📁 Generated images are in docs/images/")
                return 0
            else:
                print(f"\n⚠️  Documentation image creation had some failures")
                return 1
                
        finally:
            # Clean up OpenTiler process
            if opentiler_process:
                print("\n🧹 Cleaning up...")
                try:
                    opentiler_process.terminate()
                    opentiler_process.wait(timeout=5)
                    print("✅ OpenTiler closed gracefully")
                except subprocess.TimeoutExpired:
                    opentiler_process.kill()
                    opentiler_process.wait()
                    print("⚠️  OpenTiler force-closed")
                except Exception as e:
                    print(f"❌ Cleanup error: {e}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Documentation creation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
