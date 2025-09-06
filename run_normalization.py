#!/usr/bin/env python3
"""
Entry point for running the normalization script from the project root.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main normalization script
from zettelkasten_normalizer.normalization_zettel import main

if __name__ == "__main__":
    main()