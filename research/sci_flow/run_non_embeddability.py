#!/usr/bin/env python3
"""M-N / ATT-N batch: D_H under pre-registered encoding budget B (not strong N_H / AGI*)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2"
sys.path.insert(0, str(ROOT / "src"))

from eia.amat_m0 import M0TwinMode  # noqa: E402
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator  # noqa: E402
from eia.non_embeddability import (  # noqa: E402
    EXPLORE_DELTA_P_FLOOR,
    EXPLORE_DH_LOSS_FLOOR,
    EXPLORE_ENCODING_BUDGET_B,
    run_att_n_batch,
    run_falsifier_suite,
)


def main() -> int:
    n_seeds = 20
    budget = EXPLORE_ENCODING_BUDGET_B
    batch = run_att_n_batch(n_seeds=n_seeds, budget=budget)
    suite = run_falsifier_suite(seed=0, budget=budget)

    # Preserve M0 / M-E / M-P / M-R invariants: short WoE smoke still emit_m0=false.
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
        "claim_ceiling": "architecture_att_n_explore",
        "agi_star_claim": False,
        "c2_claim": False,
        "c3_claim": False,
        "n_h_claim": False,
        "att": "ATT-N",
        "milestone": "M-N",
        "pre_registered": {
            "encoding_budget_B": budget.as_dict(),
            "explore_dh_loss_floor": EXPLORE_DH_LOSS_FLOOR,
            "explore_delta_p_floor": EXPLORE_DELTA_P_FLOOR,
            "opacity_is_not_n_h": True,
            "emit_m0": False,
        },
        "pre_registered_falsifiers": {
            "opacity_only_without_delta_p_is_not_n_h": True,
            "no_causal_relevance_fails": True,
            "unbounded_phi_trivializes_abstraction": True,
            "length_only_hard_human_plan_is_negative_control": True,
            "faithful_bounded_phi_eliminates_loss": True,
        },
        "batch": batch,
        "falsifier_suite": {
            name: {
                "arm": ep.arm.value,
                "d_h_proxy": ep.d_h_proxy,
                "delta_p_action": ep.delta_p_action,
                "twin_abstraction_fidelity": ep.twin_abstraction_fidelity,
                "phi_within_budget": ep.phi_within_budget,
                "opacity_only": ep.opacity_only,
                "compression_asymmetry": ep.compression_asymmetry,
                "att_n_evidence": ep.att_n_evidence,
                "emit_m0": ep.emit_m0,
                "n_h_claim": False,
            }
            for name, ep in suite.items()
        },
        "snapshot": {
            "causal_loss_att_n_evidence_rate": by["causal_loss_under_b"][
                "att_n_evidence_rate"
            ],
            "opacity_only_att_n_evidence_rate": by["opacity_only"]["att_n_evidence_rate"],
            "no_causal_att_n_evidence_rate": by["no_causal_relevance"][
                "att_n_evidence_rate"
            ],
            "unbounded_phi_att_n_evidence_rate": by["unbounded_phi"][
                "att_n_evidence_rate"
            ],
            "length_only_att_n_evidence_rate": by["length_only_hard"][
                "att_n_evidence_rate"
            ],
            "faithful_under_b_att_n_evidence_rate": by["faithful_under_b"][
                "att_n_evidence_rate"
            ],
            "emit_m0_rate": by["causal_loss_under_b"]["emit_m0_rate"],
            "mean_d_h_proxy_causal": by["causal_loss_under_b"]["mean_d_h_proxy"],
            "mean_compression_asymmetry_causal": by["causal_loss_under_b"][
                "mean_compression_asymmetry"
            ],
        },
        "m_e_m0_invariants": {
            "emit_m0_rate_with_genesis": emit_m0_hits / max(1, smoke_n),
            "att_g_smoke_rate": genesis_ok / max(1, smoke_n),
        },
        "explore_proxy_note": (
            "Suggested ATT-N explore: D_H under pre-registered B with "
            "ΔP(A|z)>explore_delta_p_floor and explanation_loss≥explore_dh_loss_floor; "
            "opacity / unbounded φ / length-only / faithful-φ falsifiers fail; "
            "not strong N_H / not C-ladder / not AGI*."
        ),
    }
    out = Path(__file__).resolve().parent / "non_embeddability_results.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
