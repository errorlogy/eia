#!/usr/bin/env python3
"""Run eval scenarios and log EOI metrics."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = ROOT / "evals"
OUTPUT = ROOT / "research" / "eval_eoi_log.json"


def main() -> int:
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from eia.pipeline import run_scenario

    scenarios = sorted(EVALS_DIR.glob("twin_world_*.yaml"))
    results = []

    for scenario_path in scenarios:
        seed = 100 + int(scenario_path.stem.split("_")[-1])
        run = run_scenario(
            scenario_path,
            traces_dir=ROOT / "traces" / "evals",
            seed=seed,
        )
        auth = run["authentic_verdict"]
        twin = run["twin_result"]
        initiative = run["initiative"]

        results.append(
            {
                "scenario_id": scenario_path.stem,
                "scenario_path": str(scenario_path.relative_to(ROOT)),
                "seed": seed,
                "eoi": round(twin.eoi, 4),
                "semantic_match": round(twin.semantic_match, 4),
                "initiative_abstained": initiative.abstained,
                "initiative_kind": (
                    initiative.candidate.kind.value if initiative.candidate else None
                ),
                "contact_outcome": run["decision"].outcome.value,
                "authentic": auth.is_authentic,
                "initiative_class": auth.initiative_class,
                "source_mass_independent": auth.source_mass_independent,
                "topology": auth.topology,
                "trace_id": run["loop"].trace.trace_id,
            }
        )

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "eval_count": len(results),
        "results": results,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
