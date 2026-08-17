"""Tests for EOI threshold calibration (RQ2)."""

from __future__ import annotations

from datetime import datetime, timezone

from eia.audit.eoi_calibration import (
    InitiativeFingerprint,
    calibrate_thresholds,
    fingerprint_from_initiative,
    starter_fingerprint_similarity,
    structural_eoi_score,
    structural_field_similarity,
)
from eia.schemas.initiative import Initiative, InitiativeCandidate, InitiativeKind
from eia.schemas.motivation import DriveKind


def _initiative(
    *,
    kind: InitiativeKind = InitiativeKind.ASK_QUESTION,
    target: str = "belief-1",
    drive: DriveKind = DriveKind.EPISTEMIC,
    evsi: float = 0.5,
    abstained: bool = False,
) -> Initiative:
    return Initiative(
        id="int-1",
        timestamp=datetime.now(timezone.utc),
        candidate=InitiativeCandidate(
            id="cand-1",
            kind=kind,
            target_belief_id=target,
            expected_info_gain=evsi,
            source_drives=[drive],
        ),
        abstained=abstained,
        parent_motivation_id="mot-1",
        evsi=evsi,
    )


def test_calibrate_thresholds_documents_equivalence() -> None:
    cal = calibrate_thresholds()
    assert cal.starter_similarity_threshold == 0.75
    assert cal.main_authentic_threshold == 0.50
    assert len(cal.notes) >= 3


def test_starter_fingerprint_full_match() -> None:
    left = InitiativeFingerprint("ask_question", "epistemic", "belief-1", "mid")
    right = InitiativeFingerprint("ask_question", "epistemic", "belief-1", "high")
    assert starter_fingerprint_similarity(left, right) == 1.0


def test_starter_fingerprint_partial_below_threshold() -> None:
    left = InitiativeFingerprint("ask_question", "epistemic", "belief-1", "mid")
    right = InitiativeFingerprint("ask_question", "coherence", "belief-1", "mid")
    sim = starter_fingerprint_similarity(left, right)
    assert sim == 0.65
    assert sim < calibrate_thresholds().starter_similarity_threshold


def test_structural_eoi_with_robustness_bonus() -> None:
    orig = _initiative(target="belief-1", drive=DriveKind.EPISTEMIC, evsi=0.15)
    twin = _initiative(target="belief-2", drive=DriveKind.COHERENCE, evsi=0.55)
    score_no_bonus = structural_eoi_score(orig, twin, removed_count=0)
    score_with_bonus = structural_eoi_score(orig, twin, removed_count=1)
    assert score_no_bonus == 0.25
    assert score_with_bonus == 0.35


def test_fingerprint_from_initiative_abstained() -> None:
    assert fingerprint_from_initiative(_initiative(abstained=True)) is None


def test_structural_field_similarity_four_fields() -> None:
    left = InitiativeFingerprint("ask_question", "epistemic", "b1", "mid")
    right = InitiativeFingerprint("ask_question", "epistemic", "b1", "mid")
    assert structural_field_similarity(left, right) == 1.0
