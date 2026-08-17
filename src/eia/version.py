"""Code version helpers for trace metadata."""

from __future__ import annotations

import subprocess
from pathlib import Path


def get_code_version() -> str:
    """Return git short hash when available, else package version."""
    repo_root = Path(__file__).resolve().parents[2]
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=repo_root,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    try:
        from importlib.metadata import version

        return f"eia-{version('eia')}"
    except Exception:
        return "eia-unknown"
