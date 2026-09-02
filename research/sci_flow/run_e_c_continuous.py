#!/usr/bin/env python3
"""D1×L2 continuous E_C probe under registered do(Z) from intervention_cube.

Outputs markdown + JSON. claim_allowed=false. Pool metric E_C (proxy).
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCI_FLOW = Path(__file__).resolve().parent

if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from e_c_continuous_harness import (  # noqa: E402
    DEFAULT_E_C_SEEDS,
    run_e_c_continuous_probe,
)


def _markdown(result, json_path: Path, today: str) -> str:
    lines = [
        f"# M-D01 — Continuous E_C probe (D1×L2) — {today}",
        "",
        "**Status:** minimal proxy harness executed",
        "**Branch:** `research/cursor-starter-v0.2-woe-eis`",
        "**Claim ceiling:** C2 partial ATT-E — **not C3**, **not AGI\\***, `claim_allowed=false`",
        "**Pool metric:** `E_C` (proxy)",
        "**ATT:** ATT-E",
        "",
        "## Design",
        "",
        f"| Item | Value |",
        f"|------|-------|",
        f"| Seeds | {list(DEFAULT_E_C_SEEDS)} |",
        f"| Interventions | {list(result.intervention_ids)} |",
        f"| Formula | \\(E_C = C_{{\\mathrm{{int}}}} / (C_{{\\mathrm{{int}}}} + C_{{\\mathrm{{ext}}}})\\) |",
        f"| `claim_allowed` | **false** |",
        "",
        "## Summary by intervention",
        "",
        "| intervention_id | mean E_C | n |",
        "|-----------------|----------|---|",
    ]
    summary = result.to_dict()["summary_by_intervention"]
    for iid, stats in sorted(summary.items()):
        lines.append(f"| `{iid}` | {stats['mean_e_c']:.3f} | {stats['n']} |")

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| intervention | seed | default | do(Z) | c_int | c_ext | E_C |",
            "|--------------|------|---------|-------|-------|-------|-----|",
        ]
    )
    for row in result.rows:
        lines.append(
            f"| `{row.intervention_id}` | {row.seed} | {row.default_intent} | "
            f"{row.z_intent} | {row.c_int:.2f} | {row.c_ext:.2f} | {row.e_c:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Note",
            "",
            result.note,
            "",
            "## Artifacts",
            "",
            f"| JSON | `{json_path.as_posix()}` |",
            "| Registry | `research/cursor-starter-v0.2/src/eia/intervention_cube.py` |",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_e_c_continuous_probe()
    payload = result.to_dict()
    payload["explore_proxy_note"] = (
        "Minimal continuous E_C under registered do(Z); CF-4 WoE sim; "
        "not C-ladder gate; claim_allowed=false."
    )

    out_dir = Path(__file__).resolve().parent
    today = date.today().isoformat()
    json_path = out_dir / f"M-D01_E_C_continuous_{today}.json"
    md_path = out_dir / f"M-D01_E_C_continuous_{today}.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(result, json_path, today), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
