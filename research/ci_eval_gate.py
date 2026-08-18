#!/usr/bin/env python3
"""CI gate: eval suite quality thresholds for full_eia.

Runs all 6 eval scenarios (twin_world_001 + twin_world_002–006) under full_eia.
Fails when:
  - mean EOI < 0.8 for full_eia
  - initiative precision < 0.75 vs ground_truth labels

Set EIA_CI_EVAL_GATE=0 to skip (always exit 0).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIN_MEAN_EOI = 0.8
MIN_INITIATIVE_PRECISION = 0.75


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


def _skip() -> int:
    print("ci_eval_gate: skipped (EIA_CI_EVAL_GATE!=1)")
    return 0


def main() -> int:
    if os.environ.get("EIA_CI_EVAL_GATE", "1") != "1":
        return _skip()

    sys.path.insert(0, str(ROOT / "src"))
    from eia.experiment.baseline import BaselineCondition
    from eia.pipeline import run_scenario
    from eia.scenarios import load_ground_truth, score_initiative_against_label

    per_scenario: list[dict] = []
    errors: list[str] = []

    for scenario_path in _scenario_paths():
        seed = 100 + int(scenario_path.stem.split("_")[-1])
        run = run_scenario(
            scenario_path,
            traces_dir=ROOT / "traces" / "ci_eval_gate",
            seed=seed,
            baseline=BaselineCondition.FULL_EIA,
        )
        gt = load_ground_truth(scenario_path)
        label = gt["initiatives"][0] if gt and gt.get("initiatives") else None
        score = score_initiative_against_label(run, label) if label else None

        per_scenario.append(
            {
                "scenario_id": scenario_path.stem,
                "seed": seed,
                "eoi": round(run["twin_result"].eoi, 4),
                "initiative_class": run["authentic_verdict"].initiative_class,
                "precision_hit": score["precision_hit"] if score else None,
            }
        )

    if len(per_scenario) != 6:
        errors.append(f"expected 6 eval scenarios, got {len(per_scenario)}")

    mean_eoi = sum(r["eoi"] for r in per_scenario) / (len(per_scenario) or 1)
    precision_hits = sum(1 for r in per_scenario if r["precision_hit"])
    initiative_precision = precision_hits / (len(per_scenario) or 1)

    if mean_eoi < MIN_MEAN_EOI:
        errors.append(
            f"mean EOI {mean_eoi:.4f} < threshold {MIN_MEAN_EOI}"
        )
    if initiative_precision < MIN_INITIATIVE_PRECISION:
        errors.append(
            f"initiative precision {initiative_precision:.4f} < threshold "
            f"{MIN_INITIATIVE_PRECISION}"
        )

    payload = {
        "scenario_count": len(per_scenario),
        "mean_eoi": round(mean_eoi, 4),
        "initiative_precision": round(initiative_precision, 4),
        "precision_hits": precision_hits,
        "thresholds": {
            "min_mean_eoi": MIN_MEAN_EOI,
            "min_initiative_precision": MIN_INITIATIVE_PRECISION,
        },
        "per_scenario": per_scenario,
        "passed": not errors,
        "errors": errors,
    }
    print(json.dumps(payload, indent=2))

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    print("ci_eval_gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
