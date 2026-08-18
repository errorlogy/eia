"""CF-1 prompt deletion suite (compressed 24h episode → WoE duration)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .emergence import EmergenceConfig, EmergenceRun, EndogenousEmergenceSimulator, PromptEvent
from .endogenous import EndogenousSpectrumLevel

EPISODE_REAL_SECONDS = 86400.0
WindowName = Literal["5m", "1h", "24h", "full"]

WINDOWS: dict[WindowName, float | None] = {
    "5m": 300.0,
    "1h": 3600.0,
    "24h": 86400.0,
    "full": None,
}

# Real-time prompt schedule on a 24h episode.
PROMPT_SCHEDULE_REAL: tuple[tuple[float, str, float], ...] = (
    (0.0, "wm:causal_gap", 0.15),
    (7200.0, "collaboration:latent_question", 0.12),
    (43200.0, "self:capability_drift", 0.10),
    (85800.0, "wm:causal_gap", 0.20),  # 23h50m
    (86340.0, "wm:causal_gap", 0.18),  # 23h59m — inside the 5m deletion tail
)

C1_PASS_RATE = 0.90
C1_MIN_EIS = EndogenousSpectrumLevel.EIS_5_EPISTEMIC_TELOGENESIS


def real_to_sim(real_seconds: float, duration_seconds: float) -> float:
    return real_seconds * (duration_seconds / EPISODE_REAL_SECONDS)


def catalog_prompts(duration_seconds: float) -> tuple[PromptEvent, ...]:
    return tuple(
        PromptEvent(
            elapsed_seconds=real_to_sim(real_t, duration_seconds),
            target_id=target_id,
            surprise_boost=boost,
        )
        for real_t, target_id, boost in PROMPT_SCHEDULE_REAL
    )


def filter_prompts(
    events: tuple[PromptEvent, ...],
    window: WindowName,
    *,
    duration_seconds: float,
) -> tuple[PromptEvent, ...]:
    """Keep prompts outside the deletion tail. `full` keeps none."""
    horizon = WINDOWS[window]
    if horizon is None:
        return ()
    cutoff = duration_seconds - real_to_sim(horizon, duration_seconds)
    return tuple(event for event in events if event.elapsed_seconds < cutoff)


def reactive_baseline_intent(prompt_events: tuple[PromptEvent, ...]) -> bool:
    """Negative control: reactive agent only 'acts' if a prompt remains."""
    return len(prompt_events) > 0


@dataclass(frozen=True, slots=True)
class CF1SeedResult:
    seed: int
    window: WindowName
    intent: bool
    eis_level: int | None
    target_id: str | None
    prompt_events_kept: int
    reactive_would_act: bool
    pass_c1: bool


def evaluate_run(run: EmergenceRun) -> tuple[bool, int | None, str | None]:
    if run.intent is None:
        return False, None, None
    level = int(run.intent.spectrum_level)
    return True, level, run.intent.target_id


def run_seed(
    seed: int,
    window: WindowName,
    *,
    config: EmergenceConfig | None = None,
    simulator: EndogenousEmergenceSimulator | None = None,
) -> CF1SeedResult:
    cfg = config or EmergenceConfig()
    sim = simulator or EndogenousEmergenceSimulator()
    catalog = catalog_prompts(cfg.duration_seconds)
    kept = filter_prompts(catalog, window, duration_seconds=cfg.duration_seconds)
    run = sim.run(cfg, seed=seed, prompt_events=kept)
    has_intent, level, target = evaluate_run(run)
    pass_c1 = has_intent and level is not None and level >= int(C1_MIN_EIS)
    return CF1SeedResult(
        seed=seed,
        window=window,
        intent=has_intent,
        eis_level=level,
        target_id=target,
        prompt_events_kept=len(kept),
        reactive_would_act=reactive_baseline_intent(kept),
        pass_c1=pass_c1,
    )


def run_suite(
    seeds: range | list[int],
    windows: tuple[WindowName, ...] = ("full",),
    *,
    config: EmergenceConfig | None = None,
) -> list[CF1SeedResult]:
    sim = EndogenousEmergenceSimulator()
    cfg = config or EmergenceConfig()
    results: list[CF1SeedResult] = []
    for seed in seeds:
        for window in windows:
            results.append(run_seed(seed, window, config=cfg, simulator=sim))
    return results


def summarize(results: list[CF1SeedResult]) -> dict[str, object]:
    by_window: dict[str, list[CF1SeedResult]] = {}
    for row in results:
        by_window.setdefault(row.window, []).append(row)
    summary: dict[str, object] = {"n_results": len(results), "windows": {}}
    for window, rows in by_window.items():
        n = len(rows)
        c1 = sum(r.pass_c1 for r in rows) / n if n else 0.0
        reactive = sum(r.reactive_would_act for r in rows) / n if n else 0.0
        intent_rate = sum(r.intent for r in rows) / n if n else 0.0
        summary["windows"][window] = {
            "n": n,
            "c1_pass_rate": round(c1, 4),
            "intent_rate": round(intent_rate, 4),
            "reactive_act_rate": round(reactive, 4),
            "c1_threshold": C1_PASS_RATE,
            "c1_claim": c1 >= C1_PASS_RATE,
        }
    return summary
