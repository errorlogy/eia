#!/usr/bin/env python3
"""CLI runner for T-BRAIN-06 3D EIA visualizations.

claim_allowed=false · Tier C · C2 ceiling · observational figures only.
"""

from __future__ import annotations

import sys
from pathlib import Path

VIZ_DIR = Path(__file__).resolve().parent / "viz"
if str(VIZ_DIR) not in sys.path:
    sys.path.insert(0, str(VIZ_DIR))

from t_brain_06_3d import generate_all, load_payload  # noqa: E402


def main() -> int:
    artifact = None
    no_harness = False
    for arg in sys.argv[1:]:
        if arg.startswith("--artifact="):
            artifact = Path(arg.split("=", 1)[1])
        elif arg == "--no-harness":
            no_harness = True

    payload = load_payload(artifact_path=artifact, run_harness=not no_harness)
    outputs = generate_all(payload)

    print("T-BRAIN-06 3D figures generated:")
    for stem, (pdf, png) in outputs.items():
        print(f"  {stem}")
        print(f"    PDF: {pdf}")
        print(f"    PNG: {png}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
