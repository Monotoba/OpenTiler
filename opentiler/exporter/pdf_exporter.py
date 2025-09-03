"""
PDF exporter for OpenTiler.
"""

import os
from typing import List, Tuple, Optional
from PySide6.QtCore import QRect, Qt, QMarginsF
from PySide6.QtGui import QPixmap, QPainter, QPdfWriter, QPageSize, QPageLayout, QPen, QColor
from ..utils.overlays import draw_scale_bar
from PySide6.QtWidgets import QMessageBox

from .base_exporter import BaseExporter
from ..utils.metadata_page import MetadataPageGenerator, create_document_info
from ..settings.config import config


class PDFExporter(BaseExporter):
    """Export tiles as multi-page PDF."""

    def __init__(self):
        super().__init__()

    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return ['.pdf']

    def export(self,
               source_pixmap: QPixmap,
               page_grid: List[dict],
               output_path: str,
               page_size: str = "A4",
               **kwargs) -> bool:
        """
        Export tiled document as multi-page PDF or composite single-page PDF.

        Args:
            source_pixmap: Source document pixmap
            page_grid: List of page dictionaries with position and size info
            output_path: Output PDF file path
            page_size: Page size (A4, Letter, etc.)
            **kwargs: Additional export options (composite=True for single-page)

        Returns:
            True if export successful, False otherwise
        """
        # Check if composite export is requested
        if kwargs.get('composite', False):
            return self._export_composite_pdf(source_pixmap, page_grid, output_path, page_size, **kwargs)
        else:
            return self._export_multipage_pdf(source_pixmap, page_grid, output_path, page_size, **kwargs)

    def _export_multipage_pdf(self,
                              source_pixmap: QPixmap,
                              page_grid: List[dict],
                              output_path: str,
                              page_size: str = "A4",
                              **kwargs) -> bool:
        """Export as multi-page PDF (original functionality)."""
        try:
            print(f"PDFExporter: Starting multi-page PDF export")
            print(f"PDFExporter: Output path: {output_path}")
            print(f"PDFExporter: Page size: {page_size}")
            print(f"PDFExporter: Page grid count: {len(page_grid)}")
            print(f"PDFExporter: Source pixmap: {source_pixmap.width()}x{source_pixmap.height()}")
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Create PDF writer
            pdf_writer = QPdfWriter(output_path)

            # Set page size
            if page_size == "A4":
                page_size_obj = QPageSize(QPageSize.A4)
            elif page_size == "Letter":
                page_size_obj = QPageSize(QPageSize.Letter)
            elif page_size == "A3":
                page_size_obj = QPageSize(QPageSize.A3)
            else:
                page_size_obj = QPageSize(QPageSize.A4)  # Default

            pdf_writer.setPageSize(page_size_obj)

            # Determine optimal orientation for tiles
            # Check if we should use landscape or portrait based on tile content
            orientation = self._determine_optimal_orientation(page_grid, page_size_obj)

            # Set page layout with determined orientation
            pdf_writer.setPageLayout(QPageLayout(
                page_size_obj,
                orientation,
                QMarginsF(0, 0, 0, 0),  # Use 0mm margins; gutters are handled in content
                QPageLayout.Millimeter
            ))

            # Set resolution (300 DPI for high quality)
            pdf_writer.setResolution(300)

            # Add metadata
            self.add_default_metadata()
            pdf_writer.setTitle(self.metadata.get('title', 'OpenTiler Export'))
            pdf_writer.setCreator(self.metadata.get('application', 'OpenTiler'))

            # Create painter
            painter = QPainter(pdf_writer)

            # Check if metadata page should be included
            include_metadata = config.get_include_metadata_page()
            metadata_position = config.get_metadata_page_position()

            page_count = 0

            # Add metadata page at the beginning if configured
            if include_metadata and metadata_position == "first":
                self._add_metadata_page(painter, pdf_writer, source_pixmap, page_grid, **kwargs)
                page_count += 1

            # Export each tile page
            for i, page in enumerate(page_grid):
                if page_count > 0:  # Add new page if not the first page
                    pdf_writer.newPage()

                # Create page pixmap
                page_pixmap = self._create_page_pixmap(source_pixmap, page, kwargs.get('scale_factor', 1.0))

                # Draw page to PDF
                if page_pixmap and not page_pixmap.isNull():
                    # Draw into the printable rect to respect margins in mm
                    page_layout = pdf_writer.pageLayout()
                    pdf_rect = page_layout.paintRectPixels(pdf_writer.resolution())
                    painter.drawPixmap(pdf_rect, page_pixmap, page_pixmap.rect())

                page_count += 1

            # Add metadata page at the end if configured
            if include_metadata and metadata_position == "last":
                pdf_writer.newPage()
                self._add_metadata_page(painter, pdf_writer, source_pixmap, page_grid, **kwargs)

            painter.end()
            print(f"PDFExporter: Multi-page PDF export completed successfully")
            return True

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"PDFExporter: Multi-page PDF export error: {str(e)}")
            print(f"PDFExporter: Full traceback: {error_details}")
            return False

    def _create_page_pixmap(self, source_pixmap: QPixmap, page: dict, scale_factor: float = 1.0) -> QPixmap:
        """Create a pixmap for a single page."""
        # Extract page information
        x, y = page['x'], page['y']
        width, height = page['width'], page['height']
        gutter = page.get('gutter', 0)

        # Create blank page pixmap
        page_pixmap = QPixmap(int(width), int(height))
        page_pixmap.fill()  # Fill with white

        # Draw document content onto page
        painter = QPainter(page_pixmap)

        # Set clipping region to printable area (inside gutters)
        if gutter > 0:
            printable_rect = QRect(
                int(gutter), int(gutter),
                int(width - 2 * gutter), int(height - 2 * gutter)
            )
            painter.setClipRect(printable_rect)

        # Calculate source area that overlaps with this page
        source_rect = source_pixmap.rect()
        page_rect = QRect(int(x), int(y), int(width), int(height))

        # Find intersection
        intersection = source_rect.intersected(page_rect)

        if not intersection.isEmpty():
            # Copy intersecting area from source
            source_crop = source_pixmap.copy(intersection)

            # Calculate destination position on page
            dest_x = intersection.x() - x
            dest_y = intersection.y() - y

            painter.drawPixmap(int(dest_x), int(dest_y), source_crop)

        # Registration marks at printable corners (for export)
        try:
            from ..settings.config import config
            if gutter > 0 and config.get_reg_marks_print():
                px_per_mm = (1.0 / scale_factor) if scale_factor and scale_factor > 0 else 2.0
                diameter_mm = config.get_reg_mark_diameter_mm()
                cross_mm = config.get_reg_mark_crosshair_mm()
                radius_px = int((diameter_mm * px_per_mm) / 2)
                cross_len_px = int(cross_mm * px_per_mm)

                printable_rect = QRect(
                    int(gutter), int(gutter),
                    int(width - 2 * gutter), int(height - 2 * gutter)
                )
                painter.setClipRect(printable_rect)
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                centers = [
                    (int(gutter), int(gutter)),
                    (int(width - gutter), int(gutter)),
                    (int(gutter), int(height - gutter)),
                    (int(width - gutter), int(height - gutter)),
                ]
                for cx, cy in centers:
                    painter.drawEllipse(cx - radius_px, cy - radius_px, radius_px * 2, radius_px * 2)
                    painter.drawLine(cx - cross_len_px, cy, cx + cross_len_px, cy)
                    painter.drawLine(cx, cy - cross_len_px, cx, cy + cross_len_px)
            # Scale bar overlay
            if config.get_scale_bar_print():
                try:
                    units = config.get_default_units()
                    location = config.get_scale_bar_location()
                    opacity = config.get_scale_bar_opacity()
                    length_in = config.get_scale_bar_length_in()
                    length_cm = config.get_scale_bar_length_cm()
                    thickness_mm = config.get_scale_bar_thickness_mm()
                    padding_mm = config.get_scale_bar_padding_mm()
                    draw_scale_bar(
                        painter,
                        int(width),
                        int(height),
                        int(gutter),
                        scale_factor,
                        units,
                        location,
                        length_in,
                        length_cm,
                        opacity,
                        thickness_mm,
                        padding_mm,
                    )
                except Exception:
                    pass
        except Exception:
            pass

        painter.end()
        return page_pixmap

    def _add_metadata_page(self, painter: QPainter, pdf_writer: QPdfWriter,
                          source_pixmap: QPixmap, page_grid: List[dict], **kwargs):
        """Add a metadata summary page to the PDF."""
        try:
            # Create metadata page generator
            metadata_generator = MetadataPageGenerator()

            # Calculate grid dimensions
            if page_grid:
                min_x = min(page['x'] for page in page_grid)
                max_x = max(page['x'] + page['width'] for page in page_grid)
                min_y = min(page['y'] for page in page_grid)
                max_y = max(page['y'] + page['height'] for page in page_grid)

                tiles_x = len(set(page['x'] for page in page_grid))
                tiles_y = len(set(page['y'] for page in page_grid))
            else:
                tiles_x = tiles_y = 0

            # Get document information from metadata or kwargs
            document_name = kwargs.get('document_name', self.metadata.get('title', 'Untitled Document'))
            original_file = kwargs.get('original_file', '')
            scale_factor = kwargs.get('scale_factor', 1.0)
            units = kwargs.get('units', 'mm')
            page_size = kwargs.get('page_size', 'A4')
            gutter_size = kwargs.get('gutter_size', 10.0)

            # Create document info
            doc_info = create_document_info(
                document_name=document_name,
                original_file=original_file,
                scale_factor=scale_factor,
                units=units,
                doc_width=source_pixmap.width(),
                doc_height=source_pixmap.height(),
                tiles_x=tiles_x,
                tiles_y=tiles_y,
                page_size=page_size,
                page_orientation=kwargs.get('page_orientation', 'auto'),
                gutter_size=gutter_size,
                export_format='PDF',
                dpi=300,
                output_dir=kwargs.get('output_dir', ''),
            )

            # Add source pixmap and page grid for plan view
            doc_info['source_pixmap'] = source_pixmap
            doc_info['page_grid'] = page_grid

            # Generate metadata page sized to the printable rect
            page_layout = pdf_writer.pageLayout()
            pdf_rect = page_layout.paintRectPixels(pdf_writer.resolution())
            metadata_pixmap = metadata_generator.generate_metadata_page(doc_info, pdf_rect.size())

            # Draw metadata page to PDF
            if metadata_pixmap and not metadata_pixmap.isNull():
                # Scale to fit PDF page
                scaled_metadata = metadata_pixmap.scaled(
                    pdf_rect.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                # Center on printable page area
                x = (pdf_rect.width() - scaled_metadata.width()) // 2
                y = (pdf_rect.height() - scaled_metadata.height()) // 2
                painter.drawPixmap(x, y, scaled_metadata)

        except Exception as e:
            print(f"Error adding metadata page: {str(e)}")
            # Continue without metadata page if there's an error

    def _export_composite_pdf(self,
                             source_pixmap: QPixmap,
                             page_grid: List[dict],
                             output_path: str,
                             page_size: str = "A4",
                             **kwargs) -> bool:
        """Export as single-page composite PDF showing all tiles."""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Calculate composite image size
            max_x = max_y = 0
            for page in page_grid:
                page_right = page['x'] + page['width']
                page_bottom = page['y'] + page['height']
                max_x = max(max_x, page_right)
                max_y = max(max_y, page_bottom)

            # Create composite image
            composite = QPixmap(int(max_x), int(max_y))
            composite.fill(Qt.white)  # Fill with white

            painter = QPainter(composite)

            # Draw each page
            for page in page_grid:
                page_pixmap = self._create_page_pixmap(source_pixmap, page, kwargs.get('scale_factor', 1.0))
                if page_pixmap and not page_pixmap.isNull():
                    painter.drawPixmap(int(page['x']), int(page['y']), page_pixmap)

            painter.end()

            # Create PDF writer
            pdf_writer = QPdfWriter(output_path)

            # Set page size to fit composite image
            # Calculate appropriate page size based on composite dimensions
            aspect_ratio = composite.width() / composite.height()

            if page_size == "A4":
                page_size_obj = QPageSize(QPageSize.A4)
                orientation = QPageLayout.Landscape if aspect_ratio > 1.414 else QPageLayout.Portrait
            elif page_size == "A3":
                page_size_obj = QPageSize(QPageSize.A3)
                orientation = QPageLayout.Landscape if aspect_ratio > 1.414 else QPageLayout.Portrait
            else:
                page_size_obj = QPageSize(QPageSize.A4)  # Default
                orientation = QPageLayout.Portrait

            pdf_writer.setPageSize(page_size_obj)
            pdf_writer.setPageLayout(QPageLayout(
                page_size_obj,
                orientation,
                QMarginsF(10, 10, 10, 10),  # 10mm margins on all sides
                QPageLayout.Millimeter
            ))

            # Set resolution (300 DPI for high quality)
            pdf_writer.setResolution(300)

            # Add metadata
            self.add_default_metadata()
            pdf_writer.setTitle(self.metadata.get('title', 'OpenTiler Composite Export'))
            pdf_writer.setCreator(self.metadata.get('application', 'OpenTiler'))

            # Create painter for PDF
            pdf_painter = QPainter(pdf_writer)

            # Scale composite to fit PDF page while maintaining aspect ratio
            page_layout = pdf_writer.pageLayout()
            pdf_rect = page_layout.paintRectPixels(pdf_writer.resolution())
            scaled_composite = composite.scaled(
                pdf_rect.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Center the composite in the printable area
            x = (pdf_rect.width() - scaled_composite.width()) // 2
            y = (pdf_rect.height() - scaled_composite.height()) // 2

            pdf_painter.drawPixmap(x, y, scaled_composite)
            pdf_painter.end()

            print(f"Composite PDF exported successfully: {output_path}")
            return True

        except Exception as e:
            print(f"Composite PDF export error: {str(e)}")
            return False

    def _determine_optimal_orientation(self, page_grid: List[dict], page_size_obj: QPageSize) -> QPageLayout.Orientation:
        """
        Determine the optimal page orientation for tiles based on their content.

        Args:
            page_grid: List of page dictionaries
            page_size_obj: QPageSize object for the target page size

        Returns:
            QPageLayout.Orientation (Portrait or Landscape)
        """
        from ..settings.config import config

        # Get user preference from settings
        orientation_pref = config.get_page_orientation()

        if orientation_pref == "landscape":
            return QPageLayout.Landscape
        elif orientation_pref == "portrait":
            return QPageLayout.Portrait
        elif orientation_pref == "auto":
            # Auto-determine based on tile content
            if not page_grid:
                return QPageLayout.Portrait  # Default

            # Calculate average tile aspect ratio
            total_aspect_ratio = 0
            valid_tiles = 0

            for page in page_grid:
                width = page.get('width', 0)
                height = page.get('height', 0)
                if width > 0 and height > 0:
                    aspect_ratio = width / height
                    total_aspect_ratio += aspect_ratio
                    valid_tiles += 1

            if valid_tiles > 0:
                avg_aspect_ratio = total_aspect_ratio / valid_tiles

                # Get page size aspect ratios
                page_size_mm = page_size_obj.sizePoints()
                page_portrait_ratio = page_size_mm.width() / page_size_mm.height()
                page_landscape_ratio = page_size_mm.height() / page_size_mm.width()

                # Choose orientation that better matches tile content
                portrait_diff = abs(avg_aspect_ratio - page_portrait_ratio)
                landscape_diff = abs(avg_aspect_ratio - page_landscape_ratio)

                if landscape_diff < portrait_diff:
                    return QPageLayout.Landscape
                else:
                    return QPageLayout.Portrait
            else:
                return QPageLayout.Portrait  # Default if no valid tiles
        else:
            return QPageLayout.Portrait  # Default fallback
