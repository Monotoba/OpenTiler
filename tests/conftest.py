#!/usr/bin/env python3
"""
Pytest configuration for OpenTiler tests.

This module provides common fixtures and configuration for all OpenTiler tests,
including plugin system tests.
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Qt application for GUI tests
try:
    import os
    # Set Qt platform to offscreen for headless testing
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QCoreApplication
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests."""
    if not QT_AVAILABLE:
        pytest.skip("PySide6 not available")

    # Check if QApplication already exists
    app = QCoreApplication.instance()
    if app is None:
        # Create app with minimal arguments for testing
        app = QApplication(['--platform', 'offscreen'])

    yield app

    # Don't quit the app as it might be used by other tests


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_main_window():
    """Create mock main window for plugin tests."""
    main_window = Mock()

    # Mock document
    main_window.current_document = Mock()
    main_window.current_document.file_path = "/test/document.pdf"
    main_window.current_document.file_type = "pdf"
    main_window.current_document.page_count = 1
    main_window.current_document.dimensions = (210.0, 297.0)
    main_window.current_document.resolution = (300, 300)
    main_window.current_document.metadata = {}

    # Mock plan view
    main_window.plan_view = Mock()
    main_window.plan_view.zoom_level = 1.0
    main_window.plan_view.pan_offset = (0, 0)
    main_window.plan_view.rotation = 0.0
    main_window.plan_view.viewport_size = (800, 600)
    main_window.plan_view.content_bounds = Mock()
    main_window.plan_view.visible_area = Mock()
    main_window.plan_view.fit_mode = "fit_window"

    # Mock tile preview
    main_window.tile_preview = Mock()
    main_window.tile_preview.tile_count = 4
    main_window.tile_preview.get_tile_data.return_value = {
        'position': (0, 0),
        'bounds': Mock(),
        'size': (200, 200),
        'overlap': 10.0,
        'page_size': (210.0, 297.0),
        'export_settings': {}
    }

    # Mock measurement system
    main_window.measurement_system = Mock()
    main_window.measurement_system.get_all_measurements.return_value = []
    main_window.measurement_system.get_snap_points.return_value = []

    # Mock menu bar
    main_window.menuBar.return_value = Mock()

    # Mock status bar
    main_window.statusBar.return_value = Mock()

    return main_window


@pytest.fixture
def plugin_test_environment(temp_dir, mock_main_window):
    """Create complete plugin test environment."""
    # Create plugin directories
    plugin_dirs = {
        'builtin': temp_dir / "plugins" / "builtin",
        'external': temp_dir / "plugins" / "external",
        'user': temp_dir / "config" / "plugins" / "user"
    }

    for plugin_dir in plugin_dirs.values():
        plugin_dir.mkdir(parents=True, exist_ok=True)

    return {
        'temp_dir': temp_dir,
        'main_window': mock_main_window,
        'plugin_dirs': plugin_dirs
    }


# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "gui: mark test as requiring GUI components"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Skip GUI tests if PySide6 not available
def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip GUI tests if PySide6 not available."""
    if not QT_AVAILABLE:
        skip_gui = pytest.mark.skip(reason="PySide6 not available")
        for item in items:
            if "gui" in item.keywords:
                item.add_marker(skip_gui)
