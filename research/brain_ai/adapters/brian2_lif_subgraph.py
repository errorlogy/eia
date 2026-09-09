"""Optional Brian2 LIF subgraph simulation — graceful skip when brian2 unavailable."""

from __future__ import annotations

import math
import random
from typing import Any

from connectome_export import ConnectomeSubgraph


def brian2_available() -> bool:
    try:
        import brian2  # noqa: F401

        return True
    except ImportError:
        return False


def run_lif_subgraph(
    subgraph: ConnectomeSubgraph,
    *,
    seed: int = 42,
    duration_ms: float = 100.0,
    dt_ms: float = 1.0,
) -> dict[str, Any] | None:
    """Run Brian2 LIF on subgraph; return spike raster or None if Brian2 missing."""
    if not brian2_available():
        return None

    from brian2 import NeuronGroup, SpikeMonitor, Synapses, ms, prefs

    prefs.codegen.target = "numpy"

    rng = random.Random(seed)
    n = subgraph.n_nodes
    duration = float(duration_ms) * ms
    dt = float(dt_ms) * ms

    group = NeuronGroup(
        n,
        """
        dv/dt = (-v + I_syn) / tau : 1
        I_syn : 1
        """,
        threshold="v > 1",
        reset="v = 0",
        method="euler",
        dt=dt,
        namespace={"tau": 10 * ms},
    )
    group.v = "rand()"

    syn = Synapses(group, group, "w : 1", on_pre="I_syn += w")
    i_idx: list[int] = []
    j_idx: list[int] = []
    w_vals: list[float] = []
    for i in range(n):
        for j in range(n):
            if subgraph.adjacency[i][j]:
                i_idx.append(i)
                j_idx.append(j)
                w_vals.append(float(subgraph.weights[i][j]))
    if i_idx:
        syn.connect(i=i_idx, j=j_idx)
        syn.w = w_vals

    # Drive hub nodes with weak Poisson-like external current bursts
    for idx in range(min(2, n)):
        group.I_syn[idx] = 0.15 + 0.05 * rng.random()

    monitor = SpikeMonitor(group)
    from brian2 import Network

    net = Network(group, syn, monitor)
    net.run(duration)

    spike_times: dict[str, list[float]] = {nid: [] for nid in subgraph.node_ids}
    for neuron_idx, t_ms in zip(monitor.i, monitor.t / ms, strict=False):
        nid = subgraph.node_ids[int(neuron_idx)]
        spike_times[nid].append(float(t_ms))

    return {
        "backend": "brian2_lif",
        "duration_ms": duration_ms,
        "dt_ms": dt_ms,
        "seed": seed,
        "n_spikes": sum(len(v) for v in spike_times.values()),
        "spike_times_ms": spike_times,
    }


def synthetic_spike_trains(
    subgraph: ConnectomeSubgraph,
    *,
    seed: int = 42,
    duration_ms: float = 100.0,
    dt_ms: float = 1.0,
) -> dict[str, Any]:
    """Deterministic fallback spike trains when Brian2 is unavailable."""
    rng = random.Random(seed)
    n_steps = max(1, int(duration_ms / dt_ms))
    spike_times: dict[str, list[float]] = {}

    for i, nid in enumerate(subgraph.node_ids):
        in_degree = sum(subgraph.adjacency[j][i] for j in range(subgraph.n_nodes))
        rate = 0.02 + 0.015 * in_degree + 0.005 * (i % 3)
        times: list[float] = []
        phase_offset = (i / max(1, subgraph.n_nodes)) * 2 * math.pi
        for step in range(n_steps):
            t = step * dt_ms
            # Kuramoto-like periodic drive + stochastic jitter
            drive = 0.5 + 0.5 * math.sin(2 * math.pi * t / 40.0 + phase_offset)
            if rng.random() < rate * drive:
                times.append(round(t, 3))
        spike_times[nid] = times

    return {
        "backend": "synthetic_spike_trains",
        "duration_ms": duration_ms,
        "dt_ms": dt_ms,
        "seed": seed,
        "n_spikes": sum(len(v) for v in spike_times.values()),
        "spike_times_ms": spike_times,
    }


def run_spike_dynamics(
    subgraph: ConnectomeSubgraph,
    *,
    seed: int = 42,
    duration_ms: float = 100.0,
    dt_ms: float = 1.0,
    prefer_brian2: bool = True,
) -> dict[str, Any]:
    """Brian2 LIF when available; otherwise synthetic spike trains."""
    if prefer_brian2:
        brian_result = run_lif_subgraph(
            subgraph, seed=seed, duration_ms=duration_ms, dt_ms=dt_ms
        )
        if brian_result is not None:
            return brian_result
    return synthetic_spike_trains(
        subgraph, seed=seed, duration_ms=duration_ms, dt_ms=dt_ms
    )
