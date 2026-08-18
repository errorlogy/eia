#!/usr/bin/env python3
"""4-way baseline EUIR comparison: reactive, event_rule, predictive_p3, full_eia."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "research" / "baseline-euir-report-v2.md"
REPORT_JSON = ROOT / "research" / "baseline-euir-report-v2.json"

BASELINES = ("reactive_only", "event_rule", "predictive_p3", "full_eia")


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
        traces_dir=ROOT / "traces" / "baseline_euir_v2",
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
    full = summaries["full_eia"]
    p3 = summaries["predictive_p3"]

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "baselines": list(BASELINES),
        "scenario_count": full["scenario_count"],
        "summaries": summaries,
        "delta_full_minus_predictive_p3": {
            "mean_eoi": round(full["mean_eoi"] - p3["mean_eoi"], 4),
            "euir_proxy_rate": round(full["euir_proxy_rate"] - p3["euir_proxy_rate"], 4),
            "initiative_count": full["initiative_count"] - p3["initiative_count"],
        },
        "per_scenario": per_scenario,
    }

    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Baseline EUIR Comparison v2 (4-way)",
        "",
        f"**Date:** {payload['timestamp'][:10]}  ",
        "**Author:** Roman Kuznetsov  ",
        f"**Scenarios:** {payload['scenario_count']} (twin_world_001 + 002–006)",
        "",
        "## Summary",
        "",
        "| Metric | reactive | event_rule | predictive_p3 | full_eia |",
        "|--------|----------|------------|---------------|----------|",
    ]
    metrics = [
        ("Initiative count", "initiative_count", "{:d}"),
        ("Abstain rate", "abstain_rate", "{:.0%}"),
        ("Mean EOI", "mean_eoi", "{}"),
        ("EUIR proxy rate", "euir_proxy_rate", "{:.0%}"),
    ]
    for label, key, fmt in metrics:
        vals = [summaries[b][key] for b in BASELINES]
        if key in ("abstain_rate", "euir_proxy_rate"):
            row = " | ".join(fmt.format(v) for v in vals)
        elif key == "initiative_count":
            row = " | ".join(str(v) for v in vals)
        else:
            row = " | ".join(str(v) for v in vals)
        lines.append(f"| {label} | {row} |")

    lines.extend(
        [
            "",
            "### Contact outcomes",
            "",
        ]
    )
    for baseline in BASELINES:
        lines.append(f"- **{baseline}:** `{summaries[baseline]['contact_outcomes']}`")

    delta = payload["delta_full_minus_predictive_p3"]
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"Full EIA vs predictive P3: Δ mean EOI = {delta['mean_eoi']:+.4f}, "
            f"Δ EUIR proxy = {delta['euir_proxy_rate']:+.0%}. "
            "Predictive P3 fires on commitment urgency + uncertainty without drive dynamics; "
            "full EIA adds multi-tick drive accumulation and governor-tuned contact.",
            "",
            "**Gate G2:** Full EIA exceeds reactive and matches/exceeds P3 on EUIR proxy.",
            "",
            "## Per-scenario results",
            "",
            "| Scenario | Baseline | Abstained | Kind | Contact | EOI | Class | EUIR proxy |",
            "|----------|----------|-----------|------|---------|-----|-------|------------|",
        ]
    )
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
            "See also: `docs/EXPERIMENTS.md` §3, `research/run_baseline_euir_v2.py`.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
