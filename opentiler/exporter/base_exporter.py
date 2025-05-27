"""
Base exporter class for OpenTiler.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from datetime import datetime


class BaseExporter(ABC):
    """Base class for document exporters."""
    
    def __init__(self):
        self.metadata = {}
        
    def set_metadata(self, **kwargs):
        """Set export metadata."""
        self.metadata.update(kwargs)
        
    def add_default_metadata(self):
        """Add default metadata fields."""
        self.metadata.setdefault('timestamp', datetime.now().isoformat())
        self.metadata.setdefault('application', 'OpenTiler')
        self.metadata.setdefault('version', '0.1.0')
        
    @abstractmethod
    def export(self, 
               image_data, 
               tile_grid: List[Tuple[int, int, int, int]], 
               output_path: str,
               **kwargs) -> bool:
        """
        Export tiled document.
        
        Args:
            image_data: Source image data
            tile_grid: List of tile rectangles (x, y, width, height)
            output_path: Output file path
            **kwargs: Additional export options
            
        Returns:
            True if export successful, False otherwise
        """
        pass
        
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        pass
