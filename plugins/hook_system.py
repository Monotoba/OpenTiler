#!/usr/bin/env python3
"""
OpenTiler Plugin Hook System

This module provides a comprehensive hook system for plugins to integrate
deeply with OpenTiler's core functionality, including document processing,
rendering, measurements, and transformations.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPainter, QTransform
from PySide6.QtWidgets import QWidget


class HookType(Enum):
    """Types of hooks available in the system."""
    
    # Document lifecycle hooks
    DOCUMENT_BEFORE_LOAD = "document_before_load"
    DOCUMENT_AFTER_LOAD = "document_after_load"
    DOCUMENT_BEFORE_CLOSE = "document_before_close"
    DOCUMENT_AFTER_CLOSE = "document_after_close"
    
    # Rendering hooks
    RENDER_BEFORE_DRAW = "render_before_draw"
    RENDER_AFTER_DRAW = "render_after_draw"
    RENDER_BEFORE_TRANSFORM = "render_before_transform"
    RENDER_AFTER_TRANSFORM = "render_after_transform"
    
    # Tile processing hooks
    TILE_BEFORE_GENERATE = "tile_before_generate"
    TILE_AFTER_GENERATE = "tile_after_generate"
    TILE_BEFORE_EXPORT = "tile_before_export"
    TILE_AFTER_EXPORT = "tile_after_export"
    
    # Measurement hooks
    MEASUREMENT_BEFORE_START = "measurement_before_start"
    MEASUREMENT_AFTER_START = "measurement_after_start"
    MEASUREMENT_BEFORE_UPDATE = "measurement_before_update"
    MEASUREMENT_AFTER_UPDATE = "measurement_after_update"
    MEASUREMENT_BEFORE_FINISH = "measurement_before_finish"
    MEASUREMENT_AFTER_FINISH = "measurement_after_finish"
    
    # Scale hooks
    SCALE_BEFORE_SET = "scale_before_set"
    SCALE_AFTER_SET = "scale_after_set"
    SCALE_BEFORE_CALCULATE = "scale_before_calculate"
    SCALE_AFTER_CALCULATE = "scale_after_calculate"
    
    # View hooks
    VIEW_BEFORE_ZOOM = "view_before_zoom"
    VIEW_AFTER_ZOOM = "view_after_zoom"
    VIEW_BEFORE_PAN = "view_before_pan"
    VIEW_AFTER_PAN = "view_after_pan"
    VIEW_BEFORE_ROTATE = "view_before_rotate"
    VIEW_AFTER_ROTATE = "view_after_rotate"
    
    # Export hooks
    EXPORT_BEFORE_START = "export_before_start"
    EXPORT_AFTER_START = "export_after_start"
    EXPORT_BEFORE_PROCESS = "export_before_process"
    EXPORT_AFTER_PROCESS = "export_after_process"
    EXPORT_BEFORE_SAVE = "export_before_save"
    EXPORT_AFTER_SAVE = "export_after_save"
    
    # UI hooks
    UI_BEFORE_UPDATE = "ui_before_update"
    UI_AFTER_UPDATE = "ui_after_update"
    UI_CONTEXT_MENU = "ui_context_menu"
    UI_TOOLBAR_UPDATE = "ui_toolbar_update"
    
    # Settings hooks
    SETTINGS_BEFORE_LOAD = "settings_before_load"
    SETTINGS_AFTER_LOAD = "settings_after_load"
    SETTINGS_BEFORE_SAVE = "settings_before_save"
    SETTINGS_AFTER_SAVE = "settings_after_save"


@dataclass
class HookContext:
    """Context information passed to hook handlers."""
    hook_type: HookType
    data: Dict[str, Any]
    source: Optional[str] = None
    timestamp: Optional[float] = None
    can_cancel: bool = False
    cancelled: bool = False
    
    def cancel(self):
        """Cancel the operation if cancellation is allowed."""
        if self.can_cancel:
            self.cancelled = True


@dataclass
class DocumentContext:
    """Context for document-related operations."""
    document_path: Optional[str] = None
    document_data: Optional[Any] = None
    document_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    page_count: Optional[int] = None
    dimensions: Optional[tuple] = None


@dataclass
class RenderContext:
    """Context for rendering operations."""
    painter: Optional[QPainter] = None
    transform: Optional[QTransform] = None
    viewport_rect: Optional[tuple] = None
    zoom_level: Optional[float] = None
    rotation: Optional[float] = None
    content_bounds: Optional[tuple] = None
    render_quality: Optional[str] = None


@dataclass
class TileContext:
    """Context for tile operations."""
    tile_index: Optional[int] = None
    tile_position: Optional[tuple] = None
    tile_size: Optional[tuple] = None
    tile_bounds: Optional[tuple] = None
    overlap: Optional[float] = None
    page_size: Optional[tuple] = None
    export_format: Optional[str] = None
    quality: Optional[int] = None


@dataclass
class MeasurementContext:
    """Context for measurement operations."""
    measurement_id: Optional[str] = None
    start_point: Optional[tuple] = None
    end_point: Optional[tuple] = None
    current_point: Optional[tuple] = None
    distance: Optional[float] = None
    angle: Optional[float] = None
    units: Optional[str] = None
    scale: Optional[float] = None
    snap_enabled: Optional[bool] = None
    snap_points: Optional[List[tuple]] = None


@dataclass
class ViewContext:
    """Context for view operations."""
    zoom_level: Optional[float] = None
    pan_offset: Optional[tuple] = None
    rotation: Optional[float] = None
    viewport_size: Optional[tuple] = None
    content_size: Optional[tuple] = None
    fit_mode: Optional[str] = None


class HookHandler(ABC):
    """Abstract base class for hook handlers."""
    
    @abstractmethod
    def handle_hook(self, context: HookContext) -> bool:
        """
        Handle a hook event.
        
        Args:
            context: Hook context with event data
            
        Returns:
            True if hook was handled successfully, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def supported_hooks(self) -> List[HookType]:
        """Return list of hook types this handler supports."""
        pass
    
    @property
    def priority(self) -> int:
        """Return handler priority (higher = executed first)."""
        return 0


