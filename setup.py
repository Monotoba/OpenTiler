"""
Setup script for OpenTiler.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="opentiler",
    version="0.1.0",
    author="Randall Morgan",
    author_email="randall@example.com",
    description="A PySide6-based desktop application for scaling and tiling architectural drawings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Monotoba/OpenTiler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Viewers",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "opentiler=opentiler.main_app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
