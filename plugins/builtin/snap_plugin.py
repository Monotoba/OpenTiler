#!/usr/bin/env python3
"""
OpenTiler Snap Plugin

This plugin demonstrates the hook system by implementing intelligent snap functionality
for measurements and drawing operations. It shows how plugins can hook into OpenTiler's
measurement system to provide enhanced functionality.
"""

import math
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (QCheckBox, QGroupBox, QHBoxLayout, QLabel,
                               QSpinBox, QVBoxLayout, QWidget)

from ..base_plugin import BasePlugin, PluginInfo
from ..content_access import AccessLevel
from ..hook_system import HookContext, HookHandler, HookType, get_hook_manager


class SnapHookHandler(HookHandler):
    """Hook handler for snap functionality."""

    def __init__(self, snap_plugin):
        self.snap_plugin = snap_plugin

    @property
    def supported_hooks(self) -> List[HookType]:
        return [
            HookType.MEASUREMENT_BEFORE_START,
            HookType.MEASUREMENT_BEFORE_UPDATE,
            HookType.RENDER_AFTER_DRAW,
            HookType.DOCUMENT_AFTER_LOAD,
        ]

    @property
    def priority(self) -> int:
        return 200  # Higher priority than automation for measurement hooks

    def handle_hook(self, context: HookContext) -> bool:
        """Handle hook events for snap functionality."""
        try:
            if context.hook_type == HookType.MEASUREMENT_BEFORE_START:
                return self._handle_measurement_start(context)
            elif context.hook_type == HookType.MEASUREMENT_BEFORE_UPDATE:
                return self._handle_measurement_update(context)
            elif context.hook_type == HookType.RENDER_AFTER_DRAW:
                return self._handle_render_snap_points(context)
            elif context.hook_type == HookType.DOCUMENT_AFTER_LOAD:
                return self._handle_document_loaded(context)

            return True

        except Exception as e:
            self.snap_plugin.log_error(f"Snap hook handling error: {e}")
            return False

    def _handle_measurement_start(self, context: HookContext) -> bool:
        """Handle measurement start with snap functionality."""
        if not self.snap_plugin.config.get("snap_enabled", True):
            return True

        start_point = context.data.get("start_point")
        if start_point and isinstance(start_point, QPointF):
            # Find snap point near the start point
            snap_point = self.snap_plugin.find_snap_point(start_point)
            if snap_point:
                # Update the start point to the snap point
                context.data["start_point"] = snap_point
                self.snap_plugin.log_info(
                    f"Snapped start point to {snap_point.x():.1f}, {snap_point.y():.1f}"
                )

        return True

    def _handle_measurement_update(self, context: HookContext) -> bool:
        """Handle measurement update with snap functionality."""
        if not self.snap_plugin.config.get("snap_enabled", True):
            return True

        current_point = context.data.get("current_point")
        if current_point and isinstance(current_point, QPointF):
            # Find snap point near the current point
            snap_point = self.snap_plugin.find_snap_point(current_point)
            if snap_point:
                # Update the current point to the snap point
                context.data["current_point"] = snap_point
                context.data["snapped"] = True

        return True

    def _handle_render_snap_points(self, context: HookContext) -> bool:
        """Render snap points as visual indicators."""
        if not self.snap_plugin.config.get("show_snap_points", True):
            return True

        painter = context.data.get("painter")
        if painter and isinstance(painter, QPainter):
            self.snap_plugin.render_snap_points(painter)

        return True

    def _handle_document_loaded(self, context: HookContext) -> bool:
        """Handle document loaded to analyze snap points."""
        self.snap_plugin.analyze_document_for_snap_points()
        return True


