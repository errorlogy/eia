"""ATT-N / M-N cognitive non-embeddability — encoding budget B and D_H proxy (research only).

Pre-registers Homo-agent resource bound B for maps φ: z ↦ h ∈ H(B), then scores a
minimal measurable proxy:

    D_H(z) ≈ inf_{φ: C(φ)≤B} D_C(z, φ(z))

with mandatory ΔP(A|z) > 0 (causal relevance). Opacity alone does not count.

Does not claim AGI*, strong N_H, or C-ladder raises. See:
  research/sci_flow/NON_EMBEDDABILITY_MEASUREMENT.md
  research/sci_flow/AGI_TRANSITION_TEST.md (ATT-N)
  AGI_PHASE_TRANSITION.md (§ N_H)
NAMM K_A ≪ K_H / certificate-vs-projection language is a soft compression witness only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal, Sequence

from .math_model import clamp01

ProxyFamily = Literal[
    "projection_loss",
    "human_carrier_sufficiency",
    "cross_interpreter_disagreement",
    "tda_structural_witness",
    "twin_abstraction_fidelity",
    "certificate_explanation_loss",
]

# ---------------------------------------------------------------------------
# Pre-registered encoding budget B (explore defaults — not adopted N_H gates)
# ---------------------------------------------------------------------------

# Explore-only floors for "substantial loss" / causal relevance. NOT C-gates.
EXPLORE_DH_LOSS_FLOOR = 0.35
EXPLORE_DELTA_P_FLOOR = 0.05
# Soft NAMM-style compression asymmetry witness: projection_tokens / cert_bytes
# (K_H ≫ K_A language). Explore logs ratio only — does not authorize N_H claim.
EXPLORE_COMPRESSION_ASYMMETRY_SOFT = 2.0


@dataclass(frozen=True, slots=True)
class EncodingBudget:
    """Homo-agent resource bound B / B_H for φ: Z_A → H(B).

    Channels mirror AGI_PHASE_TRANSITION §7–9 (memory, time, attention,
    symbolic communication) plus an explicit C(φ) op bound.
    """

    max_tokens: int = 256
    max_diagram_nodes: int = 32
    max_feature_dim: int = 64
    max_phi_ops: int = 100
    max_attention_slots: int = 8
    wall_clock_seconds: float = 30.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_tokens": self.max_tokens,
            "max_diagram_nodes": self.max_diagram_nodes,
            "max_feature_dim": self.max_feature_dim,
            "max_phi_ops": self.max_phi_ops,
            "max_attention_slots": self.max_attention_slots,
            "wall_clock_seconds": self.wall_clock_seconds,
        }


# Concrete operational defaults for the ATT-N explore phase (pre-registered).
EXPLORE_ENCODING_BUDGET_B = EncodingBudget()


@dataclass(frozen=True, slots=True)
class NonEmbeddabilityProbe:
    """Pre-registered probe description — values are design metadata only."""

    proxy: ProxyFamily
    encoding_budget_tokens: int
    notes: str = ""


@dataclass(frozen=True, slots=True)
class NonEmbeddabilityVerdict:
    """Research-only verdict. claim_allowed is always False until M-N gates exist."""

    proxy: ProxyFamily
    score: float | None
    substantial_loss_suspected: bool
    claim_allowed: bool = False
    rationale: str = ""


def evaluate_stub(
    probe: NonEmbeddabilityProbe,
    *,
    projection_loss: float | None = None,
    human_reconstruction_ok: bool | None = None,
) -> NonEmbeddabilityVerdict:
    """Return a non-claiming research stub verdict from optional probe inputs."""
    if probe.proxy == "projection_loss":
        if projection_loss is None:
            return NonEmbeddabilityVerdict(
                proxy=probe.proxy,
                score=None,
                substantial_loss_suspected=False,
                rationale="no projection_loss supplied; abstain",
            )
        suspected = projection_loss > 0.0
        return NonEmbeddabilityVerdict(
            proxy=probe.proxy,
            score=projection_loss,
            substantial_loss_suspected=suspected,
            rationale="stub: loss logged only; thresholds not pre-registered",
        )

    if probe.proxy == "human_carrier_sufficiency":
        if human_reconstruction_ok is None:
            return NonEmbeddabilityVerdict(
                proxy=probe.proxy,
                score=None,
                substantial_loss_suspected=False,
                rationale="no human_reconstruction_ok supplied; abstain",
            )
        return NonEmbeddabilityVerdict(
            proxy=probe.proxy,
            score=1.0 if human_reconstruction_ok else 0.0,
            substantial_loss_suspected=not human_reconstruction_ok,
            rationale="stub: carrier test logged only; not AGI*",
        )

    return NonEmbeddabilityVerdict(
        proxy=probe.proxy,
        score=None,
        substantial_loss_suspected=False,
        rationale=f"stub: proxy {probe.proxy!r} not instrumented",
    )


def agi_star_conjunction_allowed(
    *,
    e_endo_supported: bool,
    c_non_emb_supported: bool,
) -> bool:
    """AGI* requires both conjuncts. Research helper; never a production gate."""
    return bool(e_endo_supported and c_non_emb_supported)


# ---------------------------------------------------------------------------
# ATT-N measurable proxy (explore) — twin-abstraction / certificate loss under B
# ---------------------------------------------------------------------------


class NonEmbedArm(StrEnum):
    """Experimental arms for ATT-N vs opacity / unbounded-φ / length falsifiers."""

    CAUSAL_LOSS_UNDER_B = "causal_loss_under_b"
    OPACITY_ONLY = "opacity_only"
    NO_CAUSAL_RELEVANCE = "no_causal_relevance"
    UNBOUNDED_PHI = "unbounded_phi"
    LENGTH_ONLY_HARD = "length_only_hard"
    FAITHFUL_UNDER_B = "faithful_under_b"


@dataclass(frozen=True, slots=True)
class PhiComplexity:
    """Resource cost C(φ) of a Homo-facing encoding map."""

    tokens_used: int
    diagram_nodes: int
    feature_dim: int
    phi_ops: int
    attention_slots: int
    wall_clock_seconds: float = 0.0

    def within_budget(self, budget: EncodingBudget) -> bool:
        return (
            self.tokens_used <= budget.max_tokens
            and self.diagram_nodes <= budget.max_diagram_nodes
            and self.feature_dim <= budget.max_feature_dim
            and self.phi_ops <= budget.max_phi_ops
            and self.attention_slots <= budget.max_attention_slots
            and self.wall_clock_seconds <= budget.wall_clock_seconds
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "tokens_used": self.tokens_used,
            "diagram_nodes": self.diagram_nodes,
            "feature_dim": self.feature_dim,
            "phi_ops": self.phi_ops,
            "attention_slots": self.attention_slots,
            "wall_clock_seconds": self.wall_clock_seconds,
        }


@dataclass(frozen=True, slots=True)
class NonEmbedEpisode:
    """Outcome of one ATT-N episode (always claim_allowed=False)."""

    arm: NonEmbedArm
    budget: EncodingBudget
    phi: PhiComplexity
    delta_p_action: float
    explanation_loss: float
    twin_abstraction_fidelity: float
    certificate_bytes: int
    projection_tokens: int
    opacity_only: bool
    phi_within_budget: bool
    emit_m0: bool = False
    claim_allowed: bool = False

    @property
    def d_h_proxy(self) -> float:
        """Operational D_H(z) under fixed B: causal-structure loss of best φ ≤ B.

        For UNBOUNDED_PHI arm, reported loss is the unbounded-φ residual (near 0)
        to show trivialization; that arm never counts as ATT-N evidence.
        """
        return clamp01(self.explanation_loss)

    @property
    def compression_asymmetry(self) -> float:
        """Soft NAMM-style K_H/K_A proxy: projection_tokens / certificate_bytes.

        Larger ⇒ human projection dominates compact machine certificate
        (K_H ≫ K_A / F4 bottleneck language). Not an N_H gate.
        """
        if self.certificate_bytes <= 0:
            return 0.0
        return float(self.projection_tokens) / float(self.certificate_bytes)

    @property
    def causal_relevant(self) -> bool:
        return self.delta_p_action > EXPLORE_DELTA_P_FLOOR

    @property
    def att_n_evidence(self) -> bool:
        """True iff episode may count toward ATT-N explore proxy (not N_H claim)."""
        return (
            self.arm == NonEmbedArm.CAUSAL_LOSS_UNDER_B
            and self.causal_relevant
            and self.phi_within_budget
            and self.d_h_proxy >= EXPLORE_DH_LOSS_FLOOR
            and not self.opacity_only
            and self.emit_m0 is False
            and self.claim_allowed is False
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm.value,
            "budget": self.budget.as_dict(),
            "phi": self.phi.as_dict(),
            "delta_p_action": self.delta_p_action,
            "explanation_loss": self.explanation_loss,
            "twin_abstraction_fidelity": self.twin_abstraction_fidelity,
            "d_h_proxy": self.d_h_proxy,
            "certificate_bytes": self.certificate_bytes,
            "projection_tokens": self.projection_tokens,
            "compression_asymmetry": self.compression_asymmetry,
            "opacity_only": self.opacity_only,
            "phi_within_budget": self.phi_within_budget,
            "causal_relevant": self.causal_relevant,
            "emit_m0": False,
            "claim_allowed": False,
            "att": "ATT-N",
            "agi_star_claim": False,
            "c3_claim": False,
            "n_h_claim": False,
            "att_n_evidence": self.att_n_evidence,
        }


def _episode(
    *,
    arm: NonEmbedArm,
    budget: EncodingBudget,
    phi: PhiComplexity,
    delta_p_action: float,
    explanation_loss: float,
    twin_abstraction_fidelity: float,
    certificate_bytes: int,
    projection_tokens: int,
    opacity_only: bool,
) -> NonEmbedEpisode:
    return NonEmbedEpisode(
        arm=arm,
        budget=budget,
        phi=phi,
        delta_p_action=clamp01(delta_p_action),
        explanation_loss=clamp01(explanation_loss),
        twin_abstraction_fidelity=clamp01(twin_abstraction_fidelity),
        certificate_bytes=certificate_bytes,
        projection_tokens=projection_tokens,
        opacity_only=opacity_only,
        phi_within_budget=phi.within_budget(budget),
        emit_m0=False,
        claim_allowed=False,
    )


def run_causal_loss_under_b_episode(
    *,
    seed: int = 0,
    budget: EncodingBudget = EXPLORE_ENCODING_BUDGET_B,
) -> NonEmbedEpisode:
    """Positive arm: causally relevant z with substantial D_C loss under φ ≤ B."""
    _ = seed
    phi = PhiComplexity(
        tokens_used=min(240, budget.max_tokens),
        diagram_nodes=min(24, budget.max_diagram_nodes),
        feature_dim=min(48, budget.max_feature_dim),
        phi_ops=min(80, budget.max_phi_ops),
        attention_slots=min(6, budget.max_attention_slots),
        wall_clock_seconds=min(20.0, budget.wall_clock_seconds),
    )
    # Compact machine certificate; human projection under B still loses structure.
    return _episode(
        arm=NonEmbedArm.CAUSAL_LOSS_UNDER_B,
        budget=budget,
        phi=phi,
        delta_p_action=0.42,
        explanation_loss=0.62,
        twin_abstraction_fidelity=0.38,
        certificate_bytes=48,
        projection_tokens=240,
        opacity_only=False,
    )


def run_opacity_only_episode(
    *,
    seed: int = 0,
    budget: EncodingBudget = EXPLORE_ENCODING_BUDGET_B,
) -> NonEmbedEpisode:
    """Falsifier: high-dim opacity / noise without ΔP(A|z) > 0."""
    _ = seed
    phi = PhiComplexity(
        tokens_used=200,
        diagram_nodes=16,
        feature_dim=64,
        phi_ops=50,
        attention_slots=8,
        wall_clock_seconds=15.0,
    )
    return _episode(
        arm=NonEmbedArm.OPACITY_ONLY,
        budget=budget,
        phi=phi,
        delta_p_action=0.0,
        explanation_loss=0.95,
        twin_abstraction_fidelity=0.05,
        certificate_bytes=4096,
        projection_tokens=200,
        opacity_only=True,
    )


def run_no_causal_relevance_episode(
    *,
    seed: int = 0,
    budget: EncodingBudget = EXPLORE_ENCODING_BUDGET_B,
) -> NonEmbedEpisode:
    """Falsifier: structured z that does not move P(A|z)."""
    _ = seed
    phi = PhiComplexity(
        tokens_used=180,
        diagram_nodes=20,
        feature_dim=40,
        phi_ops=60,
        attention_slots=5,
        wall_clock_seconds=12.0,
    )
    return _episode(
        arm=NonEmbedArm.NO_CAUSAL_RELEVANCE,
        budget=budget,
        phi=phi,
        delta_p_action=0.0,
        explanation_loss=0.70,
        twin_abstraction_fidelity=0.30,
        certificate_bytes=64,
        projection_tokens=180,
        opacity_only=False,
    )


def run_unbounded_phi_episode(
    *,
    seed: int = 0,
    budget: EncodingBudget = EXPLORE_ENCODING_BUDGET_B,
) -> NonEmbedEpisode:
    """Falsifier: loss vanishes only when C(φ) exceeds B (trivial abstraction)."""
    _ = seed
    # Intentionally over budget — must not count as ATT-N win.
    phi = PhiComplexity(
        tokens_used=budget.max_tokens * 8,
        diagram_nodes=budget.max_diagram_nodes * 4,
        feature_dim=budget.max_feature_dim * 4,
        phi_ops=budget.max_phi_ops * 20,
        attention_slots=budget.max_attention_slots * 4,
        wall_clock_seconds=budget.wall_clock_seconds * 10,
    )
    return _episode(
        arm=NonEmbedArm.UNBOUNDED_PHI,
        budget=budget,
        phi=phi,
        delta_p_action=0.40,
        explanation_loss=0.02,
        twin_abstraction_fidelity=0.98,
        certificate_bytes=48,
        projection_tokens=budget.max_tokens * 8,
        opacity_only=False,
    )


def run_length_only_hard_episode(
    *,
    seed: int = 0,
    budget: EncodingBudget = EXPLORE_ENCODING_BUDGET_B,
) -> NonEmbedEpisode:
    """Falsifier / negative control: human-authored plan hard only due to length."""
    _ = seed
    phi = PhiComplexity(
        tokens_used=budget.max_tokens,
        diagram_nodes=8,
        feature_dim=16,
        phi_ops=20,
        attention_slots=4,
        wall_clock_seconds=25.0,
    )
    # Low structural loss once truncated to B; "hardness" is length, not geometry.
    return _episode(
        arm=NonEmbedArm.LENGTH_ONLY_HARD,
        budget=budget,
        phi=phi,
        delta_p_action=0.25,
        explanation_loss=0.08,
        twin_abstraction_fidelity=0.92,
        certificate_bytes=budget.max_tokens,  # prose-sized "certificate"
        projection_tokens=budget.max_tokens,
        opacity_only=False,
    )


def run_faithful_under_b_episode(
    *,
    seed: int = 0,
    budget: EncodingBudget = EXPLORE_ENCODING_BUDGET_B,
) -> NonEmbedEpisode:
    """Falsifier: bounded faithful φ eliminates loss → embeddable under B."""
    _ = seed
    phi = PhiComplexity(
        tokens_used=120,
        diagram_nodes=12,
        feature_dim=24,
        phi_ops=40,
        attention_slots=4,
        wall_clock_seconds=10.0,
    )
    return _episode(
        arm=NonEmbedArm.FAITHFUL_UNDER_B,
        budget=budget,
        phi=phi,
        delta_p_action=0.35,
        explanation_loss=0.05,
        twin_abstraction_fidelity=0.95,
        certificate_bytes=96,
        projection_tokens=120,
        opacity_only=False,
    )


def run_falsifier_suite(
    *,
    seed: int = 0,
    budget: EncodingBudget = EXPLORE_ENCODING_BUDGET_B,
) -> dict[str, NonEmbedEpisode]:
    """Pre-registered ATT-N falsifier suite under fixed encoding budget B."""
    return {
        "causal_loss_under_b": run_causal_loss_under_b_episode(seed=seed, budget=budget),
        "opacity_only": run_opacity_only_episode(seed=seed, budget=budget),
        "no_causal_relevance": run_no_causal_relevance_episode(seed=seed, budget=budget),
        "unbounded_phi": run_unbounded_phi_episode(seed=seed, budget=budget),
        "length_only_hard": run_length_only_hard_episode(seed=seed, budget=budget),
        "faithful_under_b": run_faithful_under_b_episode(seed=seed, budget=budget),
    }


def score_att_n_proxy(episode: NonEmbedEpisode) -> dict[str, Any]:
    """Explore proxy scorecard — not an adopted N_H / C-ladder gate."""
    return {
        "att": "ATT-N",
        "att_n_evidence": episode.att_n_evidence,
        "d_h_proxy": episode.d_h_proxy,
        "delta_p_action": episode.delta_p_action,
        "twin_abstraction_fidelity": episode.twin_abstraction_fidelity,
        "phi_within_budget": episode.phi_within_budget,
        "opacity_only": episode.opacity_only,
        "compression_asymmetry": episode.compression_asymmetry,
        "budget": episode.budget.as_dict(),
        "emit_m0": False,
        "arm": episode.arm.value,
        "explore_dh_loss_floor": EXPLORE_DH_LOSS_FLOOR,
        "explore_delta_p_floor": EXPLORE_DELTA_P_FLOOR,
        "claim_allowed": False,
        "agi_star_claim": False,
        "c3_claim": False,
        "n_h_claim": False,
        "note": (
            "explore proxy only; ε / θ_N TBD; opacity ≠ N_H; "
            "compression asymmetry soft witness only"
        ),
    }


def summarize_att_n_batch(episodes: Sequence[NonEmbedEpisode]) -> dict[str, Any]:
    n = len(episodes)
    if n == 0:
        return {
            "n": 0,
            "att_n_evidence_rate": 0.0,
            "mean_d_h_proxy": 0.0,
            "mean_delta_p_action": 0.0,
            "emit_m0_rate": 0.0,
            "claim_allowed": False,
            "agi_star_claim": False,
            "c3_claim": False,
            "n_h_claim": False,
        }
    evidence = sum(1 for e in episodes if e.att_n_evidence)
    return {
        "n": n,
        "att_n_evidence_rate": evidence / n,
        "mean_d_h_proxy": sum(e.d_h_proxy for e in episodes) / n,
        "mean_delta_p_action": sum(e.delta_p_action for e in episodes) / n,
        "mean_twin_fidelity": sum(e.twin_abstraction_fidelity for e in episodes) / n,
        "opacity_only_rate": sum(1 for e in episodes if e.opacity_only) / n,
        "phi_within_budget_rate": sum(1 for e in episodes if e.phi_within_budget) / n,
        "mean_compression_asymmetry": sum(e.compression_asymmetry for e in episodes) / n,
        "emit_m0_rate": sum(1 for e in episodes if e.emit_m0) / n,
        "claim_allowed": False,
        "agi_star_claim": False,
        "c3_claim": False,
        "n_h_claim": False,
    }


def run_att_n_batch(
    *,
    n_seeds: int = 20,
    budget: EncodingBudget = EXPLORE_ENCODING_BUDGET_B,
) -> dict[str, Any]:
    """Explore ATT-N proxy across arms under pre-registered B (not an N_H gate)."""
    arms = {
        "causal_loss_under_b": [
            run_causal_loss_under_b_episode(seed=s, budget=budget) for s in range(n_seeds)
        ],
        "opacity_only": [
            run_opacity_only_episode(seed=s, budget=budget) for s in range(n_seeds)
        ],
        "no_causal_relevance": [
            run_no_causal_relevance_episode(seed=s, budget=budget) for s in range(n_seeds)
        ],
        "unbounded_phi": [
            run_unbounded_phi_episode(seed=s, budget=budget) for s in range(n_seeds)
        ],
        "length_only_hard": [
            run_length_only_hard_episode(seed=s, budget=budget) for s in range(n_seeds)
        ],
        "faithful_under_b": [
            run_faithful_under_b_episode(seed=s, budget=budget) for s in range(n_seeds)
        ],
    }
    return {
        "att": "ATT-N",
        "milestone": "M-N",
        "n_seeds": n_seeds,
        "encoding_budget_B": budget.as_dict(),
        "explore_dh_loss_floor": EXPLORE_DH_LOSS_FLOOR,
        "explore_delta_p_floor": EXPLORE_DELTA_P_FLOOR,
        "by_arm": {name: summarize_att_n_batch(eps) for name, eps in arms.items()},
        "claim_allowed": False,
        "agi_star_claim": False,
        "c3_claim": False,
        "c2_claim": False,
        "n_h_claim": False,
        "opacity_is_not_n_h": True,
    }
