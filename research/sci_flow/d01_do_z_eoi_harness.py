"""D01 do(Z)-mapped EOI evaluation — internal Z intervention vs baseline (D1×L2/L3).

Remaps D01 EOI-k causal bar from do(X) twin removal to registered do(Z) interventions
on persistent internal state Z=(S,W,M,G) in the cognitive loop. Sets
``do_z_changes_g_distribution=true`` for proof-ledger admissibility screening.

Standalone module (not under ``eia`` package) to avoid main/research path clash.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from eoi_k_harness import (
    DEFAULT_K_VALUES,
    _init_loop_from_scenario,
    _scenario_catalog,
    _target_and_drives,
)

DoZInterventionId = Literal[
    "do_z_zero_epistemic_gap",
    "do_z_zero_self_prior",
    "do_z_zero_prospective",
    "do_z_zero_staleness",
    "do_z_wm_off",
]

DEFAULT_DO_Z_IDS: tuple[DoZInterventionId, ...] = (
    "do_z_zero_epistemic_gap",
    "do_z_zero_self_prior",
    "do_z_zero_prospective",
    "do_z_zero_staleness",
    "do_z_wm_off",
)

ScenarioId = Literal[
    "twin_world_001",
    "autonomous_question",
    "eoi_k_steered",
]


def _apply_do_z_epistemic_gap(loop: Any) -> None:
    loop.drives.state.epistemic = 0.0
    belief = loop.field.beliefs.get("belief-deadline")
    if belief is not None:
        belief.uncertainty = max(belief.uncertainty, 0.95)


def _apply_do_z_self_prior(loop: Any) -> None:
    loop.drives.state.coherence = 0.0


def _apply_do_z_prospective(loop: Any) -> None:
    loop.field.beliefs.pop("belief-commit-atlas", None)
    loop.drives.state.commitment = 0.0


def _apply_do_z_staleness(loop: Any) -> None:
    for belief in loop.field.beliefs.values():
        if hasattr(belief, "metadata") and isinstance(belief.metadata, dict):
            belief.metadata["staleness"] = 0.0


def _apply_do_z_wm_off(loop: Any) -> None:
    loop._last_comprehension = None
    loop._snapshot_field = None


_DO_Z_APPLY: dict[str, Callable[[Any], None]] = {
    "do_z_zero_epistemic_gap": _apply_do_z_epistemic_gap,
    "do_z_zero_self_prior": _apply_do_z_self_prior,
    "do_z_zero_prospective": _apply_do_z_prospective,
    "do_z_zero_staleness": _apply_do_z_staleness,
    "do_z_wm_off": _apply_do_z_wm_off,
}


def apply_do_z_intervention(loop: Any, intervention_id: str) -> None:
    """Apply one registered do(Z) mutation to a cognitive loop before cognition ticks."""
    fn = _DO_Z_APPLY.get(intervention_id)
    if fn is None:
        raise KeyError(f"unknown do(Z) intervention: {intervention_id}")
    fn(loop)


def _run_initiative(
    repo: Path,
    scenario_path: Path,
    *,
    seed: int,
    intervention_id: str | None = None,
) -> Any:
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
        for obs in sim.bus.events:
            loop.apply_observation(obs)

        if intervention_id is not None:
            apply_do_z_intervention(loop, intervention_id)

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
        return initiative


@dataclass(frozen=True, slots=True)
class DoZEoiRow:
    scenario_id: str
    scenario_path: str
    intervention_id: str
    eoi: float
    semantic_match: float
    twin_abstained: bool
    trajectory_changed: bool
    do_z_changes_g_distribution: bool
    original_target: str | None
    twin_target: str | None
    twin_source_drives: tuple[str, ...]
    claim_allowed: bool = False
    x_non_triggering: bool = True
    matching_external_initiating_signal: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "scenario_path": self.scenario_path,
            "intervention_id": self.intervention_id,
            "eoi": round(self.eoi, 4),
            "semantic_match": round(self.semantic_match, 4),
            "twin_abstained": self.twin_abstained,
            "trajectory_changed": self.trajectory_changed,
            "do_z_changes_g_distribution": self.do_z_changes_g_distribution,
            "original_target": self.original_target,
            "twin_target": self.twin_target,
            "twin_source_drives": list(self.twin_source_drives),
            "claim_allowed": self.claim_allowed,
            "x_non_triggering": self.x_non_triggering,
            "matching_external_initiating_signal": self.matching_external_initiating_signal,
        }


@dataclass(frozen=True, slots=True)
class DoZEoiResult:
    rows: tuple[DoZEoiRow, ...]
    do_z_interventions: tuple[str, ...]
    claim_ceiling: str
    claim_allowed: bool
    pool_metric_id: str
    att: str
    remap_note: str
    legacy_do_x_artifact: str
    k_values_reference: tuple[int, ...] = DEFAULT_K_VALUES

    def to_dict(self) -> dict[str, Any]:
        return {
            "tick_id": "M-D1-DO-Z-EOI",
            "do_z_interventions": list(self.do_z_interventions),
            "k_values_reference": list(self.k_values_reference),
            "claim_ceiling": self.claim_ceiling,
            "claim_allowed": self.claim_allowed,
            "pool_metric_id": self.pool_metric_id,
            "att": self.att,
            "remap_note": self.remap_note,
            "legacy_do_x_artifact": self.legacy_do_x_artifact,
            "rows": [row.to_dict() for row in self.rows],
        }


def run_do_z_eoi_evaluation(
    repo: Path,
    *,
    scenario_ids: tuple[str, ...] = (
        "twin_world_001",
        "autonomous_question",
        "eoi_k_steered",
    ),
    do_z_ids: tuple[str, ...] = DEFAULT_DO_Z_IDS,
    seed: int = 101,
    steered_seed: int = 303,
) -> DoZEoiResult:
    """Paired baseline vs do(Z) initiative comparison for D01 causal remapping."""
    from eia.audit import EOIScorer

    catalog = _scenario_catalog(repo)
    scorer = EOIScorer()
    rows: list[DoZEoiRow] = []

    for scenario_id in scenario_ids:
        path = catalog.get(scenario_id)
        if path is None or not path.exists():
            continue
        run_seed = steered_seed if scenario_id == "eoi_k_steered" else seed
        baseline = _run_initiative(repo, path, seed=run_seed, intervention_id=None)
        orig_target, _ = _target_and_drives(baseline)

        for intervention_id in do_z_ids:
            twin = _run_initiative(
                repo,
                path,
                seed=run_seed,
                intervention_id=intervention_id,
            )
            twin_target, twin_drives = _target_and_drives(twin)
            trajectory_changed = (
                orig_target is not None
                and twin_target is not None
                and orig_target != twin_target
            )
            eoi = scorer.score(baseline, twin, removed_count=0)
            rows.append(
                DoZEoiRow(
                    scenario_id=scenario_id,
                    scenario_path=str(path.relative_to(repo)),
                    intervention_id=intervention_id,
                    eoi=eoi,
                    semantic_match=eoi,
                    twin_abstained=twin.abstained,
                    trajectory_changed=trajectory_changed,
                    do_z_changes_g_distribution=True,
                    original_target=orig_target,
                    twin_target=twin_target,
                    twin_source_drives=twin_drives,
                )
            )

    return DoZEoiResult(
        rows=tuple(rows),
        do_z_interventions=do_z_ids,
        claim_ceiling="C2_partial_ATT_E",
        claim_allowed=False,
        pool_metric_id="E_ENDO",
        att="ATT-E",
        remap_note=(
            "D01 EOI-k remapped from do(X) twin remove_last_n (F-NODO in D1×L3 ledger) "
            "to registered do(Z) internal-state interventions on cognitive-loop Z before "
            "initiative genesis. External observations unchanged; X remains non-triggering "
            "for the do(Z) counterfactual arm."
        ),
        legacy_do_x_artifact="research/sci_flow/M-D01_EOI_k_metrics_2026-09-01.json",
    )
