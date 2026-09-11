"""E04 part 2 — EOI drift on 50-tick shadow carryover session."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAIN_SRC = REPO / "src"
SCI_FLOW = REPO / "research" / "sci_flow"

if str(MAIN_SRC) not in sys.path:
    sys.path.insert(0, str(MAIN_SRC))
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from eia.runtime.shadow_multitick import (  # noqa: E402
    ShadowArm,
    run_shadow_carryover_tick,
    run_shadow_episode,
)
from eoi_drift_harness import (  # noqa: E402
    EOI_DRIFT_TARGET_COGNITIVE_TICKS,
    EOI_ENDOGENOUS_THRESHOLD,
    run_eoi_drift_longitudinal_session,
)


def test_closed_loop_exports_initiative_samples() -> None:
    ep = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=3)
    assert len(ep.initiative_samples) == 2
    assert ep.initiative_samples[0]["cognitive_tick"] == 1
    assert ep.initiative_samples[0]["initiative_id"]


def test_carryover_tick_exports_initiative_samples() -> None:
    ep1 = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=7)
    ep2 = run_shadow_carryover_tick(ep1.carryover, seed=7)
    assert len(ep2.initiative_samples) == 2
    ticks = {s["cognitive_tick"] for s in ep2.initiative_samples}
    assert ticks == {ep1.carryover.session_tick + 1, ep1.carryover.session_tick + 2}


def test_eoi_drift_longitudinal_50_tick_session() -> None:
    result = run_eoi_drift_longitudinal_session(
        target_cognitive_ticks=EOI_DRIFT_TARGET_COGNITIVE_TICKS,
        seed=0,
    )
    assert result.e04_pass is True
    assert result.cognitive_ticks_reached >= EOI_DRIFT_TARGET_COGNITIVE_TICKS
    assert result.n_initiative_samples >= EOI_DRIFT_TARGET_COGNITIVE_TICKS
    assert result.eoi_min >= EOI_ENDOGENOUS_THRESHOLD
    assert result.persistence_fraction >= 1.0
    assert result.eoi_pass is True
    assert result.claim_allowed is False
    assert result.pool_metric_id == "E_ENDO"
    assert result.att == "ATT-E"
    assert result.eoi_drift_span <= 0.25


def test_run_e04_eoi_drift_runner_smoke() -> None:
    runner = SCI_FLOW / "run_e04_eoi_drift.py"
    spec = importlib.util.spec_from_file_location("run_e04_eoi_drift", runner)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    assert mod.main() == 0
