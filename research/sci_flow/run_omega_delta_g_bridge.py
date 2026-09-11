#!/usr/bin/env python3
"""OMEGA→ΔG bridge runner — probe OMEGA_t vs shadow genesis delta (X_trigger=0).

Loads paired do(O) arms, runs omega-bridged shadow multitick across four arms
(native, neuraxon-bridged, plasticity_off, phase_scramble), and records whether
OMEGA_t changes correlate with ΔG / initiative fingerprint change.

claim_allowed=false · Tier C · C2 ceiling · no AGI* · no e_endo_support bleed.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from mo_proof_bridge_harness import ADJUNCT_ARTIFACT_JSON, ADJUNCT_ARTIFACT_MD, render_adjunct_markdown
from omega_delta_g_harness import (
    ARMS_ARTIFACT,
    BRIDGE_ARTIFACT_JSON,
    BRIDGE_ARTIFACT_MD,
    artifact_sha256,
    build_omega_delta_g_payload,
    load_arms_payload,
    maybe_refresh_adjunct_ledger,
    render_omega_delta_g_markdown,
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
    payload = build_omega_delta_g_payload(arms_payload, seed=seed, generated=today)
    payload["artifact_sha256"] = artifact_sha256(payload)

    BRIDGE_ARTIFACT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    BRIDGE_ARTIFACT_MD.write_text(render_omega_delta_g_markdown(payload), encoding="utf-8")

    refreshed = maybe_refresh_adjunct_ledger(arms_payload, payload, generated=today)
    if refreshed is not None:
        ADJUNCT_ARTIFACT_JSON.write_text(json.dumps(refreshed, indent=2), encoding="utf-8")
        ADJUNCT_ARTIFACT_MD.write_text(render_adjunct_markdown(refreshed), encoding="utf-8")
        print("adjunct ledger refreshed (witness_support improved)")

    summary = {
        k: v
        for k, v in payload.items()
        if k not in ("arms",)
    }
    summary["f_omega_decor_status"] = (payload.get("f_omega_decor") or {}).get("status")
    summary["artifact_sha256"] = payload["artifact_sha256"]
    print(json.dumps(summary, indent=2))
    print(f"wrote {BRIDGE_ARTIFACT_JSON}")
    print(f"wrote {BRIDGE_ARTIFACT_MD}")

    ok = (
        payload["e_endo_support"] == "none"
        and not payload["claim_allowed"]
        and not payload["c_ladder_raise_allowed"]
        and payload["tier"] == "C"
        and payload["x_trigger_zero"] is True
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
