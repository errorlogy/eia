"""Research stubs for C_non-emb(H) measurement (AGI* conjunct).

Not a production gate. Does not raise C-levels or claim AGI*.
See research/sci_flow/NON_EMBEDDABILITY_MEASUREMENT.md and AGI_STAR_CRITERION.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ProxyFamily = Literal[
    "projection_loss",
    "human_carrier_sufficiency",
    "cross_interpreter_disagreement",
    "tda_structural_witness",
]


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
