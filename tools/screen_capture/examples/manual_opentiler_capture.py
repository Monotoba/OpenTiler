#!/usr/bin/env python3
"""
Manual OpenTiler Screenshot Capture

Interactive script for capturing OpenTiler screenshots manually.
Perfect for documenting specific UI states and workflows.

Usage:
    # Start OpenTiler first, then run:
    python manual_opentiler_capture.py

    # Or specify output directory:
    python manual_opentiler_capture.py --output-dir custom/path/
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from screen_capture import ScreenCapture


class ManualOpenTilerCapture:
    """Manual OpenTiler screenshot capture tool."""

    def __init__(self, output_dir: str = "../../../docs/images"):
        """Initialize the capture tool.

        Args:
            output_dir: Directory to save screenshots
        """
        self.capture = ScreenCapture()
        self.output_dir = Path(__file__).parent / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.opentiler_window = None
        self.capture_count = 0

        # Predefined screenshot templates
        self.templates = {
            "main": {
                "name": "opentiler-main-interface",
                "description": "Main OpenTiler interface",
                "size": (1600, 1000),
            },
            "hero": {
                "name": "opentiler-hero-image",
                "description": "Hero image for documentation",
                "size": (1200, 800),
            },
            "thumb": {
                "name": "opentiler-thumbnail",
                "description": "Thumbnail for previews",
                "size": (800, 600),
                "format": "jpeg",
                "quality": 85,
            },
            "toolbar": {
                "name": "opentiler-toolbar-detail",
                "description": "Detailed toolbar view",
                "size": (1400, 200),
            },
            "menu": {
                "name": "opentiler-menu-open",
                "description": "Menu opened",
                "size": (1200, 800),
            },
            "dialog": {
                "name": "opentiler-dialog",
                "description": "Dialog window",
                "size": (800, 600),
            },
            "document": {
                "name": "opentiler-with-document",
                "description": "OpenTiler with document loaded",
                "size": (1600, 1000),
            },
            "preview": {
                "name": "opentiler-preview-panel",
                "description": "Preview panel with tiles",
                "size": (1400, 900),
            },
        }

    def start_interactive_session(self):
        """Start interactive screenshot capture session."""
        print("🎮 Manual OpenTiler Screenshot Capture")
        print("=" * 40)
        print(f"📁 Output directory: {self.output_dir}")
        print()

        # Find OpenTiler window
        if not self._find_opentiler_window():
            print("❌ OpenTiler not running!")
            print("   Please start OpenTiler first, then run this script again.")
            return False

        print(f"✅ Found OpenTiler: {self.opentiler_window.title}")
        print()

        self._show_help()

        # Interactive loop
        while True:
            try:
                cmd = input("\n📸 capture> ").strip()

                if not cmd:
                    continue
                elif cmd in ["quit", "exit", "q"]:
                    break
                elif cmd in ["help", "h", "?"]:
                    self._show_help()
                elif cmd == "list":
                    self._list_windows()
                elif cmd == "templates":
                    self._show_templates()
                elif cmd == "status":
                    self._show_status()
                elif cmd.startswith("capture "):
                    self._handle_capture_command(cmd)
                elif cmd.startswith("template "):
                    self._handle_template_command(cmd)
                elif cmd.startswith("quick "):
                    self._handle_quick_command(cmd)
                else:
                    print(f"❌ Unknown command: {cmd}")
                    print("   Type 'help' for available commands")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                break

        print(f"\n📊 Session complete! Captured {self.capture_count} screenshots.")
        return True

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

    def _show_help(self):
        """Show help information."""
        print("📋 Available Commands:")
        print("  capture <name> [description]  - Capture screenshot with custom name")
        print("  template <template_name>      - Use predefined template")
        print("  quick <name>                  - Quick capture with auto-naming")
        print("  templates                     - Show available templates")
        print("  list                          - List all windows")
        print("  status                        - Show current status")
        print("  help                          - Show this help")
        print("  quit                          - Exit")
        print()
        print("📸 Templates available:")
        for name, template in self.templates.items():
            print(f"  {name:10} - {template['description']}")

    def _show_templates(self):
        """Show available templates."""
        print("📋 Available Templates:")
        for name, template in self.templates.items():
            size = template["size"]
            fmt = template.get("format", "png")
            quality = template.get("quality", "")
            quality_str = f" (quality {quality})" if quality else ""

            print(f"  {name:10} - {template['description']}")
            print(f"             Size: {size[0]}x{size[1]}, Format: {fmt}{quality_str}")

    def _show_status(self):
        """Show current status."""
        print(f"📊 Current Status:")
        print(
            f"  OpenTiler window: {self.opentiler_window.title if self.opentiler_window else 'Not found'}"
        )
        print(f"  Output directory: {self.output_dir}")
        print(f"  Screenshots captured: {self.capture_count}")

        # Show recent files
        png_files = list(self.output_dir.glob("*.png"))
        jpg_files = list(self.output_dir.glob("*.jpg"))

        if png_files or jpg_files:
            print(f"  Recent files:")
            all_files = sorted(
                png_files + jpg_files, key=lambda x: x.stat().st_mtime, reverse=True
            )
            for file in all_files[:5]:
                size_kb = file.stat().st_size / 1024
                print(f"    {file.name} ({size_kb:.1f} KB)")

    def _list_windows(self):
        """List all available windows."""
        windows = self.capture.list_windows()
        print(f"📋 Available Windows ({len(windows)} total):")

        for i, window in enumerate(windows, 1):
            marker = "⭐" if window == self.opentiler_window else "  "
            print(f"{marker} {i:2d}. {window.title}")
            print(
                f"      Size: {window.width}x{window.height}, Position: ({window.left}, {window.top})"
            )

    def _handle_capture_command(self, cmd: str):
        """Handle capture command."""
        parts = cmd.split(" ", 2)
        if len(parts) < 2:
            print("❌ Usage: capture <name> [description]")
            return

        name = parts[1]
        description = parts[2] if len(parts) > 2 else f"Screenshot {name}"

        success = self._capture_screenshot(name, description)
        if success:
            self.capture_count += 1
            print(f"✅ Captured: {name}.png")
        else:
            print(f"❌ Failed to capture: {name}")

    def _handle_template_command(self, cmd: str):
        """Handle template command."""
        parts = cmd.split(" ", 1)
        if len(parts) < 2:
            print("❌ Usage: template <template_name>")
            self._show_templates()
            return

        template_name = parts[1]
        if template_name not in self.templates:
            print(f"❌ Unknown template: {template_name}")
            self._show_templates()
            return

        template = self.templates[template_name]
        success = self._capture_with_template(template)

        if success:
            self.capture_count += 1
            print(f"✅ Captured using template '{template_name}': {template['name']}")
        else:
            print(f"❌ Failed to capture with template: {template_name}")

    def _handle_quick_command(self, cmd: str):
        """Handle quick capture command."""
        parts = cmd.split(" ", 1)
        if len(parts) < 2:
            print("❌ Usage: quick <name>")
            return

        name = parts[1]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        full_name = f"opentiler-{name}-{timestamp}"

        success = self._capture_screenshot(full_name, f"Quick capture: {name}")
        if success:
            self.capture_count += 1
            print(f"✅ Quick captured: {full_name}.png")
        else:
            print(f"❌ Failed quick capture: {name}")

    def _capture_screenshot(
        self,
        name: str,
        description: str,
        size: tuple = (1600, 1000),
        format_type: str = "png",
        quality: int = 95,
    ) -> bool:
        """Capture screenshot with specified parameters."""
        try:
            if not self.opentiler_window:
                if not self._find_opentiler_window():
                    print("❌ OpenTiler window not found")
                    return False

            # Activate window
            self.opentiler_window.activate()
            time.sleep(0.5)

            # Capture screenshot
            output_path = self.output_dir / f"{name}.{format_type}"
            success = self.capture.capture_window(
                self.opentiler_window,
                str(output_path),
                target_size=size,
                format_type=format_type,
                quality=quality,
            )

            if success:
                file_size = output_path.stat().st_size / 1024
                print(f"   📄 Saved: {output_path.name} ({file_size:.1f} KB)")
                print(f"   📝 Description: {description}")

            return success

        except Exception as e:
            print(f"❌ Capture error: {e}")
            return False

    def _capture_with_template(self, template: Dict) -> bool:
        """Capture screenshot using template."""
        return self._capture_screenshot(
            name=template["name"],
            description=template["description"],
            size=template["size"],
            format_type=template.get("format", "png"),
            quality=template.get("quality", 95),
        )


def batch_capture_mode(output_dir: str):
    """Batch capture mode for predefined screenshots."""
    print("📸 Batch OpenTiler Screenshot Capture")
    print("=" * 40)

    capturer = ManualOpenTilerCapture(output_dir)

    if not capturer._find_opentiler_window():
        print("❌ OpenTiler not running!")
        return False

    print(f"✅ Found OpenTiler: {capturer.opentiler_window.title}")
    print()

    # Predefined batch captures
    batch_captures = [
        ("main", "Main interface ready"),
        ("hero", "Hero image for README"),
        ("document", "Document loaded and visible"),
        ("toolbar", "Toolbar clearly visible"),
        ("preview", "Preview panel showing tiles"),
    ]

    for template_name, instruction in batch_captures:
        print(f"📸 Next: {capturer.templates[template_name]['description']}")
        print(f"   📋 Instruction: {instruction}")

        input("   Press Enter when ready...")

        success = capturer._capture_with_template(capturer.templates[template_name])
        if success:
            capturer.capture_count += 1
            print(f"   ✅ Captured: {template_name}")
        else:
            print(f"   ❌ Failed: {template_name}")
        print()

    print(f"🎉 Batch capture complete! Generated {capturer.capture_count} screenshots.")
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Manual OpenTiler screenshot capture tool"
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        default="../../../docs/images",
        help="Output directory for screenshots",
    )

    parser.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Batch capture mode with predefined templates",
    )

    args = parser.parse_args()

    try:
        if args.batch:
            success = batch_capture_mode(args.output_dir)
        else:
            capturer = ManualOpenTilerCapture(args.output_dir)
            success = capturer.start_interactive_session()

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
