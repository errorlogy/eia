"""Kuramoto order-parameter dynamics (theory §4.2)."""

from __future__ import annotations

import numpy as np


def order_parameter(phases: np.ndarray) -> float:
    return float(np.abs(np.mean(np.exp(1j * phases))))


def simulate_kuramoto(
    n_nodes: int,
    coupling_k: float,
    natural_freq_hz: np.ndarray,
    *,
    dt_s: float = 0.001,
    duration_s: float = 2.0,
    seed: int = 42,
) -> dict[str, float | np.ndarray]:
    rng = np.random.default_rng(seed)
    phases = rng.uniform(0.0, 2.0 * np.pi, size=n_nodes)
    steps = int(duration_s / dt_s)
    r_trace = np.empty(steps, dtype=float)

    for step in range(steps):
        r_trace[step] = order_parameter(phases)
        diffs = phases[None, :] - phases[:, None]
        coupling = (coupling_k / n_nodes) * np.sum(np.sin(diffs), axis=1)
        # Scale Hz → rad/s with 42 Hz as unit frequency (theory carrier reference)
        omega_rad = natural_freq_hz * (2.0 * np.pi / 42.0)
        dtheta = omega_rad + coupling
        phases = (phases + dt_s * dtheta) % (2.0 * np.pi)

    return {
        "final_r": order_parameter(phases),
        "mean_r": float(np.mean(r_trace[-steps // 4 :])),
        "r_trace": r_trace,
    }


def sweep_coupling(
    n_nodes: int,
    k_values: np.ndarray,
    natural_freq_hz: np.ndarray,
    *,
    dt_s: float = 0.001,
    duration_s: float = 2.0,
    seed: int = 42,
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for idx, k in enumerate(k_values):
        out = simulate_kuramoto(
            n_nodes,
            float(k),
            natural_freq_hz,
            dt_s=dt_s,
            duration_s=duration_s,
            seed=seed + idx,
        )
        rows.append({"coupling_k": float(k), "mean_r": float(out["mean_r"]), "final_r": float(out["final_r"])})
    return rows


def estimate_critical_coupling(rows: list[dict[str, float]], *, r_threshold: float = 0.7) -> float | None:
    for prev, curr in zip(rows, rows[1:]):
        if prev["mean_r"] < r_threshold <= curr["mean_r"]:
            return float((prev["coupling_k"] + curr["coupling_k"]) / 2.0)
    return None
