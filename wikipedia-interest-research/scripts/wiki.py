#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "numpy>=1.26",
#   "matplotlib>=3.8",
#   "fpdf2>=2.7.8",
# ]
# ///
"""Wikipedia interest research CLI. Run `uv run scripts/wiki.py --help`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wikiinterest.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
