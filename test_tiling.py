#!/usr/bin/env python3
"""
Test script to verify tiling logic works correctly.
"""

import sys
import os

# Add the opentiler package to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from opentiler.utils.helpers import calculate_tile_grid, get_page_size_mm

def test_tiling_logic():
    """Test the tiling calculation logic."""

    # Example document: 3000x2000 pixels
    doc_width = 3000
    doc_height = 2000

    # Example scale: 0.1 mm/pixel (meaning 1 pixel = 0.1mm)
    scale_factor = 0.1  # mm/pixel

    # A4 page size
    page_width_mm, page_height_mm = get_page_size_mm('A4')
    print(f"A4 page size: {page_width_mm}x{page_height_mm} mm")

    # Convert page size to pixels using scale
    page_width_pixels = page_width_mm / scale_factor
    page_height_pixels = page_height_mm / scale_factor
    print(f"A4 in document pixels: {page_width_pixels}x{page_height_pixels}")

    # Calculate tiles
    tile_grid = calculate_tile_grid(
        doc_width,
        doc_height,
        int(page_width_pixels),
        int(page_height_pixels),
        overlap=0
    )

    print(f"\nDocument: {doc_width}x{doc_height} pixels")
    print(f"Page size: {int(page_width_pixels)}x{int(page_height_pixels)} pixels")
    print(f"Generated {len(tile_grid)} tiles:")

    for i, (x, y, w, h) in enumerate(tile_grid):
        print(f"  Tile {i+1}: ({x}, {y}) {w}x{h}")

    return len(tile_grid) > 0

if __name__ == "__main__":
    success = test_tiling_logic()
    if success:
        print("\n✅ Tiling logic works!")
    else:
        print("\n❌ Tiling logic failed!")
