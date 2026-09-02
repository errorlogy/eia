"""E04 part 2 — EOI drift on 50-tick shadow carryover session (D2×L2).

Measures longitudinal stability of initiative fingerprint vs bootstrap baseline
using main ``EOIScorer`` structural match. No user prompts; no twin intervention
(``removed_count=0``). Orthogonal to D01 twin EOI-k (user counterfactual replay).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

EOI_ENDOGENOUS_THRESHOLD = 0.50
EOI_DRIFT_TARGET_COGNITIVE_TICKS = 50

TraceMode = Literal["shadow_carryover_longitudinal"]


@dataclass(frozen=True, slots=True)
class EoiDriftRow:
    cognitive_tick: int
    eoi: float
    semantic_match: float
    abstained: bool
    target_belief_id: str | None
    kind: str | None
    source_drives: tuple[str, ...]
    initiative_id: str
    claim_allowed: bool = False
    trace_mode: TraceMode = "shadow_carryover_longitudinal"


@dataclass(frozen=True, slots=True)
class EoiDriftSessionResult:
    rows: tuple[EoiDriftRow, ...]
    target_cognitive_ticks: int
    cognitive_ticks_reached: int
    carryover_episodes: int
    n_initiative_samples: int
    eoi_min: float
    eoi_max: float
    eoi_mean: float
    eoi_drift_span: float
    persistence_fraction: float
    baseline_target: str | None
    baseline_kind: str | None
    eoi_pass: bool
    e04_pass: bool
    claim_ceiling: str
    claim_allowed: bool
    pool_metric_id: str
    att: str
    trace_mode: TraceMode

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_cognitive_ticks": self.target_cognitive_ticks,
            "cognitive_ticks_reached": self.cognitive_ticks_reached,
            "carryover_episodes": self.carryover_episodes,
            "n_initiative_samples": self.n_initiative_samples,
            "eoi_min": round(self.eoi_min, 4),
            "eoi_max": round(self.eoi_max, 4),
            "eoi_mean": round(self.eoi_mean, 4),
            "eoi_drift_span": round(self.eoi_drift_span, 4),
            "persistence_fraction": round(self.persistence_fraction, 4),
            "eoi_endogenous_threshold": EOI_ENDOGENOUS_THRESHOLD,
            "baseline_target": self.baseline_target,
            "baseline_kind": self.baseline_kind,
            "eoi_pass": self.eoi_pass,
            "e04_pass": self.e04_pass,
            "claim_ceiling": self.claim_ceiling,
            "claim_allowed": self.claim_allowed,
            "pool_metric_id": self.pool_metric_id,
            "att": self.att,
            "trace_mode": self.trace_mode,
            "rows": [
                {
                    "cognitive_tick": r.cognitive_tick,
                    "eoi": round(r.eoi, 4),
                    "semantic_match": round(r.semantic_match, 4),
                    "abstained": r.abstained,
                    "target_belief_id": r.target_belief_id,
                    "kind": r.kind,
                    "source_drives": list(r.source_drives),
                    "initiative_id": r.initiative_id,
                    "claim_allowed": r.claim_allowed,
                    "trace_mode": r.trace_mode,
                }
                for r in self.rows
            ],
        }


def _initiative_from_sample(sample: dict[str, Any]) -> Any:
    from eia.schemas.initiative import Initiative

    return Initiative.model_validate(sample["initiative"])


def run_eoi_drift_longitudinal_session(
    *,
    target_cognitive_ticks: int = EOI_DRIFT_TARGET_COGNITIVE_TICKS,
    seed: int = 0,
    eoi_threshold: float = EOI_ENDOGENOUS_THRESHOLD,
) -> EoiDriftSessionResult:
    """50-tick shadow carryover session with per-tick EOI vs bootstrap baseline."""
    from eia.audit import EOIScorer
    from eia.runtime.shadow_multitick import (
        ShadowArm,
        run_shadow_carryover_tick,
        run_shadow_episode,
    )

    bootstrap = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=seed)
    if bootstrap.carryover is None:
        raise RuntimeError("closed_loop bootstrap did not export carryover")
    if not bootstrap.initiative_samples:
        raise RuntimeError("closed_loop bootstrap did not export initiative samples")

    all_samples: list[dict[str, Any]] = list(bootstrap.initiative_samples)
    carryover = bootstrap.carryover
    carryover_episodes = 0

    while carryover.session_tick < target_cognitive_ticks:
        carryover_episodes += 1
        ep = run_shadow_carryover_tick(carryover, seed=seed + carryover_episodes)
        if ep.carryover is None:
            break
        all_samples.extend(ep.initiative_samples)
        carryover = ep.carryover

    scorer = EOIScorer(threshold=eoi_threshold)
    baseline = _initiative_from_sample(all_samples[0])
    baseline_target = all_samples[0]["target_belief_id"]
    baseline_kind = all_samples[0]["kind"]

    rows: list[EoiDriftRow] = []
    eoi_values: list[float] = []

    for sample in all_samples:
        initiative = _initiative_from_sample(sample)
        eoi = scorer.score(baseline, initiative, removed_count=0)
        eoi_values.append(eoi)
        rows.append(
            EoiDriftRow(
                cognitive_tick=sample["cognitive_tick"],
                eoi=eoi,
                semantic_match=eoi,
                abstained=sample["abstained"],
                target_belief_id=sample["target_belief_id"],
                kind=sample["kind"],
                source_drives=tuple(sample["source_drives"]),
                initiative_id=sample["initiative_id"],
            )
        )

    n = len(eoi_values)
    eoi_min = min(eoi_values) if n else 0.0
    eoi_max = max(eoi_values) if n else 0.0
    eoi_mean = sum(eoi_values) / n if n else 0.0
    persistence_fraction = (
        sum(1 for v in eoi_values if v >= eoi_threshold) / n if n else 0.0
    )
    e04_pass = carryover.session_tick >= target_cognitive_ticks
    eoi_pass = (
        e04_pass
        and persistence_fraction >= 1.0
        and eoi_min >= eoi_threshold
        and n >= target_cognitive_ticks
    )

    return EoiDriftSessionResult(
        rows=tuple(rows),
        target_cognitive_ticks=target_cognitive_ticks,
        cognitive_ticks_reached=carryover.session_tick,
        carryover_episodes=carryover_episodes,
        n_initiative_samples=n,
        eoi_min=eoi_min,
        eoi_max=eoi_max,
        eoi_mean=eoi_mean,
        eoi_drift_span=eoi_max - eoi_min,
        persistence_fraction=persistence_fraction,
        baseline_target=baseline_target,
        baseline_kind=baseline_kind,
        eoi_pass=eoi_pass,
        e04_pass=e04_pass,
        claim_ceiling="C2_partial_ATT_E",
        claim_allowed=False,
        pool_metric_id="E_ENDO",
        att="ATT-E",
        trace_mode="shadow_carryover_longitudinal",
    )
