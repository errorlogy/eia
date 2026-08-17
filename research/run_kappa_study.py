#!/usr/bin/env python3
"""SourceMass vs AuthenticReason κ study on twin_world eval set."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "research" / "source-mass-kappa-report.md"
REPORT_JSON = ROOT / "research" / "source-mass-kappa-report.json"


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
    from eia.audit.source_mass_mapping import (
        SourceMassPartition,
        classify_source_mass,
        compare_verdict_to_topology,
        expected_initiative_class,
        kappa_bin_agreement,
        partition_from_topology,
    )
    from eia.audit.topology import SourceMass, TopologyMetrics
    from eia.pipeline import run_scenario

    per_scenario: list[dict] = []
    verdict_classes: list[str] = []
    partitions: list[SourceMassPartition] = []

    for scenario_path in _scenario_paths():
        seed = 100 + int(scenario_path.stem.split("_")[-1])
        run = run_scenario(
            scenario_path,
            traces_dir=ROOT / "traces" / "kappa_study",
            seed=seed,
        )
        auth = run["authentic_verdict"]
        topo = auth.topology or {}

        sm = SourceMass(
            internal=topo.get("internal", 0.0),
            ambient=topo.get("ambient", 0.0),
            user_request=topo.get("user_request", 0.0),
        )
        metrics = TopologyMetrics(
            source_mass=sm,
            internal_transition_density=topo.get("internal_transition_density", 0.0),
            depth=int(topo.get("depth", 0)),
            branching_factor=topo.get("branching_factor", 0.0),
            target_node_id="initiative",
        )
        partition = classify_source_mass(sm)
        expected_class = expected_initiative_class(partition)
        comparison = compare_verdict_to_topology(auth, metrics)

        verdict_classes.append(auth.initiative_class)
        partitions.append(partition)

        per_scenario.append(
            {
                "scenario_id": scenario_path.stem,
                "scenario_path": str(scenario_path.relative_to(ROOT)),
                "seed": seed,
                "initiative_class": auth.initiative_class,
                "source_mass_partition": partition.value,
                "expected_class_from_partition": expected_class,
                "class_agreement": comparison["class_agreement"],
                "ri_agreement": comparison["ri_agreement"],
                "code_overlap": comparison["code_overlap"],
                "source_mass": {
                    "internal": sm.internal,
                    "ambient": sm.ambient,
                    "user_request": sm.user_request,
                    "request_independence": sm.request_independence,
                },
                "eoi": round(run["twin_result"].eoi, 4),
                "authentic": auth.is_authentic,
                "trace_id": run["loop"].trace.trace_id,
            }
        )

    kappa = kappa_bin_agreement(verdict_classes, partitions)
    observed = sum(
        1 for row in per_scenario if row["class_agreement"]
    ) / len(per_scenario) if per_scenario else 0.0

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_count": len(per_scenario),
        "kappa_bin_agreement": round(kappa, 4) if kappa is not None else None,
        "observed_class_agreement_rate": round(observed, 4),
        "verdict_class_distribution": {
            c: verdict_classes.count(c) for c in sorted(set(verdict_classes))
        },
        "partition_distribution": {
            p.value: partitions.count(p) for p in sorted(set(partitions), key=lambda x: x.value)
        },
        "per_scenario": per_scenario,
    }

    REPORT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# SourceMass vs AuthenticReason κ Study",
        "",
        f"**Date:** {payload['timestamp'][:10]}  ",
        "**Author:** Roman Kuznetsov  ",
        f"**Scenarios:** {payload['scenario_count']} (twin_world_001–006 as available)",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Cohen's κ (verdict class vs partition class) | **{payload['kappa_bin_agreement']}** |",
        f"| Observed class agreement rate | {payload['observed_class_agreement_rate']:.0%} |",
        "",
        "## Interpretation",
        "",
        "AuthenticReason `initiative_class` blends EOI, drive structure, and governor "
        "checks. SourceMass partition uses only ancestor mass bins (internal / ambient / "
        "user_request). Disagreement on user-heavy traces (RI≈0 but EOI=1) is expected: "
        "counterfactual replay proves endogeneity while static topology still shows "
        "user-request roots in the intervention window.",
        "",
        "## Per-scenario results",
        "",
        "| Scenario | Verdict class | Partition | Expected | Agree | RI agree | EOI |",
        "|----------|---------------|-----------|----------|-------|----------|-----|",
    ]
    for row in per_scenario:
        lines.append(
            f"| {row['scenario_id']} | {row['initiative_class']} | "
            f"{row['source_mass_partition']} | {row['expected_class_from_partition']} | "
            f"{'✓' if row['class_agreement'] else '✗'} | "
            f"{'✓' if row['ri_agreement'] else '✗'} | {row['eoi']} |"
        )

    lines.extend(
        [
            "",
            "## Distribution",
            "",
            f"- Verdict classes: `{payload['verdict_class_distribution']}`",
            f"- Partitions: `{payload['partition_distribution']}`",
            "",
            "See also: `src/eia/audit/source_mass_mapping.py`, MATHEMATICS.md §8.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
