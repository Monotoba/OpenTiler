"""
Metadata page generator for OpenTiler exports.
"""

import os
from datetime import datetime
from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QPen, QBrush
from PySide6.QtCore import Qt


class MetadataPageGenerator:
    """Generates metadata summary pages for tile exports."""

    def __init__(self):
        self.page_size = QSize(2480, 4200)  # Extended A4 at 300 DPI for plan view
        self.margin = 100  # Margin in pixels

    def generate_metadata_page(self, document_info: dict, page_size: QSize = None) -> QPixmap:
        """
        Generate a metadata summary page.

        Args:
            document_info: Dictionary containing document metadata
            page_size: Size of the page in pixels (defaults to A4 at 300 DPI)

        Returns:
            QPixmap containing the metadata page
        """
        if page_size:
            self.page_size = page_size

        # Create pixmap
        pixmap = QPixmap(self.page_size)
        pixmap.fill(QColor(255, 255, 255))  # White background

        # Create painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the metadata page
        self._draw_header(painter, document_info)
        self._draw_document_info(painter, document_info)
        self._draw_scale_info(painter, document_info)
        self._draw_tiling_info(painter, document_info)
        self._draw_export_info(painter, document_info)
        self._draw_plan_view(painter, document_info)
        self._draw_footer(painter, document_info)

        painter.end()
        return pixmap

    def _draw_header(self, painter: QPainter, info: dict):
        """Draw the page header."""
        # Title
        title_font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor(0, 0, 0))

        title_rect = painter.fontMetrics().boundingRect("OpenTiler - Tile Export Metadata")
        x = (self.page_size.width() - title_rect.width()) // 2
        y = self.margin + title_rect.height()

        painter.drawText(x, y, "OpenTiler - Tile Export Metadata")

        # Subtitle
        subtitle_font = QFont("Arial", 14)
        painter.setFont(subtitle_font)
        painter.setPen(QColor(100, 100, 100))

        subtitle = f"Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}"
        subtitle_rect = painter.fontMetrics().boundingRect(subtitle)
        x = (self.page_size.width() - subtitle_rect.width()) // 2
        y += 40

        painter.drawText(x, y, subtitle)

        # Draw separator line
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        y += 30
        painter.drawLine(self.margin, y, self.page_size.width() - self.margin, y)

    def _draw_document_info(self, painter: QPainter, info: dict):
        """Draw document information section."""
        y = self.margin + 150

        # Section header
        self._draw_section_header(painter, "Document Information", y)
        y += 50

        # Document details
        details = [
            ("Document Name:", info.get('document_name', 'Unknown')),
            ("Original File:", info.get('original_file', 'Unknown')),
            ("File Size:", info.get('file_size', 'Unknown')),
            ("Document Dimensions:", f"{info.get('doc_width', 0)} x {info.get('doc_height', 0)} pixels"),
            ("Real-world Size:", f"{info.get('real_width', 0):.2f} x {info.get('real_height', 0):.2f} {info.get('units', 'mm')}"),
        ]

        y = self._draw_details_list(painter, details, y)

    def _draw_scale_info(self, painter: QPainter, info: dict):
        """Draw scaling information section."""
        y = self.margin + 350

        # Section header
        self._draw_section_header(painter, "Scale Information", y)
        y += 50

        # Scale details
        scale_factor = info.get('scale_factor', 1.0)
        units = info.get('units', 'mm')

        details = [
            ("Scale Factor:", f"{scale_factor:.6f} {units}/pixel"),
            ("Units:", units),
            ("Scale Ratio:", self._calculate_scale_ratio(scale_factor, units)),
            ("Measurement Accuracy:", "±0.1mm (depending on print quality)"),
        ]

        y = self._draw_details_list(painter, details, y)

    def _draw_tiling_info(self, painter: QPainter, info: dict):
        """Draw tiling information section."""
        y = self.margin + 550

        # Section header
        self._draw_section_header(painter, "Tiling Information", y)
        y += 50

        # Tiling details
        details = [
            ("Total Tiles:", str(info.get('total_tiles', 0))),
            ("Tile Arrangement:", f"{info.get('tiles_x', 0)} x {info.get('tiles_y', 0)}"),
            ("Page Size:", info.get('page_size', 'A4')),
            ("Page Orientation:", info.get('page_orientation', 'auto')),
            ("Gutter Size:", f"{info.get('gutter_size', 10.0)} mm"),
            ("Overlap Area:", f"{info.get('gutter_size', 10.0) * 2} mm between adjacent tiles"),
        ]

        y = self._draw_details_list(painter, details, y)

    def _draw_export_info(self, painter: QPainter, info: dict):
        """Draw export information section."""
        y = self.margin + 750

        # Section header
        self._draw_section_header(painter, "Export Information", y)
        y += 50

        # Export details
        details = [
            ("Export Format:", info.get('export_format', 'PDF')),
            ("DPI:", f"{info.get('dpi', 300)} dpi"),
            ("Export Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            ("OpenTiler Version:", info.get('version', '1.0')),
            ("Output Directory:", info.get('output_dir', 'Unknown')),
        ]

        y = self._draw_details_list(painter, details, y)

    def _draw_plan_view(self, painter: QPainter, info: dict):
        """Draw a scaled-down plan view with page layout overlay."""
        y = self.margin + 950

        # Section header
        self._draw_section_header(painter, "Page Assembly Map", y)
        y += 50

        # Get source pixmap and page grid from document info
        source_pixmap = info.get('source_pixmap')
        page_grid = info.get('page_grid', [])

        if not source_pixmap or not page_grid:
            # Draw placeholder text if no plan view available
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(self.margin, y + 20, "Plan view not available for preview")
            return

        # Calculate available space for plan view
        available_width = self.page_size.width() - (2 * self.margin)
        available_height = 300  # Fixed height for plan view section

        # Calculate the total area covered by all pages
        if page_grid:
            min_x = min(page['x'] for page in page_grid)
            max_x = max(page['x'] + page['width'] for page in page_grid)
            min_y = min(page['y'] for page in page_grid)
            max_y = max(page['y'] + page['height'] for page in page_grid)

            total_width = max_x - min_x
            total_height = max_y - min_y
        else:
            total_width = source_pixmap.width()
            total_height = source_pixmap.height()
            min_x = min_y = 0

        # Calculate scale factor to fit in available space
        scale_x = available_width / total_width if total_width > 0 else 1.0
        scale_y = available_height / total_height if total_height > 0 else 1.0
        scale_factor = min(scale_x, scale_y, 1.0)  # Don't scale up

        # Calculate scaled dimensions
        scaled_width = int(total_width * scale_factor)
        scaled_height = int(total_height * scale_factor)

        # Center the plan view horizontally
        plan_x = self.margin + (available_width - scaled_width) // 2
        plan_y = y

        # Create a composite image showing the document with page overlays
        composite = self._create_plan_view_composite(source_pixmap, page_grid, total_width, total_height, min_x, min_y)

        if composite and not composite.isNull():
            # Scale the composite to fit
            scaled_composite = composite.scaled(
                scaled_width, scaled_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Draw the scaled plan view
            painter.drawPixmap(plan_x, plan_y, scaled_composite)

            # Draw border around plan view
            painter.setPen(QPen(QColor(100, 100, 100), 1))
            painter.drawRect(plan_x, plan_y, scaled_composite.width(), scaled_composite.height())

            # Add legend below the plan view
            legend_y = plan_y + scaled_composite.height() + 20
            self._draw_plan_view_legend(painter, legend_y)

    def _create_plan_view_composite(self, source_pixmap, page_grid, total_width, total_height, offset_x, offset_y):
        """Create a composite image showing the document with page boundaries."""
        # Create canvas for the composite
        composite = QPixmap(int(total_width), int(total_height))
        composite.fill(QColor(240, 240, 240))  # Light gray background

        painter = QPainter(composite)

        # Draw the source document, positioned relative to the page grid
        doc_x = -offset_x
        doc_y = -offset_y
        painter.drawPixmap(int(doc_x), int(doc_y), source_pixmap)

        # Draw page boundaries and numbers
        for i, page in enumerate(page_grid):
            page_x = page['x'] - offset_x
            page_y = page['y'] - offset_y
            page_width = page['width']
            page_height = page['height']
            gutter = page.get('gutter', 0)

            # Draw page boundary (red)
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawRect(int(page_x), int(page_y), int(page_width), int(page_height))

            # Draw gutter boundary (blue) if gutter exists
            if gutter > 1:
                painter.setPen(QPen(QColor(0, 100, 255), 1))
                gutter_x = page_x + gutter
                gutter_y = page_y + gutter
                gutter_width = page_width - (2 * gutter)
                gutter_height = page_height - (2 * gutter)

                if gutter_width > 0 and gutter_height > 0:
                    painter.drawRect(int(gutter_x), int(gutter_y), int(gutter_width), int(gutter_height))

            # Draw page number
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            font = painter.font()
            font.setPointSize(max(8, int(min(page_width, page_height) / 20)))  # Scale font with page size
            font.setBold(True)
            painter.setFont(font)

            # Calculate text position (center of page)
            text = f"P{i + 1}"
            text_rect = painter.fontMetrics().boundingRect(text)
            text_x = page_x + (page_width - text_rect.width()) / 2
            text_y = page_y + (page_height + text_rect.height()) / 2

            # Draw text background for visibility
            bg_rect = text_rect.adjusted(-3, -1, 3, 1)
            bg_rect.moveCenter(QPoint(int(text_x + text_rect.width()/2), int(text_y - text_rect.height()/2)))
            painter.fillRect(bg_rect, QColor(0, 0, 0, 150))

            # Draw page number
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(int(text_x), int(text_y), text)

        painter.end()
        return composite

    def _draw_plan_view_legend(self, painter: QPainter, y: int):
        """Draw legend for the plan view."""
        legend_font = QFont("Arial", 9)
        painter.setFont(legend_font)

        x = self.margin

        # Red line for page boundaries
        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawLine(x, y, x + 20, y)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(x + 25, y + 5, "Page boundaries (print area)")

        # Blue line for gutter boundaries
        x += 200
        painter.setPen(QPen(QColor(0, 100, 255), 1))
        painter.drawLine(x, y, x + 20, y)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(x + 25, y + 5, "Drawable area (inside gutters)")

        # Page numbers
        x += 220
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(x, y + 5, "P1, P2, etc. = Page numbers for assembly")

    def _draw_footer(self, painter: QPainter, info: dict):
        """Draw page footer."""
        y = self.page_size.height() - self.margin - 80

        # Instructions
        instruction_font = QFont("Arial", 12)
        painter.setFont(instruction_font)
        painter.setPen(QColor(100, 100, 100))

        instructions = [
            "Assembly Instructions:",
            "1. Print all tiles at 100% scale (no scaling in printer settings)",
            "2. Verify scale accuracy by measuring the scale line on each tile",
            "3. Use the Page Assembly Map above to understand tile arrangement",
            "4. Align tiles using the gutter lines and crop marks",
            "5. Overlap tiles in the gutter area for seamless assembly",
            "6. Use the page numbers (P1, P2, etc.) to ensure correct positioning"
        ]

        for instruction in instructions:
            painter.drawText(self.margin, y, instruction)
            y += 20

        # Copyright
        y += 20
        painter.drawText(self.margin, y, "Generated by OpenTiler - © 2024 Randall Morgan")

    def _draw_section_header(self, painter: QPainter, title: str, y: int):
        """Draw a section header."""
        header_font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(header_font)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(self.margin, y, title)

        # Underline
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        text_width = painter.fontMetrics().boundingRect(title).width()
        painter.drawLine(self.margin, y + 5, self.margin + text_width, y + 5)

    def _draw_details_list(self, painter: QPainter, details: list, start_y: int) -> int:
        """Draw a list of detail items."""
        detail_font = QFont("Arial", 11)
        painter.setFont(detail_font)

        y = start_y
        for label, value in details:
            # Draw label
            painter.setPen(QColor(80, 80, 80))
            painter.drawText(self.margin, y, label)

            # Draw value
            painter.setPen(QColor(0, 0, 0))
            label_width = painter.fontMetrics().boundingRect(label).width()
            painter.drawText(self.margin + label_width + 20, y, str(value))

            y += 25

        return y + 20

    def _calculate_scale_ratio(self, scale_factor: float, units: str) -> str:
        """Calculate and format scale ratio."""
        if units == "mm":
            # Convert to common architectural scales
            ratio = 1.0 / scale_factor

            # Common scales
            common_scales = [
                (1, "1:1 (Full Size)"),
                (2, "1:2"),
                (5, "1:5"),
                (10, "1:10"),
                (20, "1:20"),
                (25, "1:25"),
                (50, "1:50"),
                (100, "1:100"),
                (200, "1:200"),
                (500, "1:500"),
                (1000, "1:1000"),
            ]

            # Find closest common scale
            closest_scale = min(common_scales, key=lambda x: abs(x[0] - ratio))

            if abs(closest_scale[0] - ratio) < 0.1:
                return closest_scale[1]
            else:
                return f"1:{ratio:.1f}"
        else:
            # Inches - use different common scales
            ratio = 1.0 / scale_factor
            return f"1:{ratio:.1f}"


def create_document_info(document_name: str, original_file: str, scale_factor: float,
                        units: str, doc_width: int, doc_height: int,
                        tiles_x: int, tiles_y: int, **kwargs) -> dict:
    """
    Create a document info dictionary for metadata page generation.

    Args:
        document_name: Name of the document
        original_file: Original file path
        scale_factor: Scale factor in units/pixel
        units: Units (mm or inches)
        doc_width: Document width in pixels
        doc_height: Document height in pixels
        tiles_x: Number of tiles horizontally
        tiles_y: Number of tiles vertically
        **kwargs: Additional metadata

    Returns:
        Dictionary containing document metadata
    """
    real_width = doc_width * scale_factor
    real_height = doc_height * scale_factor

    info = {
        'document_name': document_name,
        'original_file': os.path.basename(original_file) if original_file else 'Unknown',
        'file_size': _get_file_size_string(original_file) if original_file else 'Unknown',
        'doc_width': doc_width,
        'doc_height': doc_height,
        'real_width': real_width,
        'real_height': real_height,
        'scale_factor': scale_factor,
        'units': units,
        'tiles_x': tiles_x,
        'tiles_y': tiles_y,
        'total_tiles': tiles_x * tiles_y,
        'version': '1.0',
    }

    # Add any additional metadata
    info.update(kwargs)

    return info


def _get_file_size_string(file_path: str) -> str:
    """Get formatted file size string."""
    try:
        size = os.path.getsize(file_path)
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except:
        return "Unknown"
