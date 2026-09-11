#!/usr/bin/env python3
"""K-KUR-01 runner — Kuramoto R vs OMEGA_t vs genesis_Δ."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent / "harnesses"
if str(HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIR))

from k_kur_01_kuramoto_omega_genesis import (  # noqa: E402
    ARTIFACT_JSON,
    ARTIFACT_MD,
    artifact_sha256,
    build_k_kur_01_payload,
    render_k_kur_01_markdown,
)


def main() -> int:
    seed = 42
    session_ticks = 2
    for arg in sys.argv[1:]:
        if arg.startswith("--seed="):
            seed = int(arg.split("=", 1)[1])
        elif arg.startswith("--session-ticks="):
            session_ticks = int(arg.split("=", 1)[1])

    today = date.today().isoformat()
    payload = build_k_kur_01_payload(seed=seed, generated=today, session_ticks=session_ticks)
    payload["artifact_sha256"] = artifact_sha256(payload)

    ARTIFACT_JSON.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    ARTIFACT_MD.write_text(render_k_kur_01_markdown(payload), encoding="utf-8")

    summary = {k: v for k, v in payload.items() if k != "per_source"}
    print(json.dumps(summary, indent=2))
    print(f"wrote {ARTIFACT_JSON}")
    return 0 if payload["diagnostic_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
