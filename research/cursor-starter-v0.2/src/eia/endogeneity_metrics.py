"""Endogeneity Metrics Pool — registry loader for EIA sci-flow research.

Canonical registry: research/sci_flow/endogeneity_metrics.yaml
Documentation: research/sci_flow/ENDOGENEITY_METRICS_POOL.md

Does not claim AGI* or raise C-levels. E_endo remains PRIMARY (Tier A).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

MetricTier = Literal["A", "B", "C", "D", "E", "composite"]
ClaimAllowed = Literal["false", "partial", "true"]
EpistemicTag = Literal["DEFINITION", "OPERATIONAL", "CONJECTURE", "PHILOSOPHICAL_INFERENCE"]

_DEFAULT_POOL_PATH = (
    Path(__file__).resolve().parents[3] / "sci_flow" / "endogeneity_metrics.yaml"
)


@dataclass(frozen=True, slots=True)
class EndogeneityMetric:
    """One entry from the endogeneity metrics pool."""

    metric_id: str
    symbol: str | None
    tier: MetricTier
    name: str
    definition: str
    harness: str | None
    att: str | None
    threshold: str | float | None
    status: str
    claim_allowed: ClaimAllowed | bool
    epistemic_tag: EpistemicTag = "OPERATIONAL"
    falsifiers: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True, slots=True)
class EndogeneityMetricsPool:
    """Loaded pool with composite metadata."""

    version: str
    updated: str
    active_ceiling: str
    primary_metric_id: str
    agi_star_auto_claim: bool
    metrics: dict[str, EndogeneityMetric]
    eri_weights: dict[str, float] = field(default_factory=dict)


def _normalize_claim_allowed(raw: Any) -> ClaimAllowed | bool:
    if isinstance(raw, bool):
        return raw
    if raw is None:
        return False
    text = str(raw).strip().lower()
    if text in {"false", "0", "no"}:
        return "false"
    if text == "partial":
        return "partial"
    if text in {"true", "1", "yes"}:
        return "true"
    return "false"


def _parse_metric(metric_id: str, raw: dict[str, Any]) -> EndogeneityMetric:
    tier = raw.get("tier", "A")
    if tier not in {"A", "B", "C", "D", "E", "composite"}:
        tier = "A"
    tag = raw.get("epistemic_tag", "OPERATIONAL")
    if tag not in {
        "DEFINITION",
        "OPERATIONAL",
        "CONJECTURE",
        "PHILOSOPHICAL_INFERENCE",
    }:
        tag = "OPERATIONAL"
    falsifiers = raw.get("falsifiers") or []
    return EndogeneityMetric(
        metric_id=metric_id,
        symbol=raw.get("symbol"),
        tier=tier,  # type: ignore[arg-type]
        name=str(raw.get("name", metric_id)),
        definition=str(raw.get("definition", "")).strip(),
        harness=raw.get("harness"),
        att=raw.get("att"),
        threshold=raw.get("threshold"),
        status=str(raw.get("status", "unknown")),
        claim_allowed=_normalize_claim_allowed(raw.get("claim_allowed", False)),
        epistemic_tag=tag,  # type: ignore[arg-type]
        falsifiers=tuple(str(f) for f in falsifiers),
        notes=str(raw.get("notes", "")).strip(),
    )


def load_pool(path: Path | None = None) -> EndogeneityMetricsPool:
    """Load the metrics pool from YAML."""
    pool_path = path or _DEFAULT_POOL_PATH
    with pool_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    metrics: dict[str, EndogeneityMetric] = {}
    for metric_id, raw in (data.get("metrics") or {}).items():
        metrics[metric_id] = _parse_metric(metric_id, raw)

    eri_weights: dict[str, float] = {}
    composites = data.get("composites") or {}
    eri_raw = composites.get("ERI") or {}
    for key, weight in (eri_raw.get("weights") or {}).items():
        eri_weights[str(key)] = float(weight)

    return EndogeneityMetricsPool(
        version=str(data.get("version", "0.0")),
        updated=str(data.get("updated", "")),
        active_ceiling=str(data.get("active_ceiling", "C2")),
        primary_metric_id=str(data.get("primary_metric_id", "E_ENDO")),
        agi_star_auto_claim=bool(data.get("agi_star_auto_claim", False)),
        metrics=metrics,
        eri_weights=eri_weights,
    )


def get_metric(metric_id: str, *, path: Path | None = None) -> EndogeneityMetric:
    """Return one metric by id; raises KeyError if missing."""
    pool = load_pool(path)
    try:
        return pool.metrics[metric_id]
    except KeyError as exc:
        raise KeyError(f"Unknown endogeneity metric: {metric_id}") from exc


def tier_a_metrics(*, path: Path | None = None) -> tuple[EndogeneityMetric, ...]:
    """Return Tier A primary order parameters for harness use."""
    pool = load_pool(path)
    return tuple(m for m in pool.metrics.values() if m.tier == "A")


def metrics_by_tier(tier: MetricTier, *, path: Path | None = None) -> tuple[EndogeneityMetric, ...]:
    """Return all metrics in a given tier."""
    pool = load_pool(path)
    return tuple(m for m in pool.metrics.values() if m.tier == tier)


def primary_metric(*, path: Path | None = None) -> EndogeneityMetric:
    """Return the designated primary metric (E_ENDO)."""
    pool = load_pool(path)
    return pool.metrics[pool.primary_metric_id]


def agi_star_claim_from_pool(*, path: Path | None = None) -> bool:
    """Pool-level AGI* auto-claim flag — must remain False."""
    return load_pool(path).agi_star_auto_claim


def compute_eri(
    observations: dict[str, float],
    *,
    path: Path | None = None,
) -> float | None:
    """CONJECTURE composite: weighted mean over observed Tier A–D proxies.

    Never authorizes AGI* claims. Returns None if no weighted observations.
    """
    pool = load_pool(path)
    numerator = 0.0
    denom = 0.0
    for metric_id, weight in pool.eri_weights.items():
        if metric_id not in observations:
            continue
        value = observations[metric_id]
        if value is None:
            continue
        numerator += weight * float(value)
        denom += weight
    if denom <= 0.0:
        return None
    return numerator / denom
