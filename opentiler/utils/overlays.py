from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter, QColor


def _mm_to_px(mm: float, scale_factor_mm_per_px: float) -> float:
    # scale_factor is mm per pixel; px per mm is 1/scale_factor
    if scale_factor_mm_per_px and scale_factor_mm_per_px > 0:
        return mm / scale_factor_mm_per_px
    return mm * 2.0  # Fallback heuristic


def draw_scale_bar(painter: QPainter,
                   tile_width: int,
                   tile_height: int,
                   gutter: int,
                   scale_factor_mm_per_px: float,
                   units: str,
                   location: str,
                   length_in: float,
                   length_cm: float,
                   opacity_percent: int,
                   thickness_mm: float = 5.0,
                   padding_mm: float = 5.0):
    """
    Draw a scale bar with alternating dark/light blocks.

    - Inches: 1/4" blocks for first inch, then 1/2" blocks.
    - Metric: 5mm blocks for first 3cm, then 1cm blocks.
    - Location: "Page-<dir>" or "Gutter-<dir>", dir in {N, NE, E, SE, S, SW, W, NW}.
    """
    try:
        # Compute target length in pixels
        if units.lower() == 'inches':
            total_mm = length_in * 25.4
        else:
            total_mm = length_cm * 10.0  # cm to mm

        total_px = int(round(_mm_to_px(total_mm, scale_factor_mm_per_px)))
        thickness_px = int(round(_mm_to_px(thickness_mm, scale_factor_mm_per_px)))
        padding_px = int(round(_mm_to_px(padding_mm, scale_factor_mm_per_px)))

        # Determine orientation and base rect according to location
        loc_parts = (location or 'Page-S').split('-')
        zone = (loc_parts[0] if len(loc_parts) > 0 else 'Page').lower()
        dir8 = (loc_parts[1] if len(loc_parts) > 1 else 'S').upper()

        # Compute printable rect
        printable_x = gutter
        printable_y = gutter
        printable_w = max(0, tile_width - 2 * gutter)
        printable_h = max(0, tile_height - 2 * gutter)

        # Base rect where the scale bar will be placed
        # Horizontal by default for N/S and corners; vertical for E/W
        horizontal = dir8 in ('N', 'NE', 'NW', 'S', 'SE', 'SW')

        if zone == 'page':
            if horizontal:
                x = printable_x + padding_px
                w = max(0, min(total_px, printable_w - 2 * padding_px))
                h = min(thickness_px, max(0, printable_h - 2 * padding_px))
                if dir8 in ('N', 'NE', 'NW'):
                    y = printable_y + padding_px
                else:
                    y = printable_y + printable_h - padding_px - h
            else:
                y = printable_y + padding_px
                h = max(0, min(total_px, printable_h - 2 * padding_px))
                w = min(thickness_px, max(0, printable_w - 2 * padding_px))
                if dir8 == 'E':
                    x = printable_x + printable_w - padding_px - w
                else:  # 'W'
                    x = printable_x + padding_px
        else:  # Gutter zone
            if horizontal:
                x = padding_px
                w = max(0, min(total_px, tile_width - 2 * padding_px))
                h = min(thickness_px, max(0, gutter - padding_px))
                if dir8 in ('N', 'NE', 'NW'):
                    y = max(0, gutter - h - padding_px)
                else:
                    y = tile_height - max(0, gutter - padding_px)
            else:
                y = padding_px
                h = max(0, min(total_px, tile_height - 2 * padding_px))
                w = min(thickness_px, max(0, gutter - padding_px))
                if dir8 == 'E':
                    x = tile_width - max(0, gutter - padding_px)
                else:
                    x = max(0, gutter - w - padding_px)

        bar_rect = QRect(int(x), int(y), int(w), int(h)) if horizontal else QRect(int(x), int(y), int(w), int(h))
        if bar_rect.width() <= 0 or bar_rect.height() <= 0:
            return

        # Save painter state and set opacity
        painter.save()
        painter.setOpacity(max(0.0, min(1.0, opacity_percent / 100.0)))

        # Build segment lengths in pixels
        segs = []
        if units.lower() == 'inches':
            qtr_px = _mm_to_px(25.4 / 4.0, scale_factor_mm_per_px)
            half_px = _mm_to_px(25.4 / 2.0, scale_factor_mm_per_px)
            one_in_px = _mm_to_px(25.4, scale_factor_mm_per_px)
            remaining = total_px
            # First 1 inch: 1/4 inch blocks
            first_span = min(remaining, int(round(one_in_px)))
            n_qtrs = max(1, int(round(first_span / qtr_px)))
            for _ in range(n_qtrs):
                segs.append(int(round(qtr_px)))
            remaining -= first_span
            # After: 1/2 inch blocks
            if remaining > 0:
                n_halves = max(1, int(round(remaining / half_px)))
                for _ in range(n_halves):
                    segs.append(int(round(half_px)))
        else:
            half_cm_px = _mm_to_px(5.0, scale_factor_mm_per_px)  # 5mm
            one_cm_px = _mm_to_px(10.0, scale_factor_mm_per_px)  # 1cm
            three_cm_px = _mm_to_px(30.0, scale_factor_mm_per_px)
            remaining = total_px
            # First 3 cm: 5mm blocks
            first_span = min(remaining, int(round(three_cm_px)))
            n_half_cm = max(1, int(round(first_span / half_cm_px)))
            for _ in range(n_half_cm):
                segs.append(int(round(half_cm_px)))
            remaining -= first_span
            # After: 1 cm blocks
            if remaining > 0:
                n_cm = max(1, int(round(remaining / one_cm_px)))
                for _ in range(n_cm):
                    segs.append(int(round(one_cm_px)))

        # Draw alternating blocks
        dark = True
        curr = 0
        total_drawn = 0
        for s in segs:
            if horizontal:
                seg_rect = QRect(bar_rect.left() + curr, bar_rect.top(), min(s, bar_rect.width() - curr), bar_rect.height())
            else:
                seg_rect = QRect(bar_rect.left(), bar_rect.top() + curr, bar_rect.width(), min(s, bar_rect.height() - curr))
            if seg_rect.width() <= 0 or seg_rect.height() <= 0:
                break
            color = QColor(0, 0, 0) if dark else QColor(255, 255, 255)
            painter.fillRect(seg_rect, color)
            curr += s
            total_drawn += s
            dark = not dark
            if curr >= (bar_rect.width() if horizontal else bar_rect.height()):
                break

        painter.restore()
    except Exception:
        # Fail silently to avoid breaking export
        painter.restore()
