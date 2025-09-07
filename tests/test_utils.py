"""
Tests for utility functions.
"""

import os

import pytest

# Set Qt platform to offscreen for headless testing
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from opentiler.utils.helpers import calculate_distance  # noqa: E402
from opentiler.utils.helpers import (calculate_scale_factor, convert_units,
                                     format_scale_ratio, get_page_size_mm,
                                     validate_numeric_input)


class TestUnitConversion:
    """Test unit conversion functions."""

    def test_mm_to_inches(self):
        """Test millimeter to inch conversion."""
        result = convert_units(25.4, 'mm', 'inches')
        assert abs(result - 1.0) < 0.0001

    def test_inches_to_mm(self):
        """Test inch to millimeter conversion."""
        result = convert_units(1.0, 'inches', 'mm')
        assert abs(result - 25.4) < 0.0001

    def test_same_units(self):
        """Test conversion with same units."""
        result = convert_units(100.0, 'mm', 'mm')
        assert result == 100.0


class TestDistanceCalculation:
    """Test distance calculation functions."""

    def test_calculate_distance(self):
        """Test Euclidean distance calculation."""
        point1 = (0.0, 0.0)
        point2 = (3.0, 4.0)
        result = calculate_distance(point1, point2)
        assert abs(result - 5.0) < 0.0001

    def test_zero_distance(self):
        """Test distance calculation with same points."""
        point1 = (1.0, 1.0)
        point2 = (1.0, 1.0)
        result = calculate_distance(point1, point2)
        assert result == 0.0


class TestScaleCalculation:
    """Test scale calculation functions."""

    def test_calculate_scale_factor(self):
        """Test scale factor calculation."""
        result = calculate_scale_factor(100.0, 50.0, 'mm')
        assert result == 0.5

    def test_scale_factor_inches(self):
        """Test scale factor with inches."""
        result = calculate_scale_factor(100.0, 1.0, 'inches')
        expected = 25.4 / 100.0  # 1 inch = 25.4 mm
        assert abs(result - expected) < 0.0001

    def test_invalid_scale_inputs(self):
        """Test scale calculation with invalid inputs."""
        result = calculate_scale_factor(0.0, 50.0, 'mm')
        assert result == 1.0

        result = calculate_scale_factor(100.0, 0.0, 'mm')
        assert result == 1.0


class TestScaleFormatting:
    """Test scale formatting functions."""

    def test_format_scale_ratio_large(self):
        """Test formatting scale ratio >= 1."""
        result = format_scale_ratio(2.5)
        assert result == "2.50:1"

    def test_format_scale_ratio_small(self):
        """Test formatting scale ratio < 1."""
        result = format_scale_ratio(0.01)
        assert result == "1:100.0"


class TestPageSizes:
    """Test page size functions."""

    def test_a4_page_size(self):
        """Test A4 page size."""
        width, height = get_page_size_mm('A4')
        assert width == 210.0
        assert height == 297.0

    def test_letter_page_size(self):
        """Test Letter page size."""
        width, height = get_page_size_mm('Letter')
        assert width == 215.9
        assert height == 279.4

    def test_unknown_page_size(self):
        """Test unknown page size defaults to A4."""
        width, height = get_page_size_mm('Unknown')
        assert width == 210.0
        assert height == 297.0


class TestInputValidation:
    """Test input validation functions."""

    def test_valid_numeric_input(self):
        """Test valid numeric input."""
        result = validate_numeric_input("123.45")
        assert result == 123.45

    def test_invalid_numeric_input(self):
        """Test invalid numeric input."""
        result = validate_numeric_input("abc")
        assert result is None

    def test_numeric_input_range(self):
        """Test numeric input with range validation."""
        result = validate_numeric_input("50.0", 0.0, 100.0)
        assert result == 50.0

        result = validate_numeric_input("150.0", 0.0, 100.0)
        assert result is None
