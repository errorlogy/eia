"""Digital observations — git activity, workspace file mtimes, clock."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from eia.ids import new_id
from eia.schemas.observation import Observation, ObservationSource

try:
    from git import InvalidGitRepositoryError, Repo

    _HAS_GIT = True
except ImportError:
    _HAS_GIT = False


def _git_log_summary(repo_path: Path, max_commits: int = 5) -> dict | None:
    if not _HAS_GIT:
        return None
    try:
        repo = Repo(repo_path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        return None

    commits = []
    for commit in repo.iter_commits(max_count=max_commits):
        commits.append(
            {
                "sha": commit.hexsha[:8],
                "message": commit.message.strip().split("\n")[0][:120],
                "author": str(commit.author),
                "when": commit.committed_datetime.isoformat(),
            }
        )
    if not commits:
        return None
    return {
        "branch": repo.active_branch.name if not repo.head.is_detached else "detached",
        "recent_commits": commits,
        "commit_count_sampled": len(commits),
    }


def _workspace_mtimes(workspace: Path, limit: int = 20) -> list[dict]:
    """Recent file modifications under workspace (stdlib — no watchdog required)."""
    entries: list[tuple[float, str]] = []
    skip = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in skip]
        for name in files:
            path = Path(root) / name
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            rel = str(path.relative_to(workspace))
            if rel.startswith("traces" + os.sep):
                continue
            entries.append((mtime, rel))
    entries.sort(reverse=True)
    return [
        {"path": rel, "mtime_iso": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()}
        for mtime, rel in entries[:limit]
    ]


def collect_digital_observations(
    workspace: Path | str | None = None,
    *,
    now: datetime | None = None,
) -> list[Observation]:
    """Build normalized observations from digital workspace signals."""
    ws = Path(workspace) if workspace else Path.cwd()
    now = now or datetime.now(timezone.utc)
    observations: list[Observation] = []

    observations.append(
        Observation(
            id=new_id("obs-clock"),
            timestamp=now,
            source=ObservationSource.CLOCK_TICK,
            topic="clock_tick",
            payload={
                "hour": now.hour,
                "weekday": now.weekday(),
                "iso": now.isoformat(),
            },
        )
    )

    git_summary = _git_log_summary(ws)
    if git_summary:
        observations.append(
            Observation(
                id=new_id("obs-git"),
                timestamp=now,
                source=ObservationSource.WORLD_EVENT,
                topic="git_activity",
                payload=git_summary,
            )
        )

    mtimes = _workspace_mtimes(ws)
    if mtimes:
        observations.append(
            Observation(
                id=new_id("obs-files"),
                timestamp=now,
                source=ObservationSource.WORLD_EVENT,
                topic="workspace_file_activity",
                payload={
                    "workspace": str(ws.resolve()),
                    "recent_files": mtimes,
                    "file_count_sampled": len(mtimes),
                },
            )
        )

    return observations
