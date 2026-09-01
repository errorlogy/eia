"""Tests for live daemon belief carryover via StateStore (Phase 2)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from eia.runtime.daemon import DaemonConfig, belief_carryover_enabled, run_daemon_tick
from eia.runtime.state_store import StateStore


@pytest.fixture
def tmp_state_db(tmp_path: Path) -> Path:
    return tmp_path / "carryover_state.db"


@pytest.fixture
def tmp_traces(tmp_path: Path) -> Path:
    d = tmp_path / "traces"
    d.mkdir()
    return d


@pytest.fixture
def daemon_cfg(tmp_path: Path, tmp_traces: Path, tmp_state_db: Path) -> DaemonConfig:
    return DaemonConfig(
        shadow_mode=True,
        workspace=tmp_path,
        traces_dir=tmp_traces,
        state_db=tmp_state_db,
        seed=11,
    )


def test_belief_carryover_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EIA_DAEMON_BELIEF_CARRYOVER", raising=False)
    assert belief_carryover_enabled() is False


def test_belief_carryover_env_truthy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EIA_DAEMON_BELIEF_CARRYOVER", "1")
    assert belief_carryover_enabled() is True


def test_daemon_tick_persists_carryover_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
    daemon_cfg: DaemonConfig,
    tmp_state_db: Path,
) -> None:
    monkeypatch.setenv("EIA_DAEMON_BELIEF_CARRYOVER", "1")
    store = StateStore(tmp_state_db)
    now = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)

    first = run_daemon_tick(
        shadow_mode=True,
        config=daemon_cfg,
        now=now,
        state_store=store,
    )
    assert first.belief_carryover_enabled is True
    assert first.used_carryover is False
    assert first.session_tick == 1

    saved = store.load_daemon_carryover()
    assert saved.has_beliefs
    assert saved.session_tick == 1
    assert saved.drive_tick >= 1


def test_daemon_second_tick_hydrates_from_state_store(
    monkeypatch: pytest.MonkeyPatch,
    daemon_cfg: DaemonConfig,
    tmp_state_db: Path,
) -> None:
    monkeypatch.setenv("EIA_DAEMON_BELIEF_CARRYOVER", "1")
    store = StateStore(tmp_state_db)
    t0 = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 9, 1, 12, 15, tzinfo=timezone.utc)

    run_daemon_tick(
        shadow_mode=True,
        config=daemon_cfg,
        now=t0,
        state_store=store,
    )
    before = store.load_daemon_carryover()

    second = run_daemon_tick(
        shadow_mode=True,
        config=daemon_cfg,
        now=t1,
        state_store=store,
    )
    after = store.load_daemon_carryover()

    assert second.used_carryover is True
    assert second.session_tick == 2
    assert after.session_tick == 2
    assert after.session_tick > before.session_tick
    assert after.has_beliefs
    assert after.motivation_count >= before.motivation_count
    assert after.drive_tick >= before.drive_tick


def test_daemon_carryover_off_keeps_legacy_reset(
    monkeypatch: pytest.MonkeyPatch,
    daemon_cfg: DaemonConfig,
    tmp_state_db: Path,
) -> None:
    monkeypatch.delenv("EIA_DAEMON_BELIEF_CARRYOVER", raising=False)
    store = StateStore(tmp_state_db)
    now = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)

    result = run_daemon_tick(
        shadow_mode=True,
        config=daemon_cfg,
        now=now,
        state_store=store,
    )
    assert result.belief_carryover_enabled is False
    assert result.used_carryover is False
    assert store.load_daemon_carryover().has_beliefs is False
