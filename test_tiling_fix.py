#!/usr/bin/env python3
"""
Test script to verify the tiling fix ensures all content falls within drawable areas.
"""

def calculate_page_grid_with_gutters(doc_width, doc_height, page_width, page_height, gutter_size):
    """Calculate page grid where drawable areas tile seamlessly with no gaps."""
    pages = []

    # Calculate step size based on drawable area (printable area inside gutters)
    # This ensures all document content falls within a drawable area
    drawable_width = page_width - (2 * gutter_size)
    drawable_height = page_height - (2 * gutter_size)

    # Step size equals drawable area size for seamless tiling
    step_x = drawable_width
    step_y = drawable_height

    # Start pages offset by negative gutter so drawable areas start at (0,0)
    y = -gutter_size
    row = 0
    while y < doc_height:
        x = -gutter_size
        col = 0
        while x < doc_width:
            # Pages maintain full dimensions even if they extend beyond document
            # This ensures consistent page sizes for printing
            pages.append({
                'x': x, 'y': y,
                'width': page_width, 'height': page_height,
                'row': row, 'col': col,
                'gutter': gutter_size,
                'drawable_x': x + gutter_size,
                'drawable_y': y + gutter_size,
                'drawable_width': drawable_width,
                'drawable_height': drawable_height
            })

            x += step_x
            # Continue until drawable area covers document width
            if x + gutter_size >= doc_width:
                break
            col += 1

        y += step_y
        # Continue until drawable area covers document height
        if y + gutter_size >= doc_height:
            break
        row += 1

    return pages

def test_tiling_coverage():
    """Test that tiling covers all document content without gaps."""
    print("Testing Tiling Coverage Fix")
    print("=" * 50)

    # Test case: 1000x800 document, 400x300 pages, 20 gutter
    doc_width = 1000
    doc_height = 800
    page_width = 400
    page_height = 300
    gutter_size = 20

    print(f"Document: {doc_width}x{doc_height}")
    print(f"Page size: {page_width}x{page_height}")
    print(f"Gutter: {gutter_size}")

    drawable_width = page_width - (2 * gutter_size)
    drawable_height = page_height - (2 * gutter_size)
    print(f"Drawable area per page: {drawable_width}x{drawable_height}")

    pages = calculate_page_grid_with_gutters(doc_width, doc_height, page_width, page_height, gutter_size)

    print(f"\nGenerated {len(pages)} pages:")

    # Check coverage
    covered_areas = []
    for i, page in enumerate(pages):
        drawable_left = page['drawable_x']
        drawable_top = page['drawable_y']
        drawable_right = drawable_left + page['drawable_width']
        drawable_bottom = drawable_top + page['drawable_height']

        covered_areas.append((drawable_left, drawable_top, drawable_right, drawable_bottom))

        print(f"  Page {i+1}: Page({page['x']}, {page['y']}) -> Drawable({drawable_left}, {drawable_top}, {drawable_right}, {drawable_bottom})")

    # Check for gaps
    print("\nChecking for gaps in coverage:")

    # Sample points across the document
    gap_found = False
    sample_points = []
    for y in range(0, doc_height, 50):
        for x in range(0, doc_width, 50):
            sample_points.append((x, y))

    for x, y in sample_points:
        covered = False
        for left, top, right, bottom in covered_areas:
            if left <= x < right and top <= y < bottom:
                covered = True
                break

        if not covered:
            print(f"  ❌ GAP FOUND: Point ({x}, {y}) not covered by any drawable area!")
            gap_found = True

    if not gap_found:
        print("  ✅ No gaps found - all document content is covered by drawable areas!")

    # Check for overlaps in drawable areas
    print("\nChecking drawable area overlaps:")
    overlap_found = False
    for i, (left1, top1, right1, bottom1) in enumerate(covered_areas):
        for j, (left2, top2, right2, bottom2) in enumerate(covered_areas[i+1:], i+1):
            # Check if rectangles overlap
            if not (right1 <= left2 or right2 <= left1 or bottom1 <= top2 or bottom2 <= top1):
                print(f"  ⚠️  OVERLAP: Page {i+1} and Page {j+1} drawable areas overlap!")
                overlap_found = True

    if not overlap_found:
        print("  ✅ No overlaps found - drawable areas tile perfectly!")

    return not gap_found and not overlap_found

if __name__ == "__main__":
    success = test_tiling_coverage()
    print(f"\nResult: {'✅ TILING FIX SUCCESSFUL' if success else '❌ TILING ISSUES REMAIN'}")
