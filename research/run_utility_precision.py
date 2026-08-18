#!/usr/bin/env python3
"""Score initiative precision against ground_truth labels on eval set."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "research" / "utility-precision-report.md"
REPORT_JSON = ROOT / "research" / "utility-precision-report.json"


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


def main() -> int:
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from eia.experiment.baseline import BaselineCondition
    from eia.pipeline import run_scenario
    from eia.scenarios import load_ground_truth, score_initiative_against_label

    per_scenario: list[dict] = []
    baselines = ("full_eia", "predictive_p3", "event_rule")

    for scenario_path in _scenario_paths():
        gt = load_ground_truth(scenario_path)
        if not gt or not gt.get("initiatives"):
            continue
        label = gt["initiatives"][0]
        seed = 100 + int(scenario_path.stem.split("_")[-1])

        for baseline in baselines:
            run = run_scenario(
                scenario_path,
                traces_dir=ROOT / "traces" / "utility_precision",
                seed=seed,
                baseline=BaselineCondition(baseline),
            )
            score = score_initiative_against_label(run, label)
            per_scenario.append(
                {
                    "scenario_id": scenario_path.stem,
                    "baseline": baseline,
                    "seed": seed,
                    **score,
                }
            )

    def _aggregate(baseline: str) -> dict:
        rows = [r for r in per_scenario if r["baseline"] == baseline]
        n = len(rows) or 1
        contacts = [r for r in rows if r["contact_made"]]
        return {
            "scenario_count": len(rows),
            "initiative_precision": round(
                sum(1 for r in rows if r["precision_hit"]) / n, 4
            ),
            "kind_match_rate": round(sum(1 for r in rows if r["kind_match"]) / n, 4),
            "contact_precision": round(
                sum(1 for r in contacts if r["contact_useful"]) / (len(contacts) or 1),
                4,
            ) if contacts else 0.0,
            "contacts_made": len(contacts),
            "precision_hits": sum(1 for r in rows if r["precision_hit"]),
        }

    summaries = {b: _aggregate(b) for b in baselines}
    full = summaries["full_eia"]

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_count": full["scenario_count"],
        "baselines": list(baselines),
        "summaries": summaries,
        "per_scenario": per_scenario,
        "target_initiative_precision": 0.75,
        "full_eia_meets_target": full["initiative_precision"] >= 0.75,
    }

    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Utility Precision Report — Ground Truth Scoring",
        "",
        f"**Date:** {payload['timestamp'][:10]}  ",
        "**Author:** Roman Kuznetsov  ",
        f"**Scenarios:** {payload['scenario_count']} with ground_truth labels",
        "",
        "## Summary",
        "",
        "| Baseline | Initiative precision | Kind match | Contact precision | Contacts |",
        "|----------|-------------------|------------|-------------------|----------|",
    ]
    for baseline in baselines:
        s = summaries[baseline]
        lines.append(
            f"| {baseline} | {s['initiative_precision']:.0%} "
            f"({s['precision_hits']}/{s['scenario_count']}) | "
            f"{s['kind_match_rate']:.0%} | {s['contact_precision']:.0%} | "
            f"{s['contacts_made']} |"
        )

    target = payload["target_initiative_precision"]
    lines.extend(
        [
            "",
            f"**Target initiative precision:** ≥ {target:.0%} (MVP-0 low-risk domain)",
            f"**full_eia meets target:** {'yes' if payload['full_eia_meets_target'] else 'no'}",
            "",
            "## Interpretation",
            "",
            "Initiative precision = run matches ground_truth expected_kind, EOI threshold, "
            "and endogenous class when contact expected. Contact precision = useful contacts "
            "/ all contacts made (send_now/defer).",
            "",
            "## Per-scenario results (full_eia)",
            "",
            "| Scenario | Expected | Actual kind | EOI | Class | Precision hit | Contact useful |",
            "|----------|----------|-------------|-----|-------|---------------|----------------|",
        ]
    )
    for row in per_scenario:
        if row["baseline"] != "full_eia":
            continue
        lines.append(
            f"| {row['scenario_id']} | {row['expected_kind']} | {row['actual_kind']} | "
            f"{row['eoi']} | {row['initiative_class']} | "
            f"{'✓' if row['precision_hit'] else '✗'} | "
            f"{'✓' if row['contact_useful'] else '✗'} |"
        )

    lines.extend(
        [
            "",
            "See also: `research/ground-truth-schema.md`, `src/eia/scenarios/__init__.py`.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
