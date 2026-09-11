"""Brain-AI OMEGA_t → Agent-EIA bridge (T-AGENT-03).

Lazy-imports ``research/brain_ai/adapters`` to avoid circular deps with agent harnesses.
Connectome source → spikes → ``inject_omega_from_spikes`` → Ψ(O_t) observation on tick 1.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

REPO = Path(__file__).resolve().parents[3]
BRAIN_ADAPTERS = REPO / "research" / "brain_ai" / "adapters"
AGENT_EIA = Path(__file__).resolve().parents[1]

Agent03ArmName = Literal[
    "brain_eia_endogenous",
    "brain_eia_no_psi",
    "brain_reactive",
    "agent_only_eia",
]

DEFAULT_CONNECTOME_SOURCES: tuple[str, ...] = ("bundled_tiny", "google_male_cns")

SOURCE_SEED_OFFSET: dict[str, int] = {
    "bundled_tiny": 0,
    "synthetic": 0,
    "google_male_cns": 101,
    "flywire_female": 203,
}

ARM_CONFIG: dict[str, dict[str, Any]] = {
    "brain_eia_endogenous": {
        "connectome_arm": "coupled_active",
        "eia_baseline": "full_eia",
        "inject_omega_psi": True,
        "uses_connectome": True,
    },
    "brain_eia_no_psi": {
        "connectome_arm": "coupled_active",
        "eia_baseline": "full_eia",
        "inject_omega_psi": False,
        "uses_connectome": True,
    },
    "brain_reactive": {
        "connectome_arm": "passive_quiescent",
        "eia_baseline": "reactive_only",
        "inject_omega_psi": False,
        "uses_connectome": True,
    },
    "agent_only_eia": {
        "connectome_arm": None,
        "eia_baseline": "full_eia",
        "inject_omega_psi": False,
        "uses_connectome": False,
    },
}


def _ensure_brain_paths() -> None:
    brain_path = str(BRAIN_ADAPTERS)
    src_path = str(REPO / "src")
    for path in (brain_path, src_path):
        if path not in sys.path:
            sys.path.insert(0, path)


def resolve_arm_config(arm: Agent03ArmName) -> dict[str, Any]:
    """Return connectome/EIA/Ψ mapping for one T-AGENT-03 arm."""
    cfg = ARM_CONFIG.get(arm)
    if cfg is None:
        raise KeyError(f"unknown T-AGENT-03 arm: {arm}")
    return dict(cfg)


def build_connectome_omega_context(
    source_key: str,
    connectome_arm: str,
    *,
    seed: int,
    n_nodes: int = 8,
    duration_ms: float = 100.0,
    dt_ms: float = 1.0,
    carriers: tuple[float, ...] = (20.0, 30.0, 42.0, 70.0),
    prefer_brian2: bool = False,
) -> dict[str, Any]:
    """connectome → spikes → OMEGA_t + behavior metrics for one substrate arm."""
    _ensure_brain_paths()
    from behavior_metrics import compute_behavior_metrics
    from connectome_export import load_subgraph
    from ot_injection import inject_omega_from_spikes
    from spike_arms import run_spike_arm

    src_seed = seed + SOURCE_SEED_OFFSET.get(source_key, 0)
    subgraph = load_subgraph(
        connectome_source=source_key,
        n_nodes=n_nodes,
        seed=src_seed,
        prefer_bundled=(source_key == "bundled_tiny"),
    )
    spike_payload = run_spike_arm(
        subgraph,
        connectome_arm,  # type: ignore[arg-type]
        seed=src_seed,
        duration_ms=duration_ms,
        dt_ms=dt_ms,
        prefer_brian2=prefer_brian2 and connectome_arm == "coupled_active",
    )
    behavior = compute_behavior_metrics(spike_payload)
    omega_ctx = inject_omega_from_spikes(
        spike_payload, subgraph.node_ids, carriers=carriers
    )
    omega_ctx["arm"] = connectome_arm
    omega_ctx["source_key"] = source_key
    omega_ctx["connectome_source_tag"] = subgraph.source
    omega_ctx["n_nodes"] = subgraph.n_nodes
    return {
        "source_key": source_key,
        "connectome_arm": connectome_arm,
        "seed_used": src_seed,
        "omega_ctx": omega_ctx,
        "behavior": behavior,
        "spike_backend": spike_payload.get("backend"),
        "n_spikes": spike_payload.get("n_spikes"),
    }


def apply_omega_psi_to_loop(
    loop: Any,
    bridge: dict[str, Any],
    *,
    arm_key: str,
    cognitive_tick: int = 1,
) -> None:
    """Inject Ψ(O_t) as internal observation (tick 1 only; no re-injection on carryover)."""
    from eia.schemas.belief import BeliefKind
    from eia.schemas.observation import Observation, ObservationSource

    omega_ctx = bridge["omega_ctx"]
    behavior = bridge["behavior"]
    omega_t = float(omega_ctx.get("omega_t") or 0.0)
    kuramoto_r = float(omega_ctx.get("kuramoto_r") or 0.0)
    ows = omega_ctx.get("omega_wave_state") or {}

    loop.apply_observation(
        Observation(
            id=f"obs-brain-omega-bridge-{cognitive_tick}",
            timestamp=datetime.now(timezone.utc),
            source=ObservationSource.INTERNAL,
            topic="brain_ai_omega_wave_bridge",
            payload={
                "omega_t": omega_t,
                "kuramoto_r": kuramoto_r,
                "omega_wave_state": ows,
                "bridge": "connectome_spikes_to_omega_wave_state",
                "arm_key": arm_key,
                "source_key": bridge.get("source_key"),
                "connectome_arm": bridge.get("connectome_arm"),
                "behavior": behavior,
                "x_trigger_zero": True,
                "psi_ot": True,
                "cognitive_tick": cognitive_tick,
            },
            trust=0.9,
        )
    )

    loop.field.upsert_belief(
        "belief-brain-omega-substrate",
        kind=BeliefKind.CATEGORICAL,
        subject="connectome_substrate",
        claim="omega_wave_coherence",
        distribution={
            "coherent": min(1.0, 0.35 + omega_t),
            "incoherent": max(0.0, 0.65 - omega_t),
        },
        uncertainty=min(0.98, 0.60 + omega_t * 0.35),
        metadata={
            "source": "brain_agent_bridge",
            "psi_ot": True,
            "omega_t": omega_t,
            "kuramoto_r": kuramoto_r,
            "arm_key": arm_key,
        },
    )
    if loop.field.beliefs.get("belief-epistemic-gap"):
        loop.field.register_contradiction(
            "belief-brain-omega-substrate",
            "belief-epistemic-gap",
            "substrate_coherence",
        )

    epistemic_boost = min(0.40, omega_t * 0.55)
    coherence_boost = min(0.30, kuramoto_r * 0.35)
    loop.drives.state.epistemic = min(1.0, loop.drives.state.epistemic + epistemic_boost)
    loop.drives.state.coherence = min(1.0, loop.drives.state.coherence + coherence_boost)


def bridge_summary(bridge: dict[str, Any] | None) -> dict[str, Any]:
    """Compact bridge metrics for artifact rows."""
    if bridge is None:
        return {
            "source_key": None,
            "connectome_arm": None,
            "omega_t": None,
            "kuramoto_r": None,
            "activity_rate_per_node_ms": None,
            "n_spikes": None,
        }
    omega = bridge.get("omega_ctx") or {}
    behavior = bridge.get("behavior") or {}
    return {
        "source_key": bridge.get("source_key"),
        "connectome_arm": bridge.get("connectome_arm"),
        "connectome_source_tag": omega.get("connectome_source_tag"),
        "omega_t": omega.get("omega_t"),
        "kuramoto_r": omega.get("kuramoto_r"),
        "activity_rate_per_node_ms": behavior.get("activity_rate_per_node_ms"),
        "regime_label": behavior.get("regime_label"),
        "n_spikes": bridge.get("n_spikes"),
        "spike_backend": bridge.get("spike_backend"),
    }
