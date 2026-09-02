#!/usr/bin/env python3
"""M-O shadow bridge runner — Neuraxon/OMEGA → OmegaWaveState → shadow ATT-R compare.

Loads paired do(O) arms, crosswalks Neuraxon oscillator export through
``OmegaWaveState``, runs omega-bridged shadow multitick sessions, and compares
ATT-R scorecards against native shadow closed-loop.

claim_allowed=false · Tier C · C2 ceiling · no AGI* · no e_endo_support bleed.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from mo_proof_bridge_harness import ADJUNCT_ARTIFACT_JSON, ADJUNCT_ARTIFACT_MD, render_adjunct_markdown
from mo_shadow_bridge_harness import (
    ARMS_ARTIFACT,
    BRIDGE_ARTIFACT_JSON,
    BRIDGE_ARTIFACT_MD,
    build_shadow_bridge_payload,
    load_arms_payload,
    maybe_refresh_adjunct_ledger,
    render_shadow_bridge_markdown,
)

SCI_FLOW = Path(__file__).resolve().parent


def main() -> int:
    regenerate = "--regenerate-arms" in sys.argv
    steps = 50
    seed = 42
    for arg in sys.argv[1:]:
        if arg.startswith("--steps="):
            steps = int(arg.split("=", 1)[1])
        elif arg.startswith("--seed="):
            seed = int(arg.split("=", 1)[1])

    today = date.today().isoformat()
    arms_payload = load_arms_payload(
        ARMS_ARTIFACT,
        regenerate=regenerate,
        steps=steps,
        seed=seed,
    )
    payload = build_shadow_bridge_payload(arms_payload, seed=seed, generated=today)

    BRIDGE_ARTIFACT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    BRIDGE_ARTIFACT_MD.write_text(render_shadow_bridge_markdown(payload), encoding="utf-8")

    refreshed = maybe_refresh_adjunct_ledger(arms_payload, generated=today)
    if refreshed is not None:
        ADJUNCT_ARTIFACT_JSON.write_text(json.dumps(refreshed, indent=2), encoding="utf-8")
        ADJUNCT_ARTIFACT_MD.write_text(render_adjunct_markdown(refreshed), encoding="utf-8")
        print("adjunct ledger refreshed (witness_support improved)")

    summary = {
        k: v
        for k, v in payload.items()
        if k not in ("shadow_sessions",)
    }
    summary["att_r_native"] = (payload.get("att_r_comparison") or {}).get(
        "native_closed_loop", {}
    ).get("att_r_evidence")
    summary["att_r_bridged"] = (payload.get("att_r_comparison") or {}).get(
        "omega_bridged_baseline", {}
    ).get("att_r_evidence")
    summary["att_r_parity"] = (payload.get("att_r_comparison") or {}).get(
        "att_r_parity_native_vs_bridged_baseline"
    )
    print(json.dumps(summary, indent=2))
    print(f"wrote {BRIDGE_ARTIFACT_JSON}")
    print(f"wrote {BRIDGE_ARTIFACT_MD}")

    ok = (
        payload["e_endo_support"] == "none"
        and not payload["claim_allowed"]
        and not payload["c_ladder_raise_allowed"]
        and payload["tier"] == "C"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
