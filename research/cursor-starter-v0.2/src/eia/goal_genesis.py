"""ATT-G / M-E goal genesis — endogenous goal-space expansion (research only).

Distinguishes:
  * selection — pick g from fixed catalog G_t (novelty capped < 0.75)
  * genesis   — compose g* ∉ G_t from world-model tension with reconstructible
                genealogy S → ΔW → M → g* → Π*

Does not claim AGI*, C3, or EIS-8. Catalog path alone cannot raise EIS-7 novelty.
See research/sci_flow/AGI_TRANSITION_TEST.md ATT-G / ATT-C.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping, Sequence

from .endogenous import EndogenousSpectrumLevel, measure_endogeneity_vector
from .math_model import clamp01


# Fixed designer catalog G_t at tick t (selection only).
CATALOG_GOAL_IDS: frozenset[str] = frozenset(
    {
        "wm:causal_gap",
        "self:capability_drift",
        "collaboration:latent_question",
    }
)

# Minimum typed parents for ATT-C co-requirement on genesis.
REQUIRED_GENEALOGY_ROLES: tuple[str, ...] = (
    "state",
    "delta_w",
    "motive",
    "goal",
    "policy",
)

# Pre-registered explore proxies (not C-ladder gates until metrics report adopts).
NOVELTY_GENESIS_FLOOR = 0.75
CATALOG_NOVELTY_CAP = 0.74
MIN_WORLD_MODEL_TENSION = 0.35
MIN_GENEALOGY_PARENTS = 3  # distinct parent event ids covering roles


class GenesisPath(StrEnum):
    SELECTION = "selection"
    GENESIS = "genesis"
    REJECTED = "rejected"


class RejectionReason(StrEnum):
    EMPTY_GENEALOGY = "empty_genealogy"
    INCOMPLETE_GENEALOGY = "incomplete_genealogy"
    ZERO_TENSION = "zero_world_model_tension"
    IN_CATALOG = "g_star_in_catalog"
    RANDOM_WORDING = "random_novel_wording_without_genealogy"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True, slots=True)
class GenealogyNode:
    """One typed link in S → ΔW → M → g* → Π*."""

    role: str
    node_id: str
    summary: str

    def as_dict(self) -> dict[str, Any]:
        return {"role": self.role, "node_id": self.node_id, "summary": self.summary}


@dataclass(frozen=True, slots=True)
class GoalGenesisRecord:
    """Outcome of selection or genesis attempt (always claim_allowed=False)."""

    goal_id: str
    label: str
    catalog_target: bool
    in_g_t: bool
    parent_ids: tuple[str, ...]
    genealogy: tuple[GenealogyNode, ...]
    novelty_proxy: float
    world_model_tension: float
    path: GenesisPath
    rejection_reason: str | None
    completion_criterion: str
    preferred_policy: str
    claim_allowed: bool = False
    eis_level_name: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "label": self.label,
            "catalog_target": self.catalog_target,
            "in_g_t": self.in_g_t,
            "parent_ids": list(self.parent_ids),
            "genealogy": [node.as_dict() for node in self.genealogy],
            "novelty_proxy": self.novelty_proxy,
            "world_model_tension": self.world_model_tension,
            "path": self.path.value,
            "rejection_reason": self.rejection_reason,
            "completion_criterion": self.completion_criterion,
            "preferred_policy": self.preferred_policy,
            "claim_allowed": False,
            "eis_level_name": self.eis_level_name,
            "att": "ATT-G",
            "agi_star_claim": False,
            "c3_claim": False,
        }

    @property
    def att_g_evidence(self) -> bool:
        """True iff this record may count toward ATT-G explore proxy."""
        return (
            self.path == GenesisPath.GENESIS
            and not self.catalog_target
            and not self.in_g_t
            and self.novelty_proxy >= NOVELTY_GENESIS_FLOOR
            and self.rejection_reason is None
            and _genealogy_complete(self.genealogy)
            and self.world_model_tension >= MIN_WORLD_MODEL_TENSION
            and self.claim_allowed is False
        )


def catalog_ids() -> frozenset[str]:
    return CATALOG_GOAL_IDS


def is_in_catalog(goal_id: str) -> bool:
    return goal_id in CATALOG_GOAL_IDS


def _slug(text: str, *, max_len: int = 48) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9:_-]+", "_", text.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned[:max_len] or "composed"


def _digest(*parts: str) -> str:
    material = "|".join(parts)
    return hashlib.sha256(material.encode()).hexdigest()[:12]


def _genealogy_complete(genealogy: Sequence[GenealogyNode]) -> bool:
    roles = {node.role for node in genealogy}
    return all(role in roles for role in REQUIRED_GENEALOGY_ROLES) and len(genealogy) >= len(
        REQUIRED_GENEALOGY_ROLES
    )


def _parent_ids_from_genealogy(genealogy: Sequence[GenealogyNode]) -> tuple[str, ...]:
    return tuple(node.node_id for node in genealogy)


def build_genealogy(
    *,
    seed: int,
    state_summary: str,
    delta_w_summary: str,
    motive_summary: str,
    goal_id: str,
    policy_summary: str,
) -> tuple[GenealogyNode, ...]:
    """Construct typed S → ΔW → M → g* → Π* parents (ATT-C co-requirement)."""
    base = f"gen|{seed}"
    return (
        GenealogyNode(
            role="state",
            node_id=f"woe:state:{_digest(base, 'state', state_summary)}",
            summary=state_summary,
        ),
        GenealogyNode(
            role="delta_w",
            node_id=f"woe:delta_w:{_digest(base, 'delta_w', delta_w_summary)}",
            summary=delta_w_summary,
        ),
        GenealogyNode(
            role="motive",
            node_id=f"woe:motive:{_digest(base, 'motive', motive_summary)}",
            summary=motive_summary,
        ),
        GenealogyNode(
            role="goal",
            node_id=f"woe:goal:{_digest(base, 'goal', goal_id)}",
            summary=goal_id,
        ),
        GenealogyNode(
            role="policy",
            node_id=f"woe:policy:{_digest(base, 'policy', policy_summary)}",
            summary=policy_summary,
        ),
    )


def catalog_negative_control(
    *,
    target_id: str,
    parent_ids: tuple[str, ...] = (),
    goal_separation: float = 1.0,
    world_model_tension: float = 0.8,
) -> GoalGenesisRecord:
    """Selection path: g ∈ G_t; novelty capped; not ATT-G pass evidence."""
    if target_id not in CATALOG_GOAL_IDS:
        # Still treat as catalog-style selection of a designer id.
        pass
    novelty = clamp01(0.35 + 0.40 * goal_separation)
    if novelty >= NOVELTY_GENESIS_FLOOR:
        novelty = CATALOG_NOVELTY_CAP
    genealogy = tuple(
        GenealogyNode(role="external", node_id=pid, summary="catalog_parent")
        for pid in parent_ids
    )
    return GoalGenesisRecord(
        goal_id=f"goal:catalog:{target_id}",
        label=f"catalog selection {target_id}",
        catalog_target=True,
        in_g_t=True,
        parent_ids=parent_ids,
        genealogy=genealogy,
        novelty_proxy=round(novelty, 4),
        world_model_tension=clamp01(world_model_tension),
        path=GenesisPath.SELECTION,
        rejection_reason=None,
        completion_criterion=f"resolve catalog target {target_id}",
        preferred_policy="select_catalog",
        claim_allowed=False,
        eis_level_name=EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT.name,
    )


def random_novel_wording_control(
    *,
    seed: int,
    wording: str,
) -> GoalGenesisRecord:
    """Falsifier: novel surface form without genealogy / tension ≠ genesis."""
    slug = _slug(wording)
    goal_id = f"goal:wording:{slug}:{_digest(str(seed), wording)}"
    return GoalGenesisRecord(
        goal_id=goal_id,
        label=wording,
        catalog_target=False,
        in_g_t=False,
        parent_ids=(),
        genealogy=(),
        novelty_proxy=0.92,
        world_model_tension=0.0,
        path=GenesisPath.REJECTED,
        rejection_reason=RejectionReason.RANDOM_WORDING.value,
        completion_criterion="none — wording-only control",
        preferred_policy="none",
        claim_allowed=False,
        eis_level_name=None,
    )


def propose_non_catalog_goal(
    *,
    seed_label: str,
    parent_ids: tuple[str, ...],
    goal_separation: float,
    world_model_tension: float = 0.8,
    seed: int = 0,
) -> GoalGenesisRecord:
    """Compose a non-catalog goal candidate when genealogy parents exist.

    Falsifier (pre-registered): empty parents must not count as genesis evidence.
    """
    if len(parent_ids) < 1:
        raise ValueError("goal genesis requires at least one reconstructible parent")

    tension = clamp01(world_model_tension)
    if tension < MIN_WORLD_MODEL_TENSION:
        return GoalGenesisRecord(
            goal_id=f"goal:rejected:low_tension:{_slug(seed_label)}",
            label=f"rejected genesis (low tension) from {seed_label}",
            catalog_target=False,
            in_g_t=False,
            parent_ids=parent_ids,
            genealogy=(),
            novelty_proxy=0.0,
            world_model_tension=tension,
            path=GenesisPath.REJECTED,
            rejection_reason=RejectionReason.ZERO_TENSION.value,
            completion_criterion="none",
            preferred_policy="abstain",
            claim_allowed=False,
        )

    # Compose g* from tension factors — not a catalog id.
    composed_core = _slug(f"compose_{seed_label}_t{tension:.2f}_s{goal_separation:.2f}")
    goal_id = f"goal:genesis:{composed_core}:{_digest(str(seed), seed_label, f'{tension:.4f}')}"
    if is_in_catalog(goal_id) or any(goal_id.endswith(cid) for cid in CATALOG_GOAL_IDS):
        # Extremely unlikely; force out of catalog namespace.
        goal_id = f"goal:genesis:forced:{_digest(goal_id, 'out')}"

    policy = "internal_research"
    genealogy = build_genealogy(
        seed=seed,
        state_summary=f"window_state:{seed_label}",
        delta_w_summary=f"epistemic_tension={tension:.4f}",
        motive_summary=f"motive_from:{seed_label}",
        goal_id=goal_id,
        policy_summary=policy,
    )
    # Merge caller parents into genealogy ids for reconstructibility.
    merged_parents = tuple(dict.fromkeys((*parent_ids, *_parent_ids_from_genealogy(genealogy))))
    if len(merged_parents) < MIN_GENEALOGY_PARENTS and not _genealogy_complete(genealogy):
        return GoalGenesisRecord(
            goal_id=goal_id,
            label=f"rejected genesis (incomplete genealogy) from {seed_label}",
            catalog_target=False,
            in_g_t=False,
            parent_ids=merged_parents,
            genealogy=genealogy,
            novelty_proxy=0.0,
            world_model_tension=tension,
            path=GenesisPath.REJECTED,
            rejection_reason=RejectionReason.INCOMPLETE_GENEALOGY.value,
            completion_criterion="none",
            preferred_policy="abstain",
            claim_allowed=False,
        )

    novelty = clamp01(0.75 + 0.20 * max(0.0, min(1.0, goal_separation)))
    vector = measure_endogeneity_vector(
        prompts_applied=0,
        epistemic_pressure=tension,
        peak_coherence=0.80,
        goal_separation=goal_separation,
        self_prior_mismatch=0.55,
        mean_staleness=0.70,
        catalog_target=False,
    )
    return GoalGenesisRecord(
        goal_id=goal_id,
        label=f"non-catalog genesis from {seed_label}",
        catalog_target=False,
        in_g_t=False,
        parent_ids=merged_parents,
        genealogy=genealogy,
        novelty_proxy=round(novelty, 4),
        world_model_tension=tension,
        path=GenesisPath.GENESIS,
        rejection_reason=None,
        completion_criterion=(
            f"reduce world-model tension below {MIN_WORLD_MODEL_TENSION} "
            f"for composed goal {composed_core}"
        ),
        preferred_policy=policy,
        claim_allowed=False,
        eis_level_name=vector.classify().name,
    )


def compose_from_world_state(
    *,
    seed: int,
    catalog_snapshot: Sequence[str],
    epistemic_pressure: float,
    goal_separation: float,
    top_target_id: str,
    top_target_label: str,
    self_prior_mismatch: float,
    prospective_tension: float,
    peak_coherence: float = 0.75,
    prompts_applied: int = 0,
) -> GoalGenesisRecord:
    """Primary ATT-G constructor: g* from state tension, g* ∉ G_t.

    Requires catalog_snapshot ≈ G_t. Without world-model tension → rejected.
    """
    g_t = frozenset(catalog_snapshot) | CATALOG_GOAL_IDS
    tension = clamp01(epistemic_pressure)

    if tension < MIN_WORLD_MODEL_TENSION:
        return GoalGenesisRecord(
            goal_id="goal:rejected:zero_tension",
            label="rejected: no world-model tension",
            catalog_target=False,
            in_g_t=False,
            parent_ids=(),
            genealogy=(),
            novelty_proxy=0.0,
            world_model_tension=tension,
            path=GenesisPath.REJECTED,
            rejection_reason=RejectionReason.ZERO_TENSION.value,
            completion_criterion="none",
            preferred_policy="abstain",
            claim_allowed=False,
        )

    # Instrumental composition from latent factors — not catalog selection.
    factors = (
        f"gap:{top_target_id}",
        f"mismatch:{self_prior_mismatch:.3f}",
        f"prospective:{prospective_tension:.3f}",
        f"sep:{goal_separation:.3f}",
    )
    composed = _slug("_".join(factors), max_len=64)
    goal_id = f"goal:genesis:{composed}:{_digest(str(seed), *factors)}"
    if goal_id in g_t or any(cid in goal_id for cid in g_t if ":" in cid):
        # Ensure g* ∉ G_t even if slug collides with a catalog fragment.
        goal_id = f"goal:genesis:x{_digest(goal_id, 'escape')}"

    policy = "internal_research"
    label = (
        f"compose instrumental subgoal from tension on '{top_target_label}' "
        f"(sep={goal_separation:.3f})"
    )
    genealogy = build_genealogy(
        seed=seed,
        state_summary=f"seed={seed};pressure={tension:.4f};coherence={peak_coherence:.4f}",
        delta_w_summary=(
            f"ΔW from {top_target_id}; mismatch={self_prior_mismatch:.4f}; "
            f"prospective={prospective_tension:.4f}"
        ),
        motive_summary=f"autotelic_drive:{top_target_id}",
        goal_id=goal_id,
        policy_summary=policy,
    )
    parent_ids = _parent_ids_from_genealogy(genealogy)
    novelty = clamp01(0.75 + 0.20 * clamp01(goal_separation))
    vector = measure_endogeneity_vector(
        prompts_applied=prompts_applied,
        epistemic_pressure=tension,
        peak_coherence=peak_coherence,
        goal_separation=goal_separation,
        self_prior_mismatch=self_prior_mismatch,
        mean_staleness=0.65,
        catalog_target=False,
    )
    level = vector.classify()
    in_g = goal_id in g_t
    if in_g:
        return GoalGenesisRecord(
            goal_id=goal_id,
            label=label,
            catalog_target=True,
            in_g_t=True,
            parent_ids=parent_ids,
            genealogy=genealogy,
            novelty_proxy=CATALOG_NOVELTY_CAP,
            world_model_tension=tension,
            path=GenesisPath.REJECTED,
            rejection_reason=RejectionReason.IN_CATALOG.value,
            completion_criterion="none",
            preferred_policy=policy,
            claim_allowed=False,
            eis_level_name=level.name,
        )

    return GoalGenesisRecord(
        goal_id=goal_id,
        label=label,
        catalog_target=False,
        in_g_t=False,
        parent_ids=parent_ids,
        genealogy=genealogy,
        novelty_proxy=round(novelty, 4),
        world_model_tension=tension,
        path=GenesisPath.GENESIS,
        rejection_reason=None,
        completion_criterion=(
            f"falsifiable: tension on {top_target_id} falls below "
            f"{MIN_WORLD_MODEL_TENSION} without catalog template match"
        ),
        preferred_policy=policy,
        claim_allowed=False,
        eis_level_name=level.name,
    )


def score_att_g_proxy(record: GoalGenesisRecord) -> dict[str, Any]:
    """Explore proxy fields for ATT-G (thresholds TBD until metrics adopt)."""
    novelty_ok = record.novelty_proxy >= NOVELTY_GENESIS_FLOOR
    catalog_ok = record.catalog_target is False
    genealogy_ok = _genealogy_complete(record.genealogy)
    eis7_eligible = (
        record.eis_level_name == EndogenousSpectrumLevel.EIS_7_AUTOTELIC_GOAL_CONSTRUCTION.name
    )
    return {
        "att_g_evidence": record.att_g_evidence,
        "novelty_ge_075": novelty_ok,
        "catalog_target_false": catalog_ok,
        "genealogy_complete": genealogy_ok,
        "eis7_taxonomy_eligible": eis7_eligible,
        "claim_allowed": False,
        "agi_star_claim": False,
    }


def summarize_att_g_batch(records: Sequence[GoalGenesisRecord]) -> dict[str, Any]:
    """Aggregate ATT-G explore metrics over a seed batch."""
    n = len(records)
    if n == 0:
        return {
            "n": 0,
            "genesis_rate": 0.0,
            "att_g_evidence_rate": 0.0,
            "selection_rate": 0.0,
            "rejected_rate": 0.0,
            "mean_novelty_genesis": 0.0,
            "catalog_capped_fraction": 0.0,
            "claim_allowed": False,
            "agi_star_claim": False,
            "c3_claim": False,
        }
    genesis = [r for r in records if r.path == GenesisPath.GENESIS]
    evidence = [r for r in records if r.att_g_evidence]
    selection = [r for r in records if r.path == GenesisPath.SELECTION]
    rejected = [r for r in records if r.path == GenesisPath.REJECTED]
    catalog_capped = [
        r for r in records if r.catalog_target and r.novelty_proxy < NOVELTY_GENESIS_FLOOR
    ]
    mean_nov = (
        sum(r.novelty_proxy for r in genesis) / len(genesis) if genesis else 0.0
    )
    return {
        "n": n,
        "genesis_rate": len(genesis) / n,
        "att_g_evidence_rate": len(evidence) / n,
        "selection_rate": len(selection) / n,
        "rejected_rate": len(rejected) / n,
        "mean_novelty_genesis": round(mean_nov, 4),
        "catalog_capped_fraction": len(catalog_capped) / n,
        "claim_allowed": False,
        "agi_star_claim": False,
        "c3_claim": False,
        "falsifier_notes": {
            "random_wording_neq_genesis": True,
            "genealogy_required": True,
            "zero_tension_rejects": True,
            "catalog_novelty_cap": CATALOG_NOVELTY_CAP,
        },
    }


def run_falsifier_suite(*, seed: int = 0) -> Mapping[str, GoalGenesisRecord]:
    """Deterministic controls for pre-registered ATT-G falsifiers."""
    wording = random_novel_wording_control(
        seed=seed,
        wording=f"brand new shiny objective number {seed}",
    )
    catalog = catalog_negative_control(
        target_id="wm:causal_gap",
        parent_ids=("ext:designer:1",),
        goal_separation=1.0,
    )
    zero = compose_from_world_state(
        seed=seed,
        catalog_snapshot=tuple(CATALOG_GOAL_IDS),
        epistemic_pressure=0.0,
        goal_separation=1.0,
        top_target_id="wm:causal_gap",
        top_target_label="causal gap",
        self_prior_mismatch=0.9,
        prospective_tension=0.9,
    )
    ok = compose_from_world_state(
        seed=seed,
        catalog_snapshot=tuple(CATALOG_GOAL_IDS),
        epistemic_pressure=0.85,
        goal_separation=0.9,
        top_target_id="wm:causal_gap",
        top_target_label="unexplained causal gap",
        self_prior_mismatch=0.7,
        prospective_tension=0.8,
        peak_coherence=0.88,
    )
    return {
        "random_wording": wording,
        "catalog_selection": catalog,
        "zero_tension": zero,
        "genesis_ok": ok,
    }
