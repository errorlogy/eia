"""ATT-G / M-E goal genesis scaffold — research only.

Catalog targets remain novelty-capped below 0.75 (see measure_endogeneity_vector).
Non-catalog genesis requires reconstructible parents; does not claim AGI* or C3.
See research/sci_flow/AGI_TRANSITION_TEST.md ATT-G.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class GoalGenesisRecord:
    """One proposed non-catalog goal with genealogy stubs."""

    goal_id: str
    label: str
    catalog_target: bool
    parent_ids: tuple[str, ...]
    novelty_proxy: float
    claim_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "label": self.label,
            "catalog_target": self.catalog_target,
            "parent_ids": list(self.parent_ids),
            "novelty_proxy": self.novelty_proxy,
            "claim_allowed": False,
            "att": "ATT-G",
            "agi_star_claim": False,
        }


def propose_non_catalog_goal(
    *,
    seed_label: str,
    parent_ids: tuple[str, ...],
    goal_separation: float,
) -> GoalGenesisRecord:
    """Construct a non-catalog goal candidate (scaffold; not ATT-scored).

    Falsifier (pre-registered shape): empty parents or catalog_target=True
    must not count as genesis evidence.
    """
    if len(parent_ids) < 1:
        raise ValueError("goal genesis requires at least one reconstructible parent")
    novelty = min(1.0, 0.75 + 0.20 * max(0.0, min(1.0, goal_separation)))
    return GoalGenesisRecord(
        goal_id=f"goal:non_catalog:{seed_label}",
        label=f"non-catalog genesis from {seed_label}",
        catalog_target=False,
        parent_ids=parent_ids,
        novelty_proxy=round(novelty, 4),
        claim_allowed=False,
    )


def catalog_negative_control(*, target_id: str, parent_ids: tuple[str, ...]) -> GoalGenesisRecord:
    """Catalog path: novelty capped; not ATT-G pass evidence."""
    return GoalGenesisRecord(
        goal_id=f"goal:catalog:{target_id}",
        label=f"catalog selection {target_id}",
        catalog_target=True,
        parent_ids=parent_ids,
        novelty_proxy=0.74,
        claim_allowed=False,
    )
