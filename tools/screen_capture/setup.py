#!/usr/bin/env python3
"""
Setup script for Cross-Platform Screen Capture Tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="screen-capture-tool",
    version="1.0.0",
    author="Randall Morgan",
    author_email="randall@example.com",
    description="Cross-platform screen capture utility with window and fullscreen support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Monotoba/screen-capture-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "advanced": [
            "psutil>=5.9.0",
            "opencv-python>=4.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "screen-capture=screen_capture:main",
            "screencap=screen_capture:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="screenshot screen capture window fullscreen cross-platform pywinctl mss",
    project_urls={
        "Bug Reports": "https://github.com/Monotoba/screen-capture-tool/issues",
        "Source": "https://github.com/Monotoba/screen-capture-tool",
        "Documentation": "https://github.com/Monotoba/screen-capture-tool/blob/main/docs/README.md",
    },
)
