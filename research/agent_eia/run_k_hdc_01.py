#!/usr/bin/env python3
"""K-HDC-01 runner — HDC binding in agent loop at X^trigger=0."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent / "harnesses"
if str(HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIR))

from k_hdc_01_agent_binding import (  # noqa: E402
    ARTIFACT_JSON,
    ARTIFACT_MD,
    artifact_sha256,
    build_k_hdc_01_payload,
    render_k_hdc_01_markdown,
)


def main() -> int:
    seed = 42
    for arg in sys.argv[1:]:
        if arg.startswith("--seed="):
            seed = int(arg.split("=", 1)[1])

    today = date.today().isoformat()
    payload = build_k_hdc_01_payload(seed=seed, generated=today)
    payload["artifact_sha256"] = artifact_sha256(payload)

    ARTIFACT_JSON.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    ARTIFACT_MD.write_text(render_k_hdc_01_markdown(payload), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print(f"wrote {ARTIFACT_JSON}")
    return 0 if payload["diagnostic_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
