#!/usr/bin/env python3
"""
Simple test to verify tiling calculation.
"""

def calculate_tile_grid(image_width, image_height, tile_width, tile_height, overlap=0):
    """Calculate tile grid coordinates for an image."""
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

def test_simple():
    """Test simple tiling."""
    # Document: 3000x2000 pixels
    doc_width = 3000
    doc_height = 2000
    
    # A4 at scale 0.1 mm/pixel: 210mm / 0.1 = 2100 pixels wide
    page_width = 2100  # pixels
    page_height = 2970  # pixels (297mm / 0.1)
    
    tiles = calculate_tile_grid(doc_width, doc_height, page_width, page_height)
    
    print(f"Document: {doc_width}x{doc_height}")
    print(f"Page size: {page_width}x{page_height}")
    print(f"Generated {len(tiles)} tiles:")
    
    for i, (x, y, w, h) in enumerate(tiles):
        print(f"  Tile {i+1}: ({x}, {y}) {w}x{h}")
    
    return len(tiles) > 0

if __name__ == "__main__":
    success = test_simple()
    print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")
