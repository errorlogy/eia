"""Brain-AI OMEGA_t → EIA shadow multitick bridge (T-BRAIN-03).

Injects connectome-derived OMEGA crosswalk as internal observation at X_trigger=0.
Genesis coupling follows behavioral activity proxy (not omega_t alone) so
phase_scramble preserves genesis while shifting OMEGA (F-OMEGA-DECOR probe).

Tier C only; ``claim_allowed=false``; no D1 ``e_endo_support`` bleed.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "src"
WOE_SRC = REPO / "research" / "cursor-starter-v0.2" / "src"
WOE_PKG = WOE_SRC / "eia"
SCI_FLOW = REPO / "research" / "sci_flow"

PASSIVE_ACTIVITY_THRESHOLD = 0.015


def _ensure_paths() -> None:
    for path in (str(SRC), str(SCI_FLOW)):
        if path not in sys.path:
            sys.path.insert(0, path)


def _load_woe_submodule(name: str) -> Any:
    pkg_name = "woe_eia_brain_shadow_bridge"
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        pkg.__path__ = [str(WOE_PKG)]  # type: ignore[attr-defined]
        sys.modules[pkg_name] = pkg

    full = f"{pkg_name}.{name}"
    if full in sys.modules:
        return sys.modules[full]

    path = WOE_PKG / f"{name}.py"
    spec = importlib.util.spec_from_file_location(full, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = pkg_name
    sys.modules[full] = mod
    spec.loader.exec_module(mod)
    return mod


def behavior_allows_novel_genesis(behavior: dict[str, Any]) -> bool:
    """Passive/quiescent arms suppress novel G' in bridged shadow (behavior-gated)."""
    rate = float(behavior.get("activity_rate_per_node_ms") or 0.0)
    if rate < PASSIVE_ACTIVITY_THRESHOLD:
        return False
    regime = str(behavior.get("regime_label") or "")
    return regime != "passive"


