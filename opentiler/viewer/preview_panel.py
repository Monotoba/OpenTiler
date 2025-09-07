"""
Preview panel for showing tiled layout preview.
"""

from PySide6.QtCore import QMarginsF, QPoint, QRect, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (QFrame, QLabel, QScrollArea, QSizePolicy,
                               QVBoxLayout, QWidget)

from ..dialogs.page_viewer_dialog import ClickablePageThumbnail
from ..settings.config import config
from ..utils.helpers import compute_tile_layout, summarize_page_grid
from ..utils.metadata_page import MetadataPageGenerator, create_document_info
from ..utils.overlays import draw_scale_bar


class PreviewPanel(QWidget):
    """Panel for showing real-time tile preview."""

    def __init__(self):
        super().__init__()
        self.tile_count = 0
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("Page Thumbnails")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Scrollable area for page thumbnails - maximize vertical space
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setMinimumHeight(200)  # Minimum height for usability
        # Set size policy to expand and take maximum available space
        self.preview_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container widget for thumbnails
        self.thumbnail_container = QWidget()
        self.thumbnail_layout = QVBoxLayout(self.thumbnail_container)
        self.thumbnail_layout.setSpacing(10)
        self.thumbnail_layout.setContentsMargins(5, 5, 5, 5)

        # Default message
        self.no_pages_label = QLabel("No pages generated")
        self.no_pages_label.setAlignment(Qt.AlignCenter)
        self.no_pages_label.setStyleSheet("color: gray; font-style: italic;")
        self.thumbnail_layout.addWidget(self.no_pages_label)

        self.preview_scroll.setWidget(self.thumbnail_container)

        # Add scroll area with stretch factor to take maximum space
        layout.addWidget(
            self.preview_scroll, 1
        )  # Stretch factor 1 = take all available space

        # Info labels at bottom (no stretch)
        self.info_label = QLabel("Pages: 0")
        layout.addWidget(self.info_label, 0)  # No stretch = fixed size

        self.scale_label = QLabel("Scale: Not set")
        layout.addWidget(self.scale_label, 0)  # No stretch = fixed size

        # Composite mode hint (hidden by default)
        self.composite_hint_label = QLabel(
            "Composite export: overview only — tiles are for cut-and-assemble."
        )
        self.composite_hint_label.setStyleSheet(
            "color: #555; font-style: italic; padding: 4px;"
        )
        self.composite_hint_label.setVisible(False)
        layout.addWidget(self.composite_hint_label, 0)

        # Printer-area preview hint (hidden by default)
        self.printer_area_hint_label = QLabel(
            "Preview uses printer's printable area (mirrors print)."
        )
        self.printer_area_hint_label.setStyleSheet(
            "color: #555; font-style: italic; padding: 2px;"
        )
        self.printer_area_hint_label.setVisible(False)
        layout.addWidget(self.printer_area_hint_label, 0)

        # Remove the addStretch() call - we want the scroll area to take all space
        self.setLayout(layout)

    def update_preview(
        self,
        pixmap,
        page_grid=None,
        scale_factor=1.0,
        scale_info=None,
        document_info=None,
        printer_area: bool = False,
        measurements=None,
    ):
        """Update the preview with individual page thumbnails."""
        # Clear existing thumbnails
        self._clear_thumbnails()

        if not pixmap or not page_grid:
            self.no_pages_label.show()
            self.info_label.setText("Pages: 0")
            self.scale_label.setText("Scale: Not set")
            self.printer_area_hint_label.setVisible(bool(printer_area))
            return

        self.no_pages_label.hide()
        # Toggle printer-area preview hint
        self.printer_area_hint_label.setVisible(bool(printer_area))

        # Check if metadata page should be included and its position
        include_metadata = config.get_include_metadata_page()
        metadata_position = config.get_metadata_page_position()

        page_number = 1

        # Add metadata page at the beginning if configured
        if include_metadata and metadata_position == "first":
            metadata_thumbnail = self._create_metadata_thumbnail(
                pixmap, page_grid, scale_factor, document_info
            )
            if metadata_thumbnail:
                self.thumbnail_layout.addWidget(metadata_thumbnail)
                page_number += 1

        # Generate thumbnail for each tile page
        for i, page in enumerate(page_grid):
            page_thumbnail = self._create_page_thumbnail(
                pixmap,
                page,
                page_number,
                scale_info,
                scale_factor,
                measurements=measurements or [],
            )
            self.thumbnail_layout.addWidget(page_thumbnail)
            page_number += 1

        # Add metadata page at the end if configured
        if include_metadata and metadata_position == "last":
            metadata_thumbnail = self._create_metadata_thumbnail(
                pixmap, page_grid, scale_factor, document_info
            )
            if metadata_thumbnail:
                self.thumbnail_layout.addWidget(metadata_thumbnail)

        # Add stretch at the end
        self.thumbnail_layout.addStretch()

        # Update info
        tile_count = len(page_grid)
        total_pages = tile_count + (1 if include_metadata else 0)

        if include_metadata:
            self.info_label.setText(
                f"Pages: {total_pages} ({tile_count} tiles + 1 metadata)"
            )
        else:
            self.info_label.setText(f"Pages: {tile_count}")

        if scale_factor != 1.0:
            self.scale_label.setText(f"Scale: {scale_factor:.6f} mm/px")
        else:
            self.scale_label.setText("Scale: Not set")

    def set_composite_hint_visible(self, visible: bool):
        """Show/hide a subtle hint about composite export semantics."""
        self.composite_hint_label.setVisible(bool(visible))

    def _clear_thumbnails(self):
        """Clear all existing thumbnail widgets."""
        # Remove all widgets except the no_pages_label
        while self.thumbnail_layout.count() > 0:
            child = self.thumbnail_layout.takeAt(0)
            if child.widget() and child.widget() != self.no_pages_label:
                child.widget().deleteLater()

    def _create_page_thumbnail(
        self,
        source_pixmap,
        page,
        page_number,
        scale_info=None,
        scale_factor: float = 1.0,
        measurements=None,
    ):
        """Create a thumbnail widget for a single page."""
        # Compute standardized tile layout (shared with print path)
        layout = compute_tile_layout(
            page, source_pixmap.width(), source_pixmap.height()
        )
        width = layout["tile_width"]
        height = layout["tile_height"]
        # gutter value is computed in layout; no direct use here

        # Create a blank page pixmap with the correct page dimensions
        # This maintains the page orientation and shows empty areas
        page_pixmap = QPixmap(int(width), int(height))
        page_pixmap.fill(Qt.white)  # Fill with white background

        # Draw the document content onto the page, clipped to printable area
        painter = QPainter(page_pixmap)

        # Clip to printable area only (no trimming of content)
        inner = layout["printable_rect"]
        painter.setClipRect(inner)
        if layout["source_rect"].width() > 0 and layout["source_rect"].height() > 0:
            source_crop = source_pixmap.copy(layout["source_rect"])
            dx, dy = layout["dest_pos"]
            painter.drawPixmap(int(dx), int(dy), source_crop)

        # Overlay non-printed bands (right/bottom) per printer calibration to signal printed coverage
        try:
            from ..settings.config import config as app_config

            ori = "landscape" if float(width) >= float(height) else "portrait"
            h_mm, v_mm = app_config.get_print_calibration(ori)
            calib_x_px = max(
                0,
                int(
                    round(
                        float(h_mm) / float(scale_factor)
                        if scale_factor and scale_factor > 0
                        else 0
                    )
                ),
            )
            calib_y_px = max(
                0,
                int(
                    round(
                        float(v_mm) / float(scale_factor)
                        if scale_factor and scale_factor > 0
                        else 0
                    )
                ),
            )

            painter.save()
            painter.setOpacity(0.35)
            painter.setClipping(
                False
            )  # ensure overlay draws over content for visibility
            # Right band
            if calib_x_px > 0:
                rb_x = inner.x() + max(0, inner.width() - calib_x_px)
                rb_w = min(calib_x_px, inner.width())
                painter.fillRect(
                    QRect(rb_x, inner.y(), rb_w, inner.height()), QColor(255, 255, 255)
                )
            # Bottom band
            if calib_y_px > 0:
                bb_y = inner.y() + max(0, inner.height() - calib_y_px)
                bb_h = min(calib_y_px, inner.height())
                painter.fillRect(
                    QRect(inner.x(), bb_y, inner.width(), bb_h), QColor(255, 255, 255)
                )
            painter.restore()

            # Draw registration marks at calibrated inner corners to match print visuals
            if app_config.get_reg_marks_print():
                px_per_mm = (
                    (1.0 / float(scale_factor))
                    if scale_factor and scale_factor > 0
                    else 2.0
                )
                diameter_mm = app_config.get_reg_mark_diameter_mm()
                cross_mm = app_config.get_reg_mark_crosshair_mm()
                radius_px = max(1, int(round((diameter_mm * px_per_mm) / 2.0)))
                cross_len_px = max(1, int(round(cross_mm * px_per_mm)))

                # Calibrated inner rect used for centers
                cal_inner_w = max(0, inner.width() - calib_x_px)
                cal_inner_h = max(0, inner.height() - calib_y_px)
                left = inner.x()
                top = inner.y()
                right = inner.x() + cal_inner_w - 1
                bottom = inner.y() + cal_inner_h - 1

                painter.save()
                painter.setPen(QPen(QColor(0, 0, 0), 1))
                for cx, cy in [
                    (left, top),
                    (right, top),
                    (left, bottom),
                    (right, bottom),
                ]:
                    painter.drawEllipse(
                        cx - radius_px, cy - radius_px, radius_px * 2, radius_px * 2
                    )
                    painter.drawLine(cx - cross_len_px, cy, cx + cross_len_px, cy)
                    painter.drawLine(cx, cy - cross_len_px, cx, cy + cross_len_px)
                painter.restore()
        except Exception:
            pass

        painter.end()

        # Compute calibrated inner rect for display-only (matches printed coverage)
        inner = layout["printable_rect"]
        try:
            from ..settings.config import config as app_config

            ori = "landscape" if float(width) >= float(height) else "portrait"
            h_mm, v_mm = app_config.get_print_calibration(ori)
            calib_x_px = max(
                0,
                int(
                    round(
                        float(h_mm) / float(scale_factor)
                        if scale_factor and scale_factor > 0
                        else 0
                    )
                ),
            )
            calib_y_px = max(
                0,
                int(
                    round(
                        float(v_mm) / float(scale_factor)
                        if scale_factor and scale_factor > 0
                        else 0
                    )
                ),
            )
        except Exception:
            calib_x_px = 0
            calib_y_px = 0

        cal_inner_rect = QRect(
            inner.x(),
            inner.y(),
            max(1, inner.width() - calib_x_px),
            max(1, inner.height() - calib_y_px),
        )

        # Crop a display-only pixmap to the calibrated inner area so tiles butt at marks in preview
        display_pixmap = page_pixmap.copy(cal_inner_rect)

        # Draw registration marks at corners of the display pixmap to match print
        try:
            from ..settings.config import config as app_config

            if app_config.get_reg_marks_print():
                px_per_mm = (
                    (1.0 / float(scale_factor))
                    if scale_factor and scale_factor > 0
                    else 2.0
                )
                diameter_mm = app_config.get_reg_mark_diameter_mm()
                cross_mm = app_config.get_reg_mark_crosshair_mm()
                radius_px = max(1, int(round((diameter_mm * px_per_mm) / 2.0)))
                cross_len_px = max(1, int(round(cross_mm * px_per_mm)))

                dp = QPixmap(display_pixmap)
                dp_p = QPainter(dp)
                dp_p.setPen(QPen(QColor(0, 0, 0), 1))
                w2 = dp.width()
                h2 = dp.height()
                for cx, cy in [(0, 0), (w2 - 1, 0), (0, h2 - 1), (w2 - 1, h2 - 1)]:
                    dp_p.drawEllipse(
                        cx - radius_px, cy - radius_px, radius_px * 2, radius_px * 2
                    )
                    dp_p.drawLine(cx - cross_len_px, cy, cx + cross_len_px, cy)
                    dp_p.drawLine(cx, cy - cross_len_px, cx, cy + cross_len_px)
                dp_p.end()
                display_pixmap = dp
        except Exception:
            pass

        # Draw all measurements on the display pixmap (thumbnail overlay)
        try:
            if measurements:
                dp = QPixmap(display_pixmap)
                dp_p = QPainter(dp)
                page_x = page.get("x", 0)
                page_y = page.get("y", 0)
                page_w = max(1.0, float(page.get("width", 1)))
                page_h = max(1.0, float(page.get("height", 1)))
                sx = page_pixmap.width() / page_w
                sy = page_pixmap.height() / page_h
                # Map to display by subtracting calibrated inner offset
                ox = cal_inner_rect.x()
                oy = cal_inner_rect.y()
                for m in measurements:
                    p1 = m.get("p1")
                    p2 = m.get("p2")
                    label = m.get("text", "")
                    if not (p1 and p2):
                        continue
                    # skip if no intersection
                    minx, maxx = min(p1[0], p2[0]), max(p1[0], p2[0])
                    miny, maxy = min(p1[1], p2[1]), max(p1[1], p2[1])
                    if (
                        maxx < page_x
                        or minx > page_x + page_w
                        or maxy < page_y
                        or miny > page_y + page_h
                    ):
                        continue
                    p1x = (p1[0] - page_x) * sx - ox
                    p1y = (p1[1] - page_y) * sy - oy
                    p2x = (p2[0] - page_x) * sx - ox
                    p2y = (p2[1] - page_y) * sy - oy
                    pen = QPen(QColor(255, 0, 0), 2)
                    pen.setStyle(Qt.CustomDashLine)
                    pen.setDashPattern([8, 3, 2, 3, 2, 3])
                    dp_p.setPen(pen)
                    dp_p.drawLine(int(p1x), int(p1y), int(p2x), int(p2y))
                    # endpoints
                    r = 3
                    dp_p.setBrush(QColor(255, 255, 255, 220))
                    dp_p.setPen(QPen(QColor(0, 0, 0), 1))
                    dp_p.drawEllipse(int(p1x - r), int(p1y - r), r * 2, r * 2)
                    dp_p.drawEllipse(int(p2x - r), int(p2y - r), r * 2, r * 2)
                    if label:
                        font = dp_p.font()
                        font.setPointSize(8)
                        font.setBold(True)
                        dp_p.setFont(font)
                        dp_p.setPen(QPen(QColor(255, 0, 0), 1))
                        midx = (p1x + p2x) / 2
                        midy = (p1y + p2y) / 2
                        dx = p2x - p1x
                        dy = p2y - p1y
                        dist = max(1.0, (dx * dx + dy * dy) ** 0.5)
                        if dist > 1:
                            ux, uy = dx / dist, dy / dist
                            px, py = -uy, ux
                        else:
                            px, py = 0, -1
                        text_rect = dp_p.fontMetrics().boundingRect(label)
                        if dist >= (text_rect.width() + 12):
                            tx = midx - text_rect.width() / 2 + px * 8
                            ty = midy + py * 8
                        else:
                            tx = p2x - text_rect.width() / 2 + px * 8
                            ty = p2y + py * 8 - text_rect.height() / 2
                        bg = text_rect.adjusted(-3, -2, 3, 2)
                        bg.moveTopLeft(QPoint(int(tx - 3), int(ty - 2)))
                        dp_p.fillRect(bg, QColor(255, 255, 255, 200))
                        dp_p.drawText(int(tx), int(ty + text_rect.height()), label)
                dp_p.end()
                display_pixmap = dp
        except Exception:
            pass

        # Create thumbnail widget
        thumbnail_widget = QFrame()
        thumbnail_widget.setFrameStyle(QFrame.Box)
        thumbnail_widget.setStyleSheet("border: 1px solid lightgray; margin: 2px;")

        layout = QVBoxLayout(thumbnail_widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Page number label
        page_label = QLabel(f"Page {page_number}")
        page_label.setAlignment(Qt.AlignCenter)
        page_label.setStyleSheet("font-weight: bold; color: #333;")
        layout.addWidget(page_label)

        # Clickable thumbnail image
        # Scale thumbnail to fit preview area while maintaining aspect ratio
        max_width = 150
        max_height = 200
        scaled_thumbnail = display_pixmap.scaled(
            max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # Create clickable thumbnail that opens in floating viewer
        thumbnail_label = ClickablePageThumbnail(
            page_pixmap,  # Full-size page for viewer (retain full for detail view)
            page_number,
            page,  # Page info dict
            self,
            scale_info,  # Scale info for page viewer
            measurements=measurements or [],
        )
        thumbnail_label.setPixmap(scaled_thumbnail)
        thumbnail_label.setAlignment(Qt.AlignCenter)
        thumbnail_label.setToolTip(f"Click to view Page {page_number} in detail")
        layout.addWidget(thumbnail_label)

        return thumbnail_widget

    def _create_metadata_thumbnail(
        self, source_pixmap, page_grid, scale_factor, document_info
    ):
        """Create a thumbnail widget for the metadata page."""
        try:
            # Create metadata page generator
            metadata_generator = MetadataPageGenerator()

            # Calculate grid dimensions
            summary = summarize_page_grid(page_grid or [])
            tiles_x = summary["tiles_x"]
            tiles_y = summary["tiles_y"]

            # Create document info for metadata page
            if document_info:
                doc_info = document_info.copy()
                doc_info.update(
                    {
                        "doc_width": source_pixmap.width(),
                        "doc_height": source_pixmap.height(),
                        "tiles_x": tiles_x,
                        "tiles_y": tiles_y,
                        "total_tiles": summary["total_tiles"],
                        "scale_factor": scale_factor,
                    }
                )
            else:
                doc_info = create_document_info(
                    document_name="Preview Document",
                    original_file="",
                    scale_factor=scale_factor,
                    units=config.get_default_units(),
                    doc_width=source_pixmap.width(),
                    doc_height=source_pixmap.height(),
                    tiles_x=tiles_x,
                    tiles_y=tiles_y,
                    page_size=config.get_default_page_size(),
                    gutter_size=config.get_gutter_size_mm(),
                )

            # Add source pixmap and page grid for plan view
            doc_info["source_pixmap"] = source_pixmap
            doc_info["page_grid"] = page_grid

            # Generate metadata page sized to selected page size AND orientation
            # Use printer's printable area (paintRect) to mirror print behavior.
            from PySide6.QtGui import QPageLayout, QPageSize
            from PySide6.QtPrintSupport import QPrinter

            from ..settings.config import config as app_config

            page_size_name = app_config.get_default_page_size()
            orientation_pref = app_config.get_page_orientation()

            # Decide orientation: honor explicit setting; for 'auto', infer from grid/tile shape
            if orientation_pref == "landscape":
                orientation = QPageLayout.Landscape
            elif orientation_pref == "portrait":
                orientation = QPageLayout.Portrait
            else:
                # Auto: prefer orientation of first tile if available; else doc aspect
                if page_grid and len(page_grid) > 0:
                    first = page_grid[0]
                    orientation = (
                        QPageLayout.Landscape
                        if float(first.get("width", 0)) >= float(first.get("height", 0))
                        else QPageLayout.Portrait
                    )
                else:
                    orientation = (
                        QPageLayout.Landscape
                        if source_pixmap.width() >= source_pixmap.height()
                        else QPageLayout.Portrait
                    )

            # Compute printable mm via a temp printer configured to the selected page
            try:
                qps_id = (
                    QPageSize.A4
                    if page_size_name is None
                    else QPageSize(QPageSize.A4).id()
                )
            except Exception:
                qps_id = QPageSize.A4
            # Map by name using MainWindow's helper mapping convention (duplicated minimal)
            name_to_id = {
                "A0": QPageSize.A0,
                "A1": QPageSize.A1,
                "A2": QPageSize.A2,
                "A3": QPageSize.A3,
                "A4": QPageSize.A4,
                "Letter": QPageSize.Letter,
                "Legal": QPageSize.Legal,
                "Tabloid": QPageSize.Tabloid,
            }
            qps_id = name_to_id.get((page_size_name or "A4").strip(), QPageSize.A4)

            tmp_printer = QPrinter(QPrinter.HighResolution)
            tmp_printer.setPageSize(QPageSize(qps_id))
            tmp_printer.setPageLayout(
                QPageLayout(
                    QPageSize(qps_id),
                    orientation,
                    QMarginsF(0, 0, 0, 0),
                    QPageLayout.Millimeter,
                )
            )
            pr_mm = tmp_printer.pageLayout().paintRect(QPageLayout.Millimeter)

            # Use 300 DPI equivalent: 11.811 px/mm for preview rendering
            px_per_mm = 11.811
            meta_w_px = max(1, int(round(pr_mm.width() * px_per_mm)))
            meta_h_px = max(1, int(round(pr_mm.height() * px_per_mm)))
            metadata_pixmap = metadata_generator.generate_metadata_page(
                doc_info, QSize(meta_w_px, meta_h_px)
            )

            # Create thumbnail widget
            thumbnail_widget = QFrame()
            thumbnail_widget.setFrameStyle(QFrame.Box)
            thumbnail_widget.setStyleSheet(
                "border: 2px solid #0078d4; margin: 2px; background-color: #f0f8ff;"
            )

            layout = QVBoxLayout(thumbnail_widget)
            layout.setContentsMargins(5, 5, 5, 5)

            # Metadata page label
            page_label = QLabel("Metadata Page")
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setStyleSheet("font-weight: bold; color: #0078d4;")
            layout.addWidget(page_label)

            # Clickable thumbnail image
            max_width = 150
            max_height = 200
            scaled_thumbnail = metadata_pixmap.scaled(
                max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            # Create clickable thumbnail for metadata page
            thumbnail_label = ClickablePageThumbnail(
                metadata_pixmap,  # Full-size metadata page for viewer
                "Metadata",  # Page identifier
                {
                    "type": "metadata",
                    "width": metadata_pixmap.width(),
                    "height": metadata_pixmap.height(),
                },  # Page info
                self,
                None,  # No scale info for metadata page
            )
            thumbnail_label.setPixmap(scaled_thumbnail)
            thumbnail_label.setAlignment(Qt.AlignCenter)
            thumbnail_label.setToolTip("Click to view Metadata Page in detail")
            layout.addWidget(thumbnail_label)

            return thumbnail_widget

        except Exception as e:
            print(f"Error creating metadata thumbnail: {str(e)}")
            return None

    def _add_page_decorations(
        self,
        page_pixmap,
        page_number,
        gutter_size,
        page_info=None,
        scale_info=None,
        scale_factor: float = 1.0,
    ):
        """Add crop marks, gutter lines, page number, and scale line/text to page thumbnail."""
        # Import config here to avoid circular imports
        from ..settings.config import config

        # Create a copy to draw on
        result = QPixmap(page_pixmap)
        painter = QPainter(result)

        width = result.width()
        height = result.height()

        # Draw gutter lines (blue) - printable area boundary
        if (
            gutter_size > 1 and config.get_gutter_lines_display()
        ):  # Only if gutter is visible and enabled
            gutter_pen = QPen(QColor(0, 100, 255), 2)  # Blue for gutter
            painter.setPen(gutter_pen)

            # Draw gutter rectangle
            painter.drawRect(
                int(gutter_size),
                int(gutter_size),
                int(width - 2 * gutter_size),
                int(height - 2 * gutter_size),
            )

        # Draw crop marks at gutter intersections (not page corners)
        if config.get_crop_marks_display():
            crop_pen = QPen(QColor(0, 0, 0), 1)  # Black for crop marks
            painter.setPen(crop_pen)

            crop_length = 8

            # Crop marks at gutter line intersections
            gutter_left = int(gutter_size)
            gutter_right = int(width - gutter_size)
            gutter_top = int(gutter_size)
            gutter_bottom = int(height - gutter_size)

            # Top-left gutter corner
            painter.drawLine(
                gutter_left - crop_length,
                gutter_top,
                gutter_left + crop_length,
                gutter_top,
            )
            painter.drawLine(
                gutter_left,
                gutter_top - crop_length,
                gutter_left,
                gutter_top + crop_length,
            )

            # Top-right gutter corner
            painter.drawLine(
                gutter_right - crop_length,
                gutter_top,
                gutter_right + crop_length,
                gutter_top,
            )
            painter.drawLine(
                gutter_right,
                gutter_top - crop_length,
                gutter_right,
                gutter_top + crop_length,
            )

            # Bottom-left gutter corner
            painter.drawLine(
                gutter_left - crop_length,
                gutter_bottom,
                gutter_left + crop_length,
                gutter_bottom,
            )
            painter.drawLine(
                gutter_left,
                gutter_bottom - crop_length,
                gutter_left,
                gutter_bottom + crop_length,
            )

            # Bottom-right gutter corner
            painter.drawLine(
                gutter_right - crop_length,
                gutter_bottom,
                gutter_right + crop_length,
                gutter_bottom,
            )
            painter.drawLine(
                gutter_right,
                gutter_bottom - crop_length,
                gutter_right,
                gutter_bottom + crop_length,
            )

        # Registration marks at printable-area corners (quarters), if enabled
        if config.get_reg_marks_display() and gutter_size > 0:
            try:
                # Convert mm to pixels using scale_factor (mm/px)
                # Fallback: if scale_factor is invalid, use a small default size
                diameter_mm = config.get_reg_mark_diameter_mm()
                cross_mm = config.get_reg_mark_crosshair_mm()
                px_per_mm = (
                    (1.0 / scale_factor) if scale_factor and scale_factor > 0 else 2.0
                )
                radius_px = int((diameter_mm * px_per_mm) / 2)
                cross_len_px = int(cross_mm * px_per_mm)

                # Clip to printable rect so only quarters are visible per tile
                printable_rect = QRect(
                    int(gutter_size),
                    int(gutter_size),
                    int(width - 2 * gutter_size),
                    int(height - 2 * gutter_size),
                )
                painter.save()
                painter.setClipRect(printable_rect)
                painter.setPen(QPen(QColor(0, 0, 0), 1))

                centers = [
                    (int(gutter_size), int(gutter_size)),
                    (int(width - gutter_size), int(gutter_size)),
                    (int(gutter_size), int(height - gutter_size)),
                    (int(width - gutter_size), int(height - gutter_size)),
                ]

                for cx, cy in centers:
                    # Circle
                    painter.drawEllipse(
                        cx - radius_px, cy - radius_px, radius_px * 2, radius_px * 2
                    )
                    # Crosshair
                    painter.drawLine(cx - cross_len_px, cy, cx + cross_len_px, cy)
                    painter.drawLine(cx, cy - cross_len_px, cx, cy + cross_len_px)

                painter.restore()
            except Exception:
                pass

        # Draw page number based on settings
        if config.get_page_indicator_display():
            # Get settings
            font_size = config.get_page_indicator_font_size()
            font_color = config.get_page_indicator_font_color()
            font_style = config.get_page_indicator_font_style()
            alpha = config.get_page_indicator_alpha()
            position = config.get_page_indicator_position()

            # Set up font - use larger size for thumbnails to ensure visibility
            font = QFont()
            thumbnail_font_size = max(
                8, min(font_size, 14)
            )  # Ensure readable size for thumbnails
            font.setPointSize(thumbnail_font_size)
            if font_style == "bold":
                font.setBold(True)
            elif font_style == "italic":
                font.setItalic(True)
            painter.setFont(font)

            # Set up color with alpha
            color = QColor(font_color)
            color.setAlpha(alpha)

            # Calculate text position within printable area (inside gutters)
            text = f"P{page_number}"
            text_rect = painter.fontMetrics().boundingRect(text)
            margin = 3  # Smaller margin for thumbnails

            # Define printable area (inside gutters)
            printable_x = gutter_size
            printable_y = gutter_size
            printable_width = width - (2 * gutter_size)
            printable_height = height - (2 * gutter_size)

            if position == "upper-left":
                text_x = printable_x + margin
                text_y = printable_y + margin + text_rect.height()
            elif position == "upper-right":
                text_x = printable_x + printable_width - text_rect.width() - margin
                text_y = printable_y + margin + text_rect.height()
            elif position == "bottom-left":
                text_x = printable_x + margin
                text_y = printable_y + printable_height - margin
            elif position == "bottom-right":
                text_x = printable_x + printable_width - text_rect.width() - margin
                text_y = printable_y + printable_height - margin
            else:  # center-page
                text_x = printable_x + (printable_width - text_rect.width()) // 2
                text_y = printable_y + (printable_height + text_rect.height()) // 2

            # Draw text with outline for visibility (if alpha is high enough)
            if alpha > 128:  # Only draw outline if text is reasonably opaque
                outline_color = QColor(0, 0, 0)
                outline_color.setAlpha(
                    min(255, alpha + 50)
                )  # Slightly more opaque outline
                painter.setPen(QPen(outline_color, 1))
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            painter.drawText(int(text_x + dx), int(text_y + dy), text)

            # Draw main text with alpha
            painter.setPen(QPen(color, 1))
            painter.drawText(int(text_x), int(text_y), text)

        # Draw scale bar overlay (preview)
        if config.get_scale_bar_display():
            try:
                units = config.get_default_units()
                location = config.get_scale_bar_location()
                opacity = config.get_scale_bar_opacity()
                length_in = config.get_scale_bar_length_in()
                length_cm = config.get_scale_bar_length_cm()
                thickness_mm = config.get_scale_bar_thickness_mm()
                padding_mm = config.get_scale_bar_padding_mm()
                draw_scale_bar(
                    painter,
                    width,
                    height,
                    int(gutter_size),
                    scale_factor,
                    units,
                    location,
                    length_in,
                    length_cm,
                    opacity,
                    thickness_mm,
                    padding_mm,
                )
            except Exception:
                pass

        # Draw scale line and text if this page contains the scaling points
        if scale_info and page_info:
            self._draw_scale_line_on_page(painter, scale_info, page_info, width, height)

        painter.end()
        return result

    def _draw_scale_line_on_page(
        self, painter, scale_info, page_info, page_width, page_height
    ):
        """Draw scale line and text on page if it contains the scaling points."""
        # Import config here to avoid circular imports
        from ..settings.config import config

        # Only draw if scale line display is enabled
        if not config.get_scale_line_display():
            return

        # Extract scale information
        point1 = scale_info.get("point1")
        point2 = scale_info.get("point2")
        measurement_text = scale_info.get("measurement_text", "")

        if not (point1 and point2):
            return

        # Get page boundaries in document coordinates
        page_x = page_info["x"]
        page_y = page_info["y"]
        page_doc_width = page_info["width"]
        page_doc_height = page_info["height"]

        # Check if either scaling point is within this page
        p1_in_page = (
            page_x <= point1[0] <= page_x + page_doc_width
            and page_y <= point1[1] <= page_y + page_doc_height
        )
        p2_in_page = (
            page_x <= point2[0] <= page_x + page_doc_width
            and page_y <= point2[1] <= page_y + page_doc_height
        )

        # Check if the line crosses this page
        line_crosses_page = self._line_intersects_page(point1, point2, page_info)

        if not (p1_in_page or p2_in_page or line_crosses_page):
            return

        # Convert document coordinates to page coordinates
        p1_page_x = point1[0] - page_x
        p1_page_y = point1[1] - page_y
        p2_page_x = point2[0] - page_x
        p2_page_y = point2[1] - page_y

        # Scale to page pixmap coordinates
        scale_x = page_width / page_doc_width
        scale_y = page_height / page_doc_height

        p1_x = p1_page_x * scale_x
        p1_y = p1_page_y * scale_y
        p2_x = p2_page_x * scale_x
        p2_y = p2_page_y * scale_y

        # Set up pen for scale line
        pen = QPen(QColor(255, 0, 0), 2)  # Red color, 2px width
        # Dot–dash–dot pattern
        pen.setStyle(Qt.CustomDashLine)
        pen.setDashPattern([8, 3, 2, 3, 2, 3])
        painter.setPen(pen)

        # Draw both scale line and/or datum line according to settings
        # Scale line style
        if config.get_scale_line_display():
            painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

        # Datum line style
        if config.get_datum_line_display():
            datum_pen = QPen(QColor(config.get_datum_line_color()), 2)
            style = str(config.get_datum_line_style()).lower()
            if style == "solid":
                datum_pen.setStyle(Qt.SolidLine)
            elif style == "dash":
                datum_pen.setStyle(Qt.DashLine)
            elif style == "dot":
                datum_pen.setStyle(Qt.DotLine)
            elif style == "dashdot":
                datum_pen.setStyle(Qt.DashDotLine)
            elif style == "dashdotdot":
                datum_pen.setStyle(Qt.DashDotDotLine)
            elif style == "dot-dash-dot":
                datum_pen.setStyle(Qt.CustomDashLine)
                datum_pen.setDashPattern([8, 3, 2, 3, 2, 3])
            painter.setPen(datum_pen)
            painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

        # Draw scale points
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        if p1_in_page:
            painter.drawEllipse(int(p1_x - 3), int(p1_y - 3), 6, 6)
        if p2_in_page:
            painter.drawEllipse(int(p2_x - 3), int(p2_y - 3), 6, 6)

        # Draw measurement text if enabled and line midpoint is in page
        if config.get_scale_text_display() and measurement_text:
            mid_x = (p1_x + p2_x) / 2
            mid_y = (p1_y + p2_y) / 2

            # Check if midpoint is within page bounds
            if 0 <= mid_x <= page_width and 0 <= mid_y <= page_height:
                # Set up font for measurement text (smaller for thumbnails)
                font = painter.font()
                font.setPointSize(8)
                font.setBold(True)
                painter.setFont(font)

                # Set up pen for red text
                text_pen = QPen(QColor(255, 0, 0), 1)
                painter.setPen(text_pen)

                # Calculate text position (above the line)
                text_rect = painter.fontMetrics().boundingRect(measurement_text)
                text_x = mid_x - text_rect.width() / 2
                text_y = mid_y - 8  # 8 pixels above the line

                # Draw background rectangle for better visibility
                bg_rect = text_rect.adjusted(-2, -1, 2, 1)
                bg_rect.moveTopLeft(
                    QPoint(int(text_x - 2), int(text_y - text_rect.height() - 1))
                )
                painter.fillRect(
                    bg_rect, QColor(255, 255, 255, 200)
                )  # Semi-transparent white

                # Draw the measurement text
                painter.drawText(int(text_x), int(text_y), measurement_text)

    def _line_intersects_page(self, point1, point2, page_info):
        """Check if a line intersects with the page boundaries."""
        # Simple bounding box intersection check
        page_x = page_info["x"]
        page_y = page_info["y"]
        page_right = page_x + page_info["width"]
        page_bottom = page_y + page_info["height"]

        # Line bounding box
        line_left = min(point1[0], point2[0])
        line_right = max(point1[0], point2[0])
        line_top = min(point1[1], point2[1])
        line_bottom = max(point1[1], point2[1])

        # Check if bounding boxes intersect
        return not (
            line_right < page_x
            or line_left > page_right
            or line_bottom < page_y
            or line_top > page_bottom
        )
