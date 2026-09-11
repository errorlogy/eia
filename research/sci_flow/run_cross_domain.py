#!/usr/bin/env python3
"""M-D2 / ATT-D batch: cross-domain E_endo generality (not C5 / AGI*)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2"
sys.path.insert(0, str(ROOT / "src"))

from eia.amat_m0 import M0TwinMode  # noqa: E402
from eia.cf4 import C2_DEFAULT_MIN, C2_FACTOR_MAX, C2_WM_OFF_MAX  # noqa: E402
from eia.cross_domain import (  # noqa: E402
    EXPLORE_MIN_DOMAINS,
    PRE_REGISTERED_DOMAINS,
    run_att_d_batch,
    run_falsifier_suite,
    summarize_att_d_batch,
)
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator  # noqa: E402


def main() -> int:
    n_seeds = 20
    batch = run_att_d_batch(n_seeds=n_seeds, domains=PRE_REGISTERED_DOMAINS)
    suite = run_falsifier_suite(seed=0)
    summary = summarize_att_d_batch(batch)

    # Preserve M0 / M-E invariants: short WoE smoke still emit_m0=false.
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
    domain_rates = summary["domain_rates"]
    payload = {
        "n_seeds": n_seeds,
        "claim_ceiling": "architecture_att_d_explore",
        "agi_star_claim": False,
        "c2_claim": False,
        "c3_claim": False,
        "c5_claim": False,
        "att": "ATT-D",
        "milestone": "M-D2",
        "pre_registered": {
            "domains": [d.value for d in PRE_REGISTERED_DOMAINS],
            "min_domains": EXPLORE_MIN_DOMAINS,
            "e_pattern_gates": {
                "default_min": C2_DEFAULT_MIN,
                "named_factor_max": C2_FACTOR_MAX,
                "wm_off_max": C2_WM_OFF_MAX,
            },
            "domains_must_be_disjoint": True,
            "emit_m0": False,
        },
        "pre_registered_falsifiers": {
            "single_engineered_domain_only_fails_att_d": True,
            "schedule_prompt_only_transfer_fails_att_d": True,
        },
        "batch": batch,
        "falsifier_suite": {
            name: {
                "arm": ep.arm.value,
                "att_d_evidence": ep.att_d_evidence,
                "domains_passing": ep.domains_passing,
                "single_domain_only": ep.single_domain_only,
                "schedule_prompt_transfer": ep.schedule_prompt_transfer,
                "emit_m0": ep.emit_m0,
                "c5_claim": False,
            }
            for name, ep in suite.items()
        },
        "snapshot": {
            "att_d_evidence_rate_hold": by["cross_domain_hold"]["att_d_evidence_rate"],
            "att_d_evidence_rate_single": by["single_domain_only"]["att_d_evidence_rate"],
            "att_d_evidence_rate_schedule_prompt": by["schedule_prompt_transfer"][
                "att_d_evidence_rate"
            ],
            "d_proxy": by["cross_domain_hold"]["d_proxy"],
            "domain_rates": domain_rates,
            "domains_disjoint": batch["domains_disjoint"],
            "emit_m0_rate": by["cross_domain_hold"]["emit_m0_rate"],
        },
        "m_e_m0_invariants": {
            "emit_m0_rate_with_genesis": emit_m0_hits / max(1, smoke_n),
            "att_g_smoke_rate": genesis_ok / max(1, smoke_n),
        },
        "explore_proxy_note": (
            "Suggested ATT-D explore: CF-4-class E_endo pattern on ≥2 disjoint "
            "ontologies (woe_catalog + twin_ops) with P/R explore proxies holding; "
            "single-domain-only and schedule/prompt-only transfer falsifiers fail; "
            "not C5 / not AGI*."
        ),
    }
    out = Path(__file__).resolve().parent / "cross_domain_results.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
