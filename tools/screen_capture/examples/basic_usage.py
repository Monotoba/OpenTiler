#!/usr/bin/env python3
"""
Basic Usage Examples for Screen Capture Tool

This file demonstrates basic usage patterns for the screen capture tool.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from screen_capture import ScreenCapture


def example_1_capture_active_window():
    """Example 1: Capture the currently active window."""
    
    print("📸 Example 1: Capture Active Window")
    print("-" * 40)
    
    capture = ScreenCapture()
    
    # Get active window info
    active_window = capture.get_active_window()
    if active_window:
        print(f"Active window: {active_window.title}")
        print(f"Position: ({active_window.left}, {active_window.top})")
        print(f"Size: {active_window.width}x{active_window.height}")
        
        # Capture the window
        success = capture.capture_active_window("active_window.png")
        if success:
            print("✅ Screenshot saved: active_window.png")
        else:
            print("❌ Failed to capture screenshot")
    else:
        print("❌ No active window found")
    
    print()


def example_2_capture_by_title():
    """Example 2: Capture a specific window by title."""
    
    print("📸 Example 2: Capture Window by Title")
    print("-" * 40)
    
    capture = ScreenCapture()
    
    # Try to find a common application
    app_titles = ["Terminal", "Code", "Firefox", "Chrome", "TextEdit", "Notepad"]
    
    for title in app_titles:
        window = capture.find_window_by_title(title)
        if window:
            print(f"Found window: {window.title}")
            
            success = capture.capture_window(
                window, 
                f"{title.lower()}_window.png",
                target_size=(800, 600)  # Resize to standard size
            )
            
            if success:
                print(f"✅ Screenshot saved: {title.lower()}_window.png")
            else:
                print(f"❌ Failed to capture {title}")
            break
    else:
        print("❌ No common applications found")
    
    print()


def example_3_capture_fullscreen():
    """Example 3: Capture full screen in different formats."""
    
    print("📸 Example 3: Capture Full Screen")
    print("-" * 40)
    
    capture = ScreenCapture()
    
    # Capture in different formats
    formats = [
        {"format": "png", "quality": 95, "desc": "High quality PNG"},
        {"format": "jpeg", "quality": 85, "desc": "Compressed JPEG"},
        {"format": "webp", "quality": 80, "desc": "Modern WebP"}
    ]
    
    for fmt in formats:
        filename = f"fullscreen.{fmt['format']}"
        print(f"Capturing {fmt['desc']}...")
        
        success = capture.capture_fullscreen(
            filename,
            format_type=fmt["format"],
            quality=fmt["quality"]
        )
        
        if success:
            # Get file size
            file_size = Path(filename).stat().st_size / 1024  # KB
            print(f"✅ Saved: {filename} ({file_size:.1f} KB)")
        else:
            print(f"❌ Failed: {filename}")
    
    print()


def example_4_list_and_choose():
    """Example 4: List windows and let user choose."""
    
    print("📸 Example 4: Interactive Window Selection")
    print("-" * 40)
    
    capture = ScreenCapture()
    
    # List all windows
    windows = capture.list_windows()
    
    if not windows:
        print("❌ No windows found")
        return
    
    print(f"Found {len(windows)} windows:")
    for i, window in enumerate(windows[:10], 1):  # Show first 10
        print(f"  {i:2d}. {window.title}")
        print(f"      Size: {window.width}x{window.height}")
    
    # For demo, capture the first window
    if windows:
        first_window = windows[0]
        print(f"\nCapturing first window: {first_window.title}")
        
        success = capture.capture_window(
            first_window,
            "selected_window.png"
        )
        
        if success:
            print("✅ Screenshot saved: selected_window.png")
        else:
            print("❌ Failed to capture screenshot")
    
    print()


def example_5_batch_capture():
    """Example 5: Batch capture multiple windows."""
    
    print("📸 Example 5: Batch Window Capture")
    print("-" * 40)
    
    capture = ScreenCapture()
    
    # Get all windows
    windows = capture.list_windows()
    
    if not windows:
        print("❌ No windows found")
        return
    
    # Capture first few windows
    max_captures = min(3, len(windows))
    successful_captures = 0
    
    for i, window in enumerate(windows[:max_captures]):
        filename = f"batch_capture_{i+1}.png"
        print(f"Capturing: {window.title}")
        
        success = capture.capture_window(
            window,
            filename,
            target_size=(640, 480)  # Thumbnail size
        )
        
        if success:
            successful_captures += 1
            print(f"  ✅ Saved: {filename}")
        else:
            print(f"  ❌ Failed: {filename}")
    
    print(f"\nBatch capture complete: {successful_captures}/{max_captures} successful")
    print()


def example_6_error_handling():
    """Example 6: Proper error handling."""
    
    print("📸 Example 6: Error Handling")
    print("-" * 40)
    
    capture = ScreenCapture()
    
    # Try to capture non-existent window
    print("Attempting to capture non-existent window...")
    window = capture.find_window_by_title("NonExistentApplication12345")
    
    if window:
        print("Unexpectedly found the window!")
    else:
        print("✅ Correctly handled non-existent window")
    
    # Try to capture with invalid path
    print("Attempting capture with problematic path...")
    try:
        success = capture.capture_active_window("/invalid/path/test.png")
        if success:
            print("✅ Capture succeeded (path was created)")
        else:
            print("❌ Capture failed as expected")
    except Exception as e:
        print(f"❌ Exception caught: {e}")
    
    print()


def example_7_advanced_options():
    """Example 7: Advanced capture options."""
    
    print("📸 Example 7: Advanced Options")
    print("-" * 40)
    
    capture = ScreenCapture()
    
    # Capture with different quality settings
    active_window = capture.get_active_window()
    
    if active_window:
        print(f"Capturing {active_window.title} with different settings...")
        
        # High quality PNG
        capture.capture_window(
            active_window,
            "high_quality.png",
            target_size=(1920, 1080),
            format_type="png"
        )
        print("✅ High quality PNG saved")
        
        # Compressed JPEG
        capture.capture_window(
            active_window,
            "compressed.jpg",
            target_size=(800, 600),
            format_type="jpeg",
            quality=70
        )
        print("✅ Compressed JPEG saved")
        
        # WebP format
        capture.capture_window(
            active_window,
            "modern.webp",
            target_size=(1200, 800),
            format_type="webp",
            quality=85
        )
        print("✅ WebP format saved")
    else:
        print("❌ No active window for advanced capture")
    
    print()


def main():
    """Run all examples."""
    
    print("🚀 Screen Capture Tool - Basic Usage Examples")
    print("=" * 50)
    print()
    
    try:
        # Run examples
        example_1_capture_active_window()
        example_2_capture_by_title()
        example_3_capture_fullscreen()
        example_4_list_and_choose()
        example_5_batch_capture()
        example_6_error_handling()
        example_7_advanced_options()
        
        print("🎉 All examples completed!")
        print("\nGenerated files:")
        
        # List generated files
        current_dir = Path(".")
        screenshot_files = list(current_dir.glob("*.png")) + \
                          list(current_dir.glob("*.jpg")) + \
                          list(current_dir.glob("*.webp"))
        
        for file in screenshot_files:
            if file.stat().st_size > 0:  # Only list non-empty files
                size_kb = file.stat().st_size / 1024
                print(f"  📄 {file.name} ({size_kb:.1f} KB)")
        
    except KeyboardInterrupt:
        print("\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
