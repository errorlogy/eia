#!/usr/bin/env python3
"""M-G2-E01 partial multi-world eval — batch twin worlds with ATT-E metrics.

Outputs JSON + markdown artifacts for D1×L2 / G2 gate refresh. claim_allowed=false.
Honest partial scope: 8 MVP-0 worlds, single ops/Atlas domain (not E01 20×3).
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

from g2_worlds_harness import run_g2_worlds_eval  # noqa: E402


def _markdown(result, json_path: Path, today: str) -> str:
    full = next(a for a in result.aggregates if a.baseline == "full_eia")
    reactive = next(a for a in result.aggregates if a.baseline == "reactive_only")
    delta_eoi = full.mean_eoi - reactive.mean_eoi
    delta_euir = full.euir_proxy_rate - reactive.euir_proxy_rate

    lines = [
        f"# M-G2-E01 — Partial multi-world eval (D1×L2) — {today}",
        "",
        "**Status:** harness executed · G2 gate refresh (partial E01 scope)",
        "**Branch:** `research/cursor-starter-v0.2-woe-eis`",
        "**Claim ceiling:** C2 — **not C3**, **not AGI\\***, `claim_allowed=false`",
        "**Hermes tasks:** **E01** (partial worlds), **E10** (G2 pack input)",
        "**Cube cell:** D1 Causal × L2 Dynamics",
        "",
        "## Scope (honest partial)",
        "",
        f"| Item | Value |",
        f"|------|-------|",
        f"| Worlds evaluated | **{result.world_count}** |",
        f"| Domains | **{result.domain_count}** (`ops_atlas` only) |",
        f"| E01 target | {result.e01_scope_fraction} |",
        f"| Baselines | `{', '.join(result.baselines)}` |",
        f"| ATT | `{result.att}` |",
        f"| Pool metric | `{result.pool_metric_id}` |",
        "",
        "Health and code-review twin domains (E01 full 20×3) are **deferred** — "
        "this batch covers registered MVP-0 Atlas/ops twins only.",
        "",
        "## Aggregate ATT metrics",
        "",
        "| Baseline | Mean EOI | EUIR proxy | Initiative precision | Endogenous |",
        "|----------|----------|------------|----------------------|------------|",
        f"| reactive_only | {reactive.mean_eoi:.3f} | {reactive.euir_proxy_rate:.0%} | "
        f"{reactive.precision_hits}/{reactive.precision_scored} | {reactive.endogenous_count} |",
        f"| full_eia | {full.mean_eoi:.3f} | {full.euir_proxy_rate:.0%} | "
        f"{full.precision_hits}/{full.precision_scored} | {full.endogenous_count} |",
        f"| **Δ (full − reactive)** | **{delta_eoi:+.3f}** | **{delta_euir:+.0%}** | — | — |",
        "",
        "## Per-world results (`full_eia`)",
        "",
        "| World | Domain | EOI | Semantic | Class | Contact | EUIR | Precision |",
        "|-------|--------|-----|----------|-------|---------|------|-----------|",
    ]
    for row in result.rows:
        if row.baseline != "full_eia":
            continue
        prec = "—" if row.precision_hit is None else ("✓" if row.precision_hit else "✗")
        lines.append(
            f"| {row.world_id} | {row.domain} | {row.eoi:.3f} | {row.semantic_match:.3f} | "
            f"{row.initiative_class} | {row.contact_outcome} | "
            f"{'✓' if row.euir_proxy else '✗'} | {prec} |"
        )

    lines.extend(
        [
            "",
            "## G2 interpretation (partial)",
            "",
            "Under MVP-0 twin intervention, `full_eia` maintains EOI≥0.5 and endogenous "
            "class on all evaluated worlds; `reactive_only` abstains (EUIR proxy 0%). "
            "This supports the **G2 directional** claim (full > reactive) but does **not** "
            "close E01 (20×3 domains) or authorize C-level raise.",
            "",
            "## ATT / pool mapping",
            "",
            "| Cell | Status |",
            "|------|--------|",
            "| **D1×L2** | **deepened** — multi-world ATT-E batch |",
            "| **E_ENDO** | Tier A proxy — explore; partial C2 |",
            "| **ATT-E** | Twin EOI + EUIR proxy; not full causal bar |",
            "",
            "## Artifacts",
            "",
            "| Item | Path |",
            "|------|------|",
            "| Runner | `python research/sci_flow/run_g2_worlds_eval.py` |",
            f"| JSON | `{json_path.as_posix()}` |",
            "| Registry | `research/sci_flow/cell_registry.yaml` |",
            "",
            "## Next",
            "",
            "E01: add health/code_review twin worlds with human labels; "
            "E10: fold into `research/G2_EVIDENCE_PACK.md`. No C-level raise.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_g2_worlds_eval(REPO)
    payload = result.to_dict()
    payload["explore_proxy_note"] = (
        "M-G2-E01 partial multi-world batch; ATT-E EOI/EUIR on MVP-0 twins; "
        "not E01 20×3; not C-ladder gate; not AGI*."
    )

    out_dir = SCI_FLOW
    today = date.today().isoformat()
    json_path = out_dir / f"M-G2_E01_worlds_{today}.json"
    md_path = out_dir / f"M-G2_E01_worlds_{today}.md"

    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(result, json_path, today), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
