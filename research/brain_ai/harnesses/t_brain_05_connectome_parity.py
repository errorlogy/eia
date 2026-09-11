"""T-BRAIN-05 — multi-source connectome parity (spec stub).

Compares spike→OMEGA→shadow pipeline across connectome sources:
``google_male_cns``, ``flywire_female``, ``synthetic``, ``bundled_tiny``.

Tier C · ``claim_allowed=false`` · no AGI* · C2 ceiling.

Implementation deferred until offline ego-network exports exist locally.
See ``research/brain_ai/data/README.md`` and ``CONNECTOME_SOURCES.md``.
"""

from __future__ import annotations

from typing import Any

PARITY_SOURCES: tuple[str, ...] = (
    "bundled_tiny",
    "synthetic",
    "google_male_cns",
    "flywire_female",
)

HARNESS_ID = "T-BRAIN-05"
MILESTONE = "M-BRAIN-AI"


def build_t_brain_05_spec() -> dict[str, Any]:
    """Return T-BRAIN-05 harness spec (no artifact run yet)."""
    return {
        "milestone": MILESTONE,
        "harness_id": HARNESS_ID,
        "tier": "C",
        "claim_ceiling": "C2",
        "claim_allowed": False,
        "agi_star_claim": False,
        "status": "spec_stub",
        "sources": list(PARITY_SOURCES),
        "metrics_planned": [
            "omega_t_span_per_source",
            "kuramoto_r_per_source",
            "shadow_genesis_delta_parity",
            "male_vs_female_subgraph_structural_distance",
        ],
        "falsifiers": [
            "F-OMEGA-DECOR",
            "F-SOURCE-PARITY-BLEED",
        ],
        "note": (
            "Multi-source connectome parity — observational crosswalk only. "
            "Does not establish E_endo or raise C-level."
        ),
    }
