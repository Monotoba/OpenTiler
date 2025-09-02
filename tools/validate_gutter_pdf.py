#!/usr/bin/env python3
"""
Generate a validation PDF to verify gutter handling and printable margins.

Creates a synthetic document with a grid and labeled guides, tiles it to A4
with 10mm gutters, and exports a multi-page PDF using the PDFExporter.
"""

import os
from typing import List, Dict

from PySide6.QtGui import QGuiApplication, QPainter, QPixmap, QColor, QPen
from PySide6.QtCore import Qt, QRect

from opentiler.exporter.pdf_exporter import PDFExporter
from opentiler.settings.config import config
from opentiler.utils.helpers import get_page_size_mm


def create_test_pixmap(width: int, height: int) -> QPixmap:
    pix = QPixmap(width, height)
    pix.fill(Qt.white)
    p = QPainter(pix)
    # Draw outer border
    p.setPen(QPen(QColor(0, 0, 0), 4))
    p.drawRect(2, 2, width - 4, height - 4)
    # Draw 100px grid lines
    p.setPen(QPen(QColor(200, 200, 200), 1))
    for x in range(0, width, 100):
        p.drawLine(x, 0, x, height)
    for y in range(0, height, 100):
        p.drawLine(0, y, width, y)
    # Draw thicker guides every 500px
    p.setPen(QPen(QColor(150, 150, 150), 2))
    for x in range(0, width, 500):
        p.drawLine(x, 0, x, height)
    for y in range(0, height, 500):
        p.drawLine(0, y, width, y)
    # Label corners
    p.setPen(Qt.black)
    p.drawText(10, 30, "(0,0)")
    p.drawText(width - 120, 30, f"({width},0)")
    p.drawText(10, height - 10, f"(0,{height})")
    p.drawText(width - 180, height - 10, f"({width},{height})")
    p.end()
    return pix


def calc_page_grid_with_gutters(doc_w: float, doc_h: float, page_w: float, page_h: float, gutter: float) -> List[Dict]:
    # Drawable area inside gutters
    drawable_w = page_w - (2 * gutter)
    drawable_h = page_h - (2 * gutter)
    assert drawable_w > 0 and drawable_h > 0, "Drawable area must be positive"

    step_x = drawable_w
    step_y = drawable_h

    pages: List[Dict] = []
    y = -gutter
    row = 0
    while y < doc_h:
        x = -gutter
        col = 0
        while x < doc_w:
            pages.append({
                'x': x, 'y': y,
                'width': page_w, 'height': page_h,
                'row': row, 'col': col,
                'gutter': gutter
            })
            x += step_x
            if x + gutter >= doc_w:
                break
            col += 1
        y += step_y
        if y + gutter >= doc_h:
            break
        row += 1
    return pages


def main() -> int:
    app = QGuiApplication([])

    # Synthetic doc ~ 1800x1200 px
    src = create_test_pixmap(1800, 1200)

    # Assume scale: 0.5 mm/px (i.e., 2 px/mm)
    scale_factor = 0.5

    # Page size and gutter
    page_size = 'A4'
    page_w_mm, page_h_mm = get_page_size_mm(page_size)
    gutter_mm = float(config.get_gutter_size_mm())  # default 10mm

    # Convert to pixels using doc scale (mm/pixel)
    page_w_px = page_w_mm / scale_factor
    page_h_px = page_h_mm / scale_factor
    gutter_px = gutter_mm / scale_factor

    # Build page grid
    pages = calc_page_grid_with_gutters(src.width(), src.height(), page_w_px, page_h_px, gutter_px)

    # Export multipage
    out_dir = os.path.join(os.path.dirname(__file__), 'validation_output')
    os.makedirs(out_dir, exist_ok=True)
    out_pdf = os.path.join(out_dir, 'test_gutter_fix.pdf')

    exporter = PDFExporter()
    ok = exporter.export(
        source_pixmap=src,
        page_grid=pages,
        output_path=out_pdf,
        page_size=page_size,
        document_name='Gutter Validation',
        original_file='',
        scale_factor=scale_factor,
        units='mm',
        page_orientation='auto',
        gutter_size=gutter_mm,
        output_dir=out_dir
    )

    print(f"Validation PDF written: {out_pdf}, success={ok}")
    # Export composite
    out_pdf_composite = os.path.join(out_dir, 'test_gutter_fix_composite.pdf')
    ok2 = exporter.export(
        source_pixmap=src,
        page_grid=pages,
        output_path=out_pdf_composite,
        page_size=page_size,
        document_name='Gutter Validation (Composite)',
        original_file='',
        scale_factor=scale_factor,
        units='mm',
        page_orientation='auto',
        gutter_size=gutter_mm,
        output_dir=out_dir,
        composite=True
    )
    print(f"Validation composite PDF written: {out_pdf_composite}, success={ok2}")
    return 0 if (ok and ok2) else 1


if __name__ == '__main__':
    raise SystemExit(main())
