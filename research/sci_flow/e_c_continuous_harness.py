"""D1×L2 continuous E_C probe under registered do(Z) from intervention_cube.

Minimal proxy: C_int / (C_int + C_ext) from CF-4 default vs do(Z) intent divergence.
claim_allowed=false — explore only; not C-ladder gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_E_C_SEEDS: tuple[int, ...] = (0, 7, 42)


@dataclass(frozen=True, slots=True)
class ECContinuousRow:
    intervention_id: str
    cf4_condition: str
    seed: int
    default_intent: bool
    z_intent: bool
    c_int: float
    c_ext: float
    e_c: float
    claim_allowed: bool = False


@dataclass(frozen=True, slots=True)
class ECContinuousResult:
    rows: tuple[ECContinuousRow, ...]
    seeds: tuple[int, ...]
    intervention_ids: tuple[str, ...]
    claim_ceiling: str
    claim_allowed: bool
    pool_metric_id: str
    att: str
    note: str

    def to_dict(self) -> dict[str, Any]:
        by_intervention: dict[str, list[float]] = {}
        for row in self.rows:
            by_intervention.setdefault(row.intervention_id, []).append(row.e_c)
        summary = {
            iid: {
                "mean_e_c": round(sum(vals) / len(vals), 4) if vals else 0.0,
                "n": len(vals),
            }
            for iid, vals in sorted(by_intervention.items())
        }
        return {
            "seeds": list(self.seeds),
            "intervention_ids": list(self.intervention_ids),
            "claim_ceiling": self.claim_ceiling,
            "claim_allowed": self.claim_allowed,
            "pool_metric_id": self.pool_metric_id,
            "att": self.att,
            "note": self.note,
            "summary_by_intervention": summary,
            "rows": [
                {
                    "intervention_id": r.intervention_id,
                    "cf4_condition": r.cf4_condition,
                    "seed": r.seed,
                    "default_intent": r.default_intent,
                    "z_intent": r.z_intent,
                    "c_int": round(r.c_int, 4),
                    "c_ext": round(r.c_ext, 4),
                    "e_c": round(r.e_c, 4),
                    "claim_allowed": r.claim_allowed,
                }
                for r in self.rows
            ],
        }


def _c_int_c_ext(default_intent: bool, z_intent: bool) -> tuple[float, float]:
    """Intent divergence proxy for internal vs external causal influence."""
    default_f = 1.0 if default_intent else 0.0
    z_f = 1.0 if z_intent else 0.0
    c_int = abs(default_f - z_f)
    c_ext = max(0.0, 1.0 - default_f)
    return c_int, c_ext


def _e_c_from_components(c_int: float, c_ext: float) -> float:
    denom = c_int + c_ext
    if denom <= 0.0:
        return 0.0
    return c_int / denom


def _load_research_eia_modules() -> tuple[Any, Any, dict[str, Any], str]:
    """Import research-stack ``eia.cf4`` + ``intervention_cube`` without main/research clash."""
    import importlib
    import sys

    root = Path(__file__).resolve().parents[1] / "cursor-starter-v0.2" / "src"
    root_s = str(root)
    stashed = {
        key: sys.modules.pop(key)
        for key in list(sys.modules)
        if key == "eia" or key.startswith("eia.")
    }
    if root_s in sys.path:
        sys.path.remove(root_s)
    sys.path.insert(0, root_s)
    cf4 = importlib.import_module("eia.cf4")
    cube = importlib.import_module("eia.intervention_cube")
    return cf4, cube, stashed, root_s


def _restore_eia_modules(stashed: dict[str, Any], root_s: str) -> None:
    import sys

    for key in list(sys.modules):
        if key == "eia" or key.startswith("eia."):
            del sys.modules[key]
    if root_s in sys.path:
        sys.path.remove(root_s)
    sys.modules.update(stashed)


def run_e_c_continuous_probe(
    *,
    seeds: tuple[int, ...] = DEFAULT_E_C_SEEDS,
    research_src: Path | None = None,
) -> ECContinuousResult:
    """Run minimal continuous E_C under each D1 do(Z) registered in intervention_cube."""
    if research_src is not None:
        import importlib
        import sys

        root_s = str(research_src)
        stashed = {
            key: sys.modules.pop(key)
            for key in list(sys.modules)
            if key == "eia" or key.startswith("eia.")
        }
        if root_s in sys.path:
            sys.path.remove(root_s)
        sys.path.insert(0, root_s)
        try:
            cf4 = importlib.import_module("eia.cf4")
            cube = importlib.import_module("eia.intervention_cube")
            return _run_probe(seeds, cf4, cube)
        finally:
            _restore_eia_modules(stashed, root_s)

    cf4, cube, stashed, root_s = _load_research_eia_modules()
    try:
        return _run_probe(seeds, cf4, cube)
    finally:
        _restore_eia_modules(stashed, root_s)


def _run_probe(seeds: tuple[int, ...], cf4: Any, cube: Any) -> ECContinuousResult:
    run_seed = cf4.run_seed
    Condition = cf4.Condition
    interventions = cube.d1_do_z_interventions()
    rows: list[ECContinuousRow] = []

    for item in interventions:
        condition: Condition = item.cf4_condition  # type: ignore[valid-type]
        for seed in seeds:
            default = run_seed(seed, "default")
            z_run = run_seed(seed, condition)
            c_int, c_ext = _c_int_c_ext(default.intent, z_run.intent)
            rows.append(
                ECContinuousRow(
                    intervention_id=item.id,
                    cf4_condition=condition,
                    seed=seed,
                    default_intent=default.intent,
                    z_intent=z_run.intent,
                    c_int=c_int,
                    c_ext=c_ext,
                    e_c=_e_c_from_components(c_int, c_ext),
                )
            )

    return ECContinuousResult(
        rows=tuple(rows),
        seeds=seeds,
        intervention_ids=tuple(i.id for i in interventions),
        claim_ceiling="C2_partial_ATT_E",
        claim_allowed=False,
        pool_metric_id="E_C",
        att="ATT-E",
        note=(
            "Minimal continuous E_C proxy: |intent_default - intent_do_z| / "
            "(c_int + c_ext) per registered do(Z) from intervention_cube. "
            "CF-4 WoE sim only; theta_E TBD; claim_allowed=false."
        ),
    )
