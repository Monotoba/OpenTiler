# Integration Guide

This guide shows how to integrate the Screen Capture Tool into various workflows, applications, and CI/CD pipelines.

## 🔧 Python Integration

### Basic Integration

```python
from screen_capture import ScreenCapture
import time

def basic_screenshot_workflow():
    """Basic screenshot capture workflow."""
    capture = ScreenCapture()
    
    # Capture active window
    success = capture.capture_active_window("active_window.png")
    if success:
        print("✅ Active window captured")
    
    # Capture specific application
    window = capture.find_window_by_title("OpenTiler")
    if window:
        capture.capture_window(window, "opentiler.png")
        print("✅ OpenTiler window captured")
    
    # Capture full screen
    capture.capture_fullscreen("desktop.png")
    print("✅ Desktop captured")
```

### Advanced Integration

```python
import subprocess
import time
from pathlib import Path
from screen_capture import ScreenCapture

class DocumentationScreenshots:
    """Automated documentation screenshot generator."""
    
    def __init__(self, output_dir: str = "docs/images"):
        self.capture = ScreenCapture()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def launch_app_and_capture(self, app_command: list, app_title: str, 
                              screenshots: list, startup_delay: float = 3.0):
        """Launch application and capture screenshots."""
        
        # Launch application
        process = subprocess.Popen(app_command)
        
        try:
            # Wait for application to start
            time.sleep(startup_delay)
            
            # Capture screenshots
            for screenshot in screenshots:
                self._capture_screenshot(app_title, screenshot)
                
        finally:
            # Clean up
            process.terminate()
            process.wait(timeout=5)
    
    def _capture_screenshot(self, app_title: str, screenshot_config: dict):
        """Capture individual screenshot."""
        
        # Find application window
        window = self.capture.find_window_by_title(app_title)
        if not window:
            print(f"❌ Window '{app_title}' not found")
            return False
        
        # Prepare output path
        output_path = self.output_dir / screenshot_config['filename']
        
        # Capture with specified settings
        success = self.capture.capture_window(
            window,
            str(output_path),
            target_size=screenshot_config.get('size'),
            format_type=screenshot_config.get('format', 'png'),
            quality=screenshot_config.get('quality', 95)
        )
        
        if success:
            print(f"✅ Captured: {output_path}")
        else:
            print(f"❌ Failed to capture: {output_path}")
        
        return success

# Usage example
def generate_opentiler_screenshots():
    """Generate OpenTiler documentation screenshots."""
    
    doc_gen = DocumentationScreenshots("docs/images/screenshots")
    
    screenshots = [
        {
            'filename': 'main-interface.png',
            'size': (1920, 1080),
            'format': 'png'
        },
        {
            'filename': 'main-interface-thumb.jpg', 
            'size': (800, 600),
            'format': 'jpeg',
            'quality': 85
        }
    ]
    
    doc_gen.launch_app_and_capture(
        app_command=['python', 'main.py'],
        app_title='OpenTiler',
        screenshots=screenshots,
        startup_delay=5.0
    )
```

## 🚀 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/screenshots.yml
name: Generate Screenshots

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  screenshots:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r tools/screen_capture/requirements.txt
    
    - name: Set up virtual display
      run: |
        sudo apt-get update
        sudo apt-get install -y xvfb
        export DISPLAY=:99
        Xvfb :99 -screen 0 1920x1080x24 &
    
    - name: Generate screenshots
      run: |
        export DISPLAY=:99
        python tools/generate_screenshots.py
    
    - name: Upload screenshots
      uses: actions/upload-artifact@v3
      with:
        name: screenshots
        path: docs/images/screenshots/
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - screenshots

generate_screenshots:
  stage: screenshots
  image: python:3.10
  
  before_script:
    - apt-get update -qq
    - apt-get install -y xvfb
    - pip install -r requirements.txt
    - pip install -r tools/screen_capture/requirements.txt
  
  script:
    - export DISPLAY=:99
    - Xvfb :99 -screen 0 1920x1080x24 &
    - sleep 2
    - python tools/generate_screenshots.py
  
  artifacts:
    paths:
      - docs/images/screenshots/
    expire_in: 1 week
  
  only:
    - main
```

### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pip install -r tools/screen_capture/requirements.txt'
            }
        }
        
        stage('Generate Screenshots') {
            steps {
                sh '''
                    export DISPLAY=:99
                    Xvfb :99 -screen 0 1920x1080x24 &
                    sleep 2
                    python tools/generate_screenshots.py
                '''
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'docs/images/screenshots/*', fingerprint: true
            }
        }
    }
}
```

## 📱 Application Integration

### Desktop Application Integration

