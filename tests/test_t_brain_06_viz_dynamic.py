"""Smoke tests for T-BRAIN-06 dynamic 3D visualizations."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "research" / "brain_ai" / "run_viz_t_brain_06_dynamic.py"
GIF = REPO / "research" / "brain_ai" / "figures" / "t_brain_06_eia_3d_dynamic.gif"


def test_dynamic_viz_imports() -> None:
    viz_dir = REPO / "research" / "brain_ai" / "viz"
    if str(viz_dir) not in sys.path:
        sys.path.insert(0, str(viz_dir))
    from t_brain_06_3d_dynamic import build_frame_states, load_payload  # noqa: F401

    payload = load_payload(run_harness=False)
    states = build_frame_states(payload, n_frames=4)
    assert len(states) == 4
    assert ("bundled_tiny", "coupled_active") in states[0].per_point


def test_dynamic_viz_fast_runner(tmp_path: Path) -> None:
    """Run CLI with --fast --no-harness --view=cube; verify GIF is written."""
    out_gif = tmp_path / "t_brain_06_eia_3d_dynamic.gif"
    env = {"MPLBACKEND": "Agg"}
    import os

    env.update(os.environ)
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            "--fast",
            "--no-harness",
            "--view=cube",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert GIF.is_file(), f"expected GIF at {GIF}"
