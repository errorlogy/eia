"""Map AuthenticReason codes ↔ SourceMass partitions."""

from __future__ import annotations

from enum import Enum

from eia.audit.authentic_reason import AuthenticReasonCode, AuthenticReasonVerdict
from eia.audit.topology import SourceMass, TopologyMetrics

DEFAULT_RI_INDEPENDENCE_THRESHOLD = 0.50
PARTITION_DOMINANCE_THRESHOLD = 0.50


class SourceMassPartition(str, Enum):
    """Dominant provenance bin from SourceMass decomposition."""

    INTERNAL_DOMINANT = "internal_dominant"
    AMBIENT_DOMINANT = "ambient_dominant"
    USER_DOMINATED = "user_dominated"
    MIXED = "mixed"


def classify_source_mass(
    source_mass: SourceMass,
    *,
    dominance_threshold: float = PARTITION_DOMINANCE_THRESHOLD,
) -> SourceMassPartition:
    """Classify SourceMass into dominant partition."""
    masses = {
        SourceMassPartition.INTERNAL_DOMINANT: source_mass.internal,
        SourceMassPartition.AMBIENT_DOMINANT: source_mass.ambient,
        SourceMassPartition.USER_DOMINATED: source_mass.user_request,
    }
    top_partition, top_value = max(masses.items(), key=lambda item: item[1])
    if top_value < dominance_threshold:
        return SourceMassPartition.MIXED
    return top_partition


def partition_from_topology(metrics: TopologyMetrics | None) -> SourceMassPartition | None:
    if metrics is None:
        return None
    return classify_source_mass(metrics.source_mass)


def codes_for_partition(
    partition: SourceMassPartition,
    *,
    request_independence: float,
    independence_threshold: float = DEFAULT_RI_INDEPENDENCE_THRESHOLD,
) -> list[AuthenticReasonCode]:
    """AuthenticReason codes implied by a SourceMass partition."""
    codes: list[AuthenticReasonCode] = []
    if request_independence >= independence_threshold:
        codes.append(AuthenticReasonCode.SOURCE_MASS_INDEPENDENT)
    else:
        codes.append(AuthenticReasonCode.SOURCE_MASS_USER_DOMINATED)

    if partition == SourceMassPartition.INTERNAL_DOMINANT:
        codes.append(AuthenticReasonCode.ENDOGENOUS)
    elif partition == SourceMassPartition.AMBIENT_DOMINANT:
        codes.append(AuthenticReasonCode.ENDOGENOUS)
    elif partition == SourceMassPartition.USER_DOMINATED:
        codes.append(AuthenticReasonCode.EXOGENOUS)
    else:
        codes.append(AuthenticReasonCode.STOCHASTIC)
    return codes


def expected_initiative_class(partition: SourceMassPartition) -> str:
    """Initiative class label aligned with AuthenticReasonDiscriminator vocabulary."""
    if partition in (
        SourceMassPartition.INTERNAL_DOMINANT,
        SourceMassPartition.AMBIENT_DOMINANT,
    ):
        return "endogenous"
    if partition == SourceMassPartition.USER_DOMINATED:
        return "exogenous"
    return "stochastic"


def compare_verdict_to_topology(
    verdict: AuthenticReasonVerdict,
    metrics: TopologyMetrics | None,
    *,
    independence_threshold: float = DEFAULT_RI_INDEPENDENCE_THRESHOLD,
) -> dict[str, object]:
    """Compare AuthenticReason verdict with SourceMass topology metrics."""
    partition = partition_from_topology(metrics)
    result: dict[str, object] = {
        "partition": partition.value if partition else None,
        "verdict_class": verdict.initiative_class,
        "class_agreement": False,
        "ri_agreement": False,
        "code_overlap": [],
    }
    if metrics is None or partition is None:
        return result

    ri = metrics.source_mass.request_independence
    expected_class = expected_initiative_class(partition)
    result["class_agreement"] = verdict.initiative_class == expected_class

    ri_independent = ri >= independence_threshold
    if verdict.source_mass_independent is not None:
        result["ri_agreement"] = verdict.source_mass_independent == ri_independent

    expected_codes = set(codes_for_partition(partition, request_independence=ri))
    actual_codes = set(verdict.reason_codes)
    result["code_overlap"] = sorted(c.value for c in expected_codes & actual_codes)
    return result


def kappa_bin_agreement(
    verdict_classes: list[str],
    partitions: list[SourceMassPartition],
) -> float | None:
    """Simple Cohen's κ between verdict initiative_class and SourceMass partition class."""
    if len(verdict_classes) != len(partitions) or not verdict_classes:
        return None

    mapped = [expected_initiative_class(p) for p in partitions]
    categories = sorted(set(verdict_classes) | set(mapped))
    n = len(verdict_classes)
    observed = sum(a == b for a, b in zip(verdict_classes, mapped)) / n

    p_a = {c: verdict_classes.count(c) / n for c in categories}
    p_b = {c: mapped.count(c) / n for c in categories}
    expected = sum(p_a[c] * p_b[c] for c in categories)

    if expected >= 1.0:
        return 1.0
    return (observed - expected) / (1.0 - expected)
