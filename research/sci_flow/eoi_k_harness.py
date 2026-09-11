"""D01 EOI-k window sweep — twin remove_last_n robustness (D1×L2).

Standalone harness module (not under ``eia`` package) to avoid main/research path clash.

Uses **counterfactual replay**: twin runs exclude the last *k* user observations from
belief updates (main ``run_twin`` snapshot path is documented as legacy/MVP-0).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

DEFAULT_K_VALUES: tuple[int, ...] = (1, 5, 20)
DEFAULT_BATCH_SEEDS: tuple[int, ...] = (0, 7, 42)

ScenarioId = Literal[
    "twin_world_001",
    "autonomous_question",
    "eoi_k_steered",
]

TraceMode = Literal["twin_counterfactual", "shadow_carryover"]


@dataclass(frozen=True, slots=True)
class EoiKRow:
    scenario_id: str
    scenario_path: str
    k: int
    eoi: float
    semantic_match: float
    twin_abstained: bool
    removed_user_events: int
    intervention_id: str
    claim_allowed: bool = False
    trace_mode: TraceMode = "twin_counterfactual"
    original_target: str | None = None
    twin_target: str | None = None
    twin_source_drives: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CarryoverEoiRow:
    """Shadow carryover path — no user prompts; orthogonal D1×L2 carryover witness."""

    session_ticks: int
    carryover_episodes: int
    drive_norm_min: float
    drive_norm_final: float
    trace_mode: TraceMode
    claim_allowed: bool = False
    note: str = ""


@dataclass(frozen=True, slots=True)
class EoiKSweepResult:
    rows: tuple[EoiKRow, ...]
    k_values: tuple[int, ...]
    claim_ceiling: str
    claim_allowed: bool
    pool_metric_id: str
    att: str
    carryover_note: str
    carryover: CarryoverEoiRow | None = None
    counterfactual_replay: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "k_values": list(self.k_values),
            "claim_ceiling": self.claim_ceiling,
            "claim_allowed": self.claim_allowed,
            "pool_metric_id": self.pool_metric_id,
            "att": self.att,
            "carryover_note": self.carryover_note,
            "counterfactual_replay": self.counterfactual_replay,
            "rows": [
                {
                    "scenario_id": r.scenario_id,
                    "scenario_path": r.scenario_path,
                    "k": r.k,
                    "eoi": round(r.eoi, 4),
                    "semantic_match": round(r.semantic_match, 4),
                    "twin_abstained": r.twin_abstained,
                    "removed_user_events": r.removed_user_events,
                    "intervention_id": r.intervention_id,
                    "claim_allowed": r.claim_allowed,
                    "trace_mode": r.trace_mode,
                    "original_target": r.original_target,
                    "twin_target": r.twin_target,
                    "twin_source_drives": list(r.twin_source_drives),
                }
                for r in self.rows
            ],
        }
        if self.carryover is not None:
            payload["carryover"] = {
                "session_ticks": self.carryover.session_ticks,
                "carryover_episodes": self.carryover.carryover_episodes,
                "drive_norm_min": round(self.carryover.drive_norm_min, 4),
                "drive_norm_final": round(self.carryover.drive_norm_final, 4),
                "trace_mode": self.carryover.trace_mode,
                "claim_allowed": self.carryover.claim_allowed,
                "note": self.carryover.note,
            }
        return payload


def _scenario_catalog(repo: Path) -> dict[str, Path]:
    return {
        "twin_world_001": repo / "scenarios" / "twin_world_001.yaml",
        "autonomous_question": repo / "scenarios" / "autonomous_question.yaml",
        "eoi_k_steered": repo / "scenarios" / "eoi_k_steered.yaml",
    }


def _intervention_id_for_k(k: int) -> str:
    return f"do_x_remove_last_user_k{k}"


def _init_loop_from_scenario(loop: Any, scenario: Any) -> None:
    from eia.schemas.belief import BeliefKind

    for spec in scenario.initial_beliefs:
        loop.field.upsert_belief(
            spec["id"],
            kind=BeliefKind(spec.get("kind", "categorical")),
            subject=spec["subject"],
            claim=spec["claim"],
            distribution=spec.get("distribution"),
            uncertainty=spec.get("uncertainty", 0.5),
            metadata=spec.get("metadata", {}),
        )
    for contra in scenario.metadata.get("contradictions", []):
        loop.field.register_contradiction(contra[0], contra[1], contra[2])


def _run_counterfactual_initiative(
    repo: Path,
    scenario_path: Path,
    *,
    seed: int,
    exclude_user_tail: int,
) -> tuple[Any, list[Any]]:
    """Replay scenario applying all observations except the last *k* user triggers."""
    from eia.audit.twin_policy import TwinInterventionPolicy, apply_twin_intervention
    from eia.experiment.baseline import BaselineCondition, cognition_tick_count
    from eia.ids import seeded_context
    from eia.pipeline import CognitiveLoop
    from eia.simulator import Simulator, load_scenario

    scenario = load_scenario(scenario_path)
    with seeded_context(seed):
        sim = Simulator(scenario, seed=seed)
        loop = CognitiveLoop(seed=seed)
        _init_loop_from_scenario(loop, scenario)

        max_tick = max((e.tick for e in scenario.events), default=10)
        sim.run_until(max_tick)
        all_obs = list(sim.bus.events)
        if exclude_user_tail > 0:
            remaining, removed = apply_twin_intervention(
                all_obs,
                TwinInterventionPolicy.REMOVE_LAST_USER_EVENT,
                remove_last_n=exclude_user_tail,
            )
        else:
            remaining, removed = all_obs, []

        for obs in remaining:
            loop.apply_observation(obs)

        sim.advance_quiet_period(ticks=4)
        tick_count = cognition_tick_count(BaselineCondition.FULL_EIA)
        initiative = None
        for i in range(tick_count):
            _, initiative, _, _ = loop.tick_cognition(
                tick=sim.clock.tick + i,
                hour=sim.clock.hour,
                finalize=(i == tick_count - 1),
            )
        if initiative is None:
            raise RuntimeError(f"no initiative for {scenario_path}")
        return initiative, removed


def _target_and_drives(initiative: Any) -> tuple[str | None, tuple[str, ...]]:
    if initiative.abstained or initiative.candidate is None:
        return None, ()
    cand = initiative.candidate
    drives = tuple(d.value for d in cand.source_drives)
    return cand.target_belief_id, drives


def run_carryover_witness(*, seed: int = 0, session_ticks: int = 8) -> CarryoverEoiRow:
    """Short shadow carryover session — live/daemon path witness (no user EOI-k)."""
    from eia.runtime.shadow_multitick import (
        ShadowArm,
        drive_norm,
        run_shadow_carryover_tick,
        run_shadow_episode,
    )

    bootstrap = run_shadow_episode(arm=ShadowArm.CLOSED_LOOP, seed=seed)
    if bootstrap.carryover is None:
        raise RuntimeError("shadow bootstrap missing carryover export")

    carryover = bootstrap.carryover
    norms = [drive_norm(carryover)]
    episodes = 0
    while carryover.session_tick < session_ticks:
        episodes += 1
        ep = run_shadow_carryover_tick(carryover, seed=seed + episodes)
        if ep.carryover is None:
            break
        carryover = ep.carryover
        norms.append(drive_norm(carryover))

    return CarryoverEoiRow(
        session_ticks=carryover.session_tick,
        carryover_episodes=episodes,
        drive_norm_min=min(norms) if norms else 0.0,
        drive_norm_final=norms[-1] if norms else 0.0,
        trace_mode="shadow_carryover",
        claim_allowed=False,
        note=(
            "Phase-2 shadow carryover (no user prompts); EOI-k twin applies to "
            "user-initiated scenarios only. Orthogonal D2×L2 DSR evidence in M-E04."
        ),
    )


def run_eoi_k_sweep(
    repo: Path,
    *,
    k_values: tuple[int, ...] = DEFAULT_K_VALUES,
    scenario_ids: tuple[str, ...] = (
        "twin_world_001",
        "autonomous_question",
        "eoi_k_steered",
    ),
    seed: int = 101,
    traces_dir: Path | None = None,
    include_carryover: bool = True,
    steered_seed: int = 303,
) -> EoiKSweepResult:
    """Run EOI-k sweep with counterfactual replay (requires main ``eia`` on sys.path)."""
    from eia.audit import EOIScorer

    catalog = _scenario_catalog(repo)
    out_traces = traces_dir or (repo / "traces" / "eoi_k")
    out_traces.mkdir(parents=True, exist_ok=True)

    scorer = EOIScorer()
    rows: list[EoiKRow] = []

    for scenario_id in scenario_ids:
        path = catalog.get(scenario_id)
        if path is None or not path.exists():
            continue
        run_seed = steered_seed if scenario_id == "eoi_k_steered" else seed
        original, _ = _run_counterfactual_initiative(
            repo, path, seed=run_seed, exclude_user_tail=0
        )
        orig_target, _ = _target_and_drives(original)

        for k in k_values:
            twin, removed = _run_counterfactual_initiative(
                repo, path, seed=run_seed, exclude_user_tail=k
            )
            eoi = scorer.score(original, twin, removed_count=len(removed))
            twin_target, twin_drives = _target_and_drives(twin)
            rows.append(
                EoiKRow(
                    scenario_id=scenario_id,
                    scenario_path=str(path.relative_to(repo)),
                    k=k,
                    eoi=eoi,
                    semantic_match=eoi,
                    twin_abstained=twin.abstained,
                    removed_user_events=len(removed),
                    intervention_id=_intervention_id_for_k(k),
                    trace_mode="twin_counterfactual",
                    original_target=orig_target,
                    twin_target=twin_target,
                    twin_source_drives=twin_drives,
                )
            )

    carryover = run_carryover_witness(seed=seed) if include_carryover else None

    return EoiKSweepResult(
        rows=tuple(rows),
        k_values=k_values,
        claim_ceiling="C2_partial_ATT_E",
        claim_allowed=False,
        pool_metric_id="E_ENDO",
        att="ATT-E",
        carryover_note=(
            "Twin EOI-k uses counterfactual replay (exclude last k user observations). "
            "Shadow carryover path has zero user prompts; see carryover block for "
            "session witness. Carryover DSR (M-E04) is orthogonal D2×L2 evidence."
        ),
        carryover=carryover,
        counterfactual_replay=True,
    )


@dataclass(frozen=True, slots=True)
class EoiKBatchRun:
    seed: int
    result: EoiKSweepResult


@dataclass(frozen=True, slots=True)
class EoiKBatchResult:
    seeds: tuple[int, ...]
    scenario_ids: tuple[str, ...]
    k_values: tuple[int, ...]
    runs: tuple[EoiKBatchRun, ...]
    claim_ceiling: str
    claim_allowed: bool
    pool_metric_id: str
    att: str

    def to_dict(self) -> dict[str, Any]:
        steered_summary: dict[str, dict[str, float]] = {}
        for run in self.runs:
            steered = [r for r in run.result.rows if r.scenario_id == "eoi_k_steered"]
            for row in steered:
                steered_summary.setdefault(str(run.seed), {})[str(row.k)] = round(
                    row.eoi, 4
                )

        return {
            "seeds": list(self.seeds),
            "scenario_ids": list(self.scenario_ids),
            "k_values": list(self.k_values),
            "claim_ceiling": self.claim_ceiling,
            "claim_allowed": self.claim_allowed,
            "pool_metric_id": self.pool_metric_id,
            "att": self.att,
            "steered_eoi_by_seed": steered_summary,
            "runs": [
                {"seed": run.seed, "sweep": run.result.to_dict()} for run in self.runs
            ],
        }


def run_eoi_k_batch(
    repo: Path,
    *,
    seeds: tuple[int, ...] = DEFAULT_BATCH_SEEDS,
    k_values: tuple[int, ...] = DEFAULT_K_VALUES,
    scenario_ids: tuple[str, ...] = (
        "twin_world_001",
        "autonomous_question",
        "eoi_k_steered",
    ),
    include_carryover: bool = False,
) -> EoiKBatchResult:
    """Multi-seed EOI-k batch — one sweep per seed (steered uses same seed)."""
    runs: list[EoiKBatchRun] = []
    for seed in seeds:
        sweep = run_eoi_k_sweep(
            repo,
            k_values=k_values,
            scenario_ids=scenario_ids,
            seed=seed,
            steered_seed=seed,
            include_carryover=include_carryover,
        )
        runs.append(EoiKBatchRun(seed=seed, result=sweep))

    return EoiKBatchResult(
        seeds=seeds,
        scenario_ids=scenario_ids,
        k_values=k_values,
        runs=tuple(runs),
        claim_ceiling="C2_partial_ATT_E",
        claim_allowed=False,
        pool_metric_id="E_ENDO",
        att="ATT-E",
    )
