#!/usr/bin/env python3
"""CI gate: main vs starter structural trace diff expectations.

Exit 0 when twin_world_001 structural decomposition matches known baseline.
Set EIA_CI_TRACE_DIFF=0 to skip (always exit 0).
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Baseline from Loop 15 (research/trace-structural-diff-report.md)
EXPECTED_STARTER_NODES = 22
EXPECTED_MAIN_NODES = 25
EXPECTED_MAIN_ONLY_KINDS = frozenset(
    {
        "sense_making",
        "namm_hook",
        "initiative_emission",
        "contact_governor",
        "twin_run",
        "eoi_score",
        "authentic_reason",
    }
)

KIND_MAP = {
    "user_event": "observation_ingest",
    "observation": "observation_ingest",
    "belief": "belief_update",
    "drive": "motive_formation",
    "goal": "intention_genesis",
    "abstain": "intention_genesis",
    "initiative": "intention_genesis",
    "contact": "contact_governor",
}


def _load_trace(path: Path) -> dict:
    nodes: list[dict] = []
    edges: list[dict] = []
    header: dict = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("type") == "header":
                header = rec
            elif rec.get("type") == "node":
                nodes.append(rec)
            elif rec.get("type") == "edge":
                edges.append(rec)
    return {"header": header, "nodes": nodes, "edges": edges}


def _normalize_kind(node: dict, source: str) -> str:
    if source == "main":
        return node.get("kind", "unknown")
    raw = node.get("kind", "unknown")
    return KIND_MAP.get(raw, raw)


def _kind_counts(nodes: list[dict], source: str) -> Counter:
    return Counter(_normalize_kind(n, source) for n in nodes)


def _skip() -> int:
    print("ci_trace_diff_check: skipped (EIA_CI_TRACE_DIFF!=1)")
    return 0


def main() -> int:
    if os.environ.get("EIA_CI_TRACE_DIFF", "1") != "1":
        return _skip()

    starter_trace = ROOT / "research" / "starter_trace_twin_world_001.jsonl"
    if not starter_trace.exists():
        print(f"ci_trace_diff_check: starter trace missing: {starter_trace}")
        return 1

    sys.path.insert(0, str(ROOT / "src"))
    from eia.experiment.baseline import BaselineCondition
    from eia.pipeline import run_scenario

    scenario = ROOT / "scenarios" / "twin_world_001.yaml"
    run = run_scenario(
        scenario,
        traces_dir=ROOT / "traces" / "ci_structural_diff",
        seed=101,
        baseline=BaselineCondition.FULL_EIA,
    )
    starter = _load_trace(starter_trace)
    main = _load_trace(run["trace_path"])

    starter_nodes = len(starter["nodes"])
    main_nodes = len(main["nodes"])
    starter_kinds = _kind_counts(starter["nodes"], "starter")
    main_kinds = _kind_counts(main["nodes"], "main")

    main_only = {k for k in main_kinds if k not in starter_kinds}
    errors: list[str] = []

    if starter_nodes != EXPECTED_STARTER_NODES:
        errors.append(
            f"starter nodes {starter_nodes} != expected {EXPECTED_STARTER_NODES}"
        )
    if main_nodes != EXPECTED_MAIN_NODES:
        errors.append(f"main nodes {main_nodes} != expected {EXPECTED_MAIN_NODES}")
    missing = EXPECTED_MAIN_ONLY_KINDS - main_only
    if missing:
        errors.append(f"main-only kinds missing: {sorted(missing)}")
    if main_only - EXPECTED_MAIN_ONLY_KINDS:
        extra = sorted(main_only - EXPECTED_MAIN_ONLY_KINDS)
        errors.append(f"unexpected main-only kinds: {extra}")

    payload = {
        "starter_nodes": starter_nodes,
        "main_nodes": main_nodes,
        "main_only_kinds": sorted(main_only),
        "passed": not errors,
        "errors": errors,
    }
    print(json.dumps(payload, indent=2))

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    print("ci_trace_diff_check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
