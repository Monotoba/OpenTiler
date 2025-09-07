#!/usr/bin/env python3
"""
Basic OpenTiler Documentation Generator

A simplified version that captures OpenTiler screenshots without GUI automation.
Perfect for immediate use and manual workflow documentation.

Usage:
    python basic_opentiler_docs.py [document_path]
    python basic_opentiler_docs.py "plans/original_plans/1147 Sky Skanner_2.pdf"
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from screen_capture import ScreenCapture


class BasicOpenTilerDocGenerator:
    """Basic OpenTiler documentation screenshot generator."""

    def __init__(
        self,
        document_path: Optional[str] = None,
        output_dir: str = "../../../docs/images",
    ):
        """Initialize the generator.

        Args:
            document_path: Path to document to open in OpenTiler
            output_dir: Directory to save screenshots
        """
        self.capture = ScreenCapture()
        self.document_path = document_path
        self.output_dir = Path(__file__).parent / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.opentiler_process = None
        self.opentiler_window = None

        # Basic screenshot sequence
        self.screenshots = [
            {
                "name": "opentiler-startup",
                "description": "OpenTiler startup interface",
                "delay": 2,
            },
            {
                "name": "opentiler-main-interface",
                "description": "Main OpenTiler interface",
                "delay": 1,
            },
            {
                "name": "opentiler-with-document",
                "description": "OpenTiler with document loaded",
                "delay": 3,
            },
            {
                "name": "opentiler-toolbar-detail",
                "description": "Toolbar detailed view",
                "delay": 1,
            },
            {
                "name": "opentiler-full-window",
                "description": "Full OpenTiler window",
                "delay": 1,
            },
        ]

        self.results = {}

    def generate_documentation(self) -> Dict[str, bool]:
        """Generate basic OpenTiler documentation screenshots.

        Returns:
            Dictionary mapping screenshot names to success status
        """
        print("📸 Basic OpenTiler Documentation Generator")
        print("=" * 45)
        print(f"📁 Output directory: {self.output_dir}")
        if self.document_path:
            print(f"📄 Demo document: {self.document_path}")
        print()

        try:
            # Launch OpenTiler
            if not self._launch_opentiler():
                return {}

            # Wait for startup
            print("⏳ Waiting for OpenTiler to start...")
            time.sleep(8)

            # Find OpenTiler window
            if not self._find_opentiler_window():
                print("❌ Could not find OpenTiler window")
                return {}

            print(f"✅ Found OpenTiler: {self.opentiler_window.title}")
            print()

            # Capture screenshots with manual prompts
            for i, screenshot in enumerate(self.screenshots, 1):
                print(f"📸 [{i}/{len(self.screenshots)}] {screenshot['description']}")

                # Wait for user to prepare the interface
                if i > 1:
                    input(
                        f"   Press Enter when ready to capture '{screenshot['name']}'..."
                    )

                # Wait a moment for any UI changes
                time.sleep(screenshot.get("delay", 1))

                # Capture screenshot
                success = self._capture_screenshot(
                    screenshot["name"], screenshot["description"]
                )
                self.results[screenshot["name"]] = success

                if success:
                    print(f"   ✅ Captured: {screenshot['name']}.png")
                else:
                    print(f"   ❌ Failed: {screenshot['name']}")
                print()

            # Generate summary
            self._generate_summary()

            return self.results

        except KeyboardInterrupt:
            print("\n⚠️  Generation interrupted by user")
            return self.results
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()
            return self.results
        finally:
            self._cleanup()

    def capture_current_state(self, name: str, description: str) -> bool:
        """Capture current OpenTiler state.

        Args:
            name: Screenshot name
            description: Screenshot description

        Returns:
            True if successful
        """
        if not self._find_opentiler_window():
            print("❌ OpenTiler window not found")
            return False

        return self._capture_screenshot(name, description)

    def _launch_opentiler(self) -> bool:
        """Launch OpenTiler application."""
        try:
            opentiler_root = Path(__file__).parent / "../../../"

            cmd = ["python", "main.py"]
            if self.document_path:
                cmd.append(self.document_path)

            print(f"🔧 Launching OpenTiler...")
            if self.document_path:
                print(f"   📄 With document: {self.document_path}")

            # Use shell to activate venv
            env_cmd = f"source venv/bin/activate && {' '.join(cmd)}"

            self.opentiler_process = subprocess.Popen(
                env_cmd,
                shell=True,
                cwd=opentiler_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            return True

        except Exception as e:
            print(f"❌ Failed to launch OpenTiler: {e}")
            return False

    def _find_opentiler_window(self) -> bool:
        """Find OpenTiler window."""
        windows = self.capture.list_windows()

        for window in windows:
            if (
                "OpenTiler" in window.title
                and "Visual Studio Code" not in window.title
                and "vscode" not in window.title.lower()
            ):
                self.opentiler_window = window
                return True

        return False

    def _capture_screenshot(self, name: str, description: str) -> bool:
        """Capture screenshot."""
        try:
            if not self.opentiler_window:
                return False

            # Activate window
            self.opentiler_window.activate()
            time.sleep(0.5)

            # Capture with high quality
            output_path = self.output_dir / f"{name}.png"
            success = self.capture.capture_window(
                self.opentiler_window,
                str(output_path),
                target_size=(1600, 1000),
                format_type="png",
            )

            # Also create a thumbnail
            if success:
                thumb_path = self.output_dir / f"{name}-thumb.jpg"
                self.capture.capture_window(
                    self.opentiler_window,
                    str(thumb_path),
                    target_size=(800, 600),
                    format_type="jpeg",
                    quality=85,
                )

            return success

        except Exception as e:
            print(f"   ❌ Capture error: {e}")
            return False

    def _generate_summary(self):
        """Generate summary."""
        successful = sum(1 for success in self.results.values() if success)
        total = len(self.results)

        print(f"📊 Generation Summary:")
        print(f"   ✅ Successful: {successful}/{total}")
        print(f"   📁 Output directory: {self.output_dir}")

        if successful > 0:
            print(f"\n📸 Generated files:")
            for name, success in self.results.items():
                if success:
                    png_path = self.output_dir / f"{name}.png"
                    thumb_path = self.output_dir / f"{name}-thumb.jpg"

                    if png_path.exists():
                        size_kb = png_path.stat().st_size / 1024
                        print(f"   ✅ {name}.png ({size_kb:.1f} KB)")

                    if thumb_path.exists():
                        thumb_size_kb = thumb_path.stat().st_size / 1024
                        print(f"   ✅ {name}-thumb.jpg ({thumb_size_kb:.1f} KB)")

        # Save metadata
        metadata = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "document_path": self.document_path,
            "total_screenshots": total,
            "successful_screenshots": successful,
            "results": self.results,
        }

        metadata_path = self.output_dir / "basic_docs_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"   📄 Metadata: {metadata_path.name}")

    def _cleanup(self):
        """Clean up."""
        print("\n🧹 Cleaning up...")

        if self.opentiler_process:
            try:
                self.opentiler_process.terminate()
                self.opentiler_process.wait(timeout=5)
                print("  ✅ OpenTiler closed")
            except subprocess.TimeoutExpired:
                self.opentiler_process.kill()
                self.opentiler_process.wait()
                print("  ⚠️  OpenTiler force-closed")
            except Exception as e:
                print(f"  ❌ Cleanup error: {e}")


def interactive_mode():
    """Interactive screenshot capture mode."""
    print("🎮 Interactive OpenTiler Screenshot Mode")
    print("=" * 40)

    generator = BasicOpenTilerDocGenerator()

    if not generator._find_opentiler_window():
        print("❌ OpenTiler not running. Please start OpenTiler first.")
        return

    print(f"✅ Found OpenTiler: {generator.opentiler_window.title}")
    print("\nInteractive commands:")
    print("  capture <name> <description> - Capture screenshot")
    print("  list - List available windows")
    print("  quit - Exit interactive mode")
    print()

    while True:
        try:
            cmd = input("📸 > ").strip().split(" ", 2)

            if not cmd or cmd[0] == "":
                continue
            elif cmd[0] == "quit":
                break
            elif cmd[0] == "list":
                windows = generator.capture.list_windows()
                for w in windows:
                    print(f"  - {w.title}")
            elif cmd[0] == "capture":
                if len(cmd) >= 3:
                    name = cmd[1]
                    description = " ".join(cmd[2:])
                    success = generator.capture_current_state(name, description)
                    if success:
                        print(f"✅ Captured: {name}.png")
                    else:
                        print(f"❌ Failed to capture: {name}")
                else:
                    print("Usage: capture <name> <description>")
            else:
                print(f"Unknown command: {cmd[0]}")

        except KeyboardInterrupt:
            break
        except EOFError:
            break

    print("\n👋 Interactive mode ended")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Basic OpenTiler documentation generator"
    )

    parser.add_argument(
        "document", nargs="?", help="Path to document to open in OpenTiler"
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        default="../../../docs/images",
        help="Output directory for screenshots",
    )

    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive screenshot mode (requires OpenTiler to be running)",
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return 0

    try:
        generator = BasicOpenTilerDocGenerator(
            document_path=args.document, output_dir=args.output_dir
        )

        results = generator.generate_documentation()

        if results:
            successful = sum(1 for success in results.values() if success)
            total = len(results)

            if successful == total:
                print(f"\n🎉 All {total} screenshots generated!")
                return 0
            elif successful > 0:
                print(f"\n⚠️  {successful}/{total} screenshots generated")
                return 1
            else:
                print(f"\n❌ No screenshots generated")
                return 2
        else:
            print("\n❌ Generation failed")
            return 3

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
