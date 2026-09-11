#!/usr/bin/env python3
"""T-AGENT-02 runner — paired worlds initiative architecture comparison.

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

from t_agent_02_paired_worlds import (  # noqa: E402
    ARTIFACT_JSON,
    ARTIFACT_MD,
    artifact_sha256,
    build_t_agent_02_payload,
    render_t_agent_02_markdown,
)


def main() -> int:
    num_worlds: int | None = None
    llm_backend: str | None = None
    for arg in sys.argv[1:]:
        if arg.startswith("--num-worlds="):
            num_worlds = int(arg.split("=", 1)[1])
        elif arg.startswith("--llm-backend="):
            llm_backend = arg.split("=", 1)[1]

    today = date.today().isoformat()
    payload = build_t_agent_02_payload(
        generated=today,
        num_worlds=num_worlds,
        llm_backend=llm_backend,
    )
    payload["artifact_sha256"] = artifact_sha256(payload)

    ARTIFACT_JSON.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    ARTIFACT_MD.write_text(render_t_agent_02_markdown(payload), encoding="utf-8")

    summary = {
        k: v
        for k, v in payload.items()
        if k not in ("worlds_full", "rows")
    }
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
