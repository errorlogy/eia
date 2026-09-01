#!/usr/bin/env python3
"""M-R-LIVE: shadow multi-tick closed-loop under ATT-R falsifiers (emit_m0=false).

Uses main `eia.runtime.shadow_multitick` (CognitiveLoop path) + research
`live_att_r` / `goal_recurrence` scoring. No Telegram live SEND. No governor
threshold gutting. Not C3 / not AGI*.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]

if str(REPO / 'src') not in sys.path:
    sys.path.insert(0, str(REPO / 'src'))
WOE_SRC = REPO / "research" / "cursor-starter-v0.2" / "src"
WOE_PKG = WOE_SRC / "eia"


def _load_woe_submodule(name: str) -> Any:
    """Load research eia.* without clobbering installed main `eia` package."""
    pkg_name = "woe_eia"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(WOE_PKG)]  # type: ignore[attr-defined]
        sys.modules[pkg_name] = pkg

    full = f"{pkg_name}.{name}"
    if full in sys.modules:
        return sys.modules[full]

    path = WOE_PKG / f"{name}.py"
    spec = importlib.util.spec_from_file_location(full, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = pkg_name
    sys.modules[full] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    # Main runtime (editable install) — shadow multi-tick CognitiveLoop path
    from eia.runtime.shadow_multitick import (  # noqa: WPS433
        ShadowArm,
        run_shadow_batch,
        run_shadow_carryover_tick,
        run_shadow_episode,
        run_shadow_falsifier_suite,
    )

    # Research ATT-R scoring (isolated package name)
    _load_woe_submodule("math_model")
    _load_woe_submodule("goal_recurrence")
    live_att_r = _load_woe_submodule("live_att_r")
    emergence_mod = _load_woe_submodule("emergence")
    amat_m0 = _load_woe_submodule("amat_m0")

    n_seeds = 20
    raw = run_shadow_batch(n_seeds=n_seeds)
    batch = live_att_r.run_live_att_r_batch_from_raw(
        raw["by_arm_raw"], n_seeds=n_seeds
    )

    suite_raw = {
        name: ep.as_dict() for name, ep in run_shadow_falsifier_suite(seed=0).items()
    }
    scored = live_att_r.score_shadow_suite(suite_raw)

    carryover_ep = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=0)
    carryover_smoke: dict[str, Any] | None = None
    if carryover_ep.carryover is not None:
        carryover_tick = run_shadow_carryover_tick(carryover_ep.carryover, seed=0)
        carryover_smoke = {
            "used_carryover": carryover_tick.used_carryover,
            "g_prime_from_carryover": any(
                e.kind == "G_prime" and e.novel for e in carryover_tick.events
            ),
            "no_user_prompt": not any(
                "user" in e.label.lower() or e.kind == "X" and "prompt" in e.label.lower()
                for e in carryover_tick.events
            ),
            "ticks_run": carryover_tick.ticks_run,
            "session_tick_after": (
                carryover_tick.carryover.session_tick if carryover_tick.carryover else None
            ),
            "emit_m0": False,
            "claim_allowed": False,
        }

    # Preserve M0 / M-E invariants on research simulator
    sim = emergence_mod.EndogenousEmergenceSimulator()
    cfg = emergence_mod.EmergenceConfig(duration_seconds=6.0)
    emit_m0_hits = 0
    genesis_ok = 0
    smoke_n = min(10, n_seeds)
    for seed in range(smoke_n):
        run = sim.run(
            cfg,
            seed=seed,
            m0_twin_mode=amat_m0.M0TwinMode.ON,
            enable_goal_genesis=True,
        )
        if run.m0_sketch is not None and run.m0_sketch.emit_m0:
            emit_m0_hits += 1
        if run.goal_genesis is not None and run.goal_genesis.att_g_evidence:
            genesis_ok += 1

    by = batch["by_arm"]
    payload = {
        "n_seeds": n_seeds,
        "claim_ceiling": "architecture_att_r_live_shadow_explore",
        "agi_star_claim": False,
        "c2_claim": False,
        "c3_claim": False,
        "att": "ATT-R",
        "milestone": "M-R-LIVE",
        "mode": "shadow_multitick",
        "live_telegram": False,
        "pre_registered": {
            "min_closed_cycles": batch["min_closed_cycles"],
            "kuramoto_is_not_att_r": True,
            "emit_m0": False,
            "governor_thresholds_lowered": False,
            "shadow_first": True,
        },
        "pre_registered_falsifiers": {
            "open_loop_respond_once_is_not_recurrence": True,
            "no_world_update_breaks_loop": True,
            "no_novel_motive_after_action_fails": True,
            "external_schedule_prompt_spam_is_not_recurrence": True,
            "kuramoto_sync_alone_is_not_att_r": True,
        },
        "gap_vs_live_daemon": raw["gap_vs_live_daemon"],
        "phase_2_carryover_smoke": carryover_smoke,
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
                "emit_m0": False,
            }
            for name, ep in scored.items()
        },
        "snapshot": {
            "closed_loop_att_r_evidence_rate": by["closed_loop"]["att_r_evidence_rate"],
            "open_loop_att_r_evidence_rate": by["open_loop_once"]["att_r_evidence_rate"],
            "no_world_update_att_r_evidence_rate": by["no_world_update"][
                "att_r_evidence_rate"
            ],
            "no_novel_motive_att_r_evidence_rate": by["no_novel_motive"][
                "att_r_evidence_rate"
            ],
            "external_schedule_att_r_evidence_rate": by["external_schedule"][
                "att_r_evidence_rate"
            ],
            "kuramoto_only_att_r_evidence_rate": by["kuramoto_only"][
                "att_r_evidence_rate"
            ],
            "kuramoto_alone_rate": by["kuramoto_only"]["kuramoto_alone_rate"],
            "emit_m0_rate": by["closed_loop"]["emit_m0_rate"],
        },
        "m_e_m0_invariants": {
            "emit_m0_rate_with_genesis": emit_m0_hits / max(1, smoke_n),
            "att_g_smoke_rate": genesis_ok / max(1, smoke_n),
        },
        "explore_proxy_note": (
            "Shadow multi-tick on main CognitiveLoop under ATT-R falsifiers; "
            ">=1 closed W→M→G→Π→A→X'→W'→G' with emit_m0=false; Kuramoto alone "
            "never counts; smoke threshold overrides are not evidence; "
            "not C-ladder gate. Phase 2 shadow carryover closes session gap; "
            "production daemon still per-tick loop reset until StateStore hydration."
        ),
    }
    out = Path(__file__).resolve().parent / "live_att_r_results.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
