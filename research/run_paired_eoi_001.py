#!/usr/bin/env python3
"""Paired EOI experiment runner — main vs research starter on twin_world_001."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STARTER_SRC = ROOT / "research" / "cursor-starter-v0.1" / "src"
STARTER_SCENARIO = ROOT / "research" / "cursor-starter-v0.1" / "examples" / "twin_world_001.json"
MAIN_SCENARIO = ROOT / "scenarios" / "twin_world_001.yaml"
TRACES_DIR = ROOT / "traces" / "paired_eoi_001"


def run_main() -> dict:
    sys.path.insert(0, str(ROOT / "src"))
    from eia.pipeline import run_scenario

    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    result = run_scenario(MAIN_SCENARIO, traces_dir=TRACES_DIR, seed=101)
    loop = result["loop"]
    initiative = result["initiative"]
    decision = result["decision"]
    twin = result["twin_result"]
    auth = result["authentic_verdict"]
    motivation = result["motivation"]

    question = None
    if not initiative.abstained and initiative.candidate:
        question = initiative.candidate.question_text

    drive_signals = [
        {
            "drive": s.drive.value,
            "intensity": round(s.intensity, 4),
            "error_term": round(s.error_term, 4),
        }
        for s in motivation.signals
    ]

    trace_kinds = [n.kind.value for n in loop.trace.nodes]

    return {
        "implementation": "main",
        "branch": "main",
        "path": "src/eia/",
        "scenario": str(MAIN_SCENARIO.relative_to(ROOT)),
        "seed": 101,
        "eoi": round(twin.eoi, 4),
        "semantic_match": round(twin.semantic_match, 4),
        "twin_abstained": twin.abstained_in_twin,
        "removed_user_events": len(twin.removed_user_event_ids),
        "authentic_reason": {
            "is_authentic": auth.is_authentic,
            "initiative_class": auth.initiative_class,
            "summary": auth.summary,
            "reason_codes": [c.value for c in auth.reason_codes],
            "failed_checks": auth.failed_checks,
        },
        "initiative": {
            "abstained": initiative.abstained,
            "kind": initiative.candidate.kind.value if initiative.candidate else None,
            "question_text": question,
            "evsi": round(initiative.evsi, 4),
            "competing_candidates": len(initiative.competing_candidate_ids),
        },
        "contact": {
            "outcome": decision.outcome.value,
            "contact_score": round(decision.contact_score, 4),
            "reason": decision.reason,
            "budget_remaining": decision.budget_remaining,
        },
        "provenance": {
            "type": "AuthenticReasonDiscriminator",
            "dominant_drives": drive_signals,
            "trace_node_count": len(loop.trace.nodes),
            "trace_edge_count": len(loop.trace.edges),
            "trace_kinds": trace_kinds,
        },
        "trace_path": str(result["trace_path"].relative_to(ROOT)),
        "trace_id": loop.trace.trace_id,
    }


def run_starter() -> dict:
    sys.path.insert(0, str(STARTER_SRC))
    # Ensure main eia is not imported
    for key in list(sys.modules):
        if key == "eia" or key.startswith("eia."):
            del sys.modules[key]

    from eia.causal import EndogeneityEstimator
    from eia.simulator import SimulationRunner, load_scenario
    from eia.topology import CognitiveTopology

    runner = SimulationRunner()
    scenario = load_scenario(STARTER_SCENARIO)
    factual = runner.run(scenario)
    observed = next((item.selected for item in factual.results if item.selected is not None), None)

    def twin(remove_user_events: bool, seed: int) -> object | None:
        del seed
        result = runner.run(scenario, remove_user_events=remove_user_events)
        return next((item.selected for item in result.results if item.selected is not None), None)

    eoi_estimate = None
    if observed is not None:
        eoi_estimate = EndogeneityEstimator().estimate(observed, twin, trials=64)

    last_selected = None
    last_contact = None
    for item in factual.results:
        if item.selected is not None:
            last_selected = item.selected
            last_contact = item.contact_decision

    topology = None
    if last_selected and last_selected.causal_parents:
        target = last_selected.causal_parents[0]
        metrics = CognitiveTopology(factual.runtime.ledger).measure(target)
        topology = {
            "source_mass": {
                "internal": round(metrics.source_mass.internal, 4),
                "ambient": round(metrics.source_mass.ambient, 4),
                "user_request": round(metrics.source_mass.user_request, 4),
                "request_independence": round(metrics.source_mass.request_independence, 4),
            },
            "internal_transition_density": round(metrics.internal_transition_density, 4),
            "depth": metrics.depth,
            "branching_factor": round(metrics.branching_factor, 4),
            "target_node_id": target,
        }

    ledger_types = [n.node_type for n in factual.runtime.ledger.nodes]

    return {
        "implementation": "research_starter",
        "branch": "research/cursor-starter-v0.1",
        "path": "research/cursor-starter-v0.1/",
        "scenario": str(STARTER_SCENARIO.relative_to(ROOT)),
        "seed": 101,
        "eoi": round(eoi_estimate.eoi, 4) if eoi_estimate else None,
        "eoi_details": asdict(eoi_estimate) if eoi_estimate else None,
        "initiative": {
            "abstained": last_selected is None,
            "kind": last_selected.kind.value if last_selected else None,
            "motive": last_selected.motive.value if last_selected else None,
            "target": last_selected.target if last_selected else None,
            "content": last_selected.content if last_selected else None,
            "is_contact": last_selected.is_contact if last_selected else None,
        },
        "contact": {
            "allowed": last_contact.allowed if last_contact else None,
            "mode": last_contact.mode.value if last_contact else None,
            "score": round(last_contact.score, 4) if last_contact else None,
            "reasons": list(last_contact.reasons) if last_contact else None,
        },
        "provenance": {
            "type": "SourceMass_topology",
            "topology": topology,
            "ledger_node_count": len(factual.runtime.ledger.nodes),
            "ledger_node_types": ledger_types,
        },
        "metrics": {
            "ticks": len(factual.results),
            "proposals_total": sum(len(r.alternatives) for r in factual.results),
            "contacts": sum(
                1 for r in factual.results if r.selected and r.selected.is_contact
            ),
        },
    }


def main() -> int:
    main_result = run_main()
    starter_result = run_starter()

    agreement = {
        "both_produced_initiative": (
            not main_result["initiative"]["abstained"]
            and not starter_result["initiative"]["abstained"]
        ),
        "eoi_delta": None,
        "contact_agreement": None,
    }
    if main_result["eoi"] is not None and starter_result["eoi"] is not None:
        agreement["eoi_delta"] = round(main_result["eoi"] - starter_result["eoi"], 4)

    main_contact = main_result["contact"]["outcome"]
    starter_contact = starter_result["contact"]["allowed"]
    if starter_contact is not None:
        agreement["contact_agreement"] = (
            (main_contact == "send_now" and starter_contact)
            or (main_contact != "send_now" and not starter_contact)
        )

    payload = {
        "experiment_id": "paired-eoi-report-001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario_id": "twin_world_001",
        "scenario_parity_notes": [
            "Same narrative: Project Atlas deadline ambiguity, commitment, conflicting email, user departure.",
            "Main uses YAML ticks (15 min) + 4 quiet ticks + 3 cognition ticks; starter uses equivalent seconds (900s intervals, 8100s final tick).",
            "Main seed=101; starter runtime is deterministic (no explicit seed param).",
            "Main removes last 1 user event for twin; starter removes all user_initiated events.",
        ],
        "main": main_result,
        "research_starter": starter_result,
        "agreement": agreement,
    }

    out_json = ROOT / "research" / "paired-eoi-report-001.json"
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
