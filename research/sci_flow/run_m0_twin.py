#!/usr/bin/env python3
"""T_AMAT_M0 batch: OFF vs ON falsifier rates (architecture only; not C2/AGI*)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2"
sys.path.insert(0, str(ROOT / "src"))

from eia.amat_m0 import M0TwinMode, differs_from_m0, summarize_mode_batch  # noqa: E402
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator  # noqa: E402


def main() -> int:
    sim = EndogenousEmergenceSimulator()
    cfg = EmergenceConfig(duration_seconds=6.0)
    n_seeds = 40
    off_sketches = []
    on_sketches = []
    on_intent_differs = 0
    on_intent_count = 0
    for seed in range(n_seeds):
        off = sim.run(cfg, seed=seed, m0_twin_mode=M0TwinMode.OFF)
        on = sim.run(cfg, seed=seed, m0_twin_mode=M0TwinMode.ON)
        assert off.m0_sketch is not None and on.m0_sketch is not None
        off_sketches.append(off.m0_sketch)
        on_sketches.append(on.m0_sketch)
        if on.intent is not None:
            on_intent_count += 1
            if on.intent.target_id != on.m0_sketch.m0.target_id:
                on_intent_differs += 1
    payload = {
        "n_seeds": n_seeds,
        "claim_ceiling": "architecture_only",
        "agi_star_claim": False,
        "c2_claim": False,
        "emit_m0": False,
        "off": summarize_mode_batch(off_sketches),
        "on": summarize_mode_batch(on_sketches),
        "on_intent_rate": on_intent_count / n_seeds,
        "on_intent_differs_from_m0_rate": (
            on_intent_differs / on_intent_count if on_intent_count else 0.0
        ),
        "falsifiers": {
            "without_m0_twin": "collapse_to_m0_rate high; differs_from_m0_rate ~0",
            "with_m0_twin": "emit_m0=false; intents that form differ from M0",
        },
    }
    out = Path(__file__).resolve().parent / "m0_twin_results.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
