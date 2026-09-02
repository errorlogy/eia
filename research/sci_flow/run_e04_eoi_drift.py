#!/usr/bin/env python3
"""E04 part 2: EOI drift on 50-tick shadow carryover session (D2×L2).

Longitudinal initiative-fingerprint stability vs bootstrap baseline on the same
Phase 2 carryover path as M-E04/D05 DSR. No user prompts. claim_allowed=false.
Not C3 / not AGI*.
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

from eoi_drift_harness import (  # noqa: E402
    EOI_DRIFT_TARGET_COGNITIVE_TICKS,
    EOI_ENDOGENOUS_THRESHOLD,
    run_eoi_drift_longitudinal_session,
)

ARTIFACT_STEM = "M-E04_EOI_drift_2026-09-02"


def _markdown(result, json_path: Path) -> str:
    lines = [
        f"# M-E04-DRIFT — EOI drift on shadow carryover — 2026-09-02",
        "",
        "**Status:** harness executed · OPERATIONAL explore proxy (longitudinal EOI drift)",
        "**Branch:** `research/cursor-starter-v0.2-woe-eis`",
        "**Claim ceiling:** C2 partial ATT-E — **not C3**, **not AGI\\***, `claim_allowed=false`",
        "**Hermes task:** **E04** part 2 (longitudinal EOI drift; DSR in Entry 028)",
        "**Cube cell:** D2 Dynamics × L2 Harness",
        "",
        "## Hypothesis",
        "",
        "H-EOI-DRIFT: on the Phase 2 shadow carryover path with **no user prompts**, "
        "initiative fingerprint (4-field structural match via `EOIScorer`) remains "
        "stable vs bootstrap baseline across 50 cognitive ticks — EOI ≥ 0.50 on every sample.",
        "",
        "## Pre-registered design",
        "",
        "| Item | Value |",
        "|------|-------|",
        f"| Session length | {result.target_cognitive_ticks} cognitive ticks |",
        "| Bootstrap | `CLOSED_LOOP` shadow episode (seed 0) |",
        "| Continuation | `run_shadow_carryover_tick` (ambient obs only) |",
        "| User prompts | 0 |",
        "| Twin intervention | none (`removed_count=0`) |",
        f"| EOI threshold | {EOI_ENDOGENOUS_THRESHOLD} |",
        "| Pool metric | `E_ENDO` (Tier A explore proxy) |",
        "| ATT | ATT-E longitudinal stability |",
        "| `claim_allowed` | **false** |",
        "",
        "## Results (seed 0)",
        "",
        "| Metric | Value | Target |",
        "|--------|-------|--------|",
        f"| Cognitive ticks reached | **{result.cognitive_ticks_reached}** | E04: ≥ {result.target_cognitive_ticks} |",
        f"| Initiative samples | {result.n_initiative_samples} | ≥ {result.target_cognitive_ticks} |",
        f"| `eoi_min` | **{result.eoi_min:.3f}** | ≥ {EOI_ENDOGENOUS_THRESHOLD} |",
        f"| `eoi_max` | **{result.eoi_max:.3f}** | — |",
        f"| `eoi_mean` | **{result.eoi_mean:.3f}** | — |",
        f"| `eoi_drift_span` | **{result.eoi_drift_span:.3f}** | low = stable |",
        f"| `persistence_fraction` | **{result.persistence_fraction:.3f}** | 1.0 |",
        f"| Baseline target | `{result.baseline_target}` | — |",
        f"| Baseline kind | `{result.baseline_kind}` | — |",
        f"| **EOI pass** | **{result.eoi_pass}** | — |",
        f"| **E04 pass** | **{result.e04_pass}** | — |",
        "",
        "## Sample tail (last 5 ticks)",
        "",
        "| tick | EOI | target | kind | abstained |",
        "|------|-----|--------|------|-----------|",
    ]
    for row in result.rows[-5:]:
        tgt = row.target_belief_id or "—"
        kind = row.kind or "—"
        lines.append(
            f"| {row.cognitive_tick} | {row.eoi:.3f} | `{tgt}` | `{kind}` | {row.abstained} |"
        )

    lines.extend(
        [
            "",
            "## ATT / pool mapping",
            "",
            "| Cell | Status |",
            "|------|--------|",
            "| **E04** part 2 | Longitudinal EOI drift — **done** on shadow path |",
            "| **D2×L2** | Extended with `run_e04_eoi_drift.py` |",
            "| **E_ENDO** | Tier A explore proxy; partial C2 only |",
            "| **M-E04/D05 DSR** | Orthogonal `B_D` evidence (Entry 028) |",
            "",
            "## Gap vs live daemon",
            "",
            "EOI drift measured on `ShadowSessionCarryover` + `run_shadow_carryover_tick`. "
            "Production daemon still resets loop per tick unless "
            "`EIA_DAEMON_BELIEF_CARRYOVER=1` (off by default).",
            "",
            "## Artifacts",
            "",
            "| Item | Path |",
            "|------|------|",
            "| Harness | `research/sci_flow/eoi_drift_harness.py` |",
            "| Runner | `python research/sci_flow/run_e04_eoi_drift.py` |",
            f"| JSON | `{json_path.as_posix()}` |",
            "| Tests | `tests/test_e04_eoi_drift.py` |",
            "",
            "## Next",
            "",
            "Multi-seed EOI drift batch; live daemon StateStore carryover. No C-level raise.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_eoi_drift_longitudinal_session(
        target_cognitive_ticks=EOI_DRIFT_TARGET_COGNITIVE_TICKS,
        seed=0,
    )
    payload = result.to_dict()
    payload.update(
        {
            "milestone": "M-E04-DRIFT",
            "hermes_tasks": ["E04"],
            "emit_m0": False,
            "shadow": True,
            "live_telegram": False,
            "user_prompt_ticks": 0,
            "pre_registered": {
                "target_cognitive_ticks": EOI_DRIFT_TARGET_COGNITIVE_TICKS,
                "eoi_endogenous_threshold": EOI_ENDOGENOUS_THRESHOLD,
                "no_user_prompt": True,
                "twin_intervention": False,
                "emit_m0": False,
                "shadow_first": True,
            },
            "explore_proxy_note": (
                "E04 part 2 longitudinal EOI drift on Phase 2 shadow carryover; "
                "initiative fingerprint stability vs bootstrap baseline; not C-ladder gate; "
                "orthogonal to D01 twin EOI-k counterfactual replay."
            ),
        }
    )

    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / f"{ARTIFACT_STEM}.json"
    md_path = out_dir / f"{ARTIFACT_STEM}.md"

    slim = {k: v for k, v in payload.items() if k != "rows"}
    slim["row_count"] = len(payload.get("rows", []))

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(result, json_path), encoding="utf-8")

    print(json.dumps(slim, indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0 if result.eoi_pass and result.e04_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