```python
import tkinter as tk
from tkinter import filedialog, messagebox
from screen_capture import ScreenCapture

class ScreenshotApp:
    """Simple GUI application with screenshot integration."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Screenshot Tool")
        self.capture = ScreenCapture()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        
        # Buttons
        tk.Button(self.root, text="Capture Active Window", 
                 command=self.capture_active).pack(pady=5)
        
        tk.Button(self.root, text="Capture Full Screen", 
                 command=self.capture_fullscreen).pack(pady=5)
        
        tk.Button(self.root, text="List Windows", 
                 command=self.list_windows).pack(pady=5)
    
    def capture_active(self):
        """Capture active window with file dialog."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )
        
        if filename:
            success = self.capture.capture_active_window(filename)
            if success:
                messagebox.showinfo("Success", f"Screenshot saved: {filename}")
            else:
                messagebox.showerror("Error", "Failed to capture screenshot")
    
    def capture_fullscreen(self):
        """Capture full screen with file dialog."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")]
        )
        
        if filename:
            success = self.capture.capture_fullscreen(filename)
            if success:
                messagebox.showinfo("Success", f"Screenshot saved: {filename}")
            else:
                messagebox.showerror("Error", "Failed to capture screenshot")
    
    def list_windows(self):
        """Show list of available windows."""
        windows = self.capture.list_windows()
        window_list = "\n".join([f"• {w.title}" for w in windows[:10]])
        messagebox.showinfo("Available Windows", window_list)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

# Usage
if __name__ == "__main__":
    app = ScreenshotApp()
    app.run()
```

### Web Application Integration

```python
from flask import Flask, request, jsonify, send_file
from screen_capture import ScreenCapture
import tempfile
import os

app = Flask(__name__)
capture = ScreenCapture()

@app.route('/api/screenshot/active', methods=['POST'])
def capture_active_window():
    """API endpoint to capture active window."""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        temp_path = tmp.name
    
    try:
        # Capture screenshot
        success = capture.capture_active_window(temp_path)
        
        if success:
            return send_file(temp_path, as_attachment=True, 
                           download_name='active_window.png')
        else:
            return jsonify({'error': 'Failed to capture screenshot'}), 500
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@app.route('/api/screenshot/window/<title>', methods=['POST'])
def capture_window_by_title(title):
    """API endpoint to capture window by title."""
    
    window = capture.find_window_by_title(title)
    if not window:
        return jsonify({'error': f'Window "{title}" not found'}), 404
    
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        temp_path = tmp.name
    
    try:
        success = capture.capture_window(window, temp_path)
        
        if success:
            return send_file(temp_path, as_attachment=True,
                           download_name=f'{title}.png')
        else:
            return jsonify({'error': 'Failed to capture screenshot'}), 500
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@app.route('/api/windows', methods=['GET'])
def list_windows():
    """API endpoint to list available windows."""
    
    windows = capture.list_windows()
    window_data = [
        {
            'title': w.title,
            'position': {'x': w.left, 'y': w.top},
            'size': {'width': w.width, 'height': w.height}
        }
        for w in windows
    ]
    
    return jsonify({'windows': window_data})

if __name__ == '__main__':
    app.run(debug=True)
```

## 🔄 Automated Workflows

### Documentation Generation

```python
#!/usr/bin/env python3
"""
Automated documentation screenshot generator for OpenTiler.
"""

import subprocess
import time
import json
from pathlib import Path
from screen_capture import ScreenCapture

class OpenTilerDocumentationGenerator:
    """Generate comprehensive OpenTiler documentation screenshots."""
    
    def __init__(self):
        self.capture = ScreenCapture()
        self.output_dir = Path("docs/images/screenshots")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Screenshot configuration
        self.screenshots = {
            'main-interface': {
                'filename': 'main-interface.png',
                'description': 'Main OpenTiler interface',
                'size': (1920, 1080)
            },
            'main-interface-thumb': {
                'filename': 'main-interface-thumb.jpg',
                'description': 'Main interface thumbnail',
                'size': (800, 600),
                'format': 'jpeg',
                'quality': 85
            },
            'file-dialog': {
                'filename': 'file-dialog.png', 
                'description': 'File open dialog',
                'trigger': 'file_open'
            },
            'scale-dialog': {
                'filename': 'scale-dialog.png',
                'description': 'Scale measurement dialog',
                'trigger': 'scale_tool'
            },
            'export-dialog': {
                'filename': 'export-dialog.png',
                'description': 'Export configuration dialog',
                'trigger': 'export'
            },
            'settings-dialog': {
                'filename': 'settings-dialog.png',
                'description': 'Application settings',
                'trigger': 'settings'
            }
        }
    
    def generate_all_screenshots(self):
        """Generate all documentation screenshots."""
        
        print("🚀 Starting OpenTiler documentation screenshot generation...")
        
        # Launch OpenTiler
        process = self._launch_opentiler()
        
        try:
            # Wait for application startup
            time.sleep(5)
            
            # Generate screenshots
            results = {}
            for name, config in self.screenshots.items():
                print(f"📸 Capturing: {config['description']}")
                success = self._capture_screenshot(name, config)
                results[name] = success
            
            # Generate summary
            self._generate_summary(results)
            
        finally:
            # Clean up
            self._cleanup_opentiler(process)
    
    def _launch_opentiler(self):
        """Launch OpenTiler application."""
        print("🔧 Launching OpenTiler...")
        return subprocess.Popen(['python', 'main.py'])
    
    def _capture_screenshot(self, name: str, config: dict) -> bool:
        """Capture individual screenshot."""
        
        # Handle dialog triggers
        if 'trigger' in config:
            self._trigger_dialog(config['trigger'])
            time.sleep(1)  # Wait for dialog to open
        
        # Find OpenTiler window
        window = self.capture.find_window_by_title("OpenTiler")
        if not window:
            print(f"❌ OpenTiler window not found for {name}")
            return False
        
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
        
        if success:
            print(f"  ✅ Saved: {output_path}")
        else:
            print(f"  ❌ Failed: {output_path}")
        
        return success
    
    def _trigger_dialog(self, trigger: str):
        """Trigger specific dialogs (placeholder for actual implementation)."""
        # This would need to be implemented based on OpenTiler's API
        # or through GUI automation
        print(f"  🔧 Triggering: {trigger}")
        pass
    
    def _cleanup_opentiler(self, process):
        """Clean up OpenTiler process."""
        print("🧹 Cleaning up...")
        process.terminate()
        process.wait(timeout=10)
    
    def _generate_summary(self, results: dict):
        """Generate summary of screenshot generation."""
        
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        print(f"\n📊 Screenshot Generation Summary:")
        print(f"   ✅ Successful: {successful}/{total}")
        print(f"   📁 Output directory: {self.output_dir}")
        
        # Save metadata
        metadata = {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_screenshots': total,
            'successful_screenshots': successful,
            'results': results,
            'screenshots': self.screenshots
        }
        
        metadata_path = self.output_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   📄 Metadata saved: {metadata_path}")

if __name__ == "__main__":
    generator = OpenTilerDocumentationGenerator()
    generator.generate_all_screenshots()
```

### Testing Integration

```python
import unittest
import tempfile
import os
from screen_capture import ScreenCapture

class TestScreenCaptureIntegration(unittest.TestCase):
    """Integration tests for screen capture functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.capture = ScreenCapture()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_active_window_capture(self):
        """Test active window capture."""
        output_path = os.path.join(self.temp_dir, "test_active.png")
        success = self.capture.capture_active_window(output_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)
    
    def test_fullscreen_capture(self):
        """Test fullscreen capture."""
        output_path = os.path.join(self.temp_dir, "test_fullscreen.png")
        success = self.capture.capture_fullscreen(output_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        self.assertGreater(os.path.getsize(output_path), 0)
    
    def test_window_listing(self):
        """Test window listing functionality."""
        windows = self.capture.list_windows()
        
        self.assertIsInstance(windows, list)
        self.assertGreater(len(windows), 0)
        
        # Check window properties
        for window in windows[:3]:  # Test first 3 windows
            self.assertTrue(hasattr(window, 'title'))
            self.assertTrue(hasattr(window, 'left'))
            self.assertTrue(hasattr(window, 'top'))
            self.assertTrue(hasattr(window, 'width'))
            self.assertTrue(hasattr(window, 'height'))

if __name__ == '__main__':
    unittest.main()
```

## 🎯 Best Practices

### Error Handling
```python
def robust_screenshot_capture(title, output_path, retries=3):
    """Robust screenshot capture with retries."""
    
    capture = ScreenCapture()
    
    for attempt in range(retries):
        try:
            window = capture.find_window_by_title(title)
            if not window:
                print(f"Attempt {attempt + 1}: Window '{title}' not found")
                time.sleep(1)
                continue
            
            success = capture.capture_window(window, output_path)
            if success:
                return True
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)
    
    return False
```

### Performance Optimization
```python
def batch_screenshot_capture(window_configs):
    """Optimized batch screenshot capture."""
    
    capture = ScreenCapture()
    
    # Get all windows once
    all_windows = {w.title: w for w in capture.list_windows()}
    
    results = []
    for config in window_configs:
        window = all_windows.get(config['title'])
        if window:
            success = capture.capture_window(
                window, 
                config['output_path'],
                target_size=config.get('size'),
                format_type=config.get('format', 'png')
            )
            results.append({'config': config, 'success': success})
        else:
            results.append({'config': config, 'success': False})
    
    return results
```
