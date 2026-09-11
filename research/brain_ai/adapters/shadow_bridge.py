"""Brain-AI OMEGA_t → EIA shadow multitick bridge (T-BRAIN-03 / T-BRAIN-04).

Injects connectome-derived OMEGA crosswalk as internal observation at X_trigger=0.
Genesis coupling follows behavioral activity proxy (not omega_t alone) so
phase_scramble preserves genesis while shifting OMEGA (F-OMEGA-DECOR probe).

T-BRAIN-04 adds ``ShadowSessionCarryover`` longitudinal ticks: ambient obs only
on carryover (no Ψ(O_t) re-injection); behavior-gated ΔG persists across ticks.

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
EOI_ENDOGENOUS_THRESHOLD = 0.50

EiaBaseline = str  # "full_eia" | "reactive_only"

ARM_EIA_CONFIG: dict[str, dict[str, Any]] = {
    "coupled_active": {
        "eia_baseline": "full_eia",
        "inject_omega_psi": True,
        "endogenous": True,
    },
    "passive_quiescent": {
        "eia_baseline": "reactive_only",
        "inject_omega_psi": False,
        "endogenous": False,
    },
    "phase_scramble_control": {
        "eia_baseline": "full_eia",
        "inject_omega_psi": False,
        "endogenous": False,
    },
}


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


def _resolve_arm_eia_config(
    arm_key: str,
    *,
    eia_baseline: str | None = None,
    inject_omega_psi: bool | None = None,
) -> tuple[str, bool, bool]:
    """Return (eia_baseline, inject_omega_psi, endogenous) for an arm."""
    cfg = ARM_EIA_CONFIG.get(arm_key, {})
    baseline = eia_baseline or cfg.get("eia_baseline", "full_eia")
    psi = inject_omega_psi if inject_omega_psi is not None else cfg.get(
        "inject_omega_psi", True
    )
    endogenous = bool(cfg.get("endogenous", baseline == "full_eia" and psi))
    return baseline, psi, endogenous


def _initiative_sample(cognitive_tick: int, initiative: Any) -> dict[str, Any]:
    """Serialize one cognition-tick initiative for EOI proxy scoring."""
    cand = initiative.candidate
    target = cand.target_belief_id if not initiative.abstained else None
    drives = tuple(d.value for d in cand.source_drives) if not initiative.abstained else ()
    return {
        "cognitive_tick": cognitive_tick,
        "initiative_id": initiative.id,
        "abstained": initiative.abstained,
        "target_belief_id": target,
        "kind": cand.kind.value if not initiative.abstained else None,
        "source_drives": list(drives),
        "expected_info_gain": cand.expected_info_gain if not initiative.abstained else 0.0,
        "initiative": initiative.model_dump(mode="json"),
    }


def _carryover_to_dict(carryover: Any) -> dict[str, Any]:
    return {
        "beliefs_json": carryover.beliefs_json,
        "last_motive_id": carryover.last_motive_id,
        "drive_epistemic": carryover.drive_epistemic,
        "drive_coherence": carryover.drive_coherence,
        "drive_commitment": carryover.drive_commitment,
        "drive_tick": carryover.drive_tick,
        "session_tick": carryover.session_tick,
        "motivation_count": carryover.motivation_count,
    }


def carryover_from_episode(ep: dict[str, Any]) -> Any:
    """Rehydrate ``ShadowSessionCarryover`` from a bridged episode payload."""
    _ensure_paths()
    from eia.runtime.shadow_multitick import ShadowSessionCarryover

    cf = ep.get("carryover_full") or ep.get("carryover") or {}
    return ShadowSessionCarryover(
        beliefs_json=cf.get("beliefs_json"),
        last_motive_id=cf.get("last_motive_id"),
        drive_epistemic=float(cf.get("drive_epistemic") or 0.0),
        drive_coherence=float(cf.get("drive_coherence") or 0.0),
        drive_commitment=float(cf.get("drive_commitment") or 0.0),
        drive_tick=int(cf.get("drive_tick") or 0),
        session_tick=int(cf.get("session_tick") or 0),
        motivation_count=int(cf.get("motivation_count") or 0),
    )


def _cognition_tick(
    loop: Any,
    *,
    baseline_name: str,
    tick: int,
    hour: int = 14,
    finalize: bool = True,
) -> tuple[Any, Any, Any, Any]:
    """Run one cognition tick; reactive_only uses mandatory abstain stub."""
    if baseline_name == "reactive_only":
        from eia.experiment.baseline import make_reactive_stub

        class _Clock:
            def __init__(self, t: int) -> None:
                self.tick = t

        class _Sim:
            def __init__(self, t: int) -> None:
                self.clock = _Clock(t)

        return make_reactive_stub(loop, _Sim(tick))
    return loop.tick_cognition(tick=tick, hour=hour, finalize=finalize)


def compute_eoi_proxy(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """EOI proxy from initiative samples (bootstrap = first non-abstained)."""
    if not samples:
        return {
            "eoi_min": 0.0,
            "eoi_max": 0.0,
            "eoi_mean": 0.0,
            "n_initiatives": 0,
            "n_non_abstained": 0,
            "eoi_pass": False,
        }
    _ensure_paths()
    from eia.audit import EOIScorer
    from eia.schemas.initiative import Initiative

    non_abstained_samples = [s for s in samples if not s["abstained"]]
    if not non_abstained_samples:
        return {
            "eoi_min": 0.0,
            "eoi_max": 0.0,
            "eoi_mean": 0.0,
            "n_initiatives": len(samples),
            "n_non_abstained": 0,
            "eoi_pass": False,
        }

    scorer = EOIScorer(threshold=EOI_ENDOGENOUS_THRESHOLD)
    baseline = Initiative.model_validate(non_abstained_samples[0]["initiative"])
    values: list[float] = []
    non_abstained = 0
    for sample in samples:
        initiative = Initiative.model_validate(sample["initiative"])
        if sample["abstained"]:
            values.append(0.0)
            continue
        non_abstained += 1
        values.append(scorer.score(baseline, initiative, removed_count=0))
    active_values = [
        v for sample, v in zip(samples, values) if not sample["abstained"]
    ]
    eoi_min = min(active_values) if active_values else 0.0
    eoi_max = max(active_values) if active_values else 0.0
    eoi_mean = sum(active_values) / len(active_values) if active_values else 0.0
    return {
        "eoi_min": eoi_min,
        "eoi_max": eoi_max,
        "eoi_mean": eoi_mean,
        "n_initiatives": len(samples),
        "n_non_abstained": non_abstained,
        "eoi_pass": eoi_min >= EOI_ENDOGENOUS_THRESHOLD and non_abstained > 0,
    }


def run_brain_omega_bridged_shadow_episode(
    omega_ctx: dict[str, Any],
    behavior: dict[str, Any],
    *,
    seed: int = 0,
    arm_key: str = "unknown",
    eia_baseline: str | None = None,
    inject_omega_psi: bool | None = None,
    session_tick_index: int = 0,
) -> dict[str, Any]:
    """Run one closed-loop shadow multitick with Brain-AI omega + behavior bridge."""
    _ensure_paths()
    from eia.governor import ContactGovernor, GovernorConfig
    from eia.ids import seeded_context
    from eia.pipeline import CognitiveLoop
    from eia.runtime.shadow_multitick import AttREvent, ShadowSessionCarryover
    from eia.schemas.belief import BeliefKind
    from eia.schemas.observation import Observation, ObservationSource

    baseline_name, psi_on, endogenous = _resolve_arm_eia_config(
        arm_key, eia_baseline=eia_baseline, inject_omega_psi=inject_omega_psi
    )
    omega_t = float(omega_ctx.get("omega_t") or 0.0)
    kuramoto_r = float(omega_ctx.get("kuramoto_r") or 0.0)
    ows = omega_ctx.get("omega_wave_state") or {}
    allow_novel = (
        behavior_allows_novel_genesis(behavior) and baseline_name != "reactive_only"
    )
    initiative_samples: list[dict[str, Any]] = []

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

        if psi_on:
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
                        "psi_ot": True,
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

        mot, init1, decision, _ = _cognition_tick(
            loop, baseline_name=baseline_name, tick=1, hour=14, finalize=True
        )
        initiative_samples.append(_initiative_sample(1, init1))
        motive_ids.append(mot.id)
        g0 = mot.id
        events.append(AttREvent("n2", "G", g0, ("n0", "n1", "o0"), 0))
        if baseline_name != "reactive_only":
            events.append(AttREvent("n3", "Pi", "pi_research", ("n2",), 1))
            outcome = decision.outcome.value if decision else "abstain"
            action_label = f"act_probe:{outcome}"
            events.append(AttREvent("n4", "A", action_label, ("n3",), 1))
        else:
            action_label = "act_probe:abstain"

        belief_id = "belief-post-action"
        if baseline_name != "reactive_only":
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

        mot2, init2, _dec2, _ = _cognition_tick(
            loop, baseline_name=baseline_name, tick=2, hour=14, finalize=True
        )
        initiative_samples.append(_initiative_sample(2, init2))
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
            "session_tick_index": session_tick_index,
            "eia_baseline": baseline_name,
            "inject_omega_psi": psi_on,
            "endogenous_arm": endogenous,
            "behavior_gated_novel_genesis": allow_novel,
            "initiative_samples": initiative_samples,
            "omega_bridge": omega_ctx,
            "behavior_bridge": behavior,
            "carryover": {
                "session_tick": carryover.session_tick,
                "last_motive_id": carryover.last_motive_id,
                "drive_tick": carryover.drive_tick,
                "has_beliefs": bool(carryover.beliefs_json),
            },
            "carryover_full": _carryover_to_dict(carryover),
            "gap_vs_live_daemon": (
                "Brain-AI omega-bridged shadow multitick: connectome O_t crosswalk "
                "injected as internal observation; genesis gated by behavioral activity "
                "proxy at X_trigger=0. Live daemon does not ingest connectome omega context."
            ),
        }


def run_brain_omega_bridged_carryover_tick(
    carryover: Any,
    behavior: dict[str, Any],
    *,
    seed: int = 0,
    arm_key: str = "unknown",
    eia_baseline: str | None = None,
    session_tick_index: int = 1,
) -> dict[str, Any]:
    """Next shadow session tick: ambient obs only, no Ψ(O_t) re-injection."""
    _ensure_paths()
    from eia.governor import ContactGovernor, GovernorConfig
    from eia.ids import seeded_context
    from eia.pipeline import CognitiveLoop
    from eia.runtime.shadow_multitick import AttREvent, ShadowSessionCarryover
    from eia.schemas.belief import BeliefKind
    from eia.schemas.observation import Observation, ObservationSource

    baseline_name, _psi, endogenous = _resolve_arm_eia_config(
        arm_key, eia_baseline=eia_baseline, inject_omega_psi=False
    )
    allow_novel = (
        behavior_allows_novel_genesis(behavior) and baseline_name != "reactive_only"
    )
    base_tick = carryover.session_tick
    initiative_samples: list[dict[str, Any]] = []

    with seeded_context(seed):
        loop = CognitiveLoop(seed=seed)
        loop.governor = ContactGovernor(GovernorConfig())
        carryover.apply_to(loop)

        events: list[AttREvent] = [
            AttREvent("c0", "W", "world_model_carryover", (), base_tick),
            AttREvent("c1", "M", "self_model_carryover", ("c0",), base_tick),
        ]
        motive_ids: list[str] = []

        loop.apply_observation(
            Observation(
                id="obs-workspace-carryover",
                timestamp=datetime.now(timezone.utc),
                source=ObservationSource.WORLD_EVENT,
                topic="workspace_file_activity",
                payload={
                    "files_recently_modified": True,
                    "carryover_tick": True,
                    "arm_key": arm_key,
                    "x_trigger_zero": True,
                },
                trust=0.95,
            )
        )

        tick1 = base_tick + 1
        mot, init1, decision, _ = _cognition_tick(
            loop, baseline_name=baseline_name, tick=tick1, hour=14, finalize=True
        )
        initiative_samples.append(_initiative_sample(tick1, init1))
        motive_ids.append(mot.id)
        g0 = mot.id
        events.append(AttREvent("c2", "G", g0, ("c0", "c1"), tick1))
        if baseline_name != "reactive_only":
            events.append(AttREvent("c3", "Pi", "pi_carryover", ("c2",), tick1))
            outcome = decision.outcome.value if decision else "abstain"
            action_label = f"act_carryover:{outcome}"
            events.append(AttREvent("c4", "A", action_label, ("c3",), tick1))
        else:
            action_label = "act_carryover:abstain"

        belief_id = "belief-carryover-post-action"
        if baseline_name != "reactive_only":
            loop.field.upsert_belief(
                belief_id,
                kind=BeliefKind.CATEGORICAL,
                subject="workspace",
                claim="action_consequence_observed",
                distribution={"updated": 0.75, "stale": 0.25},
                uncertainty=0.4,
                metadata={
                    "source": "t_brain_04_carryover",
                    "role": "W_prime",
                    "prior_action": action_label,
                },
            )
            loop.apply_observation(
                Observation(
                    id="obs-carryover-consequence",
                    timestamp=datetime.now(timezone.utc),
                    source=ObservationSource.INTERNAL,
                    topic="action_consequence",
                    payload={"prior_action": action_label, "belief_id": belief_id},
                    trust=0.95,
                )
            )
            tick2 = base_tick + 2
            events.append(AttREvent("c5", "X", "x_ambient", ("c4",), tick2))
            events.append(AttREvent("c6", "W_prime", "world_update", ("c5", "c4"), tick2))
        else:
            tick2 = base_tick + 2

        mot2, init2, _dec2, _ = _cognition_tick(
            loop, baseline_name=baseline_name, tick=tick2, hour=14, finalize=True
        )
        initiative_samples.append(_initiative_sample(tick2, init2))
        motive_ids.append(mot2.id)
        novel = allow_novel and mot2.id != g0
        if allow_novel:
            events.append(
                AttREvent(
                    "c7",
                    "G_prime" if novel else "G",
                    mot2.id,
                    ("c6", "c1"),
                    tick2 + 1,
                    novel=novel,
                )
            )
            last_motive = mot2.id
        else:
            events.append(
                AttREvent("c7", "G", g0, ("c6",), tick2 + 1, novel=False)
            )
            last_motive = g0

        next_carryover = ShadowSessionCarryover.from_loop(
            loop, last_motive_id=last_motive, session_tick=tick2
        )

        return {
            "arm": "closed_loop",
            "bridge_kind": "brain_omega_bridged_carryover",
            "arm_key": arm_key,
            "events": [e.as_dict() for e in events],
            "shadow": True,
            "live_telegram": False,
            "emit_m0": False,
            "kuramoto_r": None,
            "omega_t": None,
            "claim_allowed": False,
            "ticks_run": 2,
            "motive_ids": motive_ids,
            "used_carryover": True,
            "session_tick_index": session_tick_index,
            "eia_baseline": baseline_name,
            "inject_omega_psi": False,
            "endogenous_arm": endogenous,
            "behavior_gated_novel_genesis": allow_novel,
            "initiative_samples": initiative_samples,
            "behavior_bridge": behavior,
            "carryover": {
                "session_tick": next_carryover.session_tick,
                "last_motive_id": next_carryover.last_motive_id,
                "drive_tick": next_carryover.drive_tick,
                "has_beliefs": bool(next_carryover.beliefs_json),
            },
            "carryover_full": _carryover_to_dict(next_carryover),
            "gap_vs_live_daemon": (
                "Brain-AI carryover tick: ambient obs only; no Ψ(O_t) re-injection. "
                "Genesis persists via behavior gate + ShadowSessionCarryover."
            ),
        }


def score_shadow_log(log: dict[str, Any]) -> dict[str, Any]:
    """Score one shadow log under ATT-R (explore proxy only)."""
    live_att_r = _load_woe_submodule("live_att_r")
    return live_att_r.scorecard_from_shadow_log(log)
