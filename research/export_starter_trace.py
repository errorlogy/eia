#!/usr/bin/env python3
"""Export starter runtime causal ledger as JSONL for structural comparison."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STARTER = ROOT / "research" / "cursor-starter-v0.1"
DEFAULT_SCENARIO = STARTER / "examples" / "twin_world_001.json"
OUTPUT = ROOT / "research" / "starter_trace_twin_world_001.jsonl"


def _export_ledger(runtime, scenario_name: str, seed: int = 101) -> list[dict]:
    """Convert starter CausalLedger nodes to main-compatible JSONL records."""
    records: list[dict] = []
    trace_id = f"starter-{scenario_name}-{seed}"
    records.append(
        {
            "type": "header",
            "trace_id": trace_id,
            "metadata": {
                "seed": seed,
                "scenario_path": scenario_name,
                "code_version": "cursor-starter-v0.1",
                "export_source": "research/export_starter_trace.py",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
    )
    for node in runtime.ledger.nodes:
        records.append(
            {
                "type": "node",
                "id": node.node_id,
                "kind": node.node_type,
                "timestamp": node.timestamp.isoformat(),
                "payload_digest": node.payload_digest,
                "parents": list(node.parents),
            }
        )
        for parent in node.parents:
            records.append(
                {
                    "type": "edge",
                    "source_id": parent,
                    "target_id": node.node_id,
                }
            )
    return records


def main() -> int:
    scenario_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SCENARIO
    if not scenario_path.is_file():
        print(f"Scenario not found: {scenario_path}", file=sys.stderr)
        return 1

    sys.path.insert(0, str(STARTER / "src"))
    from eia.simulator import SimulationRunner, load_scenario

    scenario = load_scenario(scenario_path)
    simulation = SimulationRunner().run(scenario)
    records = _export_ledger(simulation.runtime, scenario.name)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    summary = {
        "scenario": scenario.name,
        "node_count": len(simulation.runtime.ledger.nodes),
        "output": str(OUTPUT.relative_to(ROOT)),
        "trace_id": records[0]["trace_id"],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
