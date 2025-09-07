#!/usr/bin/env python3
"""
OpenTiler - A PySide6-based desktop application for scaling and tiling architectural drawings.

Author: Randall Morgan
License: MIT License with Attribution Requirement
Copyright: © 2025 Randall Morgan
"""

import os
import sys

# Add the opentiler package to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "opentiler"))

from opentiler.main_app import main

# TODO: Complete adding measurement tool.

if __name__ == "__main__":
    main()
