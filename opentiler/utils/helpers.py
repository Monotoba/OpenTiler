"""
Helper utilities for OpenTiler.
"""

import math
import os
from typing import Any, Dict, List, Optional, Tuple, Union

# Optional Qt imports to avoid hard dependency during headless/unit testing
try:
    from PySide6.QtCore import QRect
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    _HAS_QT = True
except Exception:
    _HAS_QT = False

    # Minimal shims so non-Qt utility functions can import safely
    class QIcon:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def isNull(self):
            return True

        @staticmethod
        def fromTheme(name: str):
            return QIcon()

    class QApplication:  # type: ignore
        @staticmethod
        def instance():
            return None

    class QRect:  # type: ignore
        def __init__(self, *args, **kwargs):
            self.args = args


def _find_assets_dir(
    start_dir: Optional[str] = None, max_depth: int = 6
) -> Optional[str]:
    """
    Walk up from start_dir (or this file's dir) up to max_depth levels looking for an 'assets' dir.
    Returns absolute path to the assets dir or None if not found.
    """
    cur = os.path.abspath(start_dir or os.path.dirname(__file__))
    root = os.path.abspath(os.sep)
    depth = 0

    while True:
        candidate = os.path.join(cur, "assets")
        if os.path.isdir(candidate):
            return candidate
        if cur == root or depth >= max_depth:
            break
        cur = os.path.dirname(cur)
        depth += 1

    return None


def load_icon(
    icon_name: Union[str, QIcon], fallback: Optional[Union[int, QIcon, str]] = None
) -> QIcon:
    """
    Load an icon from the repository 'assets' folder. If not found, fall back to one of:
      - a QIcon instance (returned directly)
      - a QStyle.StandardPixmap enum / int (uses QApplication.style().standardIcon(...))
      - a filesystem path (string) pointing to an icon file
      - a theme name string (QIcon.fromTheme)
    The loader also attempts QIcon.fromTheme(base_name) before returning an empty QIcon.

    icon_name may be:
      - a QIcon (returned immediately),
      - an absolute path or path-like string,
      - a basename (without extension) — we try .png, .svg, .ico extensions.
    """
    # If Qt is unavailable, return an empty icon
    if not _HAS_QT:
        return QIcon()

    # If caller passed a QIcon already, return it
    if isinstance(icon_name, QIcon):
        return icon_name

    # Canonicalize string
    if not isinstance(icon_name, str):
        return QIcon()

    # If absolute or contains path separators, check directly
    if os.path.isabs(icon_name) or os.path.sep in icon_name:
        if os.path.exists(icon_name):
            return QIcon(icon_name)

    # Build candidate filenames (if extension not given)
    base, ext = os.path.splitext(icon_name)
    if ext:
        candidates = [icon_name]
    else:
        candidates = [f"{base}.png", f"{base}.svg", f"{base}.ico"]

    # 1) Look for an 'assets' folder up the tree (handles opentiler/assets)
    assets_dir = _find_assets_dir()
    if assets_dir:
        for candidate in candidates:
            path = os.path.join(assets_dir, candidate)
            if os.path.exists(path):
                return QIcon(path)

    # 2) Handle fallback if provided
    # If fallback is a QIcon instance
    if isinstance(fallback, QIcon):
        return fallback

    # If fallback is a path-like string, use that
    if isinstance(fallback, str):
        fp = os.fspath(fallback)
        if os.path.exists(fp):
            return QIcon(fp)
        # Try as theme name
        theme_icon = QIcon.fromTheme(fp)
        if not theme_icon.isNull():
            return theme_icon

    # If fallback is an enum/int for QStyle.StandardPixmap, try to use style
    if fallback is not None and not isinstance(fallback, str):
        try:
            app = QApplication.instance()
            if app is not None:
                style = app.style()
                # style.standardIcon accepts QStyle.StandardPixmap (enum/int)
                return style.standardIcon(fallback)
        except Exception:
            # swallow and continue to next fallback
            pass

    # 3) Try the icon theme using the base name
    if base:
        theme_icon = QIcon.fromTheme(base)
        if not theme_icon.isNull():
            return theme_icon

    # final fallback: empty icon
    return QIcon()


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
    to_mm = {"mm": 1.0, "inches": 25.4, "pixels": 25.4 / 300}  # Assume 300 DPI

    # Convert to mm first, then to target unit
    mm_value = value * to_mm.get(from_unit, 1.0)
    return mm_value / to_mm.get(to_unit, 1.0)


def calculate_distance(
    point1: Tuple[float, float], point2: Tuple[float, float]
) -> float:
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


def calculate_scale_factor(
    pixel_distance: float, real_distance: float, units: str = "mm"
) -> float:
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
    if units == "inches":
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
    overlap: int = 0,
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
        "A4": (210.0, 297.0),
        "A3": (297.0, 420.0),
        "A5": (148.0, 210.0),
        "Letter": (215.9, 279.4),
        "Legal": (215.9, 355.6),
        "Tabloid": (279.4, 431.8),
    }

    return page_sizes.get(page_size, (210.0, 297.0))  # Default to A4


def compute_page_size_pixels(
    scale_factor_mm_per_px: float,
    page_size_name: str,
    orientation: str = "auto",
) -> Tuple[float, float]:
    """
    Resolve page width/height in pixels for a given page size and orientation.

    Args:
        scale_factor_mm_per_px: Document scale in mm per pixel (mm/px).
        page_size_name: Named page size (e.g., 'A4', 'Letter').
        orientation: 'portrait' | 'landscape' | 'auto'.

    Returns:
        (page_width_pixels, page_height_pixels)

    Notes:
        pixels = mm / (mm/px) when scale_factor_mm_per_px > 0.
    """
    width_mm, height_mm = get_page_size_mm(page_size_name)

    if orientation == "landscape" and width_mm < height_mm:
        width_mm, height_mm = height_mm, width_mm
    elif orientation == "portrait" and height_mm < width_mm:
        width_mm, height_mm = height_mm, width_mm

    if scale_factor_mm_per_px > 0:
        return (width_mm / scale_factor_mm_per_px, height_mm / scale_factor_mm_per_px)
    # Fallback: return mm if scale is invalid (caller should guard)
    return (width_mm, height_mm)


