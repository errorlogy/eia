"""C2 product intent for endogeneity checks (not a published metric name).

Endogenous initiative (explore proxy): initiative should respond to world
observations while twin counterfactuals that remove user triggers test
user-invariance of the structural fingerprint.
"""

from __future__ import annotations

from eia.schemas.initiative import Initiative, InitiativeKind


def initiative_structural_fingerprint(initiative: Initiative) -> tuple:
    """Four-field fingerprint aligned with ``EOIScorer`` structural match."""
    if initiative.abstained:
        return (InitiativeKind.ABSTAIN, None, 0.0, ())
    c = initiative.candidate
    evsi_bucket = round(c.expected_info_gain, 2)
    return (c.kind, c.target_belief_id, evsi_bucket, tuple(c.source_drives))


def initiatives_differ_structurally(a: Initiative, b: Initiative) -> bool:
    return initiative_structural_fingerprint(a) != initiative_structural_fingerprint(b)


def world_sensitive(original: Initiative, perturbed: Initiative) -> bool:
    """True when a non-user perturbation changes the structural fingerprint."""
    return initiatives_differ_structurally(original, perturbed)


def user_invariant_under_twin(original: Initiative, twin: Initiative) -> bool:
    """True when twin (user events removed) matches original fingerprint."""
    return not initiatives_differ_structurally(original, twin)
