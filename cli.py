#!/usr/bin/env python3
"""
WebCompressor Pro — CLI entry point.
"""

import sys
from pathlib import Path

# Ensure project root is on path when run as script
sys.path.insert(0, str(Path(__file__).resolve().parent))

from compressor import main


if __name__ == "__main__":
    main()
