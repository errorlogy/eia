#!/usr/bin/env python3
"""Structural diff: main causal trace vs starter JSONL export."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STARTER_TRACE = ROOT / "research" / "starter_trace_twin_world_001.jsonl"
REPORT_MD = ROOT / "research" / "trace-structural-diff-report.md"
SCENARIO = ROOT / "scenarios" / "twin_world_001.yaml"

# Starter node kinds → main TraceNodeKind vocabulary (approximate mapping)
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


def _max_depth(nodes: list[dict], edges: list[dict]) -> int:
    if not nodes:
        return 0
    children: dict[str, list[str]] = {}
    for e in edges:
        src = e.get("source_id") or e.get("parent_id")
        tgt = e.get("target_id") or e.get("child_id")
        if src and tgt:
            children.setdefault(src, []).append(tgt)
    ids = {n.get("id") for n in nodes}
    roots = [n["id"] for n in nodes if n.get("id") in ids and not any(
        (e.get("target_id") or e.get("child_id")) == n.get("id") for e in edges
    )]

    def depth(node_id: str, seen: set[str]) -> int:
        if node_id in seen:
            return 0
        seen.add(node_id)
        kids = children.get(node_id, [])
        if not kids:
            return 1
        return 1 + max(depth(k, seen) for k in kids)

    return max((depth(r, set()) for r in roots), default=0)


def main() -> int:
    import sys

    sys.path.insert(0, str(ROOT / "src"))
    from eia.experiment.baseline import BaselineCondition
    from eia.pipeline import run_scenario

    run = run_scenario(
        SCENARIO,
        traces_dir=ROOT / "traces" / "structural_diff",
        seed=101,
        baseline=BaselineCondition.FULL_EIA,
    )
    main_path = run["trace_path"]
    starter = _load_trace(STARTER_TRACE)
    main = _load_trace(main_path)

    starter_kinds = _kind_counts(starter["nodes"], "starter")
    main_kinds = _kind_counts(main["nodes"], "main")
    all_kinds = sorted(set(starter_kinds) | set(main_kinds))

    comparison_rows = []
    for kind in all_kinds:
        s = starter_kinds.get(kind, 0)
        m = main_kinds.get(kind, 0)
        comparison_rows.append({"kind": kind, "starter": s, "main": m, "delta": m - s})

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario": "twin_world_001",
        "main_trace_id": run["loop"].trace.trace_id,
        "starter_trace_id": starter["header"].get("trace_id"),
        "main_path": str(main_path.relative_to(ROOT)),
        "starter_path": str(STARTER_TRACE.relative_to(ROOT)),
        "node_counts": {
            "starter": len(starter["nodes"]),
            "main": len(main["nodes"]),
        },
        "edge_counts": {
            "starter": len(starter["edges"]),
            "main": len(main["edges"]),
        },
        "max_depth": {
            "starter": _max_depth(starter["nodes"], starter["edges"]),
            "main": _max_depth(main["nodes"], main["edges"]),
        },
        "kind_comparison": comparison_rows,
        "main_only_kinds": [
            k for k in main_kinds if k not in starter_kinds
        ],
        "starter_only_kinds": [
            k for k in starter_kinds if k not in main_kinds
        ],
    }

    lines = [
        "# Structural Trace Diff — Main vs Starter",
        "",
        f"**Date:** {payload['timestamp'][:10]}  ",
        "**Author:** Roman Kuznetsov  ",
        "**Scenario:** twin_world_001 (seed 101)",
        "",
        "## Overview",
        "",
        f"| Dimension | Starter | Main |",
        f"|-----------|---------|------|",
        f"| Nodes | {payload['node_counts']['starter']} | {payload['node_counts']['main']} |",
        f"| Edges | {payload['edge_counts']['starter']} | {payload['edge_counts']['main']} |",
        f"| Max depth | {payload['max_depth']['starter']} | {payload['max_depth']['main']} |",
        "",
        "## Kind comparison (starter mapped → main vocabulary)",
        "",
        "| Kind | Starter | Main | Δ |",
        "|------|---------|------|---|",
    ]
    for row in comparison_rows:
        lines.append(
            f"| {row['kind']} | {row['starter']} | {row['main']} | {row['delta']:+d} |"
        )

    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Main adds pipeline stages not in starter export: "
            f"`{payload['main_only_kinds']}`",
            f"- Starter-only kinds (unmapped): `{payload['starter_only_kinds']}`",
            "- Main trace records twin_run, eoi_score, authentic_reason audit nodes; "
            "starter ledger stops at initiative/contact.",
            "- Edge model differs: starter emits explicit edge records per parent; "
            "main uses parent_kind chaining in CausalTrace.add_node.",
            "",
            f"Main trace: `{payload['main_path']}`  ",
            f"Starter trace: `{payload['starter_path']}`",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
