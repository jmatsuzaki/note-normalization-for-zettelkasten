#!/usr/bin/env python3
"""
Setup script for Zettelkasten Note Normalization Tool
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
here = os.path.abspath(os.path.dirname(__file__))
init_path = os.path.join(here, 'src', 'zettelkasten_normalizer', '__init__.py')
version = "0.0.0"  # Default version if not found
with open(init_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break

# Read README
readme_path = os.path.join(here, 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = "A tool for normalizing Markdown notes for Zettelkasten systems"

setup(
    name="zettelkasten-normalizer",
    version=version,
    author="jMatsuzaki",
    author_email="",
    description="A tool for normalizing Markdown notes for Zettelkasten systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jmatsuzaki/note-normalization-for-zettelkasten",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Markup",
        "Topic :: Office/Business :: Groupware",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "zettelkasten-normalizer=zettelkasten_normalizer.normalization_zettel:main",
        ],
    },
    install_requires=[
        # No external dependencies - uses only standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
            "mypy",
        ],
    },
)