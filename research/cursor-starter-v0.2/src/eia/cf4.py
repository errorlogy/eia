"""CF-4 internal-state reset suite (C2 path after CF-5 Kuramoto unsupported)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .emergence import EmergenceConfig, EndogenousEmergenceSimulator, InternalReset

Condition = Literal[
    "default",
    "zero_epistemic_gap",
    "zero_self_prior",
    "zero_prospective",
    "zero_staleness",
    "wm_off",
]

NAMED_FACTORS: tuple[Condition, ...] = (
    "zero_epistemic_gap",
    "zero_self_prior",
    "zero_prospective",
    "zero_staleness",
)

# Pre-registered C2 gates (population rates, n=100).
C2_DEFAULT_MIN = 0.85
C2_FACTOR_MAX = 0.40
C2_WM_OFF_MAX = 0.05


@dataclass(frozen=True, slots=True)
class CF4SeedResult:
    seed: int
    condition: Condition
    intent: bool
    peak_coherence: float
    peak_potential: float
    time_to_intent: float | None


def reset_for(condition: Condition) -> InternalReset:
    if condition == "zero_epistemic_gap":
        return InternalReset(zero_epistemic_gap=True)
    if condition == "zero_self_prior":
        return InternalReset(zero_self_prior=True)
    if condition == "zero_prospective":
        return InternalReset(zero_prospective=True)
    if condition == "zero_staleness":
        return InternalReset(zero_staleness=True)
    return InternalReset()


def run_seed(
    seed: int,
    condition: Condition,
    *,
    config: EmergenceConfig | None = None,
    simulator: EndogenousEmergenceSimulator | None = None,
) -> CF4SeedResult:
    cfg = config or EmergenceConfig()
    sim = simulator or EndogenousEmergenceSimulator()
    world_model_enabled = condition != "wm_off"
    run = sim.run(
        cfg,
        seed=seed,
        world_model_enabled=world_model_enabled,
        internal_reset=reset_for(condition),
    )
    tti = run.intent.emerged_at_seconds if run.intent is not None else None
    return CF4SeedResult(
        seed=seed,
        condition=condition,
        intent=run.intent is not None,
        peak_coherence=run.peak_coherence,
        peak_potential=run.peak_potential,
        time_to_intent=tti,
    )


def run_suite(
    seeds: range | list[int],
    conditions: tuple[Condition, ...] = (
        "default",
        "zero_epistemic_gap",
        "zero_self_prior",
        "zero_prospective",
        "zero_staleness",
        "wm_off",
    ),
    *,
    config: EmergenceConfig | None = None,
) -> list[CF4SeedResult]:
    sim = EndogenousEmergenceSimulator()
    cfg = config or EmergenceConfig()
    results: list[CF4SeedResult] = []
    for seed in seeds:
        for condition in conditions:
            results.append(run_seed(seed, condition, config=cfg, simulator=sim))
    return results


def summarize(results: list[CF4SeedResult]) -> dict[str, object]:
    by: dict[str, list[CF4SeedResult]] = {}
    for row in results:
        by.setdefault(row.condition, []).append(row)
    windows: dict[str, object] = {}
    for condition, rows in by.items():
        n = len(rows)
        intent_rate = sum(r.intent for r in rows) / n if n else 0.0
        mean_r = sum(r.peak_coherence for r in rows) / n if n else 0.0
        mean_p = sum(r.peak_potential for r in rows) / n if n else 0.0
        windows[condition] = {
            "n": n,
            "intent_rate": round(intent_rate, 4),
            "mean_peak_R": round(mean_r, 4),
            "mean_peak_potential": round(mean_p, 4),
        }

    default_rate = (
        windows["default"]["intent_rate"] if "default" in windows else None  # type: ignore[index]
    )
    wm_off_rate = windows["wm_off"]["intent_rate"] if "wm_off" in windows else None  # type: ignore[index]

    suppressing: list[str] = []
    if default_rate is not None:
        for factor in NAMED_FACTORS:
            if factor not in windows:
                continue
            rate = windows[factor]["intent_rate"]  # type: ignore[index]
            if rate <= C2_FACTOR_MAX:
                suppressing.append(factor)

    wm_ok = wm_off_rate is not None and wm_off_rate <= C2_WM_OFF_MAX
    c2 = (
        default_rate is not None
        and default_rate >= C2_DEFAULT_MIN
        and len(suppressing) > 0
        and wm_ok
    )
    # If only wm_off suppresses, do not claim C2 (global off ≠ named factor causation).
    only_global = (
        default_rate is not None
        and default_rate >= C2_DEFAULT_MIN
        and len(suppressing) == 0
        and wm_ok
    )
    return {
        "n_results": len(results),
        "conditions": windows,
        "c2_thresholds": {
            "default_min": C2_DEFAULT_MIN,
            "named_factor_max": C2_FACTOR_MAX,
            "wm_off_max": C2_WM_OFF_MAX,
        },
        "suppressing_named_factors": suppressing,
        "only_wm_off_suppresses": only_global,
        "c2_claim": c2,
    }
