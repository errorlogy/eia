#!/usr/bin/env python3
"""M-D1-DO-Z-EOI — D01 do(Z)-mapped EOI evaluation for D1×L3 ledger admissibility.

Outputs markdown + JSON metrics. claim_allowed=false; C2 ceiling; not AGI*.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAIN_SRC = REPO / "src"
SCI_FLOW = Path(__file__).resolve().parent

if str(MAIN_SRC) not in sys.path:
    sys.path.insert(0, str(MAIN_SRC))
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from d01_do_z_eoi_harness import DEFAULT_DO_Z_IDS, run_do_z_eoi_evaluation  # noqa: E402


def _markdown(result, json_path: Path, today: str) -> str:
    steered = [r for r in result.rows if r.scenario_id == "eoi_k_steered"]
    admissible = [r for r in steered if r.trajectory_changed and r.do_z_changes_g_distribution]
    lines = [
        f"# M-D01 do(Z) EOI — causal remapping (D1×L2/L3) — {today}",
        "",
        "**Status:** harness executed · do(Z) remapped ATT-E witness",
        "**Branch:** `research/cursor-starter-v0.2-woe-eis`",
        "**Tick:** **M-D1-DO-Z-EOI**",
        "**Claim ceiling:** C2 partial ATT-E — **not C3**, **not AGI\\***, `claim_allowed=false`",
        "**Cube cells:** D1 Causal × L2 dynamics + L3 proof ledger input",
        "",
        "## Hypothesis",
        "",
        "H-D01-DO-Z: registered internal interventions `do(Z)` change initiative target "
        "distribution G under non-triggering X, satisfying `do_z_changes_g_distribution` "
        "for proof-protocol admissibility (unlike legacy do(X) EOI-k rows rejected F-NODO).",
        "",
        "## Pre-registered design",
        "",
        "| Item | Value |",
        "|------|-------|",
        f"| do(Z) sweep | {list(DEFAULT_DO_Z_IDS)} |",
        "| Baseline | full scenario replay (all observations) |",
        "| Counterfactual | same replay + `apply_do_z_intervention` before cognition |",
        "| Scenarios | `twin_world_001`, `autonomous_question`, `eoi_k_steered` |",
        "| Legacy do(X) | `M-D01_EOI_k_metrics_2026-09-01.json` (still F-NODO) |",
        "| Pool metric | `E_ENDO` (Tier A) |",
        "| ATT | ATT-E |",
        "| `claim_allowed` | **false** |",
        "",
        "## Results",
        "",
        "| Scenario | intervention | EOI | trajectory_changed | do_z | orig → twin |",
        "|----------|--------------|-----|--------------------|------|-------------|",
    ]
    for row in result.rows:
        orig = row.original_target or "—"
        twin = row.twin_target or "—"
        lines.append(
            f"| {row.scenario_id} | `{row.intervention_id}` | {row.eoi:.3f} | "
            f"{row.trajectory_changed} | {row.do_z_changes_g_distribution} | "
            f"`{orig}` → `{twin}` |"
        )

    lines.extend(
        [
            "",
            "## Ledger admissibility (`eoi_k_steered`)",
            "",
            f"- Candidate rows with `trajectory_changed=true`: **{len(admissible)}**",
        ]
    )
    if admissible:
        lines.append(
            "- Expected proof-protocol acceptance when mapped via "
            "`evidence_item_from_d01_do_z_row` (still `claim_allowed=false`)."
        )
    else:
        lines.append("- No steered rows passed trajectory bar; D1×L3 remains CF-4-only.")

    lines.extend(
        [
            "",
            "## Remap note",
            "",
            result.remap_note,
            "",
            "## Artifacts",
            "",
            "| Item | Path |",
            "|------|------|",
            "| Runner | `python research/sci_flow/run_d01_do_z_eoi.py` |",
            f"| JSON | `{json_path.as_posix()}` |",
            "| Ledger | `python research/sci_flow/run_d1_l3_ledger.py` |",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_do_z_eoi_evaluation(REPO)
    payload = result.to_dict()
    payload["explore_proxy_note"] = (
        "D01 do(Z) EOI remapping for proof ledger; replaces do(X) F-NODO flag with "
        "instrumented internal Z intervention; not C-ladder gate; not AGI*."
    )

    today = date.today().isoformat()
    json_path = SCI_FLOW / f"M-D01_do_z_EOI_{today}.json"
    md_path = SCI_FLOW / f"M-D01_do_z_EOI_{today}.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(result, json_path, today), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
