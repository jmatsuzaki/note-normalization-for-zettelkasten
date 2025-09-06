"""
Zettelkasten Note Normalization Package

This package provides tools for normalizing Markdown notes in Zettelkasten systems.
"""

__version__ = "1.0.0"
__author__ = "jMatsuzaki"

# Import main functions for easier access
from .yfm_processor import check_and_create_yfm
from .link_processor import rename_notes_with_links, rename_images_with_links
from .file_operations import get_files
from .utils import setup_logger, query_yes_no