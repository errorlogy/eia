"""EOI similarity threshold calibration — main structural vs starter fingerprint."""

from __future__ import annotations

from dataclasses import dataclass

from eia.schemas.initiative import Initiative, InitiativeKind

# Starter EndogeneityEstimator defaults (research/cursor-starter-v0.1/src/eia/causal.py)
STARTER_FINGERPRINT_WEIGHTS = (0.25, 0.35, 0.40)  # kind, motive, target
STARTER_SIMILARITY_THRESHOLD = 0.75

# Main EOIScorer / AuthenticReasonDiscriminator defaults
MAIN_STRUCTURAL_FIELD_COUNT = 4
MAIN_STRUCTURAL_MATCH_THRESHOLD = 0.50  # 2/4 fields → semantic_match ≥ 0.50
MAIN_AUTHENTIC_THRESHOLD = 0.50
MAIN_ROBUSTNESS_BONUS = 0.10


@dataclass(frozen=True, slots=True)
class InitiativeFingerprint:
    """Cross-implementation initiative fingerprint for paired comparison."""

    kind: str
    motive: str
    target: str
    evsi_band: str  # low | mid | high


def _evsi_band(evsi: float) -> str:
    if evsi < 0.20:
        return "low"
    if evsi < 0.50:
        return "mid"
    return "high"


def fingerprint_from_initiative(initiative: Initiative) -> InitiativeFingerprint | None:
    """Build comparable fingerprint from main Initiative."""
    if initiative.abstained or initiative.candidate is None:
        return None
    cand = initiative.candidate
    if cand.kind == InitiativeKind.ABSTAIN:
        return None
    return InitiativeFingerprint(
        kind=cand.kind.value,
        motive=cand.source_drives[0].value if cand.source_drives else "none",
        target=cand.target_belief_id or "none",
        evsi_band=_evsi_band(initiative.evsi),
    )


def starter_fingerprint_similarity(
    left: InitiativeFingerprint,
    right: InitiativeFingerprint,
) -> float:
    """Starter-weighted fingerprint similarity S(I, I')."""
    w_kind, w_motive, w_target = STARTER_FINGERPRINT_WEIGHTS
    return (
        w_kind * (left.kind == right.kind)
        + w_motive * (left.motive == right.motive)
        + w_target * (left.target == right.target)
    )


def structural_field_similarity(
    left: InitiativeFingerprint,
    right: InitiativeFingerprint,
) -> float:
    """Main EOIScorer-style 4-field structural match (no robustness bonus)."""
    matches = 0
    if left.kind == right.kind:
        matches += 1
    if left.target == right.target:
        matches += 1
    if left.motive == right.motive:
        matches += 1
    if left.evsi_band == right.evsi_band:
        matches += 1
    return matches / MAIN_STRUCTURAL_FIELD_COUNT


def structural_eoi_score(
    original: Initiative,
    twin: Initiative | None,
    *,
    removed_count: int = 0,
) -> float:
    """Replicate EOIScorer.score() without importing scorer (for calibration sweeps)."""
    if twin is None or twin.abstained or original.abstained:
        return 0.0
    left = fingerprint_from_initiative(original)
    right = fingerprint_from_initiative(twin)
    if left is None or right is None:
        return 0.0
    base = structural_field_similarity(left, right)
    bonus = MAIN_ROBUSTNESS_BONUS if removed_count > 0 else 0.0
    return min(1.0, base + bonus)


@dataclass(frozen=True, slots=True)
class ThresholdCalibration:
    """Documented equivalence between main and starter EOI gates."""

    starter_similarity_threshold: float
    main_structural_threshold: float
    main_authentic_threshold: float
    equivalent_structural_match: float
    notes: tuple[str, ...]


def calibrate_thresholds() -> ThresholdCalibration:
    """Return pre-registered threshold mapping for paired EOI reports.

    Under harmonized twin policy (remove_last_user_event, N=1):
    - Starter retains trial when S ≥ 0.75 (kind+motive+target weighted).
    - Main marks endogenous when structural_match + bonus ≥ 0.50.
    - Exact match on all three starter fields → S = 1.0 → main structural = 1.0.
    - Partial match (kind+target, motive differs): S = 0.65 < 0.75 (starter rejects),
      main structural = 0.50 (borderline pass with bonus).
    """
    return ThresholdCalibration(
        starter_similarity_threshold=STARTER_SIMILARITY_THRESHOLD,
        main_structural_threshold=MAIN_STRUCTURAL_MATCH_THRESHOLD,
        main_authentic_threshold=MAIN_AUTHENTIC_THRESHOLD,
        equivalent_structural_match=0.50,
        notes=(
            "Starter threshold 0.75 is stricter on partial fingerprint matches.",
            "Main 4-field structural match at 0.50 aligns with AuthenticReason EOI gate.",
            "Paired reports must harmonize twin policy before comparing raw EOI values.",
            "Robustness bonus (+0.10) applies only when removed_count > 0 on main.",
        ),
    )
