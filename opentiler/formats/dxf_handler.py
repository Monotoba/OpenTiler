"""
DXF format handler for OpenTiler.
Handles import and export of DXF files for CAD integration.
"""

import os
import tempfile
from typing import Optional, Tuple

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QMessageBox

try:
    import ezdxf
    import matplotlib.patches as patches
    import matplotlib.pyplot as plt
    from ezdxf import recover
    from ezdxf.addons.drawing import Frontend, RenderContext
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

    DXF_AVAILABLE = True
except ImportError:
    DXF_AVAILABLE = False


class DXFHandler:
    """Handler for DXF file import and export operations."""

    def __init__(self):
        self.current_doc = None
        self.scale_factor = 1.0

    @staticmethod
    def is_available() -> bool:
        """Check if DXF support is available."""
        return DXF_AVAILABLE

    def load_dxf(self, file_path: str) -> Optional[QPixmap]:
        """
        Load a DXF file and convert it to a QPixmap.

        Args:
            file_path: Path to the DXF file

        Returns:
            QPixmap if successful, None if failed
        """
        if not DXF_AVAILABLE:
            QMessageBox.warning(
                None,
                "DXF Support",
                "DXF support requires 'ezdxf' and 'matplotlib' packages.\n"
                "Install with: pip install ezdxf matplotlib",
            )
            return None

        try:
            # Try to load the DXF file
            try:
                doc = ezdxf.readfile(file_path)
            except ezdxf.DXFStructureError:
                # Try to recover corrupted DXF files
                doc, auditor = recover.readfile(file_path)
                if auditor.has_errors:
                    print(f"DXF file has errors: {len(auditor.errors)} errors found")

            self.current_doc = doc

            # Convert DXF to pixmap
            pixmap = self._dxf_to_pixmap(doc)
            return pixmap

        except Exception as e:
            QMessageBox.critical(
                None, "DXF Load Error", f"Failed to load DXF file:\n{str(e)}"
            )
            return None

    def _dxf_to_pixmap(self, doc, width: int = 2000, height: int = 2000) -> QPixmap:
        """
        Convert DXF document to QPixmap using matplotlib backend.

        Args:
            doc: ezdxf document
            width: Output width in pixels
            height: Output height in pixels

        Returns:
            QPixmap representation of the DXF
        """
        try:
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
            ax.set_aspect("equal")

            # Set up the drawing backend
            backend = MatplotlibBackend(ax)
            Frontend(RenderContext(doc), backend).draw_layout(
                doc.modelspace(), finalize=True
            )

            # Remove axes and margins
            ax.set_xlim(ax.get_xlim())
            ax.set_ylim(ax.get_ylim())
            ax.axis("off")
            plt.tight_layout(pad=0)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                fig.savefig(
                    tmp_file.name,
                    dpi=300,
                    bbox_inches="tight",
                    pad_inches=0,
                    facecolor="white",
                )
                temp_path = tmp_file.name

            plt.close(fig)

            # Load as QPixmap
            pixmap = QPixmap(temp_path)

            # Clean up temporary file
            os.unlink(temp_path)

            return pixmap

        except Exception as e:
            print(f"DXF to pixmap conversion error: {str(e)}")
            return None

    def save_as_dxf(
        self,
        source_pixmap: QPixmap,
        output_path: str,
        scale_factor: float = 1.0,
        units: str = "mm",
    ) -> bool:
        """
        Save the current document as DXF with scale information.

        Args:
            source_pixmap: Source image to convert
            output_path: Output DXF file path
            scale_factor: Scale factor (mm/pixel or inches/pixel)
            units: Units for the DXF file ("mm" or "inches")

        Returns:
            True if successful, False otherwise
        """
        if not DXF_AVAILABLE:
            QMessageBox.warning(
                None,
                "DXF Support",
                "DXF export requires 'ezdxf' package.\n"
                "Install with: pip install ezdxf",
            )
            return False

        try:
            # Create new DXF document
            doc = ezdxf.new("R2010")  # Use AutoCAD 2010 format for compatibility

            # Set units
            if units.lower() == "mm":
                doc.units = ezdxf.units.MM
            else:
                doc.units = ezdxf.units.INCH

            # Get model space
            msp = doc.modelspace()

            # Calculate real-world dimensions
            pixel_width = source_pixmap.width()
            pixel_height = source_pixmap.height()

            real_width = pixel_width * scale_factor
            real_height = pixel_height * scale_factor

            # Create a rectangle representing the document bounds
            # This serves as a reference frame for the scaled document
            msp.add_lwpolyline(
                [
                    (0, 0),
                    (real_width, 0),
                    (real_width, real_height),
                    (0, real_height),
                    (0, 0),
                ],
                close=True,
            )

            # Add text annotation with scale information
            msp.add_text(
                f"Scale: {scale_factor:.6f} {units}/pixel",
                dxfattribs={
                    "height": real_height * 0.02,  # 2% of height
                    "insert": (real_width * 0.02, real_height * 0.98),
                },
            )

            # Add dimension annotations
            msp.add_text(
                f"Width: {real_width:.2f} {units}",
                dxfattribs={
                    "height": real_height * 0.015,
                    "insert": (real_width * 0.02, real_height * 0.94),
                },
            )

            msp.add_text(
                f"Height: {real_height:.2f} {units}",
                dxfattribs={
                    "height": real_height * 0.015,
                    "insert": (real_width * 0.02, real_height * 0.90),
                },
            )

            # Add reference grid (optional)
            grid_spacing = max(real_width, real_height) / 20  # 20 grid lines

            # Vertical grid lines
            for i in range(1, 20):
                x = i * grid_spacing
                if x < real_width:
                    msp.add_line(
                        (x, 0), (x, real_height), dxfattribs={"color": 8}  # Gray color
                    )

            # Horizontal grid lines
            for i in range(1, 20):
                y = i * grid_spacing
                if y < real_height:
                    msp.add_line(
                        (0, y), (real_width, y), dxfattribs={"color": 8}  # Gray color
                    )

            # Save the DXF file
            doc.saveas(output_path)
            return True

        except Exception as e:
            QMessageBox.critical(
                None, "DXF Export Error", f"Failed to export DXF file:\n{str(e)}"
            )
            return False

    def get_dxf_info(self, file_path: str) -> dict:
        """
        Get information about a DXF file.

        Args:
            file_path: Path to the DXF file

        Returns:
            Dictionary with DXF file information
        """
        if not DXF_AVAILABLE:
            return {}

        try:
            doc = ezdxf.readfile(file_path)

            # Get document info
            info = {
                "version": doc.dxfversion,
                "units": str(doc.units),
                "layers": len(doc.layers),
                "blocks": len(doc.blocks),
                "entities": 0,
            }

            # Count entities in model space
            msp = doc.modelspace()
            info["entities"] = len(list(msp))

            # Get extents if available
            try:
                extents = msp.get_extents()
                if extents:
                    info["extents"] = {
                        "min_x": extents.extmin.x,
                        "min_y": extents.extmin.y,
                        "max_x": extents.extmax.x,
                        "max_y": extents.extmax.y,
                        "width": extents.extmax.x - extents.extmin.x,
                        "height": extents.extmax.y - extents.extmin.y,
                    }
            except:
                pass

            return info

        except Exception as e:
            return {"error": str(e)}


def install_dxf_support():
    """
    Helper function to install DXF support packages.
    """
    import subprocess
    import sys

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "ezdxf", "matplotlib"]
        )
        return True
    except subprocess.CalledProcessError:
        return False
