"""D01 EOI-k window sweep — twin remove_last_n robustness (D1×L2).

Standalone harness module (not under ``eia`` package) to avoid main/research path clash.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

DEFAULT_K_VALUES: tuple[int, ...] = (1, 5, 20)

ScenarioId = Literal["twin_world_001", "autonomous_question"]


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


@dataclass(frozen=True, slots=True)
class EoiKSweepResult:
    rows: tuple[EoiKRow, ...]
    k_values: tuple[int, ...]
    claim_ceiling: str
    claim_allowed: bool
    pool_metric_id: str
    att: str
    carryover_note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "k_values": list(self.k_values),
            "claim_ceiling": self.claim_ceiling,
            "claim_allowed": self.claim_allowed,
            "pool_metric_id": self.pool_metric_id,
            "att": self.att,
            "carryover_note": self.carryover_note,
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
                }
                for r in self.rows
            ],
        }


def _scenario_catalog(repo: Path) -> dict[str, Path]:
    return {
        "twin_world_001": repo / "scenarios" / "twin_world_001.yaml",
        "autonomous_question": repo / "scenarios" / "autonomous_question.yaml",
    }


def _intervention_id_for_k(k: int) -> str:
    return f"do_x_remove_last_user_k{k}"


def run_eoi_k_sweep(
    repo: Path,
    *,
    k_values: tuple[int, ...] = DEFAULT_K_VALUES,
    scenario_ids: tuple[str, ...] = ("twin_world_001", "autonomous_question"),
    seed: int = 101,
    traces_dir: Path | None = None,
) -> EoiKSweepResult:
    """Run EOI-k sweep on main pipeline scenarios (requires main ``eia`` on sys.path)."""
    from eia.audit import TwinInterventionPolicy
    from eia.pipeline import run_scenario

    catalog = _scenario_catalog(repo)
    out_traces = traces_dir or (repo / "traces" / "eoi_k")
    out_traces.mkdir(parents=True, exist_ok=True)

    rows: list[EoiKRow] = []
    for scenario_id in scenario_ids:
        path = catalog.get(scenario_id)
        if path is None or not path.exists():
            continue
        for k in k_values:
            intervention_id = _intervention_id_for_k(k)
            result = run_scenario(
                path,
                traces_dir=out_traces / scenario_id / f"k{k}",
                seed=seed,
                twin_policy=TwinInterventionPolicy.REMOVE_LAST_USER_EVENT,
                twin_remove_last_n=k,
            )
            twin = result["twin_result"]
            rows.append(
                EoiKRow(
                    scenario_id=scenario_id,
                    scenario_path=str(path.relative_to(repo)),
                    k=k,
                    eoi=twin.eoi,
                    semantic_match=twin.semantic_match,
                    twin_abstained=twin.abstained_in_twin,
                    removed_user_events=len(twin.removed_user_event_ids),
                    intervention_id=intervention_id,
                )
            )

    return EoiKSweepResult(
        rows=tuple(rows),
        k_values=k_values,
        claim_ceiling="C2_partial_ATT_E",
        claim_allowed=False,
        pool_metric_id="E_ENDO",
        att="ATT-E",
        carryover_note=(
            "Shadow carryover path has zero user prompts; EOI-k applies to twin scenarios "
            "with user-initiated events. Carryover DSR (M-E04) is orthogonal D2×L2 evidence."
        ),
    )
