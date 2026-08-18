#!/usr/bin/env python3
"""PAI-EI-E0-001 smoke run — baselines on twin_world eval set."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research" / "pai-ei-e0-001-smoke.json"
EXPERIMENT_ID = "PAI-EI-E0-001"

BASELINES = ("reactive_only", "event_rule", "full_eia")


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


def _run_row(scenario_path: Path, baseline: str, seed: int) -> dict:
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from eia.experiment.baseline import BaselineCondition
    from eia.pipeline import run_scenario

    run = run_scenario(
        scenario_path,
        traces_dir=ROOT / "traces" / "pai_ei_e0_001",
        seed=seed,
        baseline=BaselineCondition(baseline),
    )
    initiative = run["initiative"]
    decision = run["decision"]
    twin = run["twin_result"]
    auth = run["authentic_verdict"]

    proactive = not initiative.abstained and decision.outcome.value != "abstain"
    endogenous_useful = (
        proactive
        and twin.eoi >= 0.5
        and auth.initiative_class == "endogenous"
    )

    return {
        "scenario_id": scenario_path.stem,
        "baseline": baseline,
        "seed": seed,
        "eoi": round(twin.eoi, 4),
        "initiative_abstained": initiative.abstained,
        "initiative_kind": (
            initiative.candidate.kind.value if initiative.candidate else None
        ),
        "contact_outcome": decision.outcome.value,
        "initiative_class": auth.initiative_class,
        "euir_proxy": endogenous_useful,
        "trace_id": run["loop"].trace.trace_id,
    }


def _aggregate(rows: list[dict]) -> dict:
    n = len(rows) or 1
    return {
        "scenario_count": len(rows),
        "mean_eoi": round(sum(r["eoi"] for r in rows) / n, 4),
        "initiative_count": sum(0 if r["initiative_abstained"] else 1 for r in rows),
        "abstain_rate": round(sum(1 for r in rows if r["initiative_abstained"]) / n, 4),
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
            row = _run_row(scenario_path, baseline, seed)
            per_scenario.append(row)
            by_baseline[baseline].append(row)

    summaries = {b: _aggregate(rows) for b, rows in by_baseline.items()}
    full = summaries["full_eia"]

    payload = {
        "experiment_id": EXPERIMENT_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": "E0",
        "status": "smoke_partial",
        "scenario_count": full["scenario_count"],
        "baselines": list(BASELINES),
        "summaries": summaries,
        "per_scenario": per_scenario,
        "targets": {
            "eoi_vs_p3": "pending_loop_18",
            "initiative_precision": "pending_loop_19",
            "contact_burden_max_per_day": 2,
        },
    }

    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
