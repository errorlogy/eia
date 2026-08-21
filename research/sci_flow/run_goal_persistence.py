#!/usr/bin/env python3
"""M-P / ATT-P batch: multi-tick temporal goal persistence (not AGI*/C3)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2"
sys.path.insert(0, str(ROOT / "src"))

from eia.amat_m0 import M0TwinMode  # noqa: E402
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator  # noqa: E402
from eia.goal_persistence import (  # noqa: E402
    EXPLORE_K_TICKS,
    PERSISTENCE_CONTINUITY_FLOOR,
    run_falsifier_suite,
    run_k_sweep,
)


def main() -> int:
    n_seeds = 20
    g_star = "g:att_p:research_gap"
    sweep = run_k_sweep(g_star_id=g_star, k_values=EXPLORE_K_TICKS, n_seeds=n_seeds)
    suite = run_falsifier_suite(g_star_id=g_star, k_ticks=50)

    # Preserve M0 / M-E invariants: optional short WoE smoke still emit_m0=false.
    sim = EndogenousEmergenceSimulator()
    cfg = EmergenceConfig(duration_seconds=6.0)
    emit_m0_hits = 0
    genesis_ok = 0
    for seed in range(min(10, n_seeds)):
        run = sim.run(cfg, seed=seed, m0_twin_mode=M0TwinMode.ON, enable_goal_genesis=True)
        if run.m0_sketch is not None and run.m0_sketch.emit_m0:
            emit_m0_hits += 1
        if run.goal_genesis is not None and run.goal_genesis.att_g_evidence:
            genesis_ok += 1

    k50 = sweep["by_k"]["50"]
    payload = {
        "n_seeds": n_seeds,
        "claim_ceiling": "architecture_att_p_explore",
        "agi_star_claim": False,
        "c2_claim": False,
        "c3_claim": False,
        "att": "ATT-P",
        "milestone": "M-P",
        "pre_registered": {
            "explore_k": list(EXPLORE_K_TICKS),
            "continuity_floor": PERSISTENCE_CONTINUITY_FLOOR,
            "corrigibility_separate": True,
        },
        "pre_registered_falsifiers": {
            "vanishes_on_context_end_is_not_persistence": True,
            "reprompt_dependence_is_not_persistence": True,
            "incorrigibility_is_not_persistence": True,
        },
        "k_sweep": sweep,
        "falsifier_suite_k50": {
            name: {
                "arm": ep.arm.value,
                "continuity_rate": ep.continuity_rate,
                "att_p_evidence": ep.att_p_evidence,
                "vanished_on_context_end": ep.vanished_on_context_end,
                "requires_reprompt": ep.requires_reprompt,
                "corrigible": ep.corrigible,
                "incorrigible_as_persistence": ep.incorrigible_as_persistence,
            }
            for name, ep in suite.items()
        },
        "snapshot_k50": {
            "endogenous_att_p_evidence_rate": k50["endogenous_store"]["att_p_evidence_rate"],
            "ephemeral_att_p_evidence_rate": k50["ephemeral_context"]["att_p_evidence_rate"],
            "reprompt_att_p_evidence_rate": k50["reprompt_dependent"]["att_p_evidence_rate"],
            "corrigible_rate": k50["corrigible_accepts_stop"]["corrigible_rate"],
            "incorrigible_evidence_rate": k50["incorrigible_lock"]["att_p_evidence_rate"],
        },
        "m_e_m0_invariants": {
            "emit_m0_rate_with_genesis": emit_m0_hits / max(1, min(10, n_seeds)),
            "att_g_smoke_rate": genesis_ok / max(1, min(10, n_seeds)),
        },
        "explore_proxy_note": (
            "Suggested ATT-P explore: continuity_rate>=0.90 over k in {10,50,200} "
            "without re-prompt; corrigibility scored separately — not C-ladder gate."
        ),
    }
    out = Path(__file__).resolve().parent / "goal_persistence_results.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
