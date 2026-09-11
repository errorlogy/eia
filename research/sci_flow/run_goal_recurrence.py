#!/usr/bin/env python3
"""M-R / ATT-R batch: closed goal-formation recurrence (not Kuramoto R; not AGI*/C3)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2"
sys.path.insert(0, str(ROOT / "src"))

from eia.amat_m0 import M0TwinMode  # noqa: E402
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator  # noqa: E402
from eia.goal_recurrence import (  # noqa: E402
    KURAMOTO_HIGH_FLOOR,
    MIN_CLOSED_CYCLES,
    run_att_r_batch,
    run_falsifier_suite,
)


def main() -> int:
    n_seeds = 20
    batch = run_att_r_batch(n_seeds=n_seeds)
    suite = run_falsifier_suite(seed=0)

    # Preserve M0 / M-E / M-P invariants: short WoE smoke still emit_m0=false.
    sim = EndogenousEmergenceSimulator()
    cfg = EmergenceConfig(duration_seconds=6.0)
    emit_m0_hits = 0
    genesis_ok = 0
    smoke_n = min(10, n_seeds)
    for seed in range(smoke_n):
        run = sim.run(cfg, seed=seed, m0_twin_mode=M0TwinMode.ON, enable_goal_genesis=True)
        if run.m0_sketch is not None and run.m0_sketch.emit_m0:
            emit_m0_hits += 1
        if run.goal_genesis is not None and run.goal_genesis.att_g_evidence:
            genesis_ok += 1

    by = batch["by_arm"]
    payload = {
        "n_seeds": n_seeds,
        "claim_ceiling": "architecture_att_r_explore",
        "agi_star_claim": False,
        "c2_claim": False,
        "c3_claim": False,
        "att": "ATT-R",
        "milestone": "M-R",
        "pre_registered": {
            "min_closed_cycles": MIN_CLOSED_CYCLES,
            "kuramoto_is_not_att_r": True,
            "kuramoto_high_floor_falsifier_only": KURAMOTO_HIGH_FLOOR,
            "emit_m0": False,
        },
        "pre_registered_falsifiers": {
            "open_loop_respond_once_is_not_recurrence": True,
            "no_world_update_breaks_loop": True,
            "no_novel_motive_after_action_fails": True,
            "external_schedule_prompt_spam_is_not_recurrence": True,
            "kuramoto_sync_alone_is_not_att_r": True,
        },
        "batch": batch,
        "falsifier_suite": {
            name: {
                "arm": ep.arm.value,
                "closed_cycle_count": ep.closed_cycle_count,
                "att_r_evidence": ep.att_r_evidence,
                "has_world_update": ep.has_world_update,
                "has_novel_motive_after_action": ep.has_novel_motive_after_action,
                "open_loop_only": ep.open_loop_only,
                "external_schedule_driven": ep.external_schedule_driven,
                "kuramoto_r": ep.kuramoto_r,
                "kuramoto_alone": ep.kuramoto_alone,
                "emit_m0": ep.emit_m0,
            }
            for name, ep in suite.items()
        },
        "snapshot": {
            "closed_loop_att_r_evidence_rate": by["closed_loop"]["att_r_evidence_rate"],
            "open_loop_att_r_evidence_rate": by["open_loop_once"]["att_r_evidence_rate"],
            "no_world_update_att_r_evidence_rate": by["no_world_update"]["att_r_evidence_rate"],
            "no_novel_motive_att_r_evidence_rate": by["no_novel_motive"]["att_r_evidence_rate"],
            "external_schedule_att_r_evidence_rate": by["external_schedule"][
                "att_r_evidence_rate"
            ],
            "kuramoto_only_att_r_evidence_rate": by["kuramoto_only"]["att_r_evidence_rate"],
            "kuramoto_alone_rate": by["kuramoto_only"]["kuramoto_alone_rate"],
            "emit_m0_rate": by["closed_loop"]["emit_m0_rate"],
        },
        "m_e_m0_invariants": {
            "emit_m0_rate_with_genesis": emit_m0_hits / max(1, smoke_n),
            "att_g_smoke_rate": genesis_ok / max(1, smoke_n),
        },
        "explore_proxy_note": (
            "Suggested ATT-R explore: >=1 closed W→M→G→Π→A→X'→W'→G' cycle with "
            "world_update parent of later novel motive; emit_m0=false; Kuramoto R "
            "alone never counts — not C-ladder gate."
        ),
    }
    out = Path(__file__).resolve().parent / "goal_recurrence_results.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