def compute_page_grid_with_gutters(
    doc_width_px: int,
    doc_height_px: int,
    page_width_px: float,
    page_height_px: float,
    gutter_px: float,
    calib_reduce_step_x_px: float = 0.0,
    calib_reduce_step_y_px: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Compute the page grid for tiling, using drawable area (inside gutters) as the step.

    Ensures seamless tiling of the document content by stepping pages by the
    printable (drawable) area size, while each page retains full page dimensions.

    Args:
        doc_width_px: Source document width in pixels.
        doc_height_px: Source document height in pixels.
        page_width_px: Target page width in pixels (including gutters).
        page_height_px: Target page height in pixels (including gutters).
        gutter_px: Gutter size in pixels to be applied on all sides.

    Returns:
        List of dicts with keys: 'x', 'y', 'width', 'height', 'row', 'col', 'gutter'.
    """
    pages: List[Dict[str, Any]] = []

    drawable_w = page_width_px - (2 * gutter_px)
    drawable_h = page_height_px - (2 * gutter_px)

    if drawable_w <= 0 or drawable_h <= 0:
        # Invalid configuration; no drawable area
        return []

    # Calibration reduces the usable area from the right/bottom edges.
    # To avoid losing content, we step pages by a smaller stride so the
    # overlapped region reappears on the next page within safe (left/top) areas.
    step_x = max(1.0, drawable_w - max(0.0, calib_reduce_step_x_px))
    step_y = max(1.0, drawable_h - max(0.0, calib_reduce_step_y_px))

    y = -gutter_px
    row = 0
    while y < doc_height_px:
        x = -gutter_px
        col = 0
        while x < doc_width_px:
            pages.append(
                {
                    "x": x,
                    "y": y,
                    "width": page_width_px,
                    "height": page_height_px,
                    "row": row,
                    "col": col,
                    "gutter": gutter_px,
                }
            )
            x += step_x
            if x + gutter_px >= doc_width_px:
                break
            col += 1

        y += step_y
        if y + gutter_px >= doc_height_px:
            break
        row += 1

    return pages


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


def validate_numeric_input(
    text: str, min_val: float = 0.0, max_val: float = float("inf")
) -> Optional[float]:
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


def summarize_page_grid(page_grid: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Summarize a page grid into tiles_x, tiles_y, and total count.

    Uses row/col indices if present for robustness; falls back to
    counting unique X and Y positions otherwise.

    Args:
        page_grid: List of page dicts produced by tiling.

    Returns:
        {'tiles_x': int, 'tiles_y': int, 'total_tiles': int}
    """
    total = len(page_grid) if page_grid else 0
    if not page_grid:
        return {"tiles_x": 0, "tiles_y": 0, "total_tiles": 0}

    has_indices = any(("row" in p and "col" in p) for p in page_grid)
    if has_indices:
        max_row = max(int(p.get("row", 0)) for p in page_grid)
        max_col = max(int(p.get("col", 0)) for p in page_grid)
        return {"tiles_x": max_col + 1, "tiles_y": max_row + 1, "total_tiles": total}

    # Fallback: unique positions (may be floats)
    xs = {p.get("x", 0) for p in page_grid}
    ys = {p.get("y", 0) for p in page_grid}
    return {"tiles_x": len(xs), "tiles_y": len(ys), "total_tiles": total}


def compute_tile_layout(
    page: Dict[str, Any], source_width: int, source_height: int
) -> Dict[str, Any]:
    """
    Compute drawing rectangles and positions to render a single tile/page from the source.

    This consolidates the math used by preview thumbnails and print rendering so that
    both paths produce identical tile content and alignment.

    Args:
        page: A page dict with keys: 'x', 'y', 'width', 'height', 'gutter'.
        source_width: Width of the source document pixmap (px).
        source_height: Height of the source document pixmap (px).

    Returns:
        {
          'tile_width': int,
          'tile_height': int,
          'gutter': int,
          'printable_rect': QRect,   # inner rect on tile (inside gutters)
          'source_rect': QRect,      # area to copy from source
          'dest_pos': (int, int),    # destination top-left on the tile
        }
    """
    tile_w = int(page.get("width", 0) or 0)
    tile_h = int(page.get("height", 0) or 0)
    gutter = int(page.get("gutter", 0) or 0)

    # Printable area on the tile (inside gutters)
    inner_w = max(0, tile_w - 2 * gutter)
    inner_h = max(0, tile_h - 2 * gutter)
    printable_rect = QRect(gutter, gutter, inner_w, inner_h)

    # Intersect page area with source to decide what to copy
    page_x = int(page.get("x", 0) or 0)
    page_y = int(page.get("y", 0) or 0)

    src_x = max(0, page_x)
    src_y = max(0, page_y)
    src_w = min(max(0, source_width - src_x), tile_w)
    src_h = min(max(0, source_height - src_y), tile_h)
    source_rect = QRect(src_x, src_y, src_w, src_h)

    # Destination position on tile (accounts for negative page offsets)
    dest_x = max(0, -page_x)
    dest_y = max(0, -page_y)

    return {
        "tile_width": tile_w,
        "tile_height": tile_h,
        "gutter": gutter,
        "printable_rect": printable_rect,
        "source_rect": source_rect,
        "dest_pos": (dest_x, dest_y),
    }
