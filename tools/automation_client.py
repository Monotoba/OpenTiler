#!/usr/bin/env python3
"""
OpenTiler Automation Client

This client connects to OpenTiler's automation plugin to control the application
and generate comprehensive documentation screenshots.

Usage:
    python automation_client.py --generate-docs
    python automation_client.py --action load_demo_document
    python automation_client.py --sequence documentation_full
"""

import sys
import time
import socket
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional


class OpenTilerAutomationClient:
    """
    Client for OpenTiler's automation plugin.
    
    Connects to the automation server and sends commands to control OpenTiler.
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8888):
        """
        Initialize the automation client.
        
        Args:
            host: Server hostname
            port: Server port
        """
        self.host = host
        self.port = port
        self.socket = None
        self.logger = logging.getLogger(__name__)
        
        # Predefined automation sequences
        self.sequences = {
            'documentation_full': [
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-empty-interface.png'}, 'description': 'Empty interface'},
                {'action': 'load_demo_document', 'delay': 3, 'description': 'Load Sky Skanner demo'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-with-document.png'}, 'description': 'With document loaded'},
                {'action': 'open_file_menu', 'delay': 1, 'description': 'Open File menu'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-file-menu.png'}, 'description': 'File menu open'},
                {'action': 'open_edit_menu', 'delay': 1, 'description': 'Open Edit menu'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-edit-menu.png'}, 'description': 'Edit menu open'},
                {'action': 'open_view_menu', 'delay': 1, 'description': 'Open View menu'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-view-menu.png'}, 'description': 'View menu open'},
                {'action': 'open_tools_menu', 'delay': 1, 'description': 'Open Tools menu'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-tools-menu.png'}, 'description': 'Tools menu open'},
                {'action': 'open_help_menu', 'delay': 1, 'description': 'Open Help menu'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-help-menu.png'}, 'description': 'Help menu open'},
                {'action': 'open_file_dialog', 'delay': 2, 'description': 'Open file dialog'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-file-dialog.png'}, 'description': 'File dialog open'},
                {'action': 'open_export_dialog', 'delay': 2, 'description': 'Open export dialog'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-export-dialog.png'}, 'description': 'Export dialog open'},
                {'action': 'open_settings_dialog', 'delay': 2, 'description': 'Open settings dialog'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-settings-dialog.png'}, 'description': 'Settings dialog open'},
                {'action': 'open_scale_tool', 'delay': 2, 'description': 'Open scale tool'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-scale-tool2.png'}, 'description': 'Scale tool open'},
                {'action': 'open_about_dialog', 'delay': 2, 'description': 'Open about dialog'},
                {'action': 'capture_screenshot', 'params': {'filename': 'opentiler-about-dialog.png'}, 'description': 'About dialog open'},
            ],
            'basic_workflow': [
                {'action': 'capture_screenshot', 'params': {'filename': 'step1-empty.png'}, 'description': 'Step 1: Empty interface'},
                {'action': 'load_demo_document', 'delay': 3, 'description': 'Step 2: Load document'},
                {'action': 'capture_screenshot', 'params': {'filename': 'step2-loaded.png'}, 'description': 'Step 2: Document loaded'},
                {'action': 'zoom_in', 'delay': 1, 'description': 'Step 3: Zoom in'},
                {'action': 'capture_screenshot', 'params': {'filename': 'step3-zoomed.png'}, 'description': 'Step 3: Zoomed view'},
                {'action': 'fit_to_window', 'delay': 1, 'description': 'Step 4: Fit to window'},
                {'action': 'capture_screenshot', 'params': {'filename': 'step4-fitted.png'}, 'description': 'Step 4: Fitted to window'},
            ],
            'menu_tour': [
                {'action': 'open_file_menu', 'delay': 1, 'description': 'File menu'},
                {'action': 'capture_screenshot', 'params': {'filename': 'menu-file.png'}, 'description': 'File menu'},
                {'action': 'open_edit_menu', 'delay': 1, 'description': 'Edit menu'},
                {'action': 'capture_screenshot', 'params': {'filename': 'menu-edit.png'}, 'description': 'Edit menu'},
                {'action': 'open_view_menu', 'delay': 1, 'description': 'View menu'},
                {'action': 'capture_screenshot', 'params': {'filename': 'menu-view.png'}, 'description': 'View menu'},
                {'action': 'open_tools_menu', 'delay': 1, 'description': 'Tools menu'},
                {'action': 'capture_screenshot', 'params': {'filename': 'menu-tools.png'}, 'description': 'Tools menu'},
                {'action': 'open_help_menu', 'delay': 1, 'description': 'Help menu'},
                {'action': 'capture_screenshot', 'params': {'filename': 'menu-help.png'}, 'description': 'Help menu'},
            ]
        }
    
    def connect(self) -> bool:
        """
        Connect to the automation server.
        
        Returns:
            True if connected successfully
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.logger.info(f"Connected to automation server at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to automation server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the automation server."""
        if self.socket:
            self.socket.close()
            self.socket = None
            self.logger.info("Disconnected from automation server")
    
    def send_command(self, action: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send a command to the automation server.
        
        Args:
            action: Action to perform
            params: Optional parameters for the action
            
        Returns:
            True if command sent successfully
        """
        if not self.socket:
            self.logger.error("Not connected to automation server")
            return False
        
        try:
            command = {
                'action': action,
                'params': params or {}
            }
            
            message = json.dumps(command)
            self.socket.send(message.encode('utf-8'))
            
            # Wait for response
            response_data = self.socket.recv(1024)
            response = json.loads(response_data.decode('utf-8'))
            
            if response.get('status') == 'received':
                self.logger.info(f"Command executed: {action}")
                return True
            else:
                self.logger.error(f"Command failed: {response}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send command {action}: {e}")
            return False
    
    def execute_sequence(self, sequence_name: str) -> bool:
        """
        Execute a predefined automation sequence.
        
        Args:
            sequence_name: Name of the sequence to execute
            
        Returns:
            True if sequence executed successfully
        """
        if sequence_name not in self.sequences:
            self.logger.error(f"Unknown sequence: {sequence_name}")
            return False
        
        sequence = self.sequences[sequence_name]
        self.logger.info(f"Executing sequence: {sequence_name} ({len(sequence)} steps)")
        
        success_count = 0
        
        for i, step in enumerate(sequence, 1):
            action = step['action']
            params = step.get('params', {})
            delay = step.get('delay', 1)
            description = step.get('description', action)
            
            print(f"Step {i}/{len(sequence)}: {description}")
            
            # Execute the action
            success = self.send_command(action, params)
            if success:
                success_count += 1
                print(f"  ✅ Success")
            else:
                print(f"  ❌ Failed")
            
            # Wait before next step
            if delay > 0:
                time.sleep(delay)
        
        print(f"\nSequence complete: {success_count}/{len(sequence)} steps successful")
        return success_count == len(sequence)
    
    def generate_documentation_screenshots(self) -> bool:
        """
        Generate comprehensive documentation screenshots.
        
        Returns:
            True if generation successful
        """
        print("🚀 Generating OpenTiler Documentation Screenshots")
        print("=" * 50)
        
        if not self.connect():
            print("❌ Failed to connect to OpenTiler automation server")
            print("   Make sure OpenTiler is running with --automation-mode")
            return False
        
        try:
            # Execute full documentation sequence
            success = self.execute_sequence('documentation_full')
            
            if success:
                print("\n🎉 Documentation screenshots generated successfully!")
                print("📁 Check docs/images/ for the generated screenshots")
            else:
                print("\n⚠️  Some screenshots may have failed to generate")
            
            return success
            
        finally:
            self.disconnect()
    
    def interactive_mode(self):
        """Run in interactive mode for manual control."""
        print("🎮 OpenTiler Automation Client - Interactive Mode")
        print("=" * 50)
        
        if not self.connect():
            print("❌ Failed to connect to automation server")
            return
        
        print("Connected to OpenTiler automation server")
        print("\nAvailable commands:")
        print("  action <action_name>     - Execute single action")
        print("  sequence <sequence_name> - Execute predefined sequence")
        print("  list                     - List available sequences")
        print("  screenshot [filename]    - Capture screenshot")
        print("  quit                     - Exit interactive mode")
        print()
        
        try:
            while True:
                try:
                    cmd = input("automation> ").strip().split()
                    
                    if not cmd:
                        continue
                    elif cmd[0] == 'quit':
                        break
                    elif cmd[0] == 'action' and len(cmd) > 1:
                        action = cmd[1]
                        success = self.send_command(action)
                        print(f"Action {action}: {'✅ Success' if success else '❌ Failed'}")
                    elif cmd[0] == 'sequence' and len(cmd) > 1:
                        sequence_name = cmd[1]
                        success = self.execute_sequence(sequence_name)
                        print(f"Sequence {sequence_name}: {'✅ Complete' if success else '❌ Failed'}")
                    elif cmd[0] == 'list':
                        print("Available sequences:")
                        for name, sequence in self.sequences.items():
                            print(f"  {name:20} - {len(sequence)} steps")
                    elif cmd[0] == 'screenshot':
                        filename = cmd[1] if len(cmd) > 1 else f'screenshot_{int(time.time())}.png'
                        success = self.send_command('capture_screenshot', {'filename': filename})
                        print(f"Screenshot: {'✅ Captured' if success else '❌ Failed'}")
                    else:
                        print(f"Unknown command: {cmd[0]}")
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                    
        finally:
            self.disconnect()
            print("\n👋 Interactive mode ended")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="OpenTiler Automation Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --generate-docs
  %(prog)s --action load_demo_document
  %(prog)s --sequence documentation_full
  %(prog)s --interactive
        """
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='Automation server hostname (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8888,
        help='Automation server port (default: 8888)'
    )
    
    parser.add_argument(
        '--generate-docs',
        action='store_true',
        help='Generate comprehensive documentation screenshots'
    )
    
    parser.add_argument(
        '--action',
        help='Execute a single automation action'
    )
    
    parser.add_argument(
        '--sequence',
        help='Execute a predefined automation sequence'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create client
    client = OpenTilerAutomationClient(args.host, args.port)
    
    try:
        if args.generate_docs:
            success = client.generate_documentation_screenshots()
            return 0 if success else 1
        elif args.action:
            if client.connect():
                success = client.send_command(args.action)
                client.disconnect()
                return 0 if success else 1
            else:
                return 1
        elif args.sequence:
            if client.connect():
                success = client.execute_sequence(args.sequence)
                client.disconnect()
                return 0 if success else 1
            else:
                return 1
        elif args.interactive:
            client.interactive_mode()
            return 0
        else:
            parser.print_help()
            return 0
            
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
