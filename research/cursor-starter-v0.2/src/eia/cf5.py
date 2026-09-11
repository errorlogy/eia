"""CF-5 / M-D Kuramoto coupling, scramble, K=0, delay, and graph suite."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .coherence import (
    CoherenceConfig,
    k_zero_config,
    permute_graph,
    sparse_typed_graph,
)
from .emergence import EmergenceConfig, EndogenousEmergenceSimulator

Condition = Literal["coupled", "scramble", "k0", "sparse", "delay_32", "delay_128", "permuted"]

C2_COUPLED_MIN = 0.85
C2_SCRAMBLE_MAX = 0.20
C2_K0_MAX = 0.40
C2_DELTA_MIN = 0.50


@dataclass(frozen=True, slots=True)
class CF5SeedResult:
    seed: int
    condition: Condition
    intent: bool
    peak_coherence: float
    time_to_intent: float | None


def coherence_for(condition: Condition, *, hz: float = 42.0) -> CoherenceConfig:
    if condition == "k0":
        return k_zero_config(nominal_frequency_hz=hz)
    if condition == "sparse":
        return CoherenceConfig(nominal_frequency_hz=hz, coupling_graph=sparse_typed_graph())
    if condition == "delay_32":
        return CoherenceConfig(nominal_frequency_hz=hz, delay_steps=32)
    if condition == "delay_128":
        return CoherenceConfig(nominal_frequency_hz=hz, delay_steps=128)
    if condition == "permuted":
        return CoherenceConfig(
            nominal_frequency_hz=hz,
            coupling_graph=permute_graph(sparse_typed_graph(), seed=19),
        )
    return CoherenceConfig(nominal_frequency_hz=hz)


def run_seed(
    seed: int,
    condition: Condition,
    *,
    config: EmergenceConfig | None = None,
    simulator: EndogenousEmergenceSimulator | None = None,
) -> CF5SeedResult:
    cfg = config or EmergenceConfig()
    sim = simulator or EndogenousEmergenceSimulator()
    run = sim.run(
        cfg,
        seed=seed,
        scramble_phases=condition == "scramble",
        coherence_config=coherence_for(condition, hz=cfg.nominal_frequency_hz),
    )
    tti = run.intent.emerged_at_seconds if run.intent is not None else None
    return CF5SeedResult(
        seed=seed,
        condition=condition,
        intent=run.intent is not None,
        peak_coherence=run.peak_coherence,
        time_to_intent=tti,
    )


def run_suite(
    seeds: range | list[int],
    conditions: tuple[Condition, ...] = ("coupled", "scramble", "k0"),
    *,
    config: EmergenceConfig | None = None,
) -> list[CF5SeedResult]:
    sim = EndogenousEmergenceSimulator()
    cfg = config or EmergenceConfig()
    results: list[CF5SeedResult] = []
    for seed in seeds:
        for condition in conditions:
            results.append(run_seed(seed, condition, config=cfg, simulator=sim))
    return results


def summarize(results: list[CF5SeedResult]) -> dict[str, object]:
    by: dict[str, list[CF5SeedResult]] = {}
    for row in results:
        by.setdefault(row.condition, []).append(row)
    windows: dict[str, object] = {}
    for condition, rows in by.items():
        n = len(rows)
        intent_rate = sum(r.intent for r in rows) / n if n else 0.0
        mean_r = sum(r.peak_coherence for r in rows) / n if n else 0.0
        windows[condition] = {
            "n": n,
            "intent_rate": round(intent_rate, 4),
            "mean_peak_R": round(mean_r, 4),
        }
    coupled = windows.get("coupled", {}).get("intent_rate") if "coupled" in windows else None
    scramble = windows.get("scramble", {}).get("intent_rate") if "scramble" in windows else None
    k0 = windows.get("k0", {}).get("intent_rate") if "k0" in windows else None
    c2 = False
    if coupled is not None and scramble is not None and k0 is not None:
        c2 = (
            coupled >= C2_COUPLED_MIN
            and scramble <= C2_SCRAMBLE_MAX
            and k0 <= C2_K0_MAX
            and (coupled - scramble) >= C2_DELTA_MIN
        )
    return {
        "n_results": len(results),
        "conditions": windows,
        "c2_thresholds": {
            "coupled_min": C2_COUPLED_MIN,
            "scramble_max": C2_SCRAMBLE_MAX,
            "k0_max": C2_K0_MAX,
            "delta_min": C2_DELTA_MIN,
        },
        "c2_claim": c2,
    }
