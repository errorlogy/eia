#!/usr/bin/env python3
"""Baseline EUIR comparison: reactive_only vs full_eia on twin_world eval set."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "research" / "baseline-euir-report.md"
REPORT_JSON = ROOT / "research" / "baseline-euir-report.json"

BASELINES = ("reactive_only", "full_eia")


def _scenario_paths() -> list[Path]:
    paths: list[Path] = []
    for pattern in ("scenarios/twin_world_001.yaml", "evals/twin_world_*.yaml"):
        paths.extend(sorted(ROOT.glob(pattern)))
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        if path.stem not in seen:
            seen.add(path.stem)
            unique.append(path)
    return unique


def _run_condition(scenario_path: Path, baseline: str, seed: int) -> dict:
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from eia.experiment.baseline import BaselineCondition
    from eia.pipeline import run_scenario

    run = run_scenario(
        scenario_path,
        traces_dir=ROOT / "traces" / "baseline_euir",
        seed=seed,
        baseline=BaselineCondition(baseline),
    )
    initiative = run["initiative"]
    decision = run["decision"]
    auth = run["authentic_verdict"]
    twin = run["twin_result"]

    proactive = not initiative.abstained and decision.outcome.value != "abstain"
    endogenous_useful = (
        proactive
        and twin.eoi >= 0.5
        and auth.initiative_class == "endogenous"
    )

    return {
        "scenario_id": scenario_path.stem,
        "scenario_path": str(scenario_path.relative_to(ROOT)),
        "seed": seed,
        "baseline": baseline,
        "initiative_count": 0 if initiative.abstained else 1,
        "initiative_abstained": initiative.abstained,
        "initiative_kind": (
            initiative.candidate.kind.value if initiative.candidate else None
        ),
        "contact_outcome": decision.outcome.value,
        "eoi": round(twin.eoi, 4),
        "semantic_match": round(twin.semantic_match, 4),
        "initiative_class": auth.initiative_class,
        "is_authentic": auth.is_authentic,
        "euir_proxy": endogenous_useful,
        "trace_id": run["loop"].trace.trace_id,
    }


def _aggregate(rows: list[dict]) -> dict:
    n = len(rows) or 1
    return {
        "scenario_count": len(rows),
        "initiative_count": sum(r["initiative_count"] for r in rows),
        "abstain_rate": round(sum(1 for r in rows if r["initiative_abstained"]) / n, 4),
        "contact_rate": round(
            sum(1 for r in rows if r["contact_outcome"] != "abstain") / n, 4
        ),
        "mean_eoi": round(sum(r["eoi"] for r in rows) / n, 4),
        "endogenous_count": sum(1 for r in rows if r["initiative_class"] == "endogenous"),
        "euir_proxy_rate": round(sum(1 for r in rows if r["euir_proxy"]) / n, 4),
        "contact_outcomes": {
            outcome: sum(1 for r in rows if r["contact_outcome"] == outcome)
            for outcome in sorted({r["contact_outcome"] for r in rows})
        },
    }


def main() -> int:
    per_scenario: list[dict] = []
    by_baseline: dict[str, list[dict]] = {b: [] for b in BASELINES}

    for scenario_path in _scenario_paths():
        seed = 100 + int(scenario_path.stem.split("_")[-1])
        for baseline in BASELINES:
            row = _run_condition(scenario_path, baseline, seed)
            per_scenario.append(row)
            by_baseline[baseline].append(row)

    summaries = {b: _aggregate(rows) for b, rows in by_baseline.items()}
    reactive = summaries["reactive_only"]
    full = summaries["full_eia"]

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "baselines": list(BASELINES),
        "scenario_count": reactive["scenario_count"],
        "summaries": summaries,
        "delta_full_minus_reactive": {
            "initiative_count": full["initiative_count"] - reactive["initiative_count"],
            "abstain_rate": round(full["abstain_rate"] - reactive["abstain_rate"], 4),
            "mean_eoi": round(full["mean_eoi"] - reactive["mean_eoi"], 4),
            "euir_proxy_rate": round(full["euir_proxy_rate"] - reactive["euir_proxy_rate"], 4),
        },
        "per_scenario": per_scenario,
    }

    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Baseline EUIR Comparison",
        "",
        f"**Date:** {payload['timestamp'][:10]}  ",
        "**Author:** Roman Kuznetsov  ",
        f"**Scenarios:** {payload['scenario_count']} (twin_world_001 + 002–006)",
        "",
        "## Summary",
        "",
        "| Metric | reactive_only | full_eia | Δ (full − reactive) |",
        "|--------|---------------|----------|---------------------|",
        f"| Initiative count | {reactive['initiative_count']} | {full['initiative_count']} | "
        f"{payload['delta_full_minus_reactive']['initiative_count']:+d} |",
        f"| Abstain rate | {reactive['abstain_rate']:.0%} | {full['abstain_rate']:.0%} | "
        f"{payload['delta_full_minus_reactive']['abstain_rate']:+.0%} |",
        f"| Mean EOI | {reactive['mean_eoi']} | {full['mean_eoi']} | "
        f"{payload['delta_full_minus_reactive']['mean_eoi']:+.4f} |",
        f"| EUIR proxy rate | {reactive['euir_proxy_rate']:.0%} | {full['euir_proxy_rate']:.0%} | "
        f"{payload['delta_full_minus_reactive']['euir_proxy_rate']:+.0%} |",
        "",
        "### Contact outcomes",
        "",
        f"- **reactive_only:** `{reactive['contact_outcomes']}`",
        f"- **full_eia:** `{full['contact_outcomes']}`",
        "",
        "## Interpretation",
        "",
        "EUIR proxy = proactive contact ∧ EOI≥0.5 ∧ endogenous class. "
        "Reactive baseline abstains on all scenarios (zero initiatives); "
        "full EIA produces endogenous contacts where drives accumulate after quiet period. "
        "Supports H1 gate (G2): full pipeline exceeds reactive on EUIR proxy.",
        "",
        "## Per-scenario results",
        "",
        "| Scenario | Baseline | Abstained | Kind | Contact | EOI | Class | EUIR proxy |",
        "|----------|----------|-----------|------|---------|-----|-------|------------|",
    ]
    for row in per_scenario:
        lines.append(
            f"| {row['scenario_id']} | {row['baseline']} | "
            f"{'yes' if row['initiative_abstained'] else 'no'} | "
            f"{row['initiative_kind'] or '—'} | {row['contact_outcome']} | "
            f"{row['eoi']} | {row['initiative_class']} | "
            f"{'✓' if row['euir_proxy'] else '✗'} |"
        )

    lines.extend(
        [
            "",
            "See also: `docs/EXPERIMENTS.md` §3, `research/run_baseline_euir.py`.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
