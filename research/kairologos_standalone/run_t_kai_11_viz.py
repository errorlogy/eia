#!/usr/bin/env python3
"""T-KAI-11 runner — export TopoLang programs and print viz open instructions."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VIZ_DIR = ROOT / "viz"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(VIZ_DIR))

from export_topo_json import export_all_examples  # noqa: E402
from harnesses.t_kai_11_topo_viz import main as run_harness  # noqa: E402

HTML_PATH = VIZ_DIR / "topo_program_3d.html"


def main() -> None:
    print("=== T-KAI-11 TopoLang 3D Visualization ===\n")
    paths = export_all_examples()
    for slug, path in sorted(paths.items()):
        print(f"  exported: {path}")

    html_uri = HTML_PATH.resolve().as_uri()
    print(f"\nOpen in browser:\n  {html_uri}\n")
    print("Recommended (avoids fetch/CORS issues):")
    print(f"  cd {VIZ_DIR.resolve()}")
    print("  python -m http.server 8765")
    print("  -> http://localhost:8765/topo_program_3d.html\n")
    print("Query param: ?program=if_then_else\n")

    run_harness()


if __name__ == "__main__":
    main()
