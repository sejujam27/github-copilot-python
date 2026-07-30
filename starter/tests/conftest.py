import sys
from pathlib import Path

# Ensure the project root is on the import path when pytest runs from the tests directory.
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))
