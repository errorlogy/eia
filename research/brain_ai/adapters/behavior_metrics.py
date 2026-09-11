"""Behavioral proxies from spike dynamics — activity, burstiness, population sync."""

from __future__ import annotations

import math
from typing import Any, Sequence


def _inter_spike_intervals(times: Sequence[float]) -> list[float]:
    if len(times) < 2:
        return []
    sorted_times = sorted(times)
    return [sorted_times[i + 1] - sorted_times[i] for i in range(len(sorted_times) - 1)]


def burstiness_cv(spike_times_ms: dict[str, list[float]]) -> float:
    """Coefficient of variation of pooled inter-spike intervals (burstiness proxy)."""
    isis: list[float] = []
    for times in spike_times_ms.values():
        isis.extend(_inter_spike_intervals(times))
    if not isis:
        return 0.0
    mean = sum(isis) / len(isis)
    if mean < 1e-9:
        return 0.0
    var = sum((x - mean) ** 2 for x in isis) / len(isis)
    return math.sqrt(var) / mean


def activity_rate_per_node_ms(spike_payload: dict[str, Any]) -> float:
    """Mean spike rate per node (spikes / node / ms)."""
    duration_ms = float(spike_payload.get("duration_ms") or 100.0)
    spike_times = spike_payload.get("spike_times_ms") or {}
    n_nodes = max(1, len(spike_times))
    n_spikes = int(spike_payload.get("n_spikes") or sum(len(v) for v in spike_times.values()))
    return n_spikes / (duration_ms * n_nodes)


def population_sync_index(
    spike_times_ms: dict[str, list[float]],
    *,
    duration_ms: float = 100.0,
    bin_ms: float = 5.0,
) -> float:
    """Fraction of time bins where ≥2 nodes fire (synchrony proxy)."""
    if not spike_times_ms:
        return 0.0
    n_bins = max(1, int(duration_ms / bin_ms))
    bin_counts = [0] * n_bins
    for times in spike_times_ms.values():
        for t in times:
            idx = min(n_bins - 1, int(t / bin_ms))
            bin_counts[idx] += 1
    multi = sum(1 for c in bin_counts if c >= 2)
    return multi / n_bins


def endogenous_fraction(
    spike_payload: dict[str, Any],
    *,
    passive_threshold: float = 0.02,
) -> float:
    """Heuristic endogenous vs passive label: 1 − clamp(rate / threshold)."""
    rate = activity_rate_per_node_ms(spike_payload)
    if passive_threshold <= 0:
        return 1.0
    return max(0.0, min(1.0, 1.0 - rate / passive_threshold))


def compute_behavior_metrics(spike_payload: dict[str, Any]) -> dict[str, Any]:
    """Aggregate behavioral proxies for one spike-dynamics arm."""
    spike_times = spike_payload.get("spike_times_ms") or {}
    duration_ms = float(spike_payload.get("duration_ms") or 100.0)
    rate = activity_rate_per_node_ms(spike_payload)
    burst = burstiness_cv(spike_times)
    sync = population_sync_index(spike_times, duration_ms=duration_ms)
    endo = endogenous_fraction(spike_payload)
    regime = "passive" if rate < 0.015 else ("bursty" if burst > 1.2 else "active")
    return {
        "activity_rate_per_node_ms": round(rate, 6),
        "burstiness_cv": round(burst, 6),
        "population_sync": round(sync, 6),
        "endogenous_fraction": round(endo, 6),
        "regime_label": regime,
        "n_spikes": int(spike_payload.get("n_spikes") or 0),
    }


def pearson_r(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    """Pearson correlation; None if insufficient variance."""
    n = len(xs)
    if n < 2 or len(ys) != n:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x < 1e-12 or den_y < 1e-12:
        return None
    return num / (den_x * den_y)
