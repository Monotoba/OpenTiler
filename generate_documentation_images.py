#!/usr/bin/env python3
"""
OpenTiler Documentation Image Generator

This script uses the OpenTiler Automation Plugin to automatically generate
comprehensive documentation screenshots. It demonstrates the plugin system
in action by:

1. Loading OpenTiler with the automation plugin enabled
2. Using the plugin's automation API to control the application
3. Capturing screenshots of all major UI components and workflows
4. Generating a complete set of documentation images

Usage:
    python generate_documentation_images.py                    # Use default demo document
    python generate_documentation_images.py --document path    # Use specific document
    python generate_documentation_images.py --output docs/images  # Custom output directory
    python generate_documentation_images.py --plugin-demo      # Demonstrate plugin system
"""

import sys
import time
import json
import socket
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import screen capture tool
sys.path.insert(0, str(project_root / "tools" / "screen_capture"))
from screen_capture import ScreenCapture


class OpenTilerAutomationClient:
    """Client for communicating with OpenTiler's automation plugin."""
    
    def __init__(self, host: str = 'localhost', port: int = 8888):
        """Initialize automation client.
        
        Args:
            host: OpenTiler automation server host
            port: OpenTiler automation server port
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
    
    def connect(self, timeout: int = 30) -> bool:
        """Connect to OpenTiler automation server.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connected successfully
        """
        print(f"🔌 Connecting to OpenTiler automation server at {self.host}:{self.port}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(5)
                self.socket.connect((self.host, self.port))
                self.connected = True
                print("✅ Connected to OpenTiler automation server")
                return True
            except (ConnectionRefusedError, socket.timeout):
                time.sleep(1)
            except Exception as e:
                print(f"❌ Connection error: {e}")
                break
        
        print("❌ Failed to connect to OpenTiler automation server")
        return False
    
    def send_command(self, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send automation command to OpenTiler.
        
        Args:
            action: Action to execute
            params: Action parameters
            
        Returns:
            Response from OpenTiler
        """
        if not self.connected:
            return {'status': 'error', 'message': 'Not connected'}
        
        try:
            command = {
                'action': action,
                'params': params or {}
            }
            
            # Send command
            message = json.dumps(command).encode('utf-8')
            self.socket.send(message)
            
            # Receive response
            response_data = self.socket.recv(1024)
            response = json.loads(response_data.decode('utf-8'))
            
            return response
            
        except Exception as e:
            print(f"❌ Command error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def disconnect(self):
        """Disconnect from automation server."""
        if self.socket:
            self.socket.close()
            self.connected = False
            print("🔌 Disconnected from automation server")


class DocumentationImageGenerator:
    """Generates comprehensive documentation images using OpenTiler automation."""
    
    def __init__(self, document_path: Optional[str] = None, output_dir: str = "docs/images"):
        """Initialize documentation generator.
        
        Args:
            document_path: Path to document to load
            output_dir: Output directory for images
        """
        self.document_path = document_path or "plans/original_plans/1147 Sky Skanner_2.pdf"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Components
        self.screen_capture = ScreenCapture()
        self.automation_client = OpenTilerAutomationClient()
        self.opentiler_process = None
        self.opentiler_window = None
        
        # Documentation sequence
        self.documentation_sequence = [
            # Basic interface
            {
                'name': 'main-interface-empty',
                'description': 'Main OpenTiler interface (empty)',
                'action': None,
                'delay': 2
            },
            {
                'name': 'main-interface-with-document',
                'description': 'Main interface with document loaded',
                'action': 'load_demo_document',
                'delay': 3
            },
            
            # Menu demonstrations
            {
                'name': 'file-menu',
                'description': 'File menu opened',
                'action': 'open_file_menu',
                'delay': 1
            },
            {
                'name': 'file-open-dialog',
                'description': 'File open dialog',
                'action': 'open_file_dialog',
                'delay': 2
            },
            {
                'name': 'export-dialog',
                'description': 'Export dialog',
                'action': 'open_export_dialog',
                'delay': 2
            },
            {
                'name': 'settings-dialog',
                'description': 'Settings dialog',
                'action': 'open_settings_dialog',
                'delay': 2
            },
            {
                'name': 'scale-tool',
                'description': 'Scale measurement tool',
                'action': 'open_scale_tool',
                'delay': 2
            },
            {
                'name': 'about-dialog',
                'description': 'About dialog',
                'action': 'open_about_dialog',
                'delay': 2
            },
            
            # View operations
            {
                'name': 'zoom-in-demo',
                'description': 'Zoom in demonstration',
                'action': 'zoom_in',
                'delay': 1
            },
            {
                'name': 'zoom-out-demo',
                'description': 'Zoom out demonstration',
                'action': 'zoom_out',
                'delay': 1
            },
            {
                'name': 'fit-to-window-demo',
                'description': 'Fit to window demonstration',
                'action': 'fit_to_window',
                'delay': 1
            },
            {
                'name': 'rotate-left-demo',
                'description': 'Rotate left demonstration',
                'action': 'rotate_left',
                'delay': 1
            },
            {
                'name': 'rotate-right-demo',
                'description': 'Rotate right demonstration',
                'action': 'rotate_right',
                'delay': 1
            },
        ]
        
        # Results
        self.results = {}
        self.metadata = {
            'document_path': self.document_path,
            'output_dir': str(self.output_dir),
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'screenshots': {}
        }
    
    def generate_all_images(self) -> Dict[str, bool]:
        """Generate all documentation images.
        
        Returns:
            Dictionary mapping image names to success status
        """
        print("📸 OpenTiler Documentation Image Generator")
        print("=" * 50)
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📄 Demo document: {self.document_path}")
        print()
        
        try:
            # Launch OpenTiler with automation plugin
            if not self._launch_opentiler():
                print("❌ Failed to launch OpenTiler")
                return {}
            
            # Connect to automation server
            if not self.automation_client.connect():
                print("❌ Failed to connect to automation server")
                return {}
            
            # Find OpenTiler window
            if not self._find_opentiler_window():
                print("❌ Could not find OpenTiler window")
                return {}
            
            print(f"✅ Found OpenTiler: {self.opentiler_window.title}")
            print()
            
            # Execute documentation sequence
            for i, step in enumerate(self.documentation_sequence, 1):
                print(f"📸 [{i:2d}/{len(self.documentation_sequence)}] {step['description']}")
                
                success = self._execute_documentation_step(step)
                self.results[step['name']] = success
                
                if success:
                    print(f"  ✅ Captured: {step['name']}.png")
                else:
                    print(f"  ❌ Failed: {step['name']}")
                
                # Brief pause between steps
                time.sleep(0.5)
            
            # Generate summary
            self._generate_summary()
            
            return self.results
            
        except KeyboardInterrupt:
            print("\n⚠️  Documentation generation interrupted by user")
            return self.results
        except Exception as e:
            print(f"\n❌ Error during generation: {e}")
            import traceback
            traceback.print_exc()
            return self.results
        finally:
            # Clean up
            self._cleanup()
    
    def _launch_opentiler(self) -> bool:
        """Launch OpenTiler with automation plugin enabled.
        
        Returns:
            True if launch successful
        """
        try:
            print("🚀 Launching OpenTiler with automation plugin...")
            
            # Build command to launch OpenTiler
            cmd = [
                sys.executable, 'main.py',
                '--enable-plugins',  # Enable plugin system
                '--plugin', 'automation',  # Load automation plugin
            ]
            
            if self.document_path and Path(self.document_path).exists():
                cmd.append(self.document_path)
                print(f"   📄 With document: {self.document_path}")
            
            # Launch OpenTiler
            self.opentiler_process = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for startup
            print("⏳ Waiting for OpenTiler to initialize...")
            time.sleep(8)  # Give time for plugin system to load
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to launch OpenTiler: {e}")
            return False
    
    def _find_opentiler_window(self) -> bool:
        """Find OpenTiler window.
        
        Returns:
            True if window found
        """
        for attempt in range(10):
            windows = self.screen_capture.list_windows()
            
            for window in windows:
                if ('OpenTiler' in window.title and 
                    'Visual Studio Code' not in window.title):
                    self.opentiler_window = window
                    return True
            
            time.sleep(1)
        
        return False
    
    def _execute_documentation_step(self, step: Dict[str, Any]) -> bool:
        """Execute a documentation step.
        
        Args:
            step: Documentation step configuration
            
        Returns:
            True if successful
        """
        try:
            # Execute automation action if specified
            if step.get('action'):
                response = self.automation_client.send_command(step['action'])
                if response.get('status') != 'received':
                    print(f"  ⚠️  Automation command failed: {response}")
            
            # Wait for UI to update
            time.sleep(step.get('delay', 1))
            
            # Capture screenshot
            return self._capture_screenshot(step['name'], step['description'])
            
        except Exception as e:
            print(f"  ❌ Step error: {e}")
            return False
    
    def _capture_screenshot(self, name: str, description: str) -> bool:
        """Capture screenshot.
        
        Args:
            name: Screenshot name
            description: Screenshot description
            
        Returns:
            True if successful
        """
        try:
            if not self.opentiler_window:
                return False
            
            # Ensure window is active
            self.opentiler_window.activate()
            time.sleep(0.5)
            
            # Capture screenshot
            output_path = self.output_dir / f"{name}.png"
            success = self.screen_capture.capture_window(
                self.opentiler_window,
                str(output_path),
                target_size=(1600, 1000),
                format_type='png',
                quality=95
            )
            
            if success:
                # Store metadata
                self.metadata['screenshots'][name] = {
                    'description': description,
                    'filename': f"{name}.png",
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return success
            
        except Exception as e:
            print(f"  ❌ Capture error: {e}")
            return False
    
    def _generate_summary(self):
        """Generate summary of image generation."""
        successful = sum(1 for success in self.results.values() if success)
        total = len(self.results)
        
        print(f"\n📊 Documentation Image Generation Summary:")
        print(f"   ✅ Successful: {successful}/{total}")
        print(f"   📁 Output directory: {self.output_dir}")
        
        if successful > 0:
            print(f"\n📸 Generated images:")
            for name, success in self.results.items():
                if success:
                    screenshot_info = self.metadata['screenshots'].get(name, {})
                    description = screenshot_info.get('description', name)
                    filename = screenshot_info.get('filename', f'{name}.png')
                    
                    file_path = self.output_dir / filename
                    if file_path.exists():
                        size_kb = file_path.stat().st_size / 1024
                        print(f"   ✅ {filename} - {description} ({size_kb:.1f} KB)")
        
        # Save metadata
        metadata_path = self.output_dir / 'documentation_metadata.json'
        self.metadata['results'] = self.results
        self.metadata['total_images'] = total
        self.metadata['successful_images'] = successful
        
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        print(f"   📄 Metadata saved: {metadata_path.name}")
    
    def _cleanup(self):
        """Clean up resources."""
        print("\n🧹 Cleaning up...")
        
        # Disconnect from automation server
        self.automation_client.disconnect()
        
        # Close OpenTiler
        if self.opentiler_process:
            try:
                self.opentiler_process.terminate()
                self.opentiler_process.wait(timeout=5)
                print("  ✅ OpenTiler closed gracefully")
            except subprocess.TimeoutExpired:
                self.opentiler_process.kill()
                self.opentiler_process.wait()
                print("  ⚠️  OpenTiler force-closed")
            except Exception as e:
                print(f"  ❌ Cleanup error: {e}")


def demonstrate_plugin_system():
    """Demonstrate the plugin system capabilities."""
    print("🔌 OpenTiler Plugin System Demonstration")
    print("=" * 45)
    
    try:
        # Import plugin system components
        from plugins.plugin_manager import PluginManager
        from plugins.builtin.automation_plugin import AutomationPlugin
        from unittest.mock import Mock
        
        print("✅ Plugin system components imported successfully")
        
        # Create mock main window
        mock_window = Mock()
        print("✅ Mock OpenTiler window created")
        
        # Create plugin manager
        plugin_manager = PluginManager(mock_window)
        print("✅ Plugin manager created")
        
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
        
        # Get automation actions
        actions = list(automation_plugin.automation_actions.keys())
        print(f"✅ Available automation actions: {len(actions)}")
        for action in actions[:5]:  # Show first 5
            print(f"   - {action}")
        if len(actions) > 5:
            print(f"   ... and {len(actions) - 5} more")
        
        # Get hook handlers
        handlers = automation_plugin.get_hook_handlers()
        print(f"✅ Plugin provides {len(handlers)} hook handlers")
        
        # Get content access requirements
        requirements = automation_plugin.get_document_access_requirements()
        required_access = [key for key, value in requirements.items() if value]
        print(f"✅ Plugin requires access to: {required_access}")
        
        print("\n🎉 Plugin system demonstration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Plugin system demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate OpenTiler documentation images using automation plugin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use default demo document
  %(prog)s --document "path/to/plan.pdf"     # Use specific document
  %(prog)s --output docs/images              # Custom output directory
  %(prog)s --plugin-demo                     # Demonstrate plugin system
        """
    )
    
    parser.add_argument(
        '--document', '-d',
        help='Path to document to load in OpenTiler'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='docs/images',
        help='Output directory for documentation images'
    )
    
    parser.add_argument(
        '--plugin-demo',
        action='store_true',
        help='Demonstrate plugin system capabilities'
    )
    
    args = parser.parse_args()
    
    # Run plugin demonstration if requested
    if args.plugin_demo:
        return 0 if demonstrate_plugin_system() else 1
    
    try:
        # Create documentation generator
        generator = DocumentationImageGenerator(
            document_path=args.document,
            output_dir=args.output
        )
        
        # Generate documentation images
        results = generator.generate_all_images()
        
        # Report results
        if results:
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            if successful == total:
                print(f"\n🎉 All {total} documentation images generated successfully!")
                return 0
            elif successful > 0:
                print(f"\n⚠️  {successful}/{total} images generated")
                return 1
            else:
                print(f"\n❌ No images generated successfully")
                return 2
        else:
            print("\n❌ Documentation generation failed")
            return 3
            
    except KeyboardInterrupt:
        print("\n⚠️  Documentation generation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
