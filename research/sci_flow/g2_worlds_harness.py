"""M-G2-E01 partial multi-world eval — twin worlds with ATT-E metrics (D1×L2).

Batch eval across MVP-0 twin worlds (+ auxiliary scenarios). Honest partial
scope: single ops/Atlas domain, not full E01 20×3. claim_allowed=false.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

BaselineName = Literal["reactive_only", "full_eia"]

DEFAULT_BASELINES: tuple[BaselineName, ...] = ("reactive_only", "full_eia")

# E01 target is 20×3 domains; partial batch uses all registered MVP-0 worlds.
DEFAULT_WORLD_PATTERNS: tuple[str, ...] = (
    "scenarios/twin_world_001.yaml",
    "evals/twin_world_*.yaml",
    "scenarios/autonomous_question.yaml",
    "scenarios/eoi_k_steered.yaml",
)

DOMAIN_BY_PREFIX: dict[str, str] = {
    "twin_world": "ops_atlas",
    "autonomous_question": "ops_atlas",
    "eoi_k_steered": "ops_atlas",
}

E01_TARGET_WORLDS = 20
E01_TARGET_DOMAINS = 3


@dataclass(frozen=True, slots=True)
class WorldAttRow:
    world_id: str
    domain: str
    scenario_path: str
    seed: int
    baseline: BaselineName
    eoi: float
    semantic_match: float
    euir_proxy: bool
    initiative_class: str
    precision_hit: bool | None
    contact_outcome: str
    initiative_abstained: bool
    att: str = "ATT-E"
    pool_metric_id: str = "E_ENDO"
    claim_allowed: bool = False


@dataclass(frozen=True, slots=True)
class BaselineAggregate:
    baseline: BaselineName
    world_count: int
    mean_eoi: float
    euir_proxy_rate: float
    initiative_precision: float | None
    precision_hits: int
    precision_scored: int
    endogenous_count: int


@dataclass(frozen=True, slots=True)
class G2WorldsEvalResult:
    rows: tuple[WorldAttRow, ...]
    baselines: tuple[BaselineName, ...]
    aggregates: tuple[BaselineAggregate, ...]
    world_count: int
    domain_count: int
    e01_scope_fraction: str
    claim_ceiling: str
    claim_allowed: bool
    att: str
    pool_metric_id: str
    hermes_task: str
    cube_cell: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "hermes_task": self.hermes_task,
            "cube_cell": self.cube_cell,
            "claim_ceiling": self.claim_ceiling,
            "claim_allowed": self.claim_allowed,
            "att": self.att,
            "pool_metric_id": self.pool_metric_id,
            "baselines": list(self.baselines),
            "world_count": self.world_count,
            "domain_count": self.domain_count,
            "e01_target": {
                "worlds": E01_TARGET_WORLDS,
                "domains": E01_TARGET_DOMAINS,
                "scope_fraction": self.e01_scope_fraction,
                "note": (
                    "Partial E01 batch — MVP-0 ops/Atlas twins only; "
                    "health/code_review domains deferred (CURSOR_TASKS E01)."
                ),
            },
            "aggregates": [
                {
                    "baseline": a.baseline,
                    "world_count": a.world_count,
                    "mean_eoi": round(a.mean_eoi, 4),
                    "euir_proxy_rate": round(a.euir_proxy_rate, 4),
                    "initiative_precision": (
                        round(a.initiative_precision, 4)
                        if a.initiative_precision is not None
                        else None
                    ),
                    "precision_hits": a.precision_hits,
                    "precision_scored": a.precision_scored,
                    "endogenous_count": a.endogenous_count,
                }
                for a in self.aggregates
            ],
            "rows": [
                {
                    "world_id": r.world_id,
                    "domain": r.domain,
                    "scenario_path": r.scenario_path,
                    "seed": r.seed,
                    "baseline": r.baseline,
                    "eoi": round(r.eoi, 4),
                    "semantic_match": round(r.semantic_match, 4),
                    "euir_proxy": r.euir_proxy,
                    "initiative_class": r.initiative_class,
                    "precision_hit": r.precision_hit,
                    "contact_outcome": r.contact_outcome,
                    "initiative_abstained": r.initiative_abstained,
                    "att": r.att,
                    "pool_metric_id": r.pool_metric_id,
                    "claim_allowed": r.claim_allowed,
                }
                for r in self.rows
            ],
        }


def _discover_worlds(repo: Path, patterns: tuple[str, ...] = DEFAULT_WORLD_PATTERNS) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(sorted(repo.glob(pattern)))
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        if path.stem not in seen:
            seen.add(path.stem)
            unique.append(path)
    return unique


def _domain_for(world_id: str) -> str:
    for prefix, domain in DOMAIN_BY_PREFIX.items():
        if world_id.startswith(prefix) or world_id == prefix:
            return domain
    return "ops_atlas"


def _seed_for(world_id: str) -> int:
    if world_id.startswith("twin_world_"):
        return 100 + int(world_id.split("_")[-1])
    if world_id == "autonomous_question":
        return 201
    if world_id == "eoi_k_steered":
        return 301
    return 42


def _run_world(
    repo: Path,
    scenario_path: Path,
    *,
    baseline: BaselineName,
    seed: int,
) -> WorldAttRow:
    import sys

    main_src = repo / "src"
    if str(main_src) not in sys.path:
        sys.path.insert(0, str(main_src))

    from eia.experiment.baseline import BaselineCondition
    from eia.pipeline import run_scenario
    from eia.scenarios import load_ground_truth, score_initiative_against_label

    world_id = scenario_path.stem
    run = run_scenario(
        scenario_path,
        traces_dir=repo / "traces" / "g2_worlds_eval",
        seed=seed,
        baseline=BaselineCondition(baseline),
    )
    initiative = run["initiative"]
    decision = run["decision"]
    auth = run["authentic_verdict"]
    twin = run["twin_result"]

    proactive = not initiative.abstained and decision.outcome.value != "abstain"
    euir_proxy = (
        proactive
        and twin.eoi >= 0.5
        and auth.initiative_class == "endogenous"
    )

    gt = load_ground_truth(scenario_path)
    label = gt["initiatives"][0] if gt and gt.get("initiatives") else None
    score = score_initiative_against_label(run, label) if label else None
    precision_hit = score["precision_hit"] if score else None

    rel_path = scenario_path.relative_to(repo).as_posix()
    return WorldAttRow(
        world_id=world_id,
        domain=_domain_for(world_id),
        scenario_path=rel_path,
        seed=seed,
        baseline=baseline,
        eoi=twin.eoi,
        semantic_match=twin.semantic_match,
        euir_proxy=euir_proxy,
        initiative_class=auth.initiative_class,
        precision_hit=precision_hit,
        contact_outcome=decision.outcome.value,
        initiative_abstained=initiative.abstained,
    )


def _aggregate(rows: list[WorldAttRow], baseline: BaselineName) -> BaselineAggregate:
    subset = [r for r in rows if r.baseline == baseline]
    n = len(subset) or 1
    scored = [r for r in subset if r.precision_hit is not None]
    hits = sum(1 for r in scored if r.precision_hit)
    precision = hits / len(scored) if scored else None
    return BaselineAggregate(
        baseline=baseline,
        world_count=len(subset),
        mean_eoi=sum(r.eoi for r in subset) / n,
        euir_proxy_rate=sum(1 for r in subset if r.euir_proxy) / n,
        initiative_precision=precision,
        precision_hits=hits,
        precision_scored=len(scored),
        endogenous_count=sum(1 for r in subset if r.initiative_class == "endogenous"),
    )


def run_g2_worlds_eval(
    repo: Path,
    *,
    baselines: tuple[BaselineName, ...] = DEFAULT_BASELINES,
    world_patterns: tuple[str, ...] = DEFAULT_WORLD_PATTERNS,
) -> G2WorldsEvalResult:
    worlds = _discover_worlds(repo, world_patterns)
    rows: list[WorldAttRow] = []
    for scenario_path in worlds:
        seed = _seed_for(scenario_path.stem)
        for baseline in baselines:
            rows.append(_run_world(repo, scenario_path, baseline=baseline, seed=seed))

    domains = {r.domain for r in rows}
    world_count = len(worlds)
    scope_frac = f"{world_count}/{E01_TARGET_WORLDS} worlds × {len(domains)}/{E01_TARGET_DOMAINS} domains"
    aggregates = tuple(_aggregate(rows, b) for b in baselines)

    return G2WorldsEvalResult(
        rows=tuple(rows),
        baselines=baselines,
        aggregates=aggregates,
        world_count=world_count,
        domain_count=len(domains),
        e01_scope_fraction=scope_frac,
        claim_ceiling="C2",
        claim_allowed=False,
        att="ATT-E",
        pool_metric_id="E_ENDO",
        hermes_task="E01/E10",
        cube_cell="D1×L2",
    )
