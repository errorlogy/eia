"""Multi-arm spike dynamics for T-BRAIN-02 behavioral falsifier suite."""

from __future__ import annotations

import math
import random
from typing import Any, Literal

from connectome_export import ConnectomeSubgraph, generate_synthetic_subgraph
from brian2_lif_subgraph import run_spike_dynamics, synthetic_spike_trains

ArmKey = Literal[
    "coupled_active",
    "passive_quiescent",
    "burst_clustered",
    "decoupled_sparse",
    "phase_scramble_control",
]

ARM_KEYS: tuple[ArmKey, ...] = (
    "coupled_active",
    "passive_quiescent",
    "burst_clustered",
    "decoupled_sparse",
    "phase_scramble_control",
)

ARM_SEED_OFFSET: dict[ArmKey, int] = {
    "coupled_active": 0,
    "passive_quiescent": 101,
    "burst_clustered": 202,
    "decoupled_sparse": 303,
    "phase_scramble_control": 404,
}


def subgraph_for_arm(
    base: ConnectomeSubgraph,
    arm_key: ArmKey,
    *,
    seed: int,
) -> ConnectomeSubgraph:
    """Return connectome variant per arm (decoupled uses sparse rewiring)."""
    if arm_key != "decoupled_sparse":
        return base
    sparse = generate_synthetic_subgraph(
        n_nodes=base.n_nodes, seed=seed + 17, p_edge=0.08
    )
    return sparse


def _synthetic_arm_trains(
    subgraph: ConnectomeSubgraph,
    arm_key: ArmKey,
    *,
    seed: int,
    duration_ms: float,
    dt_ms: float,
) -> dict[str, Any]:
    """Deterministic arm-specific synthetic spike trains."""
    rng = random.Random(seed)
    n_steps = max(1, int(duration_ms / dt_ms))
    specs: dict[ArmKey, dict[str, float]] = {
        "coupled_active": {"rate_scale": 1.0, "drive_amp": 1.0, "jitter": 1.0},
        "passive_quiescent": {"rate_scale": 0.12, "drive_amp": 0.15, "jitter": 0.5},
        "burst_clustered": {"rate_scale": 0.7, "drive_amp": 1.0, "jitter": 0.3},
        "decoupled_sparse": {"rate_scale": 0.45, "drive_amp": 0.35, "jitter": 1.0},
        "phase_scramble_control": {"rate_scale": 1.0, "drive_amp": 1.0, "jitter": 1.0},
    }
    spec = specs[arm_key]
    spike_times: dict[str, list[float]] = {}

    for i, nid in enumerate(subgraph.node_ids):
        in_degree = sum(subgraph.adjacency[j][i] for j in range(subgraph.n_nodes))
        base_rate = (0.02 + 0.015 * in_degree + 0.005 * (i % 3)) * spec["rate_scale"]
        times: list[float] = []
        phase_offset = (i / max(1, subgraph.n_nodes)) * 2 * math.pi

        if arm_key == "burst_clustered":
            burst_centers = [duration_ms * 0.2, duration_ms * 0.55, duration_ms * 0.85]
            for step in range(n_steps):
                t = step * dt_ms
                in_burst = any(abs(t - c) < 8.0 for c in burst_centers)
                drive = spec["drive_amp"] * (1.5 if in_burst else 0.15)
                if rng.random() < base_rate * drive:
                    times.append(round(t, 3))
        else:
            for step in range(n_steps):
                t = step * dt_ms
                drive = 0.5 + 0.5 * spec["drive_amp"] * math.sin(
                    2 * math.pi * t / 40.0 + phase_offset
                )
                p = base_rate * drive * spec["jitter"]
                if rng.random() < p:
                    times.append(round(t, 3))
        spike_times[nid] = times

    return {
        "backend": "synthetic_spike_trains",
        "arm_key": arm_key,
        "duration_ms": duration_ms,
        "dt_ms": dt_ms,
        "seed": seed,
        "n_spikes": sum(len(v) for v in spike_times.values()),
        "spike_times_ms": spike_times,
        "phase_scramble_omega_only": arm_key == "phase_scramble_control",
    }


def run_spike_arm(
    subgraph: ConnectomeSubgraph,
    arm_key: ArmKey,
    *,
    seed: int = 42,
    duration_ms: float = 100.0,
    dt_ms: float = 1.0,
    prefer_brian2: bool = False,
    coupled_reference: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Spike dynamics for one falsifier arm (synthetic MVP; Brian2 only on coupled_active)."""
    if arm_key == "phase_scramble_control" and coupled_reference is not None:
        return {
            **coupled_reference,
            "arm_key": arm_key,
            "phase_scramble_omega_only": True,
        }

    sg = subgraph_for_arm(subgraph, arm_key, seed=seed)
    if prefer_brian2 and arm_key == "coupled_active":
        payload = run_spike_dynamics(
            sg, seed=seed, duration_ms=duration_ms, dt_ms=dt_ms, prefer_brian2=True
        )
        payload["arm_key"] = arm_key
        return payload
    payload = _synthetic_arm_trains(
        sg,
        arm_key,
        seed=seed + ARM_SEED_OFFSET[arm_key],
        duration_ms=duration_ms,
        dt_ms=dt_ms,
    )
    return payload


def scramble_spike_phases_for_omega(
    spike_payload: dict[str, Any],
    node_ids: list[str] | tuple[str, ...],
    *,
    carriers: tuple[float, ...],
    duration_ms: float,
    seed: int,
) -> list[float]:
    """Phase-scramble control: same spikes, permuted carrier phases (F-OMEGA-DECOR probe)."""
    from ot_injection import aggregate_node_phases

    phases = aggregate_node_phases(
        spike_payload.get("spike_times_ms") or {},
        carriers=carriers,
        duration_ms=duration_ms,
    )
    n = len(phases)
    if n < 2:
        return list(phases)
    # Deterministic maximal separation: reverse order ensures large phase delta vs baseline
    return [phases[(n - 1 - i) % n] for i in range(n)]