class SnapPlugin(BasePlugin):
    """
    OpenTiler Snap Plugin.

    Provides intelligent snap functionality for measurements and drawing operations.
    Demonstrates the hook system by intercepting measurement events and providing
    enhanced snap-to-point functionality.
    """

    @property
    def plugin_info(self) -> PluginInfo:
        """Return plugin information."""
        return PluginInfo(
            name="Snap",
            version="1.0.0",
            description="Intelligent snap functionality for measurements and drawing operations",
            author="OpenTiler Development Team",
            website="https://github.com/opentiler/opentiler",
            license="MIT",
            dependencies=[],
            min_opentiler_version="1.0.0",
        )

    def __init__(self, main_window=None):
        """Initialize the snap plugin."""
        super().__init__(main_window)

        # Hook system
        self.hook_handler = SnapHookHandler(self)
        self.hook_manager = get_hook_manager()

        # Content access
        self.plan_view_access = None
        self.measurement_access = None

        # Snap points storage
        self.snap_points: List[QPointF] = []
        self.grid_snap_points: List[QPointF] = []
        self.content_snap_points: List[QPointF] = []

        # Configuration
        self.config = {
            "snap_enabled": True,
            "snap_distance": 10.0,  # pixels
            "show_snap_points": True,
            "grid_snap": True,
            "grid_spacing": 50.0,  # pixels
            "content_snap": True,
            "corner_snap": True,
            "edge_snap": True,
            "intersection_snap": True,
        }

    def initialize(self) -> bool:
        """Initialize the snap plugin."""
        try:
            self.log_info("Initializing Snap Plugin")

            # Register hook handlers
            self.hook_manager.register_handler(self.hook_handler, "snap")

            self._initialized = True
            self.log_info("Snap plugin initialized successfully")
            return True

        except Exception as e:
            self.log_error(f"Failed to initialize: {e}")
            return False

    def enable(self) -> bool:
        """Enable the snap plugin."""
        try:
            self.log_info("Enabling Snap Plugin")

            # Generate initial snap points
            self.generate_snap_points()

            self._enabled = True
            self.log_info("Snap plugin enabled")
            return True

        except Exception as e:
            self.log_error(f"Failed to enable: {e}")
            return False

    def disable(self) -> bool:
        """Disable the snap plugin."""
        try:
            self.log_info("Disabling Snap Plugin")

            # Clear snap points
            self.snap_points.clear()
            self.grid_snap_points.clear()
            self.content_snap_points.clear()

            self._enabled = False
            self.log_info("Snap plugin disabled")
            return True

        except Exception as e:
            self.log_error(f"Failed to disable: {e}")
            return False

    def cleanup(self) -> bool:
        """Clean up plugin resources."""
        try:
            if self.enabled:
                self.disable()

            # Unregister hook handlers
            self.hook_manager.unregister_handler(self.hook_handler, "snap")

            self.log_info("Snap plugin cleaned up")
            return True

        except Exception as e:
            self.log_error(f"Failed to cleanup: {e}")
            return False

    def get_hook_handlers(self) -> List[HookHandler]:
        """Get hook handlers provided by this plugin."""
        return [self.hook_handler]

    def get_document_access_requirements(self) -> Dict[str, bool]:
        """Get document access requirements for this plugin."""
        return {
            "plan_view": True,
            "tile_preview": False,
            "document_data": True,
            "metadata": False,
            "measurements": True,
            "transformations": False,
        }

    def find_snap_point(self, point: QPointF) -> Optional[QPointF]:
        """
        Find the nearest snap point to the given point.

        Args:
            point: Point to find snap for

        Returns:
            Nearest snap point within snap distance, or None
        """
        if not self.config.get("snap_enabled", True):
            return None

        snap_distance = self.config.get("snap_distance", 10.0)
        nearest_point = None
        nearest_distance = float("inf")

        # Check all snap points
        for snap_point in self.snap_points:
            distance = self._calculate_distance(point, snap_point)
            if distance < snap_distance and distance < nearest_distance:
                nearest_distance = distance
                nearest_point = snap_point

        return nearest_point

    def generate_snap_points(self):
        """Generate snap points based on current configuration."""
        self.snap_points.clear()

        # Generate grid snap points
        if self.config.get("grid_snap", True):
            self._generate_grid_snap_points()

        # Generate content-based snap points
        if self.config.get("content_snap", True):
            self._generate_content_snap_points()

        # Combine all snap points
        self.snap_points = self.grid_snap_points + self.content_snap_points

        self.log_info(f"Generated {len(self.snap_points)} snap points")

    def _generate_grid_snap_points(self):
        """Generate grid-based snap points."""
        self.grid_snap_points.clear()

        if not self.plan_view_access:
            return

        # Get viewport information
        view_info = self.plan_view_access.get_view_info()
        if not view_info:
            return

        grid_spacing = self.config.get("grid_spacing", 50.0)
        viewport_size = view_info.viewport_size

        # Generate grid points within viewport
        for x in range(0, viewport_size[0], int(grid_spacing)):
            for y in range(0, viewport_size[1], int(grid_spacing)):
                self.grid_snap_points.append(QPointF(x, y))

    def _generate_content_snap_points(self):
        """Generate content-based snap points."""
        self.content_snap_points.clear()

        if not self.plan_view_access:
            return

        # Get document content bounds
        content_bounds = self.plan_view_access.get_content_bounds()
        if not content_bounds:
            return

        # Add corner points
        if self.config.get("corner_snap", True):
            self.content_snap_points.extend(
                [
                    content_bounds.topLeft(),
                    content_bounds.topRight(),
                    content_bounds.bottomLeft(),
                    content_bounds.bottomRight(),
                ]
            )

        # Add edge midpoints
        if self.config.get("edge_snap", True):
            self.content_snap_points.extend(
                [
                    QPointF(content_bounds.center().x(), content_bounds.top()),
                    QPointF(content_bounds.center().x(), content_bounds.bottom()),
                    QPointF(content_bounds.left(), content_bounds.center().y()),
                    QPointF(content_bounds.right(), content_bounds.center().y()),
                ]
            )

        # Add center point
        self.content_snap_points.append(content_bounds.center())

    def analyze_document_for_snap_points(self):
        """Analyze the loaded document to find additional snap points."""
        # This would analyze the document content for lines, intersections, etc.
        # For now, just regenerate basic snap points
        self.generate_snap_points()

    def render_snap_points(self, painter: QPainter):
        """
        Render snap points as visual indicators.

        Args:
            painter: QPainter to draw with
        """
        if not self.config.get("show_snap_points", True):
            return

        # Set up pen for snap points
        pen = QPen(QColor(255, 0, 0, 128))  # Semi-transparent red
        pen.setWidth(2)
        painter.setPen(pen)

        # Draw snap points as small circles
        for point in self.snap_points:
            painter.drawEllipse(point, 3, 3)

    def _calculate_distance(self, point1: QPointF, point2: QPointF) -> float:
        """Calculate distance between two points."""
        dx = point1.x() - point2.x()
        dy = point1.y() - point2.y()
        return math.sqrt(dx * dx + dy * dy)

    def get_settings_widget(self) -> Optional[QWidget]:
        """Get settings widget for snap configuration."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Snap enable/disable
        self.snap_enabled_cb = QCheckBox("Enable snap functionality")
        self.snap_enabled_cb.setChecked(self.config.get("snap_enabled", True))
        layout.addWidget(self.snap_enabled_cb)

        # Snap distance
        distance_group = QGroupBox("Snap Distance")
        distance_layout = QHBoxLayout(distance_group)
        distance_layout.addWidget(QLabel("Distance (pixels):"))
        self.snap_distance_spin = QSpinBox()
        self.snap_distance_spin.setRange(1, 100)
        self.snap_distance_spin.setValue(int(self.config.get("snap_distance", 10)))
        distance_layout.addWidget(self.snap_distance_spin)
        layout.addWidget(distance_group)

        # Snap types
        types_group = QGroupBox("Snap Types")
        types_layout = QVBoxLayout(types_group)

        self.grid_snap_cb = QCheckBox("Grid snap")
        self.grid_snap_cb.setChecked(self.config.get("grid_snap", True))
        types_layout.addWidget(self.grid_snap_cb)

        self.content_snap_cb = QCheckBox("Content snap")
        self.content_snap_cb.setChecked(self.config.get("content_snap", True))
        types_layout.addWidget(self.content_snap_cb)

        self.corner_snap_cb = QCheckBox("Corner snap")
        self.corner_snap_cb.setChecked(self.config.get("corner_snap", True))
        types_layout.addWidget(self.corner_snap_cb)

        layout.addWidget(types_group)

        # Visual settings
        visual_group = QGroupBox("Visual Settings")
        visual_layout = QVBoxLayout(visual_group)

        self.show_snap_points_cb = QCheckBox("Show snap points")
        self.show_snap_points_cb.setChecked(self.config.get("show_snap_points", True))
        visual_layout.addWidget(self.show_snap_points_cb)

        layout.addWidget(visual_group)

        return widget

    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration."""
        return self.config.copy()

    def set_config(self, config: Dict[str, Any]) -> bool:
        """Set plugin configuration."""
        try:
            self.config.update(config)

            # Regenerate snap points if enabled
            if self.enabled:
                self.generate_snap_points()

            return True
        except Exception:
            return False
