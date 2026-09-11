#!/usr/bin/env python3
"""CLI runner for D3×L3 boundary witness harness."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SCI_FLOW = Path(__file__).resolve().parent
REPO = SCI_FLOW.parents[1]
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from boundary_witness_harness import run_boundary_witness  # noqa: E402


def main() -> int:
    result = run_boundary_witness(REPO, att_n_seeds=2)
    today = date.today().isoformat()
    payload = {"date": today, **result.to_dict()}
    out = SCI_FLOW / f"M-D3-L3_boundary_witness_{today}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {out}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
