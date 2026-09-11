#!/usr/bin/env python3
"""M-LIVE-PATH: shadow vs opt-in live daemon carryover witness (D2×L3).

Produces dated JSON + markdown artifacts comparing in-process shadow carryover
against the real ``run_daemon_tick`` + ``StateStore`` hydration path.

claim_allowed=false · C2 ceiling · no AGI* · no WoE→main merge.
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

from live_path_witness_harness import run_live_path_witness  # noqa: E402

ARTIFACT_DATE = "2026-09-02"
ARTIFACT_STEM = f"M-LIVE_PATH_witness_{ARTIFACT_DATE}"


def _markdown(result, json_path: Path) -> str:
    shadow_last = result.shadow_snapshots[-1]
    live_on_2 = result.live_on_snapshots[-1]
    checks = result.parity_checks

    lines = [
        f"# M-LIVE-PATH — shadow vs live carryover witness — {ARTIFACT_DATE}",
        "",
        "**Status:** harness executed · structural parity witness (D2×L3)",
        "**Branch:** `research/cursor-starter-v0.2-woe-eis`",
        "**Claim ceiling:** C2 — **not C3**, **not AGI\\***, `claim_allowed=false`",
        "**Cube cell:** D2 Dynamics × L3 Witness",
        "",
        "## Hypothesis",
        "",
        "H-LIVE-PATH: opt-in live daemon carryover (`EIA_DAEMON_BELIEF_CARRYOVER=1`) "
        "round-trips beliefs + drives through `StateStore` across consecutive "
        "`run_daemon_tick` calls, matching the structural persistence properties "
        "of in-process `ShadowSessionCarryover` (session tick advance, hydration on "
        "tick 2, beliefs present). Default-off live path resets per tick.",
        "",
        "## Pre-registered design",
        "",
        "| Item | Value |",
        "|------|-------|",
        f"| Seed | {result.seed} |",
        f"| Shadow bootstrap | `CLOSED_LOOP` + {result.shadow_carryover_ticks} carryover ticks |",
        "| Live path | `run_daemon_tick(shadow_mode=True)` × 2 |",
        "| Carryover gate | `EIA_DAEMON_BELIEF_CARRYOVER=1` (live_on arm only) |",
        "| StateStore | SQLite temp DB per arm |",
        "| User prompts | 0 |",
        "| `claim_allowed` | **false** |",
        "",
        "## Shadow path (last snapshot)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| `session_tick` | **{shadow_last['session_tick']}** |",
        f"| `drive_tick` | **{shadow_last['drive_tick']}** |",
        f"| `drive_norm` | **{shadow_last['drive_norm']:.3f}** |",
        f"| `has_beliefs` | **{shadow_last['has_beliefs']}** |",
        f"| `used_carryover` | **{shadow_last['used_carryover']}** |",
        "",
        "## Live path — carryover ON (tick 2)",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| `session_tick` | **{live_on_2['session_tick']}** |",
        f"| `drive_tick` | **{live_on_2['drive_tick']}** |",
        f"| `drive_norm` | **{live_on_2['drive_norm']:.3f}** |",
        f"| `has_beliefs` | **{live_on_2['has_beliefs']}** |",
        f"| `used_carryover` | **{live_on_2['used_carryover']}** |",
        "",
        "## Parity checks",
        "",
        "| Check | Pass |",
        "|-------|------|",
    ]
    for name, passed in checks.items():
        lines.append(f"| `{name}` | **{passed}** |")

    lines.extend(
        [
            "",
            f"| **witness_pass** | **{result.witness_pass}** |",
            f"| **gap_narrowed** | **{result.gap_narrowed}** |",
            "",
            "## Gap vs shadow-only longitudinal",
            "",
            result.gap_vs_shadow,
            "",
            "DSR 50-tick and EOI drift remain shadow-instrumented; this witness "
            "documents that live `StateStore` hydration is operational when opted in. "
            "Residual gap: observation source and tick granularity differ.",
            "",
            "## Artifacts",
            "",
            "| Item | Path |",
            "|------|------|",
            "| Harness | `research/sci_flow/live_path_witness_harness.py` |",
            "| Runner | `python research/sci_flow/run_live_path_witness.py` |",
            f"| JSON | `{json_path.as_posix()}` |",
            "| Tests | `tests/test_live_path_witness.py` |",
            "",
            "## Next",
            "",
            "Multi-tick live longitudinal benchmark; APScheduler production soak. No C-level raise.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    result = run_live_path_witness()
    payload = {
        "date": ARTIFACT_DATE,
        "branch": "research/cursor-starter-v0.2-woe-eis",
        **result.to_dict(),
    }
    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / f"{ARTIFACT_STEM}.json"
    md_path = out_dir / f"{ARTIFACT_STEM}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(result, json_path), encoding="utf-8")

    summary = {k: v for k, v in payload.items() if not k.endswith("_snapshots")}
    print(json.dumps(summary, indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0 if result.witness_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
