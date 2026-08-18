#!/usr/bin/env python3
"""CI gate: multi-seed determinism bootstrap for twin_world_001.

Runs twin_world_001 with seeds [42, 123, 999]:
  - identical trace fingerprints per seed (two runs each)
  - distinct fingerprints across seeds

Set EIA_CI_SEED_BOOTSTRAP=0 to skip (always exit 0).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "scenarios" / "twin_world_001.yaml"
BOOTSTRAP_SEEDS = (42, 123, 999)


def _skip() -> int:
    print("ci_seed_bootstrap: skipped (EIA_CI_SEED_BOOTSTRAP!=1)")
    return 0


def main() -> int:
    if os.environ.get("EIA_CI_SEED_BOOTSTRAP", "1") != "1":
        return _skip()

    sys.path.insert(0, str(ROOT / "src"))
    from eia.audit.replay import trace_fingerprint
    from eia.pipeline import run_scenario

    traces_root = ROOT / "traces" / "ci_seed_bootstrap"
    per_seed: list[dict] = []
    errors: list[str] = []

    for seed in BOOTSTRAP_SEEDS:
        r1 = run_scenario(
            SCENARIO,
            traces_dir=traces_root / f"a-{seed}",
            seed=seed,
        )
        r2 = run_scenario(
            SCENARIO,
            traces_dir=traces_root / f"b-{seed}",
            seed=seed,
        )
        fp1 = trace_fingerprint(r1["loop"].trace)
        fp2 = trace_fingerprint(r2["loop"].trace)
        eoi1 = round(r1["twin_result"].eoi, 4)
        eoi2 = round(r2["twin_result"].eoi, 4)

        if fp1 != fp2:
            errors.append(f"seed {seed}: fingerprint mismatch {fp1} != {fp2}")
        if eoi1 != eoi2:
            errors.append(f"seed {seed}: EOI mismatch {eoi1} != {eoi2}")

        per_seed.append(
            {
                "seed": seed,
                "fingerprint": fp1,
                "eoi": eoi1,
                "within_seed_match": fp1 == fp2,
            }
        )

    unique_fps = {row["fingerprint"] for row in per_seed}
    if len(unique_fps) != len(BOOTSTRAP_SEEDS):
        errors.append(
            f"expected {len(BOOTSTRAP_SEEDS)} distinct fingerprints, got {len(unique_fps)}"
        )

    payload = {
        "scenario": SCENARIO.name,
        "seeds": list(BOOTSTRAP_SEEDS),
        "per_seed": per_seed,
        "unique_fingerprints": len(unique_fps),
        "passed": not errors,
        "errors": errors,
    }
    print(json.dumps(payload, indent=2))

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    print("ci_seed_bootstrap: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
