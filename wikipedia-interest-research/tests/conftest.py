import sys
from pathlib import Path

# The skill's code lives in scripts/ (run as `uv run scripts/wiki.py`); make it importable in tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
