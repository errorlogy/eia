#!/usr/bin/env python3
"""CLI runner for T-BRAIN-06 dynamic 3D EIA animations.

claim_allowed=false · Tier C · C2 ceiling · observational figures only.
"""

from __future__ import annotations

import sys
from pathlib import Path

VIZ_DIR = Path(__file__).resolve().parent / "viz"
if str(VIZ_DIR) not in sys.path:
    sys.path.insert(0, str(VIZ_DIR))

from t_brain_06_3d import load_payload  # noqa: E402
from t_brain_06_3d_dynamic import (  # noqa: E402
    DEFAULT_FPS,
    DEFAULT_FRAMES,
    FAST_FPS,
    FAST_FRAMES,
    generate_all_dynamic,
)


def main() -> int:
    artifact = None
    no_harness = False
    fast = False
    session_ticks = 4
    use_session_ticks = False
    views: list[str] = []
    n_frames = DEFAULT_FRAMES
    fps = DEFAULT_FPS

    for arg in sys.argv[1:]:
        if arg.startswith("--artifact="):
            artifact = Path(arg.split("=", 1)[1])
        elif arg == "--no-harness":
            no_harness = True
        elif arg == "--fast":
            fast = True
            n_frames = FAST_FRAMES
            fps = FAST_FPS
        elif arg.startswith("--session-ticks="):
            session_ticks = int(arg.split("=", 1)[1])
            use_session_ticks = True
        elif arg.startswith("--frames="):
            n_frames = int(arg.split("=", 1)[1])
        elif arg.startswith("--fps="):
            fps = int(arg.split("=", 1)[1])
        elif arg.startswith("--view="):
            views.append(arg.split("=", 1)[1])

    run_harness = not no_harness and (artifact is None or use_session_ticks)
    if use_session_ticks and artifact is None:
        if str(VIZ_DIR.parent / "harnesses") not in sys.path:
            sys.path.insert(0, str(VIZ_DIR.parent / "harnesses"))
        from t_brain_06_eia_integrated import build_t_brain_06_payload

        payload = build_t_brain_06_payload(seed=42, session_ticks=session_ticks)
    else:
        payload = load_payload(artifact_path=artifact, run_harness=run_harness)

    view_tuple = tuple(views) if views else ("cube", "connectome", "trajectory")
    outputs = generate_all_dynamic(
        payload,
        n_frames=n_frames,
        fps=fps,
        views=view_tuple,
    )

    print("T-BRAIN-06 dynamic 3D animations generated:")
    for stem, paths in outputs.items():
        print(f"  {stem}")
        for fmt, path in paths.items():
            size_kb = path.stat().st_size / 1024
            print(f"    {fmt.upper()}: {path} ({size_kb:.0f} KB)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
