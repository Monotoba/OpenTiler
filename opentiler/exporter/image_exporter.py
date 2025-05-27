"""
Image exporter for OpenTiler.
"""

import os
from typing import List, Tuple, Optional
from PySide6.QtCore import QRect
from PySide6.QtGui import QPixmap, QPainter

from .base_exporter import BaseExporter


class ImageExporter(BaseExporter):
    """Export tiles as individual image files."""
    
    def __init__(self):
        super().__init__()
        
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        
    def export(self, 
               source_pixmap: QPixmap,
               page_grid: List[dict], 
               output_path: str,
               image_format: str = "PNG",
               **kwargs) -> bool:
        """
        Export tiled document as individual image files.
        
        Args:
            source_pixmap: Source document pixmap
            page_grid: List of page dictionaries with position and size info
            output_path: Output directory path or base filename
            image_format: Image format (PNG, JPEG, TIFF, BMP)
            **kwargs: Additional export options
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Determine output directory and base filename
            if os.path.isdir(output_path):
                output_dir = output_path
                base_name = "tile"
            else:
                output_dir = os.path.dirname(output_path)
                base_name = os.path.splitext(os.path.basename(output_path))[0]
                
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Determine file extension
            format_lower = image_format.lower()
            if format_lower == "jpeg":
                ext = ".jpg"
            else:
                ext = f".{format_lower}"
                
            # Export each page
            exported_files = []
            for i, page in enumerate(page_grid):
                # Create filename
                filename = f"{base_name}_page_{i+1:03d}{ext}"
                file_path = os.path.join(output_dir, filename)
                
                # Create page pixmap
                page_pixmap = self._create_page_pixmap(source_pixmap, page)
                
                # Save page image
                if page_pixmap and not page_pixmap.isNull():
                    quality = kwargs.get('quality', 95)  # High quality by default
                    if page_pixmap.save(file_path, image_format.upper(), quality):
                        exported_files.append(file_path)
                    else:
                        print(f"Failed to save: {file_path}")
                        return False
                        
            print(f"Exported {len(exported_files)} image files to: {output_dir}")
            return True
            
        except Exception as e:
            print(f"Image export error: {str(e)}")
            return False
            
    def export_composite(self,
                        source_pixmap: QPixmap,
                        page_grid: List[dict],
                        output_path: str,
                        image_format: str = "PNG",
                        **kwargs) -> bool:
        """
        Export as single composite image showing all tiles.
        
        Args:
            source_pixmap: Source document pixmap
            page_grid: List of page dictionaries
            output_path: Output file path
            image_format: Image format
            **kwargs: Additional options
            
        Returns:
            True if successful
        """
        try:
            # Calculate composite image size
            max_x = max_y = 0
            for page in page_grid:
                page_right = page['x'] + page['width']
                page_bottom = page['y'] + page['height']
                max_x = max(max_x, page_right)
                max_y = max(max_y, page_bottom)
                
            # Create composite image
            composite = QPixmap(int(max_x), int(max_y))
            composite.fill()  # Fill with white
            
            painter = QPainter(composite)
            
            # Draw each page
            for page in page_grid:
                page_pixmap = self._create_page_pixmap(source_pixmap, page)
                if page_pixmap and not page_pixmap.isNull():
                    painter.drawPixmap(int(page['x']), int(page['y']), page_pixmap)
                    
            painter.end()
            
            # Save composite image
            quality = kwargs.get('quality', 95)
            return composite.save(output_path, image_format.upper(), quality)
            
        except Exception as e:
            print(f"Composite export error: {str(e)}")
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
