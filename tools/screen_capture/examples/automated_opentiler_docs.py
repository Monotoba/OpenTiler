#!/usr/bin/env python3
"""
Automated OpenTiler Documentation Generator

This script automatically launches OpenTiler, exercises all menus and dialogs,
and captures comprehensive screenshots for documentation.

Usage:
    python automated_opentiler_docs.py [document_path]
    python automated_opentiler_docs.py "plans/original_plans/1147 Sky Skanner_2.pdf"
"""

import sys
import time
import subprocess
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from screen_capture import ScreenCapture

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.5
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("⚠️  pyautogui not available - will use basic window capture only")


class OpenTilerDocumentationGenerator:
    """Automated OpenTiler documentation screenshot generator."""
    
    def __init__(self, document_path: Optional[str] = None, output_dir: str = "../../../docs/images/screenshots"):
        """Initialize the documentation generator.
        
        Args:
            document_path: Path to document to open in OpenTiler
            output_dir: Directory to save screenshots
        """
        self.capture = ScreenCapture()
        self.document_path = document_path
        self.output_dir = Path(__file__).parent / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # OpenTiler process
        self.opentiler_process = None
        self.opentiler_window = None
        
        # Screenshot sequence
        self.screenshot_sequence = [
            # Basic interface
            {'name': 'main-interface', 'description': 'Main OpenTiler interface', 'action': 'capture_main'},
            {'name': 'main-with-document', 'description': 'Main interface with document loaded', 'action': 'load_document'},
            
            # File menu
            {'name': 'file-menu', 'description': 'File menu opened', 'action': 'open_file_menu'},
            {'name': 'file-open-dialog', 'description': 'File open dialog', 'action': 'open_file_dialog'},
            {'name': 'file-export-dialog', 'description': 'Export dialog', 'action': 'open_export_dialog'},
            
            # Edit menu
            {'name': 'edit-menu', 'description': 'Edit menu opened', 'action': 'open_edit_menu'},
            
            # View menu
            {'name': 'view-menu', 'description': 'View menu opened', 'action': 'open_view_menu'},
            {'name': 'zoom-controls', 'description': 'Zoom controls demonstration', 'action': 'demonstrate_zoom'},
            
            # Tools menu
            {'name': 'tools-menu', 'description': 'Tools menu opened', 'action': 'open_tools_menu'},
            {'name': 'scale-tool', 'description': 'Scale measurement tool', 'action': 'open_scale_tool'},
            {'name': 'settings-dialog', 'description': 'Settings dialog', 'action': 'open_settings'},
            
            # Help menu
            {'name': 'help-menu', 'description': 'Help menu opened', 'action': 'open_help_menu'},
            {'name': 'about-dialog', 'description': 'About dialog', 'action': 'open_about_dialog'},
            
            # Workflow demonstrations
            {'name': 'document-viewer', 'description': 'Document viewer with plan loaded', 'action': 'show_document_viewer'},
            {'name': 'preview-panel', 'description': 'Preview panel with tiles', 'action': 'show_preview_panel'},
            {'name': 'toolbar-detail', 'description': 'Toolbar detailed view', 'action': 'capture_toolbar'},
            
            # Export workflow
            {'name': 'export-preview', 'description': 'Export preview window', 'action': 'show_export_preview'},
            {'name': 'export-settings', 'description': 'Export settings configuration', 'action': 'configure_export'},
        ]
        
        # Results tracking
        self.results = {}
        self.metadata = {
            'document_path': document_path,
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'screenshots': {}
        }
    
    def generate_all_documentation(self) -> Dict[str, bool]:
        """Generate complete OpenTiler documentation screenshots.
        
        Returns:
            Dictionary mapping screenshot names to success status
        """
        print("🚀 Starting Automated OpenTiler Documentation Generation")
        print("=" * 60)
        print(f"📁 Output directory: {self.output_dir}")
        if self.document_path:
            print(f"📄 Demo document: {self.document_path}")
        print()
        
        try:
            # Launch OpenTiler
            if not self._launch_opentiler():
                print("❌ Failed to launch OpenTiler")
                return {}
            
            # Wait for startup
            print("⏳ Waiting for OpenTiler to initialize...")
            time.sleep(5)
            
            # Find OpenTiler window
            if not self._find_opentiler_window():
                print("❌ Could not find OpenTiler window")
                return {}
            
            print(f"✅ Found OpenTiler: {self.opentiler_window.title}")
            print()
            
            # Execute screenshot sequence
            for i, screenshot in enumerate(self.screenshot_sequence, 1):
                print(f"📸 [{i:2d}/{len(self.screenshot_sequence)}] {screenshot['description']}")
                
                success = self._execute_screenshot_action(screenshot)
                self.results[screenshot['name']] = success
                
                if success:
                    print(f"  ✅ Captured: {screenshot['name']}.png")
                else:
                    print(f"  ❌ Failed: {screenshot['name']}")
                
                # Brief pause between actions
                time.sleep(1)
            
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
        """Launch OpenTiler application.
        
        Returns:
            True if launch successful
        """
        try:
            # Change to OpenTiler root directory
            opentiler_root = Path(__file__).parent / "../../../"
            
            # Build command
            cmd = ['python', 'main.py']
            if self.document_path:
                cmd.append(self.document_path)
            
            print(f"🔧 Launching OpenTiler...")
            if self.document_path:
                print(f"   📄 With document: {self.document_path}")
            
            # Activate virtual environment and launch
            env_cmd = f"source venv/bin/activate && {' '.join(cmd)}"
            
            self.opentiler_process = subprocess.Popen(
                env_cmd,
                shell=True,
                cwd=opentiler_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to launch OpenTiler: {e}")
            return False
    
    def _find_opentiler_window(self) -> bool:
        """Find the OpenTiler application window.
        
        Returns:
            True if window found
        """
        # Try multiple times to find the window
        for attempt in range(10):
            windows = self.capture.list_windows()
            
            # Look for OpenTiler window (not VS Code)
            for window in windows:
                if ('OpenTiler' in window.title and 
                    'Visual Studio Code' not in window.title and
                    'vscode' not in window.title.lower()):
                    self.opentiler_window = window
                    return True
            
            time.sleep(1)
        
        return False
    
    def _execute_screenshot_action(self, screenshot: Dict) -> bool:
        """Execute a screenshot action.
        
        Args:
            screenshot: Screenshot configuration
            
        Returns:
            True if successful
        """
        try:
            action = screenshot['action']
            
            # Execute the action
            if hasattr(self, f'_action_{action}'):
                action_method = getattr(self, f'_action_{action}')
                action_method()
            else:
                print(f"  ⚠️  Action '{action}' not implemented")
            
            # Capture the screenshot
            return self._capture_screenshot(screenshot['name'], screenshot['description'])
            
        except Exception as e:
            print(f"  ❌ Action error: {e}")
            return False
    
    def _capture_screenshot(self, name: str, description: str) -> bool:
        """Capture a screenshot of the current OpenTiler state.
        
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
            success = self.capture.capture_window(
                self.opentiler_window,
                str(output_path),
                target_size=(1600, 1000),
                format_type='png'
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
    
    # Action methods for different UI interactions
    def _action_capture_main(self):
        """Capture main interface."""
        # Just ensure window is focused
        self.opentiler_window.activate()
        time.sleep(0.5)
    
    def _action_load_document(self):
        """Load document if specified."""
        if self.document_path and HAS_PYAUTOGUI:
            # Try to open file via keyboard shortcut
            pyautogui.hotkey('ctrl', 'o')
            time.sleep(1)
            # Type file path (simplified)
            # In real implementation, would navigate file dialog
    
    def _action_open_file_menu(self):
        """Open File menu."""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('alt', 'f')
            time.sleep(0.5)
    
    def _action_open_file_dialog(self):
        """Open file dialog."""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('ctrl', 'o')
            time.sleep(1)
    
    def _action_open_export_dialog(self):
        """Open export dialog."""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('ctrl', 'e')
            time.sleep(1)
    
    def _action_open_edit_menu(self):
        """Open Edit menu."""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('alt', 'e')
            time.sleep(0.5)
    
    def _action_open_view_menu(self):
        """Open View menu."""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('alt', 'v')
            time.sleep(0.5)
    
    def _action_demonstrate_zoom(self):
        """Demonstrate zoom controls."""
        if HAS_PYAUTOGUI:
            # Zoom in
            pyautogui.hotkey('ctrl', 'plus')
            time.sleep(0.5)
    
    def _action_open_tools_menu(self):
        """Open Tools menu."""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('alt', 't')
            time.sleep(0.5)
    
    def _action_open_scale_tool(self):
        """Open scale tool."""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('ctrl', 'm')  # Assuming Ctrl+M for measure
            time.sleep(1)
    
    def _action_open_settings(self):
        """Open settings dialog."""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('ctrl', 'comma')  # Common settings shortcut
            time.sleep(1)
    
    def _action_open_help_menu(self):
        """Open Help menu."""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('alt', 'h')
            time.sleep(0.5)
    
    def _action_open_about_dialog(self):
        """Open About dialog."""
        if HAS_PYAUTOGUI:
            pyautogui.key('f1')  # Common help key
            time.sleep(1)
    
    def _action_show_document_viewer(self):
        """Show document viewer."""
        # Focus on document area
        pass
    
    def _action_show_preview_panel(self):
        """Show preview panel."""
        # Focus on preview area
        pass
    
    def _action_capture_toolbar(self):
        """Capture toolbar detail."""
        # Focus on toolbar area
        pass
    
    def _action_show_export_preview(self):
        """Show export preview."""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey('ctrl', 'shift', 'e')
            time.sleep(1)
    
    def _action_configure_export(self):
        """Configure export settings."""
        # Open export configuration
        pass
    
    def _generate_summary(self):
        """Generate summary of screenshot generation."""
        successful = sum(1 for success in self.results.values() if success)
        total = len(self.results)
        
        print(f"\n📊 Documentation Generation Summary:")
        print(f"   ✅ Successful: {successful}/{total}")
        print(f"   📁 Output directory: {self.output_dir}")
        
        if successful > 0:
            print(f"\n📸 Generated screenshots:")
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
        self.metadata['total_screenshots'] = total
        self.metadata['successful_screenshots'] = successful
        
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        print(f"   📄 Metadata saved: {metadata_path.name}")
    
    def _cleanup(self):
        """Clean up OpenTiler process."""
        print("\n🧹 Cleaning up...")
        
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


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Automated OpenTiler documentation generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s "plans/original_plans/1147 Sky Skanner_2.pdf"
  %(prog)s --output-dir custom/screenshots/
        """
    )
    
    parser.add_argument(
        'document',
        nargs='?',
        help='Path to document to open in OpenTiler'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='../../../docs/images/screenshots',
        help='Output directory for screenshots'
    )
    
    args = parser.parse_args()
    
    try:
        # Create generator
        generator = OpenTilerDocumentationGenerator(
            document_path=args.document,
            output_dir=args.output_dir
        )
        
        # Generate documentation
        results = generator.generate_all_documentation()
        
        # Report results
        if results:
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            if successful == total:
                print(f"\n🎉 All {total} screenshots generated successfully!")
                return 0
            elif successful > 0:
                print(f"\n⚠️  {successful}/{total} screenshots generated")
                return 1
            else:
                print(f"\n❌ No screenshots generated successfully")
                return 2
        else:
            print("\n❌ Documentation generation failed")
            return 3
        
    except KeyboardInterrupt:
        print("\n⚠️  Generation interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
