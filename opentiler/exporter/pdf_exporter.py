"""
PDF exporter for OpenTiler.
"""

import os
from typing import List, Tuple, Optional
from PySide6.QtCore import QRect
from PySide6.QtGui import QPixmap, QPainter, QPdfWriter, QPageSize, QPageLayout
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
        Export tiled document as multi-page PDF.

        Args:
            source_pixmap: Source document pixmap
            page_grid: List of page dictionaries with position and size info
            output_path: Output PDF file path
            page_size: Page size (A4, Letter, etc.)
            **kwargs: Additional export options

        Returns:
            True if export successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Create PDF writer
            pdf_writer = QPdfWriter(output_path)

            # Set page size
            if page_size == "A4":
                pdf_writer.setPageSize(QPageSize(QPageSize.A4))
            elif page_size == "Letter":
                pdf_writer.setPageSize(QPageSize(QPageSize.Letter))
            elif page_size == "A3":
                pdf_writer.setPageSize(QPageSize(QPageSize.A3))
            else:
                pdf_writer.setPageSize(QPageSize(QPageSize.A4))  # Default

            # Set page layout
            pdf_writer.setPageLayout(QPageLayout(
                QPageSize(pdf_writer.pageSize()),
                QPageLayout.Portrait,
                QPageLayout.Margins()
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
                page_pixmap = self._create_page_pixmap(source_pixmap, page)

                # Draw page to PDF
                if page_pixmap and not page_pixmap.isNull():
                    # Scale to fit PDF page while maintaining aspect ratio
                    pdf_rect = painter.viewport()
                    scaled_pixmap = page_pixmap.scaled(
                        pdf_rect.size(),
                        aspectRatioMode=1,  # Qt.KeepAspectRatio
                        transformMode=1     # Qt.SmoothTransformation
                    )

                    # Center the image on the page
                    x = (pdf_rect.width() - scaled_pixmap.width()) // 2
                    y = (pdf_rect.height() - scaled_pixmap.height()) // 2

                    painter.drawPixmap(x, y, scaled_pixmap)

                page_count += 1

            # Add metadata page at the end if configured
            if include_metadata and metadata_position == "last":
                pdf_writer.newPage()
                self._add_metadata_page(painter, pdf_writer, source_pixmap, page_grid, **kwargs)

            painter.end()
            return True

        except Exception as e:
            print(f"PDF export error: {str(e)}")
            return False

    def _create_page_pixmap(self, source_pixmap: QPixmap, page: dict) -> QPixmap:
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

            # Generate metadata page
            pdf_rect = painter.viewport()
            metadata_pixmap = metadata_generator.generate_metadata_page(doc_info, pdf_rect.size())

            # Draw metadata page to PDF
            if metadata_pixmap and not metadata_pixmap.isNull():
                # Scale to fit PDF page
                scaled_metadata = metadata_pixmap.scaled(
                    pdf_rect.size(),
                    aspectRatioMode=1,  # Qt.KeepAspectRatio
                    transformMode=1     # Qt.SmoothTransformation
                )

                # Center on page
                x = (pdf_rect.width() - scaled_metadata.width()) // 2
                y = (pdf_rect.height() - scaled_metadata.height()) // 2

                painter.drawPixmap(x, y, scaled_metadata)

        except Exception as e:
            print(f"Error adding metadata page: {str(e)}")
            # Continue without metadata page if there's an error
