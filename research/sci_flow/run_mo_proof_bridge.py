#!/usr/bin/env python3
"""M-O proof adjunct bridge runner — paired do(O) arms → D2×L3 witness ledger.

Runs Neuraxon/native oscillatory arms through OmegaWaveState crosswalk, evaluates
under ``sci-flow-mo-adjunct-v0.1``, and writes dated JSON + markdown artifacts.

claim_allowed=false · Tier C · C2 ceiling · no AGI* · no e_endo_support bleed.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from mo_proof_bridge_harness import (
    ADJUNCT_ARTIFACT_JSON,
    ADJUNCT_ARTIFACT_MD,
    ARMS_ARTIFACT,
    build_adjunct_ledger,
    load_arms_payload,
    render_adjunct_markdown,
    _load_evidence_proofs,
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
    ledger = build_adjunct_ledger(arms_payload, generated=today)

    ADJUNCT_ARTIFACT_JSON.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    ADJUNCT_ARTIFACT_MD.write_text(render_adjunct_markdown(ledger), encoding="utf-8")

    ep = _load_evidence_proofs()
    proof = ep.evaluate_mo_adjunct_proof_version(
        ep.build_mo_adjunct_evidence_from_arms_payload(
            arms_payload,
            provenance=str(ARMS_ARTIFACT.name),
        )
    )
    print(ep.render_mo_adjunct_report(proof).encode("ascii", errors="replace").decode("ascii"))
    print(json.dumps(ledger, indent=2))
    print(f"wrote {ADJUNCT_ARTIFACT_JSON}")
    print(f"wrote {ADJUNCT_ARTIFACT_MD}")

    ok = (
        ledger["e_endo_support"] == "none"
        and not ledger["claim_allowed"]
        and not ledger["c_ladder_raise_allowed"]
        and ledger["witness_support"] in {"partial", "none"}
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
