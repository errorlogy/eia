#!/usr/bin/env python3
"""Thin shadow ATT-R closed-loop runner — rates JSON only (emit_m0=false).

Wraps main `shadow_multitick` + research `live_att_r` scoring.
Not C3 / not AGI*. No Telegram. No governor threshold gutting.
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
    from eia.runtime.shadow_multitick import (  # noqa: WPS433
        run_shadow_batch,
        run_shadow_falsifier_suite,
    )

    _load_woe_submodule("math_model")
    _load_woe_submodule("goal_recurrence")
    live_att_r = _load_woe_submodule("live_att_r")

    n_seeds = 20
    raw = run_shadow_batch(n_seeds=n_seeds)
    batch = live_att_r.run_live_att_r_batch_from_raw(raw["by_arm_raw"], n_seeds=n_seeds)
    suite_raw = {
        name: ep.as_dict() for name, ep in run_shadow_falsifier_suite(seed=0).items()
    }
    scored = live_att_r.score_shadow_suite(suite_raw)
    by = batch["by_arm"]

    snapshot = {
        "closed_loop_att_r_evidence_rate": by["closed_loop"]["att_r_evidence_rate"],
        "open_loop_att_r_evidence_rate": by["open_loop_once"]["att_r_evidence_rate"],
        "no_world_update_att_r_evidence_rate": by["no_world_update"]["att_r_evidence_rate"],
        "no_novel_motive_att_r_evidence_rate": by["no_novel_motive"]["att_r_evidence_rate"],
        "external_schedule_att_r_evidence_rate": by["external_schedule"]["att_r_evidence_rate"],
        "kuramoto_only_att_r_evidence_rate": by["kuramoto_only"]["att_r_evidence_rate"],
        "kuramoto_alone_rate": by["kuramoto_only"]["kuramoto_alone_rate"],
        "emit_m0_rate": by["closed_loop"]["emit_m0_rate"],
    }

    payload = {
        "n_seeds": n_seeds,
        "claim_ceiling": "architecture_att_r_live_shadow_explore",
        "agi_star_claim": False,
        "c3_claim": False,
        "att": "ATT-R",
        "milestone": "M-R-LIVE",
        "mode": "shadow_multitick",
        "live_telegram": False,
        "snapshot": snapshot,
        "falsifier_suite_evidence": {
            name: bool(ep.att_r_evidence) for name, ep in scored.items()
        },
        "gap_vs_live_daemon": raw["gap_vs_live_daemon"],
    }

    out = Path(__file__).resolve().parent / "shadow_att_r_results.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(snapshot, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
