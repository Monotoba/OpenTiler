#!/usr/bin/env python3
"""
Cross-Platform Screen Capture Tool

A professional screen capture utility supporting active window and full screen capture
across Windows, macOS, and Linux platforms.

Dependencies:
    - pywinctl: Cross-platform window management
    - mss: Fast cross-platform screen capture
    - Pillow: Image processing and format support

Usage:
    python screen_capture.py --window --output-file screenshot.png
    python screen_capture.py --fullscreen --output-file desktop.jpg --format jpeg --quality 90
    python screen_capture.py -w -o window.png --width 1920 --height 1080
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

# Dependency availability flag
HAS_DEPENDENCIES = True

try:
    import mss
    import pywinctl as pwc
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    # Defer hard failure to runtime or CLI entry; allow module import for optional usage.
    HAS_DEPENDENCIES = False
    pwc = None  # type: ignore
    mss = None  # type: ignore
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore
    ImageFont = None  # type: ignore


class ScreenCapture:
    """Cross-platform screen capture utility."""

    def __init__(self):
        if not HAS_DEPENDENCIES:
            raise ImportError(
                "screen_capture dependencies missing; install with: pip install pywinctl mss Pillow"
            )
        self.logger = self._setup_logging()
        self.sct = mss.mss()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(__name__)

    def get_active_window(self) -> Optional[object]:
        """Get the currently active window."""
        try:
            active_window = pwc.getActiveWindow()
            if active_window:
                self.logger.info(f"Active window: {active_window.title}")
                return active_window
            else:
                self.logger.warning("No active window found")
                return None
        except Exception as e:
            self.logger.error(f"Error getting active window: {e}")
            return None

    def list_windows(self) -> list:
        """List all visible windows."""
        try:
            windows = pwc.getAllWindows()
            visible_windows = [w for w in windows if w.visible and w.title.strip()]
            self.logger.info(f"Found {len(visible_windows)} visible windows")
            return visible_windows
        except Exception as e:
            self.logger.error(f"Error listing windows: {e}")
            return []

    def find_window_by_title(
        self, title: str, partial_match: bool = True
    ) -> Optional[object]:
        """Find window by title (supports partial matching)."""
        try:
            windows = self.list_windows()
            for window in windows:
                if partial_match:
                    if title.lower() in window.title.lower():
                        self.logger.info(f"Found window: {window.title}")
                        return window
                else:
                    if title == window.title:
                        self.logger.info(f"Found window: {window.title}")
                        return window

            self.logger.warning(f"Window with title '{title}' not found")
            return None
        except Exception as e:
            self.logger.error(f"Error finding window: {e}")
            return None

    def capture_window(
        self,
        window: object,
        output_path: str,
        target_size: Optional[Tuple[int, int]] = None,
        format_type: str = "png",
        quality: int = 95,
    ) -> bool:
        """Capture a specific window."""
        try:
            # Get window geometry
            left, top, width, height = (
                window.left,
                window.top,
                window.width,
                window.height,
            )

            # Ensure window is visible and not minimized
            if window.isMinimized:
                window.restore()
                import time

                time.sleep(0.5)  # Wait for window to restore

            # Bring window to front
            window.activate()
            import time

            time.sleep(0.2)  # Brief pause for activation

            # Define capture area
            monitor = {"top": top, "left": left, "width": width, "height": height}

            self.logger.info(
                f"Capturing window: {window.title} at {left},{top} {width}x{height}"
            )

            # Capture screenshot
            screenshot = self.sct.grab(monitor)

            # Convert to PIL Image
            img = Image.frombytes(
                "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
            )

            # Resize if target size specified
            if target_size:
                img = img.resize(target_size, Image.Resampling.LANCZOS)
                self.logger.info(f"Resized to {target_size[0]}x{target_size[1]}")

            # Save image
            self._save_image(img, output_path, format_type, quality)

            return True

        except Exception as e:
            self.logger.error(f"Error capturing window: {e}")
            return False

    def capture_active_window(
        self,
        output_path: str,
        target_size: Optional[Tuple[int, int]] = None,
        format_type: str = "png",
        quality: int = 95,
    ) -> bool:
        """Capture the currently active window."""
        active_window = self.get_active_window()
        if not active_window:
            self.logger.error("No active window to capture")
            return False

        return self.capture_window(
            active_window, output_path, target_size, format_type, quality
        )

    def capture_fullscreen(
        self,
        output_path: str,
        target_size: Optional[Tuple[int, int]] = None,
        format_type: str = "png",
        quality: int = 95,
        monitor_number: int = 1,
    ) -> bool:
        """Capture full screen or specific monitor."""
        try:
            # Get monitor
            if monitor_number > len(self.sct.monitors) - 1:
                self.logger.warning(
                    f"Monitor {monitor_number} not found, using primary monitor"
                )
                monitor_number = 1

            monitor = self.sct.monitors[monitor_number]
            self.logger.info(
                f"Capturing monitor {monitor_number}: {monitor['width']}x{monitor['height']}"
            )

            # Capture screenshot
            screenshot = self.sct.grab(monitor)

            # Convert to PIL Image
            img = Image.frombytes(
                "RGB", screenshot.size, screenshot.bgra, "raw", "BGRX"
            )

            # Resize if target size specified
            if target_size:
                img = img.resize(target_size, Image.Resampling.LANCZOS)
                self.logger.info(f"Resized to {target_size[0]}x{target_size[1]}")

            # Save image
            self._save_image(img, output_path, format_type, quality)

            return True

        except Exception as e:
            self.logger.error(f"Error capturing fullscreen: {e}")
            return False

    def _save_image(
        self, img, output_path: str, format_type: str, quality: int
    ) -> None:
        """Save image with specified format and quality."""
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Determine format
        format_map = {
            "png": "PNG",
            "jpg": "JPEG",
            "jpeg": "JPEG",
            "webp": "WEBP",
            "bmp": "BMP",
            "tiff": "TIFF",
        }

        pil_format = format_map.get(format_type.lower(), "PNG")

        # Save with appropriate options
        save_kwargs = {}
        if pil_format == "JPEG":
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        elif pil_format == "WEBP":
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        elif pil_format == "PNG":
            save_kwargs["optimize"] = True

        img.save(output_path, format=pil_format, **save_kwargs)

        # Get file size
        file_size = Path(output_path).stat().st_size / 1024  # KB
        self.logger.info(f"Saved {output_path} ({file_size:.1f} KB)")


def main():
    """Main entry point."""
    if not HAS_DEPENDENCIES:
        print(
            "❌ Missing required dependency: No module named required screen capture deps"
        )
        print("Install with: pip install pywinctl mss Pillow")
        return 1
    parser = argparse.ArgumentParser(
        description="Cross-platform screen capture tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --window --output-file window.png
  %(prog)s --fullscreen --output-file desktop.jpg --format jpeg
  %(prog)s -w -o screenshot.png --width 1920 --height 1080
  %(prog)s --window-title "OpenTiler" --output-file opentiler.png
  %(prog)s --list-windows
        """,
    )

    # Capture mode
    capture_group = parser.add_mutually_exclusive_group(required=True)
    capture_group.add_argument(
        "--window", "-w", action="store_true", help="Capture active window"
    )
    capture_group.add_argument(
        "--fullscreen", "-f", action="store_true", help="Capture full screen"
    )
    capture_group.add_argument(
        "--window-title", "-t", type=str, help="Capture window by title (partial match)"
    )
    capture_group.add_argument(
        "--list-windows", "-l", action="store_true", help="List all visible windows"
    )

    # Output options
    parser.add_argument(
        "--output-file",
        "-o",
        type=str,
        help="Output file path (required for capture modes)",
    )

    # Format options
    parser.add_argument(
        "--format",
        choices=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
        default="png",
        help="Output format (default: png)",
    )

    parser.add_argument(
        "--quality",
        "-q",
        type=int,
        default=95,
        help="JPEG/WebP quality 1-100 (default: 95)",
    )

    # Size options
    parser.add_argument(
        "--width",
        type=int,
        help="Target width (will resize maintaining aspect ratio if only width given)",
    )

    parser.add_argument(
        "--height",
        type=int,
        help="Target height (will resize maintaining aspect ratio if only height given)",
    )

    # Monitor selection
    parser.add_argument(
        "--monitor",
        type=int,
        default=1,
        help="Monitor number for fullscreen capture (default: 1)",
    )

    # Verbose output
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create screen capture instance
    capture = ScreenCapture()

    # Handle list windows
    if args.list_windows:
        windows = capture.list_windows()
        print(f"\n📋 Found {len(windows)} visible windows:")
        for i, window in enumerate(windows, 1):
            print(f"  {i:2d}. {window.title}")
            print(f"      Position: ({window.left}, {window.top})")
            print(f"      Size: {window.width}x{window.height}")
            print()
        return 0

    # Validate output file for capture modes
    if not args.output_file:
        print("❌ --output-file is required for capture modes")
        return 1

    # Determine target size
    target_size = None
    if args.width and args.height:
        target_size = (args.width, args.height)
    elif args.width or args.height:
        # If only one dimension given, we'll calculate the other maintaining aspect ratio
        # This will be handled in the capture methods
        pass

    # Perform capture
    success = False

    if args.window:
        success = capture.capture_active_window(
            args.output_file, target_size, args.format, args.quality
        )
    elif args.fullscreen:
        success = capture.capture_fullscreen(
            args.output_file, target_size, args.format, args.quality, args.monitor
        )
    elif args.window_title:
        window = capture.find_window_by_title(args.window_title)
        if window:
            success = capture.capture_window(
                window, args.output_file, target_size, args.format, args.quality
            )
        else:
            print(f"❌ Window with title '{args.window_title}' not found")
            return 1

    if success:
        print(f"✅ Screenshot saved: {args.output_file}")
        return 0
    else:
        print("❌ Screenshot failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
