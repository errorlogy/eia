"""Pytest: prefer research ``eia`` over editable main install."""
from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
_src = str(_SRC)
if _src not in sys.path:
    sys.path.insert(0, _src)
