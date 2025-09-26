#!/usr/bin/env python3
"""
Direct runner script for HyprSTT
This script can be run directly without needing to use the module import system
"""

import os
import sys

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function from src.main
from src.main import main

if __name__ == "__main__":
    # Run the application
    main()