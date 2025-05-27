"""
FreeCAD format handler for OpenTiler.
Handles import and export of FreeCAD files for CAD integration.
"""

import os
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtWidgets import QMessageBox

# FreeCAD detection variables (will be set lazily)
FREECAD_AVAILABLE = None  # None means not yet checked
FREECAD_COMMAND = None
_FREECAD_DETECTION_DONE = False


def _detect_freecad():
    """Lazy detection of FreeCAD availability."""
    global FREECAD_AVAILABLE, FREECAD_COMMAND, _FREECAD_DETECTION_DONE

    if _FREECAD_DETECTION_DONE:
        return

    _FREECAD_DETECTION_DONE = True
    FREECAD_AVAILABLE = False
    FREECAD_COMMAND = None

    try:
        # Check for different FreeCAD commands
        import shutil
        freecad_commands = ['freecad', 'FreeCAD', '/snap/bin/freecad']

        for cmd in freecad_commands:
            if shutil.which(cmd):
                FREECAD_COMMAND = cmd
                break

        # Try to import FreeCAD Python modules
        try:
            # Common FreeCAD installation paths for Python module
            freecad_paths = [
                '/usr/lib/freecad/lib',
                '/usr/lib/freecad-python3/lib',
                '/snap/freecad/current/usr/lib/freecad/lib',
                '/snap/freecad/current/usr/lib/freecad-python3/lib',
                '/Applications/FreeCAD.app/Contents/Resources/lib',
                'C:\\Program Files\\FreeCAD 0.20\\lib',
                'C:\\Program Files\\FreeCAD 0.21\\lib',
                'C:\\Program Files (x86)\\FreeCAD 0.20\\lib',
                'C:\\Program Files (x86)\\FreeCAD 0.21\\lib'
            ]

            # Try to find and add FreeCAD to path
            for path in freecad_paths:
                if os.path.exists(path):
                    sys.path.append(path)
                    break

            import FreeCAD
            import Part
            import Draft
            import TechDraw
            FREECAD_AVAILABLE = True
        except ImportError:
            # If Python module not available but command exists, we can still use external command
            if FREECAD_COMMAND:
                FREECAD_AVAILABLE = "command_only"
            else:
                FREECAD_AVAILABLE = False

    except Exception as e:
        # Silently fail - don't print errors during normal operation
        FREECAD_AVAILABLE = False


class FreeCADHandler:
    """Handler for FreeCAD file import and export operations."""

    def __init__(self):
        self.current_doc = None
        self.scale_factor = 1.0

    @staticmethod
    def is_available() -> bool:
        """Check if FreeCAD support is available."""
        _detect_freecad()
        return FREECAD_AVAILABLE is not False

    @staticmethod
    def get_availability_status() -> str:
        """Get detailed availability status."""
        _detect_freecad()
        if FREECAD_AVAILABLE is True:
            return "Full Python API available"
        elif FREECAD_AVAILABLE == "command_only":
            return f"Command-line only ({FREECAD_COMMAND})"
        else:
            return "Not available"

    def load_freecad(self, file_path: str) -> Optional[QPixmap]:
        """
        Load a FreeCAD file and convert it to a QPixmap.

        Args:
            file_path: Path to the FreeCAD file (.FCStd)

        Returns:
            QPixmap if successful, None if failed
        """
        _detect_freecad()
        if not FREECAD_AVAILABLE:
            QMessageBox.warning(None, "FreeCAD Support",
                              "FreeCAD support requires FreeCAD to be installed.\n"
                              "Please install FreeCAD and ensure it's in your system PATH.")
            return None

        try:
            if FREECAD_AVAILABLE is True:
                # Use Python API
                doc = FreeCAD.openDocument(file_path)
                self.current_doc = doc
                pixmap = self._freecad_to_pixmap(doc)
                return pixmap
            elif FREECAD_AVAILABLE == "command_only":
                # Use command-line approach
                return self._load_freecad_via_command(file_path)
            else:
                return None

        except Exception as e:
            QMessageBox.critical(None, "FreeCAD Load Error", f"Failed to load FreeCAD file:\n{str(e)}")
            return None

    def _freecad_to_pixmap(self, doc, width: int = 2000, height: int = 2000) -> Optional[QPixmap]:
        """
        Convert FreeCAD document to QPixmap.

        Args:
            doc: FreeCAD document
            width: Output width in pixels
            height: Output height in pixels

        Returns:
            QPixmap representation of the FreeCAD document
        """
        try:
            # Create a TechDraw page for 2D representation
            page = doc.addObject('TechDraw::DrawPage', 'Page')
            template = doc.addObject('TechDraw::DrawSVGTemplate', 'Template')

            # Set up template (A4 size)
            template.Template = os.path.join(
                FreeCAD.getResourceDir(), 'Mod', 'TechDraw', 'Templates', 'A4_Portrait_plain.svg'
            )
            page.Template = template

            # Add views for all visible objects
            for obj in doc.Objects:
                if hasattr(obj, 'ViewObject') and obj.ViewObject.Visibility:
                    if hasattr(obj, 'Shape') and obj.Shape.isValid():
                        # Create a view of the object
                        view = doc.addObject('TechDraw::DrawViewPart', f'View_{obj.Name}')
                        view.Source = [obj]
                        view.Direction = FreeCAD.Vector(0, 0, 1)  # Top view
                        page.addView(view)

            # Recompute the document
            doc.recompute()

            # Export page as SVG
            with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp_file:
                page.exportSvg(tmp_file.name)
                svg_path = tmp_file.name

            # Convert SVG to QPixmap
            pixmap = QPixmap(svg_path)
            if pixmap.isNull():
                # Fallback: create a simple representation
                pixmap = self._create_simple_representation(doc, width, height)

            # Clean up
            os.unlink(svg_path)

            return pixmap

        except Exception as e:
            print(f"FreeCAD to pixmap conversion error: {str(e)}")
            # Fallback to simple representation
            return self._create_simple_representation(doc, width, height)

    def _create_simple_representation(self, doc, width: int, height: int) -> QPixmap:
        """
        Create a simple visual representation of the FreeCAD document.

        Args:
            doc: FreeCAD document
            width: Output width
            height: Output height

        Returns:
            Simple QPixmap representation
        """
        pixmap = QPixmap(width, height)
        pixmap.fill()  # Fill with white

        painter = QPainter(pixmap)
        painter.drawText(50, 50, f"FreeCAD Document: {doc.Name}")
        painter.drawText(50, 80, f"Objects: {len(doc.Objects)}")

        # Draw simple bounding box representation
        if doc.Objects:
            painter.drawRect(100, 100, width-200, height-200)
            painter.drawText(50, height-50, "Simplified representation - use FreeCAD for full view")

        painter.end()
        return pixmap

    def _load_freecad_via_command(self, file_path: str) -> Optional[QPixmap]:
        """
        Load FreeCAD file using command-line interface.

        Args:
            file_path: Path to the FreeCAD file

        Returns:
            QPixmap if successful, None if failed
        """
        try:
            import subprocess

            # Create a temporary Python script for FreeCAD
            script_content = f'''
import FreeCAD
import TechDraw
import os
import tempfile

# Open document
doc = FreeCAD.openDocument("{file_path}")

# Create a TechDraw page for 2D representation
page = doc.addObject('TechDraw::DrawPage', 'Page')
template = doc.addObject('TechDraw::DrawSVGTemplate', 'Template')

# Set up template (A4 size)
template_path = os.path.join(FreeCAD.getResourceDir(), 'Mod', 'TechDraw', 'Templates', 'A4_Portrait_plain.svg')
if os.path.exists(template_path):
    template.Template = template_path
    page.Template = template

# Add views for all visible objects
for obj in doc.Objects:
    if hasattr(obj, 'ViewObject') and obj.ViewObject.Visibility:
        if hasattr(obj, 'Shape') and obj.Shape.isValid():
            view = doc.addObject('TechDraw::DrawViewPart', f'View_{{obj.Name}}')
            view.Source = [obj]
            view.Direction = FreeCAD.Vector(0, 0, 1)
            page.addView(view)

# Recompute
doc.recompute()

# Export as SVG
output_path = "/tmp/freecad_export.svg"
page.exportSvg(output_path)

print(f"EXPORT_PATH:{{output_path}}")

# Close document
FreeCAD.closeDocument(doc.Name)
'''

            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as script_file:
                script_file.write(script_content)
                script_path = script_file.name

            try:
                # Run FreeCAD with the script
                result = subprocess.run([
                    FREECAD_COMMAND, '-c', script_path
                ], capture_output=True, text=True, timeout=30)

                # Look for export path in output
                svg_path = None
                for line in result.stdout.split('\\n'):
                    if line.startswith('EXPORT_PATH:'):
                        svg_path = line.split(':', 1)[1]
                        break

                if svg_path and os.path.exists(svg_path):
                    # Load SVG as QPixmap
                    pixmap = QPixmap(svg_path)

                    # Clean up
                    os.unlink(svg_path)

                    if not pixmap.isNull():
                        return pixmap

                # Fallback: create simple representation
                return self._create_simple_representation_from_file(file_path)

            finally:
                # Clean up script file
                if os.path.exists(script_path):
                    os.unlink(script_path)

        except Exception as e:
            print(f"Command-line FreeCAD load error: {str(e)}")
            return self._create_simple_representation_from_file(file_path)

    def _create_simple_representation_from_file(self, file_path: str, width: int = 800, height: int = 600) -> QPixmap:
        """
        Create a simple visual representation when FreeCAD processing fails.
        """
        pixmap = QPixmap(width, height)
        pixmap.fill()  # Fill with white

        painter = QPainter(pixmap)
        painter.drawText(50, 50, f"FreeCAD Document: {os.path.basename(file_path)}")
        painter.drawText(50, 80, "Limited preview - use FreeCAD for full view")
        painter.drawRect(100, 100, width-200, height-200)
        painter.end()

        return pixmap

    def save_as_freecad(self, source_pixmap: QPixmap, output_path: str,
                       scale_factor: float = 1.0, units: str = "mm") -> bool:
        """
        Save the current document as FreeCAD file with scale information.

        Args:
            source_pixmap: Source image to convert
            output_path: Output FreeCAD file path (.FCStd)
            scale_factor: Scale factor (mm/pixel or inches/pixel)
            units: Units for the FreeCAD file ("mm" or "inches")

        Returns:
            True if successful, False otherwise
        """
        _detect_freecad()
        if not FREECAD_AVAILABLE:
            QMessageBox.warning(None, "FreeCAD Support",
                              "FreeCAD export requires FreeCAD to be installed.\n"
                              "Please install FreeCAD and ensure it's in your system PATH.")
            return False

        try:
            # Create new FreeCAD document
            doc = FreeCAD.newDocument("OpenTilerExport")

            # Set units
            if units.lower() == "mm":
                doc.addObject("App::PropertyLength", "Units").Value = "mm"
            else:
                doc.addObject("App::PropertyLength", "Units").Value = "inch"

            # Calculate real-world dimensions
            pixel_width = source_pixmap.width()
            pixel_height = source_pixmap.height()

            real_width = pixel_width * scale_factor
            real_height = pixel_height * scale_factor

            # Create a rectangle representing the document bounds
            rect_points = [
                FreeCAD.Vector(0, 0, 0),
                FreeCAD.Vector(real_width, 0, 0),
                FreeCAD.Vector(real_width, real_height, 0),
                FreeCAD.Vector(0, real_height, 0),
                FreeCAD.Vector(0, 0, 0)
            ]

            # Create wire from points
            wire = Draft.makeWire(rect_points)
            wire.Label = "Document_Boundary"

            # Add scale information as text
            scale_text = Draft.makeText([f"Scale: {scale_factor:.6f} {units}/pixel"],
                                      FreeCAD.Vector(real_width * 0.02, real_height * 0.98, 0))
            scale_text.Label = "Scale_Info"

            # Add dimension information
            width_text = Draft.makeText([f"Width: {real_width:.2f} {units}"],
                                      FreeCAD.Vector(real_width * 0.02, real_height * 0.94, 0))
            width_text.Label = "Width_Info"

            height_text = Draft.makeText([f"Height: {real_height:.2f} {units}"],
                                       FreeCAD.Vector(real_width * 0.02, real_height * 0.90, 0))
            height_text.Label = "Height_Info"

            # Add reference grid
            grid_spacing = max(real_width, real_height) / 20

            # Create grid lines
            for i in range(1, 20):
                x = i * grid_spacing
                if x < real_width:
                    # Vertical line
                    line = Draft.makeLine(FreeCAD.Vector(x, 0, 0),
                                        FreeCAD.Vector(x, real_height, 0))
                    line.Label = f"Grid_V_{i}"

            for i in range(1, 20):
                y = i * grid_spacing
                if y < real_height:
                    # Horizontal line
                    line = Draft.makeLine(FreeCAD.Vector(0, y, 0),
                                        FreeCAD.Vector(real_width, y, 0))
                    line.Label = f"Grid_H_{i}"

            # Recompute document
            doc.recompute()

            # Save the document
            doc.saveAs(output_path)

            # Close the document
            FreeCAD.closeDocument(doc.Name)

            return True

        except Exception as e:
            QMessageBox.critical(None, "FreeCAD Export Error", f"Failed to export FreeCAD file:\n{str(e)}")
            return False

    def get_freecad_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a FreeCAD file.

        Args:
            file_path: Path to the FreeCAD file

        Returns:
            Dictionary with FreeCAD file information
        """
        _detect_freecad()
        if not FREECAD_AVAILABLE:
            return {}

        try:
            # FreeCAD files are ZIP archives, try to read metadata
            info = {}

            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Read document.xml for basic info
                if 'Document.xml' in zip_file.namelist():
                    xml_content = zip_file.read('Document.xml')
                    root = ET.fromstring(xml_content)

                    info['objects'] = len(root.findall('.//Object'))
                    info['properties'] = len(root.findall('.//Property'))

                # List all files in the archive
                info['files'] = zip_file.namelist()
                info['file_count'] = len(info['files'])

            return info

        except Exception as e:
            return {'error': str(e)}


def install_freecad_support():
    """
    Helper function to provide FreeCAD installation guidance.
    """
    return """
    FreeCAD Installation Guide:

    Windows:
    - Download from https://www.freecadweb.org/downloads.php
    - Install to default location
    - Add FreeCAD/lib to system PATH

    Linux (Ubuntu/Debian):
    - sudo apt install freecad
    - Or use AppImage from website

    macOS:
    - Download DMG from website
    - Install to Applications folder

    After installation, restart OpenTiler to detect FreeCAD.
    """
