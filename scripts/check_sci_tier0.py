#!/usr/bin/env python3
"""Tier 0 sci-flow regression lock (M-CLI Phase 0). No LLM calls."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _run(cmd: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd or REPO, check=True)


def _verify_express_nine_pass() -> None:
    """M-EXPRESS-CI: 9-cell smoke must be 9/9 pass and under 60s budget."""
    json_path = REPO / "research" / "sci_flow" / f"M-3D-EXPRESS_{date.today().isoformat()}.json"
    if not json_path.is_file():
        raise SystemExit(f"express: missing artifact {json_path.relative_to(REPO)}")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    cells = payload.get("cells") or []
    if len(cells) != 9:
        raise SystemExit(f"express: expected 9 cells, got {len(cells)}")
    bad = [c["cell"] for c in cells if c.get("status") != "pass"]
    if bad:
        raise SystemExit(f"express: expected 9/9 pass, non-pass: {bad}")
    if not payload.get("under_60s", False):
        ms = payload.get("total_duration_ms")
        raise SystemExit(f"express: exceeded 60s budget ({ms} ms)")


def main() -> int:
    py = sys.executable
    _run([py, "endogeneity_stack_sim.py"])
    _run([py, "research/sci_flow/run_shadow_att_r.py"])
    _run([py, "research/sci_flow/run_live_att_r.py"])
    _run([py, "research/sci_flow/run_3d_express.py"])
    _verify_express_nine_pass()
    _run(
        [
            py,
            "-m",
            "pytest",
            "tests/test_shadow_multitick.py",
            "tests/test_daemon_carryover.py",
            "tests/test_oscillatory_mo.py",
            "tests/test_mo_do_o_arms.py",
            "tests/test_eoi_k_batch.py",
            "tests/test_b05_no_llm_mood.py",
            "tests/test_check_sci_tier0.py",
            "-q",
        ]
    )
    research = REPO / "research" / "cursor-starter-v0.2"
    _run(
        [
            py,
            "-m",
            "pytest",
            "tests/test_agi_transition.py",
            "tests/test_live_att_r.py",
            "tests/test_model_roles.py",
            "tests/test_intervention_cube.py",
            "-q",
        ],
        cwd=research,
    )
    print("check-sci-tier0: OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
