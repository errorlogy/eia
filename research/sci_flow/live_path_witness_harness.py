"""M-LIVE-PATH: shadow vs opt-in live daemon carryover witness (D2×L3).

Compares in-process ``ShadowSessionCarryover`` ticks against the real
``run_daemon_tick`` + ``StateStore`` path when ``EIA_DAEMON_BELIEF_CARRYOVER=1``.
Tier 0: no LLM, no Telegram send (shadow_mode=True), ``claim_allowed=false``.
"""

from __future__ import annotations

import math
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eia.runtime.daemon import DaemonConfig, run_daemon_tick
from eia.runtime.shadow_multitick import (
    ShadowArm,
    ShadowSessionCarryover,
    drive_norm,
    run_shadow_carryover_tick,
    run_shadow_episode,
)
from eia.runtime.state_store import StateStore


@dataclass
class CarryoverSnapshot:
    """Comparable carryover state across shadow and live paths."""

    path: str
    tick_label: str
    session_tick: int
    drive_tick: int
    motivation_count: int
    drive_epistemic: float
    drive_coherence: float
    drive_commitment: float
    drive_norm: float
    has_beliefs: bool
    used_carryover: bool
    belief_carryover_enabled: bool

    @classmethod
    def from_shadow(
        cls,
        carryover: ShadowSessionCarryover | None,
        *,
        path: str,
        tick_label: str,
        used_carryover: bool,
        belief_carryover_enabled: bool = True,
    ) -> CarryoverSnapshot:
        if carryover is None:
            return cls(
                path=path,
                tick_label=tick_label,
                session_tick=0,
                drive_tick=0,
                motivation_count=0,
                drive_epistemic=0.0,
                drive_coherence=0.0,
                drive_commitment=0.0,
                drive_norm=0.0,
                has_beliefs=False,
                used_carryover=used_carryover,
                belief_carryover_enabled=belief_carryover_enabled,
            )
        return cls(
            path=path,
            tick_label=tick_label,
            session_tick=carryover.session_tick,
            drive_tick=carryover.drive_tick,
            motivation_count=carryover.motivation_count,
            drive_epistemic=carryover.drive_epistemic,
            drive_coherence=carryover.drive_coherence,
            drive_commitment=carryover.drive_commitment,
            drive_norm=drive_norm(carryover),
            has_beliefs=bool(carryover.beliefs_json),
            used_carryover=used_carryover,
            belief_carryover_enabled=belief_carryover_enabled,
        )

    @classmethod
    def from_live_tick(
        cls,
        *,
        path: str,
        tick_label: str,
        tick_result,
        store_state,
    ) -> CarryoverSnapshot:
        norm = math.sqrt(
            store_state.drive_epistemic ** 2
            + store_state.drive_coherence ** 2
            + store_state.drive_commitment ** 2
        )
        return cls(
            path=path,
            tick_label=tick_label,
            session_tick=tick_result.session_tick,
            drive_tick=store_state.drive_tick,
            motivation_count=store_state.motivation_count,
            drive_epistemic=store_state.drive_epistemic,
            drive_coherence=store_state.drive_coherence,
            drive_commitment=store_state.drive_commitment,
            drive_norm=norm,
            has_beliefs=store_state.has_beliefs,
            used_carryover=tick_result.used_carryover,
            belief_carryover_enabled=tick_result.belief_carryover_enabled,
        )


@dataclass
class LivePathWitnessResult:
    milestone: str = "M-LIVE-PATH"
    tick: str = "M-LIVE-PATH"
    cube_cell: str = "D2×L3"
    claim_ceiling: str = "C2"
    claim_allowed: bool = False
    seed: int = 11
    shadow_carryover_ticks: int = 2
    shadow_snapshots: list[dict[str, Any]] = field(default_factory=list)
    live_off_snapshots: list[dict[str, Any]] = field(default_factory=list)
    live_on_snapshots: list[dict[str, Any]] = field(default_factory=list)
    parity_checks: dict[str, bool] = field(default_factory=dict)
    gap_vs_shadow: str = ""
    gap_narrowed: bool = False
    witness_pass: bool = False
    explore_proxy_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _run_shadow_path(*, seed: int, n_carryover: int) -> list[CarryoverSnapshot]:
    bootstrap = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=seed)
    snapshots = [
        CarryoverSnapshot.from_shadow(
            bootstrap.carryover,
            path="shadow",
            tick_label="bootstrap",
            used_carryover=bootstrap.used_carryover,
        )
    ]
    carryover = bootstrap.carryover
    if carryover is None:
        return snapshots
    for i in range(n_carryover):
        ep = run_shadow_carryover_tick(carryover, seed=seed + i + 1)
        carryover = ep.carryover
        snapshots.append(
            CarryoverSnapshot.from_shadow(
                carryover,
                path="shadow",
                tick_label=f"carryover_{i + 1}",
                used_carryover=ep.used_carryover,
            )
        )
    return snapshots


