#!/usr/bin/env python3
"""
OpenTiler Documentation Screenshot Generator

This example demonstrates how to use the screen capture tool to automatically
generate documentation screenshots for the OpenTiler application.
"""

import sys
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from screen_capture import ScreenCapture


class OpenTilerDocumentationGenerator:
    """Automated documentation screenshot generator for OpenTiler."""
    
    def __init__(self, output_dir: str = "../../../docs/images/screenshots"):
        """Initialize the documentation generator.
        
        Args:
            output_dir: Directory to save screenshots (relative to this file)
        """
        self.capture = ScreenCapture()
        self.output_dir = Path(__file__).parent / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Screenshot configuration
        self.screenshots = {
            'main-interface': {
                'filename': 'main-interface.png',
                'description': 'Main OpenTiler interface showing toolbar and panels',
                'size': (1920, 1080),
                'delay': 3.0
            },
            'main-interface-thumb': {
                'filename': 'main-interface-thumb.jpg',
                'description': 'Main interface thumbnail for documentation',
                'size': (800, 600),
                'format': 'jpeg',
                'quality': 85,
                'delay': 3.0
            },
            'document-loaded': {
                'filename': 'document-loaded.png',
                'description': 'OpenTiler with a document loaded',
                'size': (1600, 1000),
                'delay': 5.0,
                'requires_document': True
            },
            'toolbar-detail': {
                'filename': 'toolbar-detail.png',
                'description': 'Detailed view of the toolbar',
                'size': (1200, 300),
                'delay': 2.0
            }
        }
        
        # Test document path (relative to OpenTiler root)
        self.test_document = "../../../plans/original_plans/1147 Sky Skanner_2.pdf"
    
    def generate_all_screenshots(self) -> Dict[str, bool]:
        """Generate all documentation screenshots.
        
        Returns:
            Dictionary mapping screenshot names to success status
        """
        print("🚀 Starting OpenTiler documentation screenshot generation...")
        print(f"📁 Output directory: {self.output_dir}")
        print()
        
        # Launch OpenTiler
        process = self._launch_opentiler()
        
        if not process:
            print("❌ Failed to launch OpenTiler")
            return {}
        
        try:
            # Wait for application startup
            print("⏳ Waiting for OpenTiler to start...")
            time.sleep(5)
            
            # Verify OpenTiler is running
            if not self._verify_opentiler_running():
                print("❌ OpenTiler not detected")
                return {}
            
            print("✅ OpenTiler detected and ready")
            print()
            
            # Generate screenshots
            results = {}
            for name, config in self.screenshots.items():
                print(f"📸 Capturing: {config['description']}")
                success = self._capture_screenshot(name, config)
                results[name] = success
                
                if success:
                    print(f"  ✅ Saved: {config['filename']}")
                else:
                    print(f"  ❌ Failed: {config['filename']}")
                
                # Brief pause between captures
                time.sleep(1)
            
            # Generate summary
            self._generate_summary(results)
            
            return results
            
        finally:
            # Clean up
            self._cleanup_opentiler(process)
    
    def _launch_opentiler(self) -> Optional[subprocess.Popen]:
        """Launch OpenTiler application.
        
        Returns:
            Process object or None if launch failed
        """
        try:
            # Change to OpenTiler root directory
            opentiler_root = Path(__file__).parent / "../../../"
            
            # Launch OpenTiler
            print(f"🔧 Launching OpenTiler from: {opentiler_root.resolve()}")
            
            process = subprocess.Popen(
                ['python', 'main.py'],
                cwd=opentiler_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return process
            
        except Exception as e:
            print(f"❌ Failed to launch OpenTiler: {e}")
            return None
    
    def _verify_opentiler_running(self) -> bool:
        """Verify that OpenTiler is running and detectable.
        
        Returns:
            True if OpenTiler window is found
        """
        # Try multiple possible window titles
        possible_titles = ["OpenTiler", "OpenTiler - Professional Document Scaling"]
        
        for title in possible_titles:
            window = self.capture.find_window_by_title(title)
            if window:
                print(f"  Found window: {window.title}")
                return True
        
        # List all windows for debugging
        print("  Available windows:")
        windows = self.capture.list_windows()
        for window in windows[:5]:  # Show first 5
            print(f"    - {window.title}")
        
        return False
    
    def _capture_screenshot(self, name: str, config: Dict) -> bool:
        """Capture individual screenshot.
        
        Args:
            name: Screenshot identifier
            config: Screenshot configuration
            
        Returns:
            True if capture successful
        """
        try:
            # Handle document loading requirement
            if config.get('requires_document'):
                if not self._load_test_document():
                    print("  ⚠️  Could not load test document, capturing anyway")
            
            # Wait for any UI updates
            if 'delay' in config:
                time.sleep(config['delay'])
            
            # Find OpenTiler window
            window = self.capture.find_window_by_title("OpenTiler")
            if not window:
                print("  ❌ OpenTiler window not found")
                return False
            
            # Ensure window is active and visible
            if window.isMinimized:
                window.restore()
                time.sleep(0.5)
            
            window.activate()
            time.sleep(0.5)  # Wait for activation
            
            # Prepare output path
            output_path = self.output_dir / config['filename']
            
            # Capture screenshot
            success = self.capture.capture_window(
                window,
                str(output_path),
                target_size=config.get('size'),
                format_type=config.get('format', 'png'),
                quality=config.get('quality', 95)
            )
            
            return success
            
        except Exception as e:
            print(f"  ❌ Capture error: {e}")
            return False
    
    def _load_test_document(self) -> bool:
        """Load a test document in OpenTiler.
        
        Returns:
            True if document loaded successfully
        """
        # This is a placeholder for document loading
        # In a real implementation, this would:
        # 1. Send keyboard shortcuts to open file dialog
        # 2. Navigate to test document
        # 3. Open the document
        # 4. Wait for loading to complete
        
        print("  📄 Loading test document...")
        
        # Check if test document exists
        test_doc_path = Path(__file__).parent / self.test_document
        if test_doc_path.exists():
            print(f"  📄 Test document found: {test_doc_path.name}")
            # In real implementation, would automate file opening
            time.sleep(2)  # Simulate loading time
            return True
        else:
            print(f"  ⚠️  Test document not found: {test_doc_path}")
            return False
    
    def _cleanup_opentiler(self, process: subprocess.Popen):
        """Clean up OpenTiler process.
        
        Args:
            process: OpenTiler process to terminate
        """
        print("\n🧹 Cleaning up...")
        
        try:
            # Try graceful termination first
            process.terminate()
            
            # Wait for process to end
            try:
                process.wait(timeout=5)
                print("  ✅ OpenTiler closed gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if needed
                process.kill()
                process.wait()
                print("  ⚠️  OpenTiler force-closed")
                
        except Exception as e:
            print(f"  ❌ Cleanup error: {e}")
    
    def _generate_summary(self, results: Dict[str, bool]):
        """Generate summary of screenshot generation.
        
        Args:
            results: Dictionary of screenshot results
        """
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        print(f"\n📊 Screenshot Generation Summary:")
        print(f"   ✅ Successful: {successful}/{total}")
        print(f"   📁 Output directory: {self.output_dir}")
        
        # List successful screenshots
        if successful > 0:
            print(f"\n📸 Generated screenshots:")
            for name, success in results.items():
                if success:
                    config = self.screenshots[name]
                    file_path = self.output_dir / config['filename']
                    if file_path.exists():
                        size_kb = file_path.stat().st_size / 1024
                        print(f"   ✅ {config['filename']} ({size_kb:.1f} KB)")
        
        # Save metadata
        metadata = {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_screenshots': total,
            'successful_screenshots': successful,
            'results': results,
            'screenshots': self.screenshots
        }
        
        metadata_path = self.output_dir / 'generation_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   📄 Metadata saved: {metadata_path.name}")


def main():
    """Main function to run the documentation generator."""
    
    print("📚 OpenTiler Documentation Screenshot Generator")
    print("=" * 50)
    print()
    
    try:
        # Create generator
        generator = OpenTilerDocumentationGenerator()
        
        # Generate all screenshots
        results = generator.generate_all_screenshots()
        
        # Check results
        if results:
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            if successful == total:
                print(f"\n🎉 All {total} screenshots generated successfully!")
            elif successful > 0:
                print(f"\n⚠️  {successful}/{total} screenshots generated")
            else:
                print(f"\n❌ No screenshots generated successfully")
        else:
            print("\n❌ Screenshot generation failed")
        
    except KeyboardInterrupt:
        print("\n⚠️  Generation interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
