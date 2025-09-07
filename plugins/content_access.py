#!/usr/bin/env python3
"""
OpenTiler Plugin Content Access System

This module provides plugins with controlled access to OpenTiler's document content,
including plan views, tile previews, measurements, and transformations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from PySide6.QtCore import QObject, QPointF, QRectF, Signal
from PySide6.QtGui import QImage, QPainter, QPixmap, QTransform


class AccessLevel(Enum):
    """Access levels for plugin content access."""

    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL_CONTROL = "full_control"


@dataclass
class DocumentInfo:
    """Information about the loaded document."""

    file_path: str
    file_type: str
    page_count: int
    dimensions: Tuple[float, float]  # width, height
    resolution: Tuple[int, int]  # dpi_x, dpi_y
    metadata: Dict[str, Any]
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None


@dataclass
class ViewInfo:
    """Information about the current view state."""

    zoom_level: float
    pan_offset: Tuple[float, float]
    rotation: float
    viewport_size: Tuple[int, int]
    content_bounds: QRectF
    visible_area: QRectF
    fit_mode: str


@dataclass
class TileInfo:
    """Information about a tile."""

    index: int
    position: Tuple[int, int]  # row, column
    bounds: QRectF
    size: Tuple[int, int]
    overlap: float
    page_size: Tuple[float, float]
    export_settings: Dict[str, Any]


@dataclass
class MeasurementInfo:
    """Information about a measurement."""

    id: str
    start_point: QPointF
    end_point: QPointF
    distance: float
    angle: float
    units: str
    scale: float
    timestamp: float
    metadata: Dict[str, Any]


class PlanViewAccess(QObject):
    """Provides access to the plan view content and functionality."""

    # Signals
    content_changed = Signal()
    view_changed = Signal()

    def __init__(self, main_window, access_level: AccessLevel = AccessLevel.READ_ONLY):
        """
        Initialize plan view access.

        Args:
            main_window: Reference to OpenTiler main window
            access_level: Level of access granted
        """
        super().__init__()
        self.main_window = main_window
        self.access_level = access_level

    def get_document_info(self) -> Optional[DocumentInfo]:
        """Get information about the currently loaded document."""
        # This would interface with OpenTiler's document system
        if not hasattr(self.main_window, "current_document"):
            return None

        doc = self.main_window.current_document
        return DocumentInfo(
            file_path=getattr(doc, "file_path", ""),
            file_type=getattr(doc, "file_type", ""),
            page_count=getattr(doc, "page_count", 0),
            dimensions=getattr(doc, "dimensions", (0, 0)),
            resolution=getattr(doc, "resolution", (72, 72)),
            metadata=getattr(doc, "metadata", {}),
        )

    def get_view_info(self) -> Optional[ViewInfo]:
        """Get information about the current view state."""
        if not hasattr(self.main_window, "plan_view"):
            return None

        view = self.main_window.plan_view
        return ViewInfo(
            zoom_level=getattr(view, "zoom_level", 1.0),
            pan_offset=getattr(view, "pan_offset", (0, 0)),
            rotation=getattr(view, "rotation", 0.0),
            viewport_size=getattr(view, "viewport_size", (0, 0)),
            content_bounds=getattr(view, "content_bounds", QRectF()),
            visible_area=getattr(view, "visible_area", QRectF()),
            fit_mode=getattr(view, "fit_mode", "fit_window"),
        )

    def get_content_image(
        self,
        bounds: Optional[QRectF] = None,
        resolution: Optional[Tuple[int, int]] = None,
    ) -> Optional[QImage]:
        """
        Get rendered image of the plan view content.

        Args:
            bounds: Specific bounds to render (None for full content)
            resolution: Target resolution (None for current view resolution)

        Returns:
            QImage of the rendered content
        """
        if self.access_level == AccessLevel.READ_ONLY:
            # Interface with OpenTiler's rendering system
            if hasattr(self.main_window, "plan_view"):
                return self.main_window.plan_view.render_to_image(bounds, resolution)
        return None

    def get_content_bounds(self) -> Optional[QRectF]:
        """Get the bounds of the document content."""
        if hasattr(self.main_window, "plan_view"):
            return self.main_window.plan_view.content_bounds
        return None

    def set_view_transform(
        self,
        zoom: Optional[float] = None,
        pan: Optional[Tuple[float, float]] = None,
        rotation: Optional[float] = None,
    ) -> bool:
        """
        Set view transformation parameters.

        Args:
            zoom: Zoom level to set
            pan: Pan offset to set
            rotation: Rotation angle to set

        Returns:
            True if transformation was applied
        """
        if self.access_level in [AccessLevel.READ_WRITE, AccessLevel.FULL_CONTROL]:
            if hasattr(self.main_window, "plan_view"):
                view = self.main_window.plan_view
                if zoom is not None:
                    view.set_zoom(zoom)
                if pan is not None:
                    view.set_pan(pan)
                if rotation is not None:
                    view.set_rotation(rotation)
                return True
        return False

    def add_overlay(self, overlay_id: str, painter_func: callable) -> bool:
        """
        Add a custom overlay to the plan view.

        Args:
            overlay_id: Unique identifier for the overlay
            painter_func: Function that takes QPainter and draws the overlay

        Returns:
            True if overlay was added
        """
        if self.access_level == AccessLevel.FULL_CONTROL:
            if hasattr(self.main_window, "plan_view"):
                return self.main_window.plan_view.add_overlay(overlay_id, painter_func)
        return False

    def remove_overlay(self, overlay_id: str) -> bool:
        """Remove a custom overlay from the plan view."""
        if self.access_level == AccessLevel.FULL_CONTROL:
            if hasattr(self.main_window, "plan_view"):
                return self.main_window.plan_view.remove_overlay(overlay_id)
        return False


class TilePreviewAccess(QObject):
    """Provides access to the tile preview content and functionality."""

    # Signals
    tiles_changed = Signal()
    preview_updated = Signal()

    def __init__(self, main_window, access_level: AccessLevel = AccessLevel.READ_ONLY):
        """
        Initialize tile preview access.

        Args:
            main_window: Reference to OpenTiler main window
            access_level: Level of access granted
        """
        super().__init__()
        self.main_window = main_window
        self.access_level = access_level

    def get_tile_count(self) -> int:
        """Get the total number of tiles."""
        if hasattr(self.main_window, "tile_preview"):
            return self.main_window.tile_preview.tile_count
        return 0

    def get_tile_info(self, tile_index: int) -> Optional[TileInfo]:
        """Get information about a specific tile."""
        if hasattr(self.main_window, "tile_preview"):
            tile_data = self.main_window.tile_preview.get_tile_data(tile_index)
            if tile_data:
                return TileInfo(
                    index=tile_index,
                    position=tile_data.get("position", (0, 0)),
                    bounds=tile_data.get("bounds", QRectF()),
                    size=tile_data.get("size", (0, 0)),
                    overlap=tile_data.get("overlap", 0.0),
                    page_size=tile_data.get("page_size", (0, 0)),
                    export_settings=tile_data.get("export_settings", {}),
                )
        return None

    def get_tile_image(
        self, tile_index: int, resolution: Optional[Tuple[int, int]] = None
    ) -> Optional[QImage]:
        """
        Get rendered image of a specific tile.

        Args:
            tile_index: Index of the tile to render
            resolution: Target resolution for the tile image

        Returns:
            QImage of the rendered tile
        """
        if self.access_level == AccessLevel.READ_ONLY:
            if hasattr(self.main_window, "tile_preview"):
                return self.main_window.tile_preview.render_tile(tile_index, resolution)
        return None

    def get_all_tiles_info(self) -> List[TileInfo]:
        """Get information about all tiles."""
        tiles = []
        tile_count = self.get_tile_count()
        for i in range(tile_count):
            tile_info = self.get_tile_info(i)
            if tile_info:
                tiles.append(tile_info)
        return tiles

    def set_tile_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Set tile configuration parameters.

        Args:
            config: Dictionary with tile configuration

        Returns:
            True if configuration was applied
        """
        if self.access_level in [AccessLevel.READ_WRITE, AccessLevel.FULL_CONTROL]:
            if hasattr(self.main_window, "tile_preview"):
                return self.main_window.tile_preview.set_configuration(config)
        return False

    def regenerate_tiles(self) -> bool:
        """Regenerate tiles with current configuration."""
        if self.access_level in [AccessLevel.READ_WRITE, AccessLevel.FULL_CONTROL]:
            if hasattr(self.main_window, "tile_preview"):
                return self.main_window.tile_preview.regenerate()
        return False


