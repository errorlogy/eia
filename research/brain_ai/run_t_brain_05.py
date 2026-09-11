#!/usr/bin/env python3
"""T-BRAIN-05 runner — multi-source connectome parity harness.

claim_allowed=false · Tier C · C2 ceiling · no AGI* · no e_endo_support bleed.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent / "harnesses"
if str(HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIR))

from t_brain_05_connectome_parity import (  # noqa: E402
    ARTIFACT_JSON,
    ARTIFACT_MD,
    artifact_sha256,
    build_t_brain_05_payload,
    render_t_brain_05_markdown,
)


def main() -> int:
    seed = 42
    prefer_brian2 = False
    include_shadow = True
    for arg in sys.argv[1:]:
        if arg.startswith("--seed="):
            seed = int(arg.split("=", 1)[1])
        elif arg == "--prefer-brian2":
            prefer_brian2 = True
        elif arg == "--no-shadow":
            include_shadow = False

    today = date.today().isoformat()
    payload = build_t_brain_05_payload(
        seed=seed,
        generated=today,
        prefer_brian2=prefer_brian2,
        include_shadow=include_shadow,
    )
    payload["artifact_sha256"] = artifact_sha256(payload)

    ARTIFACT_JSON.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    ARTIFACT_MD.write_text(render_t_brain_05_markdown(payload), encoding="utf-8")

    summary = {k: v for k, v in payload.items() if k not in ("per_source",)}
    print(json.dumps(summary, indent=2))
    print(f"wrote {ARTIFACT_JSON}")
    print(f"wrote {ARTIFACT_MD}")

    ok = (
        payload["e_endo_support"] == "none"
        and not payload["claim_allowed"]
        and not payload["c_ladder_raise_allowed"]
        and payload["tier"] == "C"
        and not payload["agi_star_claim"]
        and payload["diagnostic_pass"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