def _run_live_path(
    *,
    seed: int,
    carryover_enabled: bool,
    workspace: Path,
    state_db: Path,
    traces_dir: Path,
) -> list[CarryoverSnapshot]:
    prev = os.environ.get("EIA_DAEMON_BELIEF_CARRYOVER")
    if carryover_enabled:
        os.environ["EIA_DAEMON_BELIEF_CARRYOVER"] = "1"
    else:
        os.environ.pop("EIA_DAEMON_BELIEF_CARRYOVER", None)

    cfg = DaemonConfig(
        shadow_mode=True,
        workspace=workspace,
        traces_dir=traces_dir,
        state_db=state_db,
        seed=seed,
    )
    store = StateStore(state_db)
    t0 = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 9, 2, 12, 15, tzinfo=timezone.utc)
    path = "live_on" if carryover_enabled else "live_off"

    try:
        first = run_daemon_tick(
            shadow_mode=True,
            config=cfg,
            now=t0,
            state_store=store,
        )
        after_first = store.load_daemon_carryover()
        snapshots = [
            CarryoverSnapshot.from_live_tick(
                path=path,
                tick_label="tick_1",
                tick_result=first,
                store_state=after_first,
            )
        ]

        second = run_daemon_tick(
            shadow_mode=True,
            config=cfg,
            now=t1,
            state_store=store,
        )
        after_second = store.load_daemon_carryover()
        snapshots.append(
            CarryoverSnapshot.from_live_tick(
                path=path,
                tick_label="tick_2",
                tick_result=second,
                store_state=after_second,
            )
        )
        return snapshots
    finally:
        if prev is None:
            os.environ.pop("EIA_DAEMON_BELIEF_CARRYOVER", None)
        else:
            os.environ["EIA_DAEMON_BELIEF_CARRYOVER"] = prev
        del store


def _parity_checks(
    shadow: list[CarryoverSnapshot],
    live_off: list[CarryoverSnapshot],
    live_on: list[CarryoverSnapshot],
) -> dict[str, bool]:
    shadow_last = shadow[-1]
    live_off_1, live_off_2 = live_off
    live_on_1, live_on_2 = live_on

    return {
        "shadow_session_tick_advances": shadow_last.session_tick > shadow[0].session_tick,
        "shadow_beliefs_persist": shadow_last.has_beliefs,
        "shadow_second_tick_uses_carryover": any(s.used_carryover for s in shadow[1:]),
        "live_off_no_store_beliefs": not live_off_1.has_beliefs and not live_off_2.has_beliefs,
        "live_off_session_tick_zero": live_off_1.session_tick == 0 and live_off_2.session_tick == 0,
        "live_on_first_tick_persists": live_on_1.has_beliefs and live_on_1.session_tick == 1,
        "live_on_second_tick_hydrates": live_on_2.used_carryover,
        "live_on_session_tick_monotonic": live_on_2.session_tick > live_on_1.session_tick,
        "live_on_drive_tick_monotonic": live_on_2.drive_tick >= live_on_1.drive_tick,
        "live_on_beliefs_round_trip": live_on_2.has_beliefs,
        "structural_parity_session_tick": live_on_2.session_tick >= 2,
        "structural_parity_drive_norm_positive": live_on_2.drive_norm > 0.0,
    }


def run_live_path_witness(
    *,
    seed: int = 11,
    shadow_carryover_ticks: int = 2,
    workspace: Path | None = None,
) -> LivePathWitnessResult:
    """Execute shadow vs live carryover witness; uses temp StateStore by default."""
    workspace_tmp = tempfile.mkdtemp(prefix="eia_live_path_")
    root = workspace or Path(workspace_tmp)
    traces_root = root / "traces"
    traces_root.mkdir(parents=True, exist_ok=True)
    off_tmp = tempfile.mkdtemp(prefix="eia_live_off_")
    on_tmp = tempfile.mkdtemp(prefix="eia_live_on_")

    try:
        shadow = _run_shadow_path(seed=seed, n_carryover=shadow_carryover_ticks)
        live_off = _run_live_path(
            seed=seed,
            carryover_enabled=False,
            workspace=root,
            state_db=Path(off_tmp) / "live_off.db",
            traces_dir=traces_root / "off",
        )
        live_on = _run_live_path(
            seed=seed,
            carryover_enabled=True,
            workspace=root,
            state_db=Path(on_tmp) / "live_on.db",
            traces_dir=traces_root / "on",
        )

        checks = _parity_checks(shadow, live_off, live_on)
        witness_pass = all(checks.values())

        gap_narrowed = (
            checks["live_on_second_tick_hydrates"]
            and checks["live_on_beliefs_round_trip"]
            and checks["live_on_session_tick_monotonic"]
        )

        return LivePathWitnessResult(
            seed=seed,
            shadow_carryover_ticks=shadow_carryover_ticks,
            shadow_snapshots=[asdict(s) for s in shadow],
            live_off_snapshots=[asdict(s) for s in live_off],
            live_on_snapshots=[asdict(s) for s in live_on],
            parity_checks=checks,
            gap_vs_shadow=(
                "Shadow closes W'→G' in-process via run_shadow_carryover_tick; "
                "live daemon uses run_daemon_tick + digital observations + StateStore "
                "round-trip when EIA_DAEMON_BELIEF_CARRYOVER=1 (off by default). "
                "Tick granularity differs (shadow 2 cognition ticks/episode vs 1 daemon tick)."
            ),
            gap_narrowed=gap_narrowed,
            witness_pass=witness_pass,
            explore_proxy_note=(
                "M-LIVE-PATH structural witness: shadow-only longitudinal metrics "
                "(DSR, EOI drift, ATT-R) now have opt-in live StateStore parity for "
                "belief+drive carryover; not C-ladder gate; emit_m0=false."
            ),
        )
    finally:
        if workspace is None:
            shutil.rmtree(workspace_tmp, ignore_errors=True)
        shutil.rmtree(off_tmp, ignore_errors=True)
        shutil.rmtree(on_tmp, ignore_errors=True)
