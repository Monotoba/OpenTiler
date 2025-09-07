#!/usr/bin/env python3
"""
OpenTiler Setup Script

Installation script for OpenTiler - Professional Document Scaling and Tiling Application
Supports Windows 7/10/11, macOS, Ubuntu/Debian, and Arch Linux
"""

import os
import sys

from setuptools import find_packages, setup


# Read long description from README
def get_long_description():
    """Read long description from README.md"""
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "OpenTiler - Professional Document Scaling and Tiling Application"


# Core requirements (always needed)
CORE_REQUIREMENTS = [
    "PySide6>=6.5.0",
    "Pillow>=9.0.0",
    "PyMuPDF>=1.23.0",
]

# Optional requirements for enhanced functionality
OPTIONAL_REQUIREMENTS = {
    "cad": ["ezdxf>=1.0.0"],
    "raw": ["rawpy>=0.18.0", "numpy>=1.21.0"],
    "automation": ["mss>=9.0.0", "pywinctl>=0.0.50"],
    "all": [
        "ezdxf>=1.0.0",
        "rawpy>=0.18.0",
        "numpy>=1.21.0",
        "mss>=9.0.0",
        "pywinctl>=0.0.50",
    ],
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=22.0.0",
        "flake8>=5.0.0",
        "isort>=5.0.0",
        "mypy>=1.0.0",
        "bandit>=1.7.0",
        "safety>=2.0.0",
        "pyinstaller>=5.0.0",
    ],
    "docs": [
        "sphinx>=5.0.0",
        "sphinx-rtd-theme>=1.0.0",
    ],
}

# All optional requirements combined
ALL_OPTIONAL = []
for deps in OPTIONAL_REQUIREMENTS.values():
    ALL_OPTIONAL.extend(deps)
OPTIONAL_REQUIREMENTS["all"] = ALL_OPTIONAL

setup(
    name="opentiler",
    version="1.3.2-rc3",
    author="Randall Morgan",
    author_email="randall@example.com",
    description="Professional Document Scaling and Tiling Application",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Monotoba/OpenTiler",
    license="MIT",
    # Package configuration
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "opentiler": [
            "assets/*",
            "assets/icons/*",
            "docs/*",
            "docs/images/*",
            "help/*",
            "help/assets/*",
            "help/assets/style/*",
            "help/assets/img/*",
        ],
    },
    # Requirements
    install_requires=CORE_REQUIREMENTS,
    extras_require=OPTIONAL_REQUIREMENTS,
    python_requires=">=3.8",
    # Entry points
    entry_points={
        "console_scripts": [
            "opentiler=main:main",
        ],
        "gui_scripts": [
            "opentiler-gui=main:main",
        ],
    },
    # Classification
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Office/Business",
        "Topic :: Printing",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    # Keywords
    keywords=[
        "pdf",
        "tiling",
        "scaling",
        "printing",
        "documents",
        "plans",
        "architectural",
        "engineering",
        "cad",
        "measurement",
        "conversion",
        "qt",
        "pyside6",
        "gui",
        "desktop",
    ],
    # Project URLs
    project_urls={
        "Documentation": "https://github.com/Monotoba/OpenTiler/docs",
        "Source": "https://github.com/Monotoba/OpenTiler",
        "Tracker": "https://github.com/Monotoba/OpenTiler/issues",
    },
    # Additional metadata
    zip_safe=False,
    platforms=["any"],
)
