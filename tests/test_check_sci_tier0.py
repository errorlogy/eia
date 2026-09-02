"""Self-test: tier-0 lock includes M-EXPRESS-CI 3D cube smoke."""

from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECK = REPO / "scripts" / "check_sci_tier0.py"


def test_tier0_includes_run_3d_express() -> None:
    text = CHECK.read_text(encoding="utf-8")
    assert "run_3d_express.py" in text
    assert "_verify_express_nine_pass" in text


def test_verify_express_nine_pass_defined() -> None:
    tree = ast.parse(CHECK.read_text(encoding="utf-8"))
    names = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    assert "_verify_express_nine_pass" in names