def run_brain_omega_bridged_shadow_episode(
    omega_ctx: dict[str, Any],
    behavior: dict[str, Any],
    *,
    seed: int = 0,
    arm_key: str = "unknown",
) -> dict[str, Any]:
    """Run one closed-loop shadow multitick with Brain-AI omega + behavior bridge."""
    _ensure_paths()
    from eia.governor import ContactGovernor, GovernorConfig
    from eia.ids import seeded_context
    from eia.pipeline import CognitiveLoop
    from eia.runtime.shadow_multitick import AttREvent, ShadowSessionCarryover
    from eia.schemas.belief import BeliefKind
    from eia.schemas.observation import Observation, ObservationSource

    omega_t = float(omega_ctx.get("omega_t") or 0.0)
    kuramoto_r = float(omega_ctx.get("kuramoto_r") or 0.0)
    ows = omega_ctx.get("omega_wave_state") or {}
    allow_novel = behavior_allows_novel_genesis(behavior)

    with seeded_context(seed):
        loop = CognitiveLoop(seed=seed)
        loop.governor = ContactGovernor(GovernorConfig())

        events: list[AttREvent] = [
            AttREvent(
                "o0",
                "X",
                f"brain_omega_bridge:omega_t={omega_t:.4f}",
                (),
                0,
            ),
            AttREvent("n0", "W", "world_model", ("o0",), 0),
            AttREvent("n1", "M", "self_model", ("n0",), 0),
        ]
        motive_ids: list[str] = []

        loop.apply_observation(
            Observation(
                id="obs-brain-omega-bridge",
                timestamp=datetime.now(timezone.utc),
                source=ObservationSource.INTERNAL,
                topic="brain_ai_omega_wave_bridge",
                payload={
                    "omega_t": omega_t,
                    "kuramoto_r": kuramoto_r,
                    "omega_wave_state": ows,
                    "bridge": "connectome_spikes_to_omega_wave_state",
                    "arm_key": arm_key,
                    "behavior": behavior,
                    "x_trigger_zero": True,
                },
                trust=0.9,
            )
        )
        loop.apply_observation(
            Observation(
                id="obs-workspace",
                timestamp=datetime.now(timezone.utc),
                source=ObservationSource.WORLD_EVENT,
                topic="workspace_file_activity",
                payload={
                    "files_recently_modified": True,
                    "omega_bridged": True,
                    "activity_rate": behavior.get("activity_rate_per_node_ms"),
                },
                trust=0.95,
            )
        )

        mot, _init1, decision, _ = loop.tick_cognition(tick=1, hour=14, finalize=True)
        motive_ids.append(mot.id)
        g0 = mot.id
        events.append(AttREvent("n2", "G", g0, ("n0", "n1", "o0"), 0))
        events.append(AttREvent("n3", "Pi", "pi_research", ("n2",), 1))
        outcome = decision.outcome.value if decision else "abstain"
        action_label = f"act_probe:{outcome}"
        events.append(AttREvent("n4", "A", action_label, ("n3",), 1))

        belief_id = "belief-post-action"
        loop.field.upsert_belief(
            belief_id,
            kind=BeliefKind.CATEGORICAL,
            subject="workspace",
            claim="action_consequence_observed",
            distribution={"updated": 0.8, "stale": 0.2},
            uncertainty=0.35,
            metadata={
                "source": "t_brain_03_shadow_bridge",
                "role": "W_prime",
                "prior_action": action_label,
            },
        )
        loop.apply_observation(
            Observation(
                id="obs-consequence",
                timestamp=datetime.now(timezone.utc),
                source=ObservationSource.INTERNAL,
                topic="action_consequence",
                payload={"prior_action": action_label, "belief_id": belief_id},
                trust=0.95,
            )
        )
        events.append(AttREvent("n5", "X", "x_observation", ("n4",), 2))
        events.append(AttREvent("n6", "W_prime", "world_update", ("n5", "n4"), 2))

        mot2, _init2, _dec2, _ = loop.tick_cognition(tick=2, hour=14, finalize=True)
        motive_ids.append(mot2.id)
        last_motive = mot2.id

        if allow_novel:
            events.append(
                AttREvent(
                    "n7",
                    "G_prime",
                    mot2.id,
                    ("n6", "n1", "o0"),
                    3,
                    novel=True,
                )
            )
        else:
            events.append(AttREvent("n7", "G", g0, ("n6",), 3, novel=False))
            last_motive = g0

        carryover = ShadowSessionCarryover.from_loop(
            loop, last_motive_id=last_motive, session_tick=2
        )

        return {
            "arm": "closed_loop",
            "bridge_kind": "brain_omega_bridged_closed_loop",
            "arm_key": arm_key,
            "events": [e.as_dict() for e in events],
            "shadow": True,
            "live_telegram": False,
            "emit_m0": False,
            "kuramoto_r": kuramoto_r,
            "omega_t": omega_t,
            "claim_allowed": False,
            "ticks_run": 2,
            "motive_ids": motive_ids,
            "used_carryover": False,
            "behavior_gated_novel_genesis": allow_novel,
            "omega_bridge": omega_ctx,
            "behavior_bridge": behavior,
            "carryover": {
                "session_tick": carryover.session_tick,
                "last_motive_id": carryover.last_motive_id,
                "drive_tick": carryover.drive_tick,
                "has_beliefs": bool(carryover.beliefs_json),
            },
            "gap_vs_live_daemon": (
                "Brain-AI omega-bridged shadow multitick: connectome O_t crosswalk "
                "injected as internal observation; genesis gated by behavioral activity "
                "proxy at X_trigger=0. Live daemon does not ingest connectome omega context."
            ),
        }


def score_shadow_log(log: dict[str, Any]) -> dict[str, Any]:
    """Score one shadow log under ATT-R (explore proxy only)."""
    live_att_r = _load_woe_submodule("live_att_r")
    return live_att_r.scorecard_from_shadow_log(log)
