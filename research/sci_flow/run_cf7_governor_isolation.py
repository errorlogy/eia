#!/usr/bin/env python3
"""M-D3-L2-CF7: governor isolation paired harness (CF-7 / D3×L2).

Runs governor-off vs governor-on under X^trigger=0 (no prompt events).
Output: M-D3-L2_CF7_2026-09-02.json + markdown witness.

claim_allowed=false · C2 ceiling · no AGI* · no WoE→main merge.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SCI_FLOW = Path(__file__).resolve().parent
REPO = SCI_FLOW.parents[1]
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from cf7_governor_isolation_harness import run_cf7_paired_batch  # noqa: E402

ARTIFACT_STEM = "M-D3-L2_CF7_2026-09-02"
DEFAULT_SEEDS = tuple(range(10))


def _markdown_summary(payload: dict[str, object]) -> str:
    pairs = payload.get("pairs", [])
    n_pass = payload.get("n_pass", 0)
    n_paired = payload.get("n_paired", 0)
    lines = [
        f"# {ARTIFACT_STEM} — CF-7 governor isolation (D3×L2)",
        "",
        f"**Date:** {payload.get('date', '')}",
        "**Branch:** `research/cursor-starter-v0.2-woe-eis`",
        "**Claim ceiling:** C2 — `claim_allowed=false`, no AGI*",
        "",
        "## Hypothesis",
        "",
        "Under non-triggering external environment (X^trigger=0), CF-7 isolates the",
        "governor from the proposer: internal emergent intent is preserved as a typed",
        "causal receipt while external contact is denied.",
        "",
        "## Paired arms",
        "",
        "| Arm | Intervention | Expected |",
        "|-----|--------------|----------|",
        "| `governor_off` | none | Internal receipt emitted; no governor gate |",
        "| `governor_on` | `do_z_governor_isolation` | Governor denies contact; receipt parents preserved |",
        "",
        "## Results",
        "",
        f"- Seeds attempted: {payload.get('n_seeds', 0)}",
        f"- Paired (intent emitted): {n_paired}",
        f"- Isolation pass: {n_pass}/{n_paired}",
        f"- Harness passed: **{payload.get('passed', False)}**",
        "",
        "## Falsifiers",
        "",
        "- F-EXT: external trigger required for intent (not claimed)",
        "- F-NODO: no governor isolation boundary (structural pass if paired ok)",
        "",
        "## Command",
        "",
        "```bash",
        "python research/sci_flow/run_cf7_governor_isolation.py",
        "```",
        "",
        "## Cross-links",
        "",
        "- [`intervention_cube.py`](../cursor-starter-v0.2/src/eia/intervention_cube.py) — `do_z_governor_isolation`",
        "- [`boundary_witness_harness.py`](boundary_witness_harness.py) — D3×L3 governor gate smoke",
        "- [`SCI_FLOW_3D_CUBE.md`](SCI_FLOW_3D_CUBE.md) — D3×L2 cell",
        "",
    ]
    if pairs:
        lines.append("### Per-seed summary")
        lines.append("")
        lines.append("| seed | off ok | on ok | denied | parents ok |")
        lines.append("|------|--------|-------|--------|------------|")
        for row in pairs:
            off = row["governor_off"]
            on = row["governor_on"]
            lines.append(
                f"| {row['seed']} | {off['ok']} | {on['ok']} | {on['governor_denied']} | {on['parent_ids_preserved']} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    seeds = DEFAULT_SEEDS
    if len(sys.argv) > 1:
        seeds = tuple(int(s) for s in sys.argv[1].split(","))

    result = run_cf7_paired_batch(REPO, seeds=seeds)
    today = date.today().isoformat()
    payload: dict[str, object] = {
        "artifact_id": ARTIFACT_STEM,
        "milestone": "M-D3-L2-CF7",
        "date": today,
        "branch": "research/cursor-starter-v0.2-woe-eis",
        "cube_cell": "D3×L2",
        "intervention": "do_z_governor_isolation",
        "x_trigger_zero": True,
        **result.to_dict(),
    }

    json_path = SCI_FLOW / f"{ARTIFACT_STEM}.json"
    md_path = SCI_FLOW / f"{ARTIFACT_STEM}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown_summary(payload), encoding="utf-8")

    summary = {
        k: v
        for k, v in payload.items()
        if k != "pairs"
    }
    print(json.dumps(summary, indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
