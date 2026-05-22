# PhytoGraph M1.8 — pytest fixtures + sys.path bootstrap. cycle 2, worker.
import sys
from pathlib import Path

# Make `harness` importable without installing the package.
HARNESS_ROOT = Path(__file__).resolve().parent.parent
if str(HARNESS_ROOT) not in sys.path:
    sys.path.insert(0, str(HARNESS_ROOT))