class HookManager(QObject):
    """
    Manages the hook system for OpenTiler plugins.
    
    Provides registration, execution, and management of hooks throughout
    the OpenTiler application lifecycle.
    """
    
    # Signals
    hook_executed = Signal(HookType, str)  # hook_type, plugin_name
    hook_failed = Signal(HookType, str, str)  # hook_type, plugin_name, error
    
    def __init__(self):
        """Initialize the hook manager."""
        super().__init__()
        
        # Hook handlers organized by type
        self.handlers: Dict[HookType, List[tuple]] = {}  # (handler, plugin_name, priority)
        
        # Hook execution statistics
        self.execution_stats: Dict[HookType, Dict[str, int]] = {}
        
        # Hook configuration
        self.hook_config: Dict[HookType, Dict[str, Any]] = {}
        
        # Initialize all hook types
        for hook_type in HookType:
            self.handlers[hook_type] = []
            self.execution_stats[hook_type] = {}
    
    def register_handler(self, handler: HookHandler, plugin_name: str) -> bool:
        """
        Register a hook handler.
        
        Args:
            handler: Hook handler instance
            plugin_name: Name of the plugin registering the handler
            
        Returns:
            True if registered successfully
        """
        try:
            for hook_type in handler.supported_hooks:
                # Add handler with priority
                handler_tuple = (handler, plugin_name, handler.priority)
                self.handlers[hook_type].append(handler_tuple)
                
                # Sort by priority (highest first)
                self.handlers[hook_type].sort(key=lambda x: x[2], reverse=True)
                
                # Initialize stats
                if plugin_name not in self.execution_stats[hook_type]:
                    self.execution_stats[hook_type][plugin_name] = 0
            
            return True
            
        except Exception as e:
            print(f"Failed to register hook handler for {plugin_name}: {e}")
            return False
    
    def unregister_handler(self, handler: HookHandler, plugin_name: str) -> bool:
        """
        Unregister a hook handler.
        
        Args:
            handler: Hook handler instance
            plugin_name: Name of the plugin
            
        Returns:
            True if unregistered successfully
        """
        try:
            for hook_type in handler.supported_hooks:
                # Remove handler
                self.handlers[hook_type] = [
                    (h, name, priority) for h, name, priority in self.handlers[hook_type]
                    if h != handler or name != plugin_name
                ]
            
            return True
            
        except Exception as e:
            print(f"Failed to unregister hook handler for {plugin_name}: {e}")
            return False
    
    def execute_hook(self, hook_type: HookType, context_data: Dict[str, Any], 
                    source: Optional[str] = None, can_cancel: bool = False) -> HookContext:
        """
        Execute all handlers for a specific hook type.
        
        Args:
            hook_type: Type of hook to execute
            context_data: Data to pass to hook handlers
            source: Source of the hook execution
            can_cancel: Whether handlers can cancel the operation
            
        Returns:
            Hook context with results
        """
        import time
        
        # Create hook context
        context = HookContext(
            hook_type=hook_type,
            data=context_data,
            source=source,
            timestamp=time.time(),
            can_cancel=can_cancel,
            cancelled=False
        )
        
        # Execute handlers in priority order
        for handler, plugin_name, priority in self.handlers[hook_type]:
            try:
                # Execute handler
                success = handler.handle_hook(context)
                
                # Update statistics
                if success:
                    self.execution_stats[hook_type][plugin_name] += 1
                    self.hook_executed.emit(hook_type, plugin_name)
                
                # Check if operation was cancelled
                if context.cancelled:
                    break
                    
            except Exception as e:
                error_msg = f"Hook handler error: {e}"
                self.hook_failed.emit(hook_type, plugin_name, error_msg)
                print(f"Hook execution failed for {plugin_name} on {hook_type}: {e}")
        
        return context
    
    def get_handlers(self, hook_type: HookType) -> List[str]:
        """
        Get list of plugin names that handle a specific hook type.
        
        Args:
            hook_type: Hook type to query
            
        Returns:
            List of plugin names
        """
        return [plugin_name for _, plugin_name, _ in self.handlers[hook_type]]
    
    def get_execution_stats(self) -> Dict[HookType, Dict[str, int]]:
        """Get hook execution statistics."""
        return self.execution_stats.copy()
    
    def configure_hook(self, hook_type: HookType, config: Dict[str, Any]):
        """
        Configure hook behavior.
        
        Args:
            hook_type: Hook type to configure
            config: Configuration settings
        """
        self.hook_config[hook_type] = config
    
    def get_hook_config(self, hook_type: HookType) -> Dict[str, Any]:
        """Get configuration for a hook type."""
        return self.hook_config.get(hook_type, {})


# Convenience functions for creating context objects
def create_document_context(**kwargs) -> DocumentContext:
    """Create a document context with the provided parameters."""
    return DocumentContext(**kwargs)

def create_render_context(**kwargs) -> RenderContext:
    """Create a render context with the provided parameters."""
    return RenderContext(**kwargs)

def create_tile_context(**kwargs) -> TileContext:
    """Create a tile context with the provided parameters."""
    return TileContext(**kwargs)

def create_measurement_context(**kwargs) -> MeasurementContext:
    """Create a measurement context with the provided parameters."""
    return MeasurementContext(**kwargs)

def create_view_context(**kwargs) -> ViewContext:
    """Create a view context with the provided parameters."""
    return ViewContext(**kwargs)


# Global hook manager instance
_hook_manager = None

def get_hook_manager() -> HookManager:
    """Get the global hook manager instance."""
    global _hook_manager
    if _hook_manager is None:
        _hook_manager = HookManager()
    return _hook_manager
