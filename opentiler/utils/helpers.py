"""
Helper utilities for OpenTiler.
"""

import math
from typing import Tuple, List, Optional


def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert between different units.
    
    Args:
        value: The value to convert
        from_unit: Source unit ('mm', 'inches', 'pixels')
        to_unit: Target unit ('mm', 'inches', 'pixels')
        
    Returns:
        Converted value
    """
    # Conversion factors to mm
    to_mm = {
        'mm': 1.0,
        'inches': 25.4,
        'pixels': 25.4 / 300  # Assume 300 DPI
    }
    
    # Convert to mm first, then to target unit
    mm_value = value * to_mm.get(from_unit, 1.0)
    return mm_value / to_mm.get(to_unit, 1.0)


def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Distance between points
    """
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx * dx + dy * dy)


def calculate_scale_factor(pixel_distance: float, real_distance: float, units: str = 'mm') -> float:
    """
    Calculate scale factor from pixel and real-world distances.
    
    Args:
        pixel_distance: Distance in pixels
        real_distance: Real-world distance
        units: Units of real distance ('mm' or 'inches')
        
    Returns:
        Scale factor (real-world units per pixel)
    """
    if pixel_distance <= 0 or real_distance <= 0:
        return 1.0
        
    # Convert real distance to mm if needed
    if units == 'inches':
        real_distance_mm = real_distance * 25.4
    else:
        real_distance_mm = real_distance
        
    return real_distance_mm / pixel_distance


def format_scale_ratio(scale_factor: float) -> str:
    """
    Format scale factor as a ratio string.
    
    Args:
        scale_factor: Scale factor value
        
    Returns:
        Formatted ratio string (e.g., "1:100" or "2:1")
    """
    if scale_factor >= 1.0:
        return f"{scale_factor:.2f}:1"
    else:
        ratio = 1.0 / scale_factor
        return f"1:{ratio:.1f}"


def calculate_tile_grid(
    image_width: int, 
    image_height: int, 
    tile_width: int, 
    tile_height: int,
    overlap: int = 0
) -> List[Tuple[int, int, int, int]]:
    """
    Calculate tile grid coordinates for an image.
    
    Args:
        image_width: Width of the image
        image_height: Height of the image
        tile_width: Width of each tile
        tile_height: Height of each tile
        overlap: Overlap between tiles in pixels
        
    Returns:
        List of tile rectangles (x, y, width, height)
    """
    tiles = []
    
    # Calculate step size (tile size minus overlap)
    step_x = tile_width - overlap
    step_y = tile_height - overlap
    
    # Generate tile grid
    y = 0
    while y < image_height:
        x = 0
        while x < image_width:
            # Calculate actual tile dimensions (may be smaller at edges)
            actual_width = min(tile_width, image_width - x)
            actual_height = min(tile_height, image_height - y)
            
            tiles.append((x, y, actual_width, actual_height))
            
            x += step_x
            if x >= image_width:
                break
                
        y += step_y
        if y >= image_height:
            break
            
    return tiles


def get_page_size_mm(page_size: str) -> Tuple[float, float]:
    """
    Get page dimensions in millimeters.
    
    Args:
        page_size: Page size name (e.g., 'A4', 'Letter')
        
    Returns:
        Tuple of (width, height) in mm
    """
    page_sizes = {
        'A4': (210.0, 297.0),
        'A3': (297.0, 420.0),
        'A5': (148.0, 210.0),
        'Letter': (215.9, 279.4),
        'Legal': (215.9, 355.6),
        'Tabloid': (279.4, 431.8)
    }
    
    return page_sizes.get(page_size, (210.0, 297.0))  # Default to A4


def pixels_to_mm(pixels: float, dpi: int = 300) -> float:
    """
    Convert pixels to millimeters.
    
    Args:
        pixels: Number of pixels
        dpi: Dots per inch
        
    Returns:
        Equivalent millimeters
    """
    inches = pixels / dpi
    return inches * 25.4


def mm_to_pixels(mm: float, dpi: int = 300) -> float:
    """
    Convert millimeters to pixels.
    
    Args:
        mm: Millimeters
        dpi: Dots per inch
        
    Returns:
        Equivalent pixels
    """
    inches = mm / 25.4
    return inches * dpi


def validate_numeric_input(text: str, min_val: float = 0.0, max_val: float = float('inf')) -> Optional[float]:
    """
    Validate and convert numeric input.
    
    Args:
        text: Input text
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validated float value or None if invalid
    """
    try:
        value = float(text)
        if min_val <= value <= max_val:
            return value
        return None
    except ValueError:
        return None
