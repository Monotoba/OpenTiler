"""
PDF exporter for OpenTiler.
"""

import os
from typing import List, Tuple, Optional
from PySide6.QtCore import QRect
from PySide6.QtGui import QPixmap, QPainter, QPdfWriter, QPageSize, QPageLayout
from PySide6.QtWidgets import QMessageBox

from .base_exporter import BaseExporter


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
            
            # Export each page
            for i, page in enumerate(page_grid):
                if i > 0:
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
