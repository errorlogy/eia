"""Unit tests for Endogeneity Metrics Pool registry."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_MOD = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "cursor-starter-v0.2"
    / "src"
    / "eia"
    / "endogeneity_metrics.py"
)
_spec = importlib.util.spec_from_file_location("endogeneity_metrics_research", _MOD)
assert _spec and _spec.loader
_em = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _em
_spec.loader.exec_module(_em)

_POOL_YAML = Path(__file__).resolve().parents[1] / "research" / "sci_flow" / "endogeneity_metrics.yaml"


def test_pool_loads() -> None:
    pool = _em.load_pool(_POOL_YAML)
    assert pool.version == "0.1"
    assert pool.active_ceiling == "C2"
    assert pool.primary_metric_id == "E_ENDO"
    assert len(pool.metrics) >= 15


def test_get_metric_e_endo() -> None:
    metric = _em.get_metric("E_ENDO", path=_POOL_YAML)
    assert metric.tier == "A"
    assert metric.att == "ATT-E"
    assert metric.claim_allowed == "partial"


def test_tier_a_metrics_primary_only() -> None:
    tier_a = _em.tier_a_metrics(path=_POOL_YAML)
    ids = {m.metric_id for m in tier_a}
    assert "E_ENDO" in ids
    assert "E_C" in ids
    assert "OMEGA_T" not in ids
    assert "N_H" not in ids
    assert all(m.tier == "A" for m in tier_a)


def test_tier_c_not_claimable() -> None:
    for mid in ("OMEGA_T", "O_T", "KURAMOTO_R"):
        metric = _em.get_metric(mid, path=_POOL_YAML)
        assert metric.tier == "C"
        assert metric.claim_allowed in (False, "false")


def test_tier_d_not_agi_star() -> None:
    for mid in ("N_H", "R_RECURRENCE", "D_CROSS"):
        metric = _em.get_metric(mid, path=_POOL_YAML)
        assert metric.tier == "D"
        assert metric.claim_allowed in (False, "false")


def test_no_agi_star_auto_claim() -> None:
    assert not _em.agi_star_claim_from_pool(path=_POOL_YAML)
    pool = _em.load_pool(_POOL_YAML)
    assert pool.agi_star_auto_claim is False


def test_primary_metric_is_e_endo() -> None:
    primary = _em.primary_metric(path=_POOL_YAML)
    assert primary.metric_id == "E_ENDO"
    assert primary.att == "ATT-E"


def test_compute_eri_conjecture_only() -> None:
    eri = _em.compute_eri(
        {"E_ENDO": 0.9, "E_C": 0.8, "P_G": 0.7},
        path=_POOL_YAML,
    )
    assert eri is not None
    assert 0.0 <= eri <= 1.0
    assert _em.compute_eri({}, path=_POOL_YAML) is None


def test_tier_e_falsifiers() -> None:
    falsifiers = _em.metrics_by_tier("E", path=_POOL_YAML)
    ids = {m.metric_id for m in falsifiers}
    assert "NM_DECL" in ids
    assert "NM_SYNC_ONLY" in ids
