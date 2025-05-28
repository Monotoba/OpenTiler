#!/usr/bin/env python3
"""
Generate OpenTiler UI Images

This script connects to the running OpenTiler automation server and
generates documentation screenshots.
"""

import sys
import time
import json
import socket
from pathlib import Path

def connect_to_automation_server(host='localhost', port=8888, timeout=10):
    """Connect to OpenTiler automation server."""
    print(f"🔌 Connecting to OpenTiler automation server at {host}:{port}")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        print("✅ Connected to automation server")
        return sock
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return None

def send_automation_command(sock, action, params=None):
    """Send automation command to OpenTiler."""
    try:
        command = {
            'action': action,
            'params': params or {}
        }
        
        print(f"📤 Sending command: {action}")
        if params:
            print(f"   Parameters: {params}")
        
        # Send command
        message = json.dumps(command).encode('utf-8')
        sock.send(message)
        
        # Receive response
        response_data = sock.recv(1024)
        response = json.loads(response_data.decode('utf-8'))
        
        print(f"📥 Response: {response.get('status', 'unknown')}")
        return response
        
    except Exception as e:
        print(f"❌ Command error: {e}")
        return {'status': 'error', 'message': str(e)}

def generate_documentation_images():
    """Generate OpenTiler documentation images."""
    print("📸 OpenTiler Documentation Image Generation")
    print("=" * 45)
    
    # Connect to automation server
    sock = connect_to_automation_server()
    if not sock:
        return False
    
    try:
        # Create output directory
        output_dir = Path("docs/images")
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {output_dir}")
        
        # Define documentation sequence
        documentation_sequence = [
            {
                'action': 'capture_screenshot',
                'params': {'filename': 'opentiler-with-sky-skanner.png'},
                'description': 'OpenTiler with Sky Skanner document loaded',
                'delay': 2
            },
            {
                'action': 'zoom_in',
                'params': {},
                'description': 'Zoom in on document',
                'delay': 1
            },
            {
                'action': 'capture_screenshot',
                'params': {'filename': 'opentiler-zoomed-in.png'},
                'description': 'OpenTiler zoomed in view',
                'delay': 1
            },
            {
                'action': 'zoom_out',
                'params': {},
                'description': 'Zoom out',
                'delay': 1
            },
            {
                'action': 'fit_to_window',
                'params': {},
                'description': 'Fit document to window',
                'delay': 1
            },
            {
                'action': 'capture_screenshot',
                'params': {'filename': 'opentiler-fit-to-window.png'},
                'description': 'OpenTiler fit to window view',
                'delay': 1
            },
            {
                'action': 'open_file_menu',
                'params': {},
                'description': 'Open File menu',
                'delay': 2
            },
            {
                'action': 'capture_screenshot',
                'params': {'filename': 'opentiler-file-menu.png'},
                'description': 'OpenTiler File menu',
                'delay': 1
            },
            {
                'action': 'open_settings_dialog',
                'params': {},
                'description': 'Open Settings dialog',
                'delay': 2
            },
            {
                'action': 'capture_screenshot',
                'params': {'filename': 'opentiler-settings-dialog.png'},
                'description': 'OpenTiler Settings dialog',
                'delay': 1
            },
        ]
        
        print(f"🎬 Executing documentation sequence ({len(documentation_sequence)} steps):")
        print()
        
        successful_screenshots = 0
        
        for i, step in enumerate(documentation_sequence, 1):
            print(f"Step {i:2d}/{len(documentation_sequence)}: {step['description']}")
            
            # Execute action
            response = send_automation_command(sock, step['action'], step.get('params'))
            
            if response.get('status') == 'received':
                print(f"  ✅ Action completed: {step['action']}")
                
                # Count screenshots
                if step['action'] == 'capture_screenshot':
                    successful_screenshots += 1
                    filename = step['params'].get('filename', 'screenshot.png')
                    print(f"  📸 Screenshot: {filename}")
            else:
                print(f"  ❌ Action failed: {step['action']}")
            
            # Wait before next action
            time.sleep(step.get('delay', 1))
            print()
        
        print(f"📊 Documentation Generation Summary:")
        print(f"   ✅ Steps completed: {len(documentation_sequence)}")
        print(f"   📸 Screenshots captured: {successful_screenshots}")
        print(f"   📁 Output directory: {output_dir}")
        
        return successful_screenshots > 0
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False
    finally:
        sock.close()
        print("🔌 Disconnected from automation server")

def main():
    """Main function."""
    try:
        success = generate_documentation_images()
        
        if success:
            print("\n🎉 Documentation images generated successfully!")
            
            # Check generated files
            output_dir = Path("docs/images")
            if output_dir.exists():
                image_files = list(output_dir.glob("*.png"))
                if image_files:
                    print(f"\n📸 Generated images ({len(image_files)}):")
                    for img_file in sorted(image_files):
                        size_kb = img_file.stat().st_size / 1024
                        print(f"   ✅ {img_file.name} ({size_kb:.1f} KB)")
                else:
                    print("\n⚠️  No image files found in output directory")
            
            return 0
        else:
            print("\n❌ Documentation generation failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Generation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
