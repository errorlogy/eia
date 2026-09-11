#!/usr/bin/env python3
"""D01 multi-seed EOI-k batch + E_C continuous probe (D1×L2 deepen).

Seeds 0, 7, 42 on twin scenarios + eoi_k_steered. claim_allowed=false.
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

from e_c_continuous_harness import run_e_c_continuous_probe  # noqa: E402
from eoi_k_harness import (  # noqa: E402
    DEFAULT_BATCH_SEEDS,
    DEFAULT_K_VALUES,
    run_eoi_k_batch,
)


def _markdown(batch, e_c, json_path: Path, today: str) -> str:
    lines = [
        f"# M-D01 — EOI-k multi-seed batch + E_C probe (D1×L2) — {today}",
        "",
        "**Status:** batch harness executed · OPERATIONAL explore proxy",
        "**Branch:** `research/cursor-starter-v0.2-woe-eis`",
        "**Claim ceiling:** C2 partial ATT-E — **not C3**, **not AGI\\***, `claim_allowed=false`",
        "**Hermes tasks:** **D01** (multi-seed EOI-k), **E05** (continuous E_C stub)",
        "**Cube cell:** D1 Causal × L2 Dynamics",
        "",
        "## Pre-registered design",
        "",
        "| Item | Value |",
        "|------|-------|",
        f"| Seeds | {list(DEFAULT_BATCH_SEEDS)} |",
        f"| k sweep | {list(DEFAULT_K_VALUES)} |",
        "| Scenarios | `twin_world_001`, `autonomous_question`, `eoi_k_steered` |",
        "| EOI pool metric | `E_ENDO` |",
        "| E_C pool metric | `E_C` (proxy) |",
        "| `claim_allowed` | **false** |",
        "",
        "## EOI-k — `eoi_k_steered` by seed",
        "",
        "| seed | k=1 | k=5 | k=20 |",
        "|------|-----|-----|------|",
    ]
    steered = batch.to_dict()["steered_eoi_by_seed"]
    for seed in batch.seeds:
        vals = steered.get(str(seed), {})
        lines.append(
            f"| {seed} | {vals.get('1', '—')} | {vals.get('5', '—')} | {vals.get('20', '—')} |"
        )

    lines.extend(
        [
            "",
            "## E_C — mean by intervention (do(Z))",
            "",
            "| intervention_id | mean E_C |",
            "|-----------------|----------|",
        ]
    )
    for iid, stats in sorted(e_c.to_dict()["summary_by_intervention"].items()):
        lines.append(f"| `{iid}` | {stats['mean_e_c']:.3f} |")

    lines.extend(
        [
            "",
            "## ATT / pool mapping",
            "",
            "| Cell | Status |",
            "|------|--------|",
            "| **D01** D1×L2 | **deepened** — multi-seed EOI-k + E_C probe |",
            "| **E_ENDO** | Tier A explore via EOI-k batch |",
            "| **E_C** | Tier A proxy — continuous stub under do(Z) |",
            "",
            "## Artifacts",
            "",
            "| Item | Path |",
            "|------|------|",
            "| Batch runner | `python research/sci_flow/run_eoi_k_batch.py` |",
            "| E_C runner | `python research/sci_flow/run_e_c_continuous.py` |",
            f"| JSON | `{json_path.as_posix()}` |",
            "",
            "## Next",
            "",
            "Wire E_C + D01 rows into D1×L3 proof ledger; D1-L3 empirical batch. No C-level raise.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    batch = run_eoi_k_batch(REPO, seeds=DEFAULT_BATCH_SEEDS, k_values=DEFAULT_K_VALUES)
    e_c = run_e_c_continuous_probe()

    today = date.today().isoformat()
    payload: dict = {
        "artifact_id": "M-D01_EOI_k_batch",
        "date": today,
        "claim_ceiling": "C2_partial_ATT_E",
        "claim_allowed": False,
        "seeds": list(DEFAULT_BATCH_SEEDS),
        "k_values": list(DEFAULT_K_VALUES),
        "eoi_k_batch": batch.to_dict(),
        "e_c_continuous": e_c.to_dict(),
        "explore_proxy_note": (
            "Multi-seed EOI-k counterfactual batch + minimal continuous E_C under "
            "registered do(Z); not C-ladder gate; claim_allowed=false."
        ),
    }

    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / f"M-D01_EOI_k_batch_{today}.json"
    md_path = out_dir / f"M-D01_EOI_k_batch_{today}.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(batch, e_c, json_path, today), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