class MeasurementAccess(QObject):
    """Provides access to measurement functionality."""

    # Signals
    measurement_added = Signal(str)  # measurement_id
    measurement_updated = Signal(str)  # measurement_id
    measurement_removed = Signal(str)  # measurement_id

    def __init__(self, main_window, access_level: AccessLevel = AccessLevel.READ_ONLY):
        """
        Initialize measurement access.

        Args:
            main_window: Reference to OpenTiler main window
            access_level: Level of access granted
        """
        super().__init__()
        self.main_window = main_window
        self.access_level = access_level

    def get_measurements(self) -> List[MeasurementInfo]:
        """Get all current measurements."""
        measurements = []
        if hasattr(self.main_window, "measurement_system"):
            measurement_data = (
                self.main_window.measurement_system.get_all_measurements()
            )
            for data in measurement_data:
                measurements.append(
                    MeasurementInfo(
                        id=data.get("id", ""),
                        start_point=data.get("start_point", QPointF()),
                        end_point=data.get("end_point", QPointF()),
                        distance=data.get("distance", 0.0),
                        angle=data.get("angle", 0.0),
                        units=data.get("units", "mm"),
                        scale=data.get("scale", 1.0),
                        timestamp=data.get("timestamp", 0.0),
                        metadata=data.get("metadata", {}),
                    )
                )
        return measurements

    def add_measurement(
        self,
        start_point: QPointF,
        end_point: QPointF,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Add a new measurement.

        Args:
            start_point: Starting point of the measurement
            end_point: Ending point of the measurement
            metadata: Optional metadata for the measurement

        Returns:
            Measurement ID if successful, None otherwise
        """
        if self.access_level in [AccessLevel.READ_WRITE, AccessLevel.FULL_CONTROL]:
            if hasattr(self.main_window, "measurement_system"):
                measurement_id = self.main_window.measurement_system.add_measurement(
                    start_point, end_point, metadata or {}
                )
                if measurement_id:
                    self.measurement_added.emit(measurement_id)
                return measurement_id
        return None

    def get_snap_points(self, point: QPointF, radius: float = 10.0) -> List[QPointF]:
        """
        Get snap points near the specified point.

        Args:
            point: Point to search around
            radius: Search radius in pixels

        Returns:
            List of snap points
        """
        if hasattr(self.main_window, "measurement_system"):
            return self.main_window.measurement_system.get_snap_points(point, radius)
        return []

    def enable_snap(self, enabled: bool) -> bool:
        """Enable or disable snap functionality."""
        if self.access_level in [AccessLevel.READ_WRITE, AccessLevel.FULL_CONTROL]:
            if hasattr(self.main_window, "measurement_system"):
                return self.main_window.measurement_system.set_snap_enabled(enabled)
        return False


class ContentAccessManager(QObject):
    """
    Manages content access for plugins.

    Provides controlled access to OpenTiler's document content, views, and functionality
    based on plugin permissions and access levels.
    """

    def __init__(self, main_window):
        """
        Initialize the content access manager.

        Args:
            main_window: Reference to OpenTiler main window
        """
        super().__init__()
        self.main_window = main_window
        self.plugin_access: Dict[str, Dict[str, Any]] = {}

    def grant_access(
        self,
        plugin_name: str,
        requirements: Dict[str, bool],
        access_level: AccessLevel = AccessLevel.READ_ONLY,
    ) -> Dict[str, Any]:
        """
        Grant content access to a plugin.

        Args:
            plugin_name: Name of the plugin requesting access
            requirements: Dictionary of access requirements
            access_level: Level of access to grant

        Returns:
            Dictionary of access objects
        """
        access_objects = {}

        # Plan view access
        if requirements.get("plan_view", False):
            access_objects["plan_view"] = PlanViewAccess(self.main_window, access_level)

        # Tile preview access
        if requirements.get("tile_preview", False):
            access_objects["tile_preview"] = TilePreviewAccess(
                self.main_window, access_level
            )

        # Measurement access
        if requirements.get("measurements", False):
            access_objects["measurements"] = MeasurementAccess(
                self.main_window, access_level
            )

        # Store access for the plugin
        self.plugin_access[plugin_name] = {
            "access_objects": access_objects,
            "access_level": access_level,
            "requirements": requirements,
        }

        return access_objects

    def revoke_access(self, plugin_name: str):
        """Revoke all access for a plugin."""
        if plugin_name in self.plugin_access:
            del self.plugin_access[plugin_name]

    def get_plugin_access(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get access objects for a plugin."""
        return self.plugin_access.get(plugin_name, {}).get("access_objects")

    def list_plugin_access(self) -> Dict[str, Dict[str, Any]]:
        """List all plugin access information."""
        return self.plugin_access.copy()
