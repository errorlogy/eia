#!/usr/bin/env python3
"""E04/D05: 50-tick longitudinal DSR harness on shadow carryover session.

Measures Drive Sustainability (DSR) via M-SE Tier B ``B_D`` proxy on the main
``run_shadow_carryover_tick`` path. No user prompts. ``emit_m0=false``.
Not C3 / not AGI*.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

from eia.runtime.shadow_multitick import (  # noqa: E402
    D05_DRIVE_NORM_FLOOR,
    DSR_TARGET_COGNITIVE_TICKS,
    run_dsr_longitudinal_session,
)


def main() -> int:
    result = run_dsr_longitudinal_session(
        target_cognitive_ticks=DSR_TARGET_COGNITIVE_TICKS,
        seed=0,
    )

    payload = {
        **result,
        "claim_ceiling": "architecture_m_se_dsr_explore",
        "pre_registered": {
            "target_cognitive_ticks": DSR_TARGET_COGNITIVE_TICKS,
            "d05_drive_norm_floor": D05_DRIVE_NORM_FLOOR,
            "no_user_prompt": True,
            "emit_m0": False,
            "governor_thresholds_lowered": False,
            "shadow_first": True,
        },
        "explore_proxy_note": (
            "E04 longitudinal 50-tick session on Phase 2 shadow carryover; "
            "DSR = sustained ||d_t|| above D05 floor with bounded B_D envelope; "
            "not C-ladder gate; live daemon loop reset gap remains."
        ),
    }

    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / "dsr_carryover_results.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "drive_samples"}, indent=2))
    print(f"wrote {json_path}")
    return 0 if result["d05_pass"] and result["e04_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
