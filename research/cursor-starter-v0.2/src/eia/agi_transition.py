"""Research stubs for AGI* phase-transition order parameters.

Not a production gate. Does not claim AGI* or raise C-levels.
See research/sci_flow/AGI_PHASE_TRANSITION.md and AGI_TRANSITION_TEST.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

EpistemicTag = Literal[
    "DEFINITION",
    "OPERATIONAL",
    "CONJECTURE",
    "PHILOSOPHICAL_INFERENCE",
]

OrderParameterId = Literal["E", "N_H", "P", "R", "D"]

# Suggested first proxies only — numeric AGI* thresholds remain TBD.
SUGGESTED_PROXY_NOTES: dict[OrderParameterId, str] = {
    "E": (
        "CF-4 / EOI / e_endo_partial; causal endogeneity bar "
        "(declaration/simulation ≠ E_endo); continuous E index not pre-registered"
    ),
    "N_H": (
        "ATT-N under pre-registered B; D_H + ΔP(A|z); "
        "NAMM compression soft witness; claim_allowed=False"
    ),
    "P": "LoopScheduler multi-tick persistence without re-prompting",
    "R": (
        "Closed observe→motive→action→world-update goal-formation loop "
        "(not Kuramoto R); M-R typed-trace + M-R-LIVE shadow multitick"
    ),
    "D": (
        "ATT-D cross-domain E_endo (CF-4-class) on ≥2 disjoint ontologies; "
        "P/R explore where applicable; claim_allowed=False / no C5"
    ),
}


@dataclass(frozen=True, slots=True)
class OrderParameterSpec:
    """Design metadata for one ATT order parameter."""

    param_id: OrderParameterId
    name: str
    att_id: str
    threshold: float | None  # None => TBD
    epistemic_tag: EpistemicTag = "OPERATIONAL"
    notes: str = ""


@dataclass(frozen=True, slots=True)
class PhaseTransitionSnapshot:
    """Research-only snapshot. agi_star_claim must stay False until ATT conjunction."""

    e_score: float | None
    n_h_score: float | None
    p_score: float | None
    r_score: float | None
    d_score: float | None
    e_endo_partial: bool = False
    agi_star_claim: bool = False
    rationale: str = ""


def default_order_parameter_specs() -> tuple[OrderParameterSpec, ...]:
    """Return ATT-aligned specs with thresholds left TBD."""
    return (
        OrderParameterSpec(
            param_id="E",
            name="Endogenous Cognitive Causality",
            att_id="ATT-E",
            threshold=None,
            notes=SUGGESTED_PROXY_NOTES["E"],
        ),
        OrderParameterSpec(
            param_id="N_H",
            name="Trans-Anthropic Non-Embeddability",
            att_id="ATT-N",
            threshold=None,
            notes=SUGGESTED_PROXY_NOTES["N_H"],
        ),
        OrderParameterSpec(
            param_id="P",
            name="Temporal Goal Persistence",
            att_id="ATT-P",
            threshold=None,
            notes=SUGGESTED_PROXY_NOTES["P"],
        ),
        OrderParameterSpec(
            param_id="R",
            name="Endogenous Cognitive Recurrence",
            att_id="ATT-R",
            threshold=None,
            notes=SUGGESTED_PROXY_NOTES["R"],
        ),
        OrderParameterSpec(
            param_id="D",
            name="Cross-Domain Generality",
            att_id="ATT-D",
            threshold=None,
            notes=SUGGESTED_PROXY_NOTES["D"],
        ),
    )


# Labels that never establish E_endo (ATT-E / CAUSAL_ENDOGENEITY.md).
DECLARATION_ONLY_AGENCY_LABELS: frozenset[str] = frozenset(
    {
        "declaration_only",
        "declaration",
        "self_ascription",
        "self_description",
        "roleplay_agency",
        "simulated_agency",
        "simulation",
        "prompt_narrative",
        "agency_narrative",
        "narrative_only",
    }
)


def e_endo_label_admissible(
    *,
    agency_label: str,
    trajectory_changed: bool,
    matching_external_initiating_signal: bool,
    do_z_changes_g_distribution: bool,
    x_non_triggering: bool,
) -> bool:
    """Reject declaration/simulation/roleplay-only agency as E_endo evidence.

    OPERATIONAL stub for the causal endogeneity bar. Does not raise C-levels
    or authorize agi_star_claim. Pass only if the label is not declaration-class
    and do(Z) support holds under non-triggering X without a matching external
    initiator for the new trajectory.
    """
    label = agency_label.strip().lower().replace("-", "_").replace(" ", "_")
    if label in DECLARATION_ONLY_AGENCY_LABELS:
        return False
    if not trajectory_changed:
        return False
    if matching_external_initiating_signal:
        return False
    if not (do_z_changes_g_distribution and x_non_triggering):
        return False
    return True


def tau_agi_claim_allowed(
    *,
    e_above: bool,
    n_h_above: bool,
    p_above: bool,
    r_above: bool,
    d_above: bool,
    sustained: bool,
    thresholds_preregistered: bool,
) -> bool:
    """Conjunction helper for research logs. Never a production gate.

    Returns True only if all order-parameter gates and pre-registration hold.
    Callers must still keep agi_star_claim=False until an ATT metrics report
    explicitly authorizes a research claim (currently none does).
    """
    if not thresholds_preregistered:
        return False
    return bool(e_above and n_h_above and p_above and r_above and d_above and sustained)


def snapshot_from_partial_e(*, e_endo_partial: bool) -> PhaseTransitionSnapshot:
    """Build a non-claiming snapshot from scoped CF-4-style E evidence."""
    return PhaseTransitionSnapshot(
        e_score=1.0 if e_endo_partial else 0.0,
        n_h_score=None,
        p_score=None,
        r_score=None,
        d_score=None,
        e_endo_partial=e_endo_partial,
        agi_star_claim=False,
        rationale="scoped E only; N_H/P/R/D unmeasured; agi_star_claim forced false",
    )


def snapshot_with_p_explore(
    *,
    e_endo_partial: bool,
    p_explore_proxy: float | None,
) -> PhaseTransitionSnapshot:
    """Attach ATT-P explore proxy without authorizing AGI* or C-ladder raises."""
    return PhaseTransitionSnapshot(
        e_score=1.0 if e_endo_partial else 0.0,
        n_h_score=None,
        p_score=p_explore_proxy,
        r_score=None,
        d_score=None,
        e_endo_partial=e_endo_partial,
        agi_star_claim=False,
        rationale=(
            "scoped E + ATT-P explore P proxy only; N_H/R/D unmeasured; "
            "agi_star_claim forced false"
        ),
    )


def snapshot_with_r_explore(
    *,
    e_endo_partial: bool,
    p_explore_proxy: float | None,
    r_explore_proxy: float | None,
) -> PhaseTransitionSnapshot:
    """Attach ATT-R explore proxy (not Kuramoto R) without AGI*/C-ladder raises."""
    return PhaseTransitionSnapshot(
        e_score=1.0 if e_endo_partial else 0.0,
        n_h_score=None,
        p_score=p_explore_proxy,
        r_score=r_explore_proxy,
        d_score=None,
        e_endo_partial=e_endo_partial,
        agi_star_claim=False,
        rationale=(
            "scoped E + ATT-P/ATT-R explore proxies only; N_H/D unmeasured; "
            "R is endogenous cognitive recurrence not Kuramoto; "
            "agi_star_claim forced false"
        ),
    )


def snapshot_with_n_h_explore(
    *,
    e_endo_partial: bool,
    p_explore_proxy: float | None,
    r_explore_proxy: float | None,
    n_h_explore_proxy: float | None,
) -> PhaseTransitionSnapshot:
    """Attach ATT-N explore proxy without authorizing AGI* or strong N_H claims."""
    return PhaseTransitionSnapshot(
        e_score=1.0 if e_endo_partial else 0.0,
        n_h_score=n_h_explore_proxy,
        p_score=p_explore_proxy,
        r_score=r_explore_proxy,
        d_score=None,
        e_endo_partial=e_endo_partial,
        agi_star_claim=False,
        rationale=(
            "scoped E + ATT-P/ATT-R/ATT-N explore proxies only; D unmeasured; "
            "N_H explore is D_H under pre-registered B with ΔP(A|z)>0 — "
            "not strong N_H; opacity ≠ non-embeddability; "
            "agi_star_claim forced false"
        ),
    )


def snapshot_with_d_explore(
    *,
    e_endo_partial: bool,
    p_explore_proxy: float | None,
    r_explore_proxy: float | None,
    n_h_explore_proxy: float | None,
    d_explore_proxy: float | None,
) -> PhaseTransitionSnapshot:
    """Attach ATT-D explore proxy without authorizing AGI* or C5 raises."""
    return PhaseTransitionSnapshot(
        e_score=1.0 if e_endo_partial else 0.0,
        n_h_score=n_h_explore_proxy,
        p_score=p_explore_proxy,
        r_score=r_explore_proxy,
        d_score=d_explore_proxy,
        e_endo_partial=e_endo_partial,
        agi_star_claim=False,
        rationale=(
            "scoped E + ATT-P/ATT-R/ATT-N/ATT-D explore proxies; "
            "D explore is cross-domain E_endo on ≥2 disjoint ontologies — "
            "not C5; schedule/prompt-only transfer falsified; "
            "agi_star_claim forced false"
        ),
    )
