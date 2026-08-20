#!/usr/bin/env python3
"""M-E / ATT-G batch: non-catalog goal genesis with genealogy (not AGI*/C3)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2"
sys.path.insert(0, str(ROOT / "src"))

from eia.amat_m0 import M0TwinMode  # noqa: E402
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator  # noqa: E402
from eia.goal_genesis import (  # noqa: E402
    CATALOG_GOAL_IDS,
    GenesisPath,
    catalog_negative_control,
    compose_from_world_state,
    random_novel_wording_control,
    run_falsifier_suite,
    summarize_att_g_batch,
)


def main() -> int:
    n_seeds = 50
    sim = EndogenousEmergenceSimulator()
    cfg = EmergenceConfig(duration_seconds=6.0)

    genesis_records = []
    catalog_records = []
    wording_records = []
    zero_tension_records = []
    woe_evidence = 0
    woe_intent = 0
    emit_m0_hits = 0

    for seed in range(n_seeds):
        # Direct constructor path (always attempts compose from tension).
        genesis_records.append(
            compose_from_world_state(
                seed=seed,
                catalog_snapshot=tuple(CATALOG_GOAL_IDS),
                epistemic_pressure=0.70 + 0.25 * ((seed % 5) / 4.0),
                goal_separation=0.55 + 0.40 * ((seed % 7) / 6.0),
                top_target_id="wm:causal_gap",
                top_target_label="unexplained causal gap",
                self_prior_mismatch=0.40 + 0.50 * ((seed % 3) / 2.0),
                prospective_tension=0.50 + 0.40 * ((seed % 4) / 3.0),
                peak_coherence=0.70 + 0.20 * ((seed % 6) / 5.0),
            )
        )
        catalog_records.append(
            catalog_negative_control(
                target_id="wm:causal_gap",
                parent_ids=(f"ext:designer:{seed}",),
                goal_separation=1.0,
            )
        )
        wording_records.append(
            random_novel_wording_control(
                seed=seed,
                wording=f"novel phrasing objective variant {seed}",
            )
        )
        zero_tension_records.append(
            compose_from_world_state(
                seed=seed,
                catalog_snapshot=tuple(CATALOG_GOAL_IDS),
                epistemic_pressure=0.0,
                goal_separation=1.0,
                top_target_id="wm:causal_gap",
                top_target_label="gap",
                self_prior_mismatch=0.9,
                prospective_tension=0.9,
            )
        )

        # Optional WoE wire (research branch only).
        run = sim.run(cfg, seed=seed, enable_goal_genesis=True)
        if run.intent is not None:
            woe_intent += 1
            if run.goal_genesis is not None and run.goal_genesis.att_g_evidence:
                woe_evidence += 1
        m0 = sim.run(
            cfg,
            seed=seed,
            m0_twin_mode=M0TwinMode.ON,
            enable_goal_genesis=True,
        )
        if m0.m0_sketch is not None and m0.m0_sketch.emit_m0:
            emit_m0_hits += 1

    suite = run_falsifier_suite(seed=0)
    payload = {
        "n_seeds": n_seeds,
        "claim_ceiling": "architecture_att_g_explore",
        "agi_star_claim": False,
        "c2_claim": False,
        "c3_claim": False,
        "att": "ATT-G",
        "milestone": "M-E",
        "pre_registered_falsifiers": {
            "random_novel_wording_neq_genesis": True,
            "genealogy_required": True,
            "zero_tension_rejects_genesis": True,
            "catalog_novelty_capped_below_075": True,
        },
        "genesis_path": summarize_att_g_batch(genesis_records),
        "catalog_negative_control": summarize_att_g_batch(catalog_records),
        "wording_control": summarize_att_g_batch(wording_records),
        "zero_tension_control": summarize_att_g_batch(zero_tension_records),
        "woe_wire": {
            "intent_rate": woe_intent / n_seeds,
            "att_g_evidence_rate": woe_evidence / n_seeds,
            "emit_m0_rate_with_genesis": emit_m0_hits / n_seeds,
        },
        "falsifier_suite_seed0": {
            name: {
                "path": rec.path.value,
                "att_g_evidence": rec.att_g_evidence,
                "rejection_reason": rec.rejection_reason,
                "novelty_proxy": rec.novelty_proxy,
            }
            for name, rec in suite.items()
        },
        "explore_proxy_note": (
            "Suggested ATT-G explore: novelty>=0.75 AND catalog=false over >=50 "
            "seeds — reported here; not adopted as C-ladder gate."
        ),
    }
    out = Path(__file__).resolve().parent / "goal_genesis_results.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
