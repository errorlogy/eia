#!/usr/bin/env python3
"""Tier 0 sci-flow regression lock (M-CLI Phase 0). No LLM calls."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd or REPO, check=True)


def main() -> int:
    py = sys.executable
    _run([py, "endogeneity_stack_sim.py"])
    _run([py, "research/sci_flow/run_shadow_att_r.py"])
    _run([py, "research/sci_flow/run_live_att_r.py"])
    _run([py, "-m", "pytest", "tests/test_shadow_multitick.py", "-q"])
    research = REPO / "research" / "cursor-starter-v0.2"
    _run(
        [
            py,
            "-m",
            "pytest",
            "tests/test_agi_transition.py",
            "tests/test_live_att_r.py",
            "-q",
        ],
        cwd=research,
    )
    print("check-sci-tier0: OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
