#!/usr/bin/env python3
"""D01 EOI-k (k=1,5,20) window sweep on twin scenarios.

Outputs markdown + JSON metrics for D1×L2 cell. claim_allowed=false.
Links ATT-E / pool E_ENDO. Not C-ladder gate; not AGI*.
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

from eoi_k_harness import DEFAULT_K_VALUES, run_eoi_k_sweep  # noqa: E402


def _markdown(result, json_path: Path) -> str:
    lines = [
        "# M-D01 — EOI-k window sweep (D1×L2) — 2026-09-01",
        "",
        "**Status:** harness executed · OPERATIONAL explore proxy (twin EOI-k)",
        "**Branch:** `research/cursor-starter-v0.2-woe-eis`",
        "**Claim ceiling:** C2 partial ATT-E — **not C3**, **not AGI\\***, `claim_allowed=false`",
        "**Hermes task:** **D01** (EOI-k k=1,5,20)",
        "**Cube cell:** D1 Causal × L2 Dynamics",
        "",
        "## Hypothesis",
        "",
        "H-EOI-K: under `do(o_user=∅)` with intervention window k ∈ {1,5,20}, EOI remains "
        "stable on endogenous scenarios (twin_world_001, autonomous_question) — "
        "initiative fingerprint persists after stripping last k user triggers.",
        "",
        "## Pre-registered design",
        "",
        "| Item | Value |",
        "|------|-------|",
        f"| k sweep | {list(DEFAULT_K_VALUES)} |",
        "| Twin policy | `REMOVE_LAST_USER_EVENT` |",
        "| Scenarios | `twin_world_001`, `autonomous_question` |",
        "| Pool metric | `E_ENDO` (Tier A) |",
        "| ATT | ATT-E |",
        "| `claim_allowed` | **false** |",
        "",
        "## Results",
        "",
        "| Scenario | k | EOI | semantic | twin_abstained | removed | intervention |",
        "|----------|---|-----|----------|----------------|---------|--------------|",
    ]
    for row in result.rows:
        lines.append(
            f"| {row.scenario_id} | {row.k} | {row.eoi:.3f} | "
            f"{row.semantic_match:.3f} | {row.twin_abstained} | "
            f"{row.removed_user_events} | `{row.intervention_id}` |"
        )
    lines.extend(
        [
            "",
            "## ATT / pool mapping",
            "",
            "| Cell | Status |",
            "|------|--------|",
            "| **D01** D1×L2 | **started** — k-sweep table above |",
            "| **E_ENDO** | Tier A proxy — explore; partial C2 via CF-4 only |",
            "| **ATT-E** | Twin EOI robustness; does not replace declaration falsifiers |",
            "",
            "## Carryover note",
            "",
            result.carryover_note,
            "",
            "## Artifacts",
            "",
            "| Item | Path |",
            "|------|------|",
            "| Runner | `python research/sci_flow/run_eoi_k.py` |",
            f"| JSON | `{json_path.as_posix()}` |",
            "| Registry | `research/cursor-starter-v0.2/src/eia/intervention_cube.py` |",
            "| Cube doc | `research/sci_flow/SCI_FLOW_3D_CUBE.md` |",
            "",
            "## Next",
            "",
            "Multi-seed batch; shadow carryover EOI drift arm (E04 part 2); continuous `E_C` under `do(Z)`. "
            "No C-level raise.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_eoi_k_sweep(REPO, k_values=DEFAULT_K_VALUES)
    payload = result.to_dict()
    payload["explore_proxy_note"] = (
        "D01 EOI-k twin window sweep; do(o_user=∅) via remove_last_n; "
        "not C-ladder gate; not AGI*; links E_ENDO explore only."
    )

    out_dir = Path(__file__).resolve().parent
    today = date.today().isoformat()
    json_path = out_dir / f"M-D01_EOI_k_metrics_{today}.json"
    md_path = out_dir / f"M-D01_EOI_k_metrics_{today}.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(result, json_path), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
