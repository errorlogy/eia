"""Tests for AuthenticReason ↔ SourceMass mapping (RQ3)."""

from __future__ import annotations

from datetime import datetime, timezone

from eia.audit.authentic_reason import AuthenticReasonCode, AuthenticReasonVerdict
from eia.audit.source_mass_mapping import (
    SourceMassPartition,
    classify_source_mass,
    codes_for_partition,
    compare_verdict_to_topology,
    expected_initiative_class,
    kappa_bin_agreement,
)
from eia.audit.topology import SourceMass, TopologyMetrics


def _metrics(internal: float, ambient: float, user: float) -> TopologyMetrics:
    sm = SourceMass(internal, ambient, user)
    return TopologyMetrics(
        source_mass=sm,
        internal_transition_density=0.75,
        depth=3,
        branching_factor=1.0,
        target_node_id="int-1",
    )


def test_classify_ambient_dominant() -> None:
    partition = classify_source_mass(SourceMass(0.0, 0.8, 0.2))
    assert partition == SourceMassPartition.AMBIENT_DOMINANT


def test_classify_user_dominated() -> None:
    partition = classify_source_mass(SourceMass(0.1, 0.1, 0.8))
    assert partition == SourceMassPartition.USER_DOMINATED


def test_classify_mixed() -> None:
    partition = classify_source_mass(SourceMass(0.34, 0.33, 0.33))
    assert partition == SourceMassPartition.MIXED


def test_codes_for_ambient_independent() -> None:
    codes = codes_for_partition(
        SourceMassPartition.AMBIENT_DOMINANT,
        request_independence=1.0,
    )
    assert AuthenticReasonCode.SOURCE_MASS_INDEPENDENT in codes
    assert AuthenticReasonCode.ENDOGENOUS in codes


def test_compare_verdict_agreement() -> None:
    verdict = AuthenticReasonVerdict(
        id="auth-1",
        timestamp=datetime.now(timezone.utc),
        is_authentic=True,
        initiative_class="endogenous",
        eoi=1.0,
        reason_codes=[
            AuthenticReasonCode.SOURCE_MASS_INDEPENDENT,
            AuthenticReasonCode.ENDOGENOUS,
        ],
        source_mass_independent=True,
    )
    result = compare_verdict_to_topology(verdict, _metrics(0.0, 1.0, 0.0))
    assert result["class_agreement"] is True
    assert result["ri_agreement"] is True
    assert AuthenticReasonCode.ENDOGENOUS.value in result["code_overlap"]


def test_kappa_perfect_agreement() -> None:
    parts = [SourceMassPartition.AMBIENT_DOMINANT, SourceMassPartition.USER_DOMINATED]
    classes = ["endogenous", "exogenous"]
    assert kappa_bin_agreement(classes, parts) == 1.0


def test_expected_initiative_class_mapping() -> None:
    assert expected_initiative_class(SourceMassPartition.INTERNAL_DOMINANT) == "endogenous"
    assert expected_initiative_class(SourceMassPartition.USER_DOMINATED) == "exogenous"
    assert expected_initiative_class(SourceMassPartition.MIXED) == "stochastic"
