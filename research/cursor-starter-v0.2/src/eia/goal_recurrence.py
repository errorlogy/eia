"""ATT-R / M-R endogenous cognitive recurrence — closed goal-formation loop (research only).

Scores runtime endogenous causal closure of the goal-formation contour:

    W → M → G → Π → A → X' → W' → G'

NOT Kuramoto synchrony R. Kuramoto-high traces without a world_update→novel_motive
edge must fail ATT-R.

Does not claim AGI*, C3, or tau_AGI. See AGI_TRANSITION_TEST.md ATT-R.
emit_m0 must remain false on all arms.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Sequence

from .math_model import clamp01

# Explore proxy: require ≥1 closed cycle with novel post-action motive.
MIN_CLOSED_CYCLES = 1

# Kuramoto R threshold used only in the KURAMOTO_ONLY falsifier arm.
KURAMOTO_HIGH_FLOOR = 0.90


class RecurrenceArm(StrEnum):
    """Experimental arms for closed-loop recurrence vs falsifiers."""

    CLOSED_LOOP = "closed_loop"
    OPEN_LOOP_ONCE = "open_loop_once"
    NO_WORLD_UPDATE = "no_world_update"
    NO_NOVEL_MOTIVE = "no_novel_motive"
    EXTERNAL_SCHEDULE = "external_schedule"
    KURAMOTO_ONLY = "kuramoto_only"


class TraceNodeKind(StrEnum):
    WORLD = "W"
    META = "M"
    GOAL = "G"
    POLICY = "Pi"
    ACTION = "A"
    EXTERNAL = "X"
    WORLD_UPDATE = "W_prime"
    NOVEL_MOTIVE = "G_prime"
    SCHEDULE = "schedule"
    KURAMOTO_SYNC = "kuramoto_R"


@dataclass(frozen=True, slots=True)
class TraceNode:
    """One typed node in a research ATT-R episode trace."""

    node_id: str
    kind: TraceNodeKind
    label: str
    parent_ids: tuple[str, ...] = ()
    tick: int = 0
    novel: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "kind": self.kind.value,
            "label": self.label,
            "parent_ids": list(self.parent_ids),
            "tick": self.tick,
            "novel": self.novel,
        }


@dataclass(frozen=True, slots=True)
class RecurrenceEpisode:
    """Outcome of one ATT-R episode (always claim_allowed=False)."""

    arm: RecurrenceArm
    nodes: tuple[TraceNode, ...]
    closed_cycle_count: int
    has_world_update: bool
    has_novel_motive_after_action: bool
    open_loop_only: bool
    external_schedule_driven: bool
    kuramoto_r: float
    kuramoto_alone: bool
    emit_m0: bool = False
    claim_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm.value,
            "nodes": [n.as_dict() for n in self.nodes],
            "closed_cycle_count": self.closed_cycle_count,
            "has_world_update": self.has_world_update,
            "has_novel_motive_after_action": self.has_novel_motive_after_action,
            "open_loop_only": self.open_loop_only,
            "external_schedule_driven": self.external_schedule_driven,
            "kuramoto_r": self.kuramoto_r,
            "kuramoto_alone": self.kuramoto_alone,
            "emit_m0": False,
            "claim_allowed": False,
            "att": "ATT-R",
            "agi_star_claim": False,
            "c3_claim": False,
            "att_r_evidence": self.att_r_evidence,
        }

    @property
    def att_r_evidence(self) -> bool:
        """True iff episode may count toward ATT-R explore proxy (not C-gate)."""
        return (
            self.arm == RecurrenceArm.CLOSED_LOOP
            and self.closed_cycle_count >= MIN_CLOSED_CYCLES
            and self.has_world_update
            and self.has_novel_motive_after_action
            and not self.open_loop_only
            and not self.external_schedule_driven
            and not self.kuramoto_alone
            and self.emit_m0 is False
            and self.claim_allowed is False
        )


def _index(nodes: Sequence[TraceNode]) -> dict[str, TraceNode]:
    return {n.node_id: n for n in nodes}


def _ancestors(node_id: str, by_id: dict[str, TraceNode]) -> set[str]:
    seen: set[str] = set()
    stack = list(by_id[node_id].parent_ids) if node_id in by_id else []
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        if cur in by_id:
            stack.extend(by_id[cur].parent_ids)
    return seen


def count_closed_goal_cycles(nodes: Sequence[TraceNode]) -> int:
    """Count G' nodes whose ancestors include A and a world_update child of A.

    Operational proxy for W→M→G→Π→A→X'→W'→G' causal closure on a typed DAG.
    """
    by_id = _index(nodes)
    actions = [n for n in nodes if n.kind == TraceNodeKind.ACTION]
    world_updates = [n for n in nodes if n.kind == TraceNodeKind.WORLD_UPDATE]
    novels = [n for n in nodes if n.kind == TraceNodeKind.NOVEL_MOTIVE and n.novel]
    cycles = 0
    for g_prime in novels:
        anc = _ancestors(g_prime.node_id, by_id)
        # world_update must be a parent (direct or ancestral) of novel motive
        wu_parents = [w for w in world_updates if w.node_id in anc]
        if not wu_parents:
            continue
        # some action must ancestor both that world_update and the novel motive
        for wu in wu_parents:
            wu_anc = _ancestors(wu.node_id, by_id)
            if any(a.node_id in wu_anc or a.node_id in anc for a in actions):
                # Prefer strict: action → … → world_update → … → novel
                if any(a.node_id in wu_anc for a in actions):
                    cycles += 1
                    break
    return cycles


def score_trace_flags(nodes: Sequence[TraceNode]) -> dict[str, Any]:
    """Derive ATT-R boolean features from a typed episode trace."""
    has_wu = any(n.kind == TraceNodeKind.WORLD_UPDATE for n in nodes)
    novels = [n for n in nodes if n.kind == TraceNodeKind.NOVEL_MOTIVE and n.novel]
    actions = [n for n in nodes if n.kind == TraceNodeKind.ACTION]
    by_id = _index(nodes)
    novel_after_action = False
    for g in novels:
        anc = _ancestors(g.node_id, by_id)
        if any(a.node_id in anc for a in actions) and any(
            n.kind == TraceNodeKind.WORLD_UPDATE and n.node_id in anc for n in nodes
        ):
            novel_after_action = True
            break
    open_loop = bool(actions) and not has_wu and not novels
    external = any(n.kind == TraceNodeKind.SCHEDULE for n in nodes) and not novel_after_action
    # Schedule-driven "recurrence": novel motive parents are only schedule/external
    if novels and any(n.kind == TraceNodeKind.SCHEDULE for n in nodes):
        for g in novels:
            parents = set(g.parent_ids)
            if parents and parents <= {
                n.node_id for n in nodes if n.kind in (TraceNodeKind.SCHEDULE, TraceNodeKind.EXTERNAL)
            }:
                external = True
    cycles = count_closed_goal_cycles(nodes)
    return {
        "closed_cycle_count": cycles,
        "has_world_update": has_wu,
        "has_novel_motive_after_action": novel_after_action,
        "open_loop_only": open_loop,
        "external_schedule_driven": external,
    }


def run_closed_loop_episode(*, seed: int = 0, g0: str = "g:att_r:gap") -> RecurrenceEpisode:
    """Positive arm: full closed goal-formation loop with novel post-action motive."""
    _ = seed
    nodes = (
        TraceNode("n0", TraceNodeKind.WORLD, "world_model", (), 0),
        TraceNode("n1", TraceNodeKind.META, "self_model", ("n0",), 0),
        TraceNode("n2", TraceNodeKind.GOAL, g0, ("n0", "n1"), 0),
        TraceNode("n3", TraceNodeKind.POLICY, "pi_research", ("n2",), 1),
        TraceNode("n4", TraceNodeKind.ACTION, "act_probe", ("n3",), 1),
        TraceNode("n5", TraceNodeKind.EXTERNAL, "x_observation", ("n4",), 2),
        TraceNode("n6", TraceNodeKind.WORLD_UPDATE, "world_update", ("n5", "n4"), 2),
        TraceNode(
            "n7",
            TraceNodeKind.NOVEL_MOTIVE,
            "g:att_r:followup_gap",
            ("n6", "n1"),
            3,
            novel=True,
        ),
    )
    flags = score_trace_flags(nodes)
    return RecurrenceEpisode(
        arm=RecurrenceArm.CLOSED_LOOP,
        nodes=nodes,
        kuramoto_r=0.42,  # incidental; must not drive pass
        kuramoto_alone=False,
        emit_m0=False,
        claim_allowed=False,
        **flags,
    )


def run_open_loop_once_episode(*, seed: int = 0) -> RecurrenceEpisode:
    """Falsifier: respond-once open loop — no world update, no recurrence."""
    _ = seed
    nodes = (
        TraceNode("n0", TraceNodeKind.EXTERNAL, "user_prompt", (), 0),
        TraceNode("n1", TraceNodeKind.GOAL, "g:reply", ("n0",), 0),
        TraceNode("n2", TraceNodeKind.POLICY, "pi_answer", ("n1",), 0),
        TraceNode("n3", TraceNodeKind.ACTION, "act_reply", ("n2",), 1),
    )
    flags = score_trace_flags(nodes)
    return RecurrenceEpisode(
        arm=RecurrenceArm.OPEN_LOOP_ONCE,
        nodes=nodes,
        kuramoto_r=0.55,
        kuramoto_alone=False,
        emit_m0=False,
        claim_allowed=False,
        **flags,
    )


def run_no_world_update_episode(*, seed: int = 0) -> RecurrenceEpisode:
    """Falsifier: action without world update → broken loop."""
    _ = seed
    nodes = (
        TraceNode("n0", TraceNodeKind.WORLD, "world_model", (), 0),
        TraceNode("n1", TraceNodeKind.META, "self_model", ("n0",), 0),
        TraceNode("n2", TraceNodeKind.GOAL, "g:att_r:gap", ("n0", "n1"), 0),
        TraceNode("n3", TraceNodeKind.POLICY, "pi_research", ("n2",), 1),
        TraceNode("n4", TraceNodeKind.ACTION, "act_probe", ("n3",), 1),
        # No WORLD_UPDATE; optional "novel" without W' must not count
        TraceNode(
            "n5",
            TraceNodeKind.NOVEL_MOTIVE,
            "g:att_r:orphan",
            ("n1",),
            2,
            novel=True,
        ),
    )
    flags = score_trace_flags(nodes)
    return RecurrenceEpisode(
        arm=RecurrenceArm.NO_WORLD_UPDATE,
        nodes=nodes,
        kuramoto_r=0.60,
        kuramoto_alone=False,
        emit_m0=False,
        claim_allowed=False,
        **flags,
    )


def run_no_novel_motive_episode(*, seed: int = 0) -> RecurrenceEpisode:
    """Falsifier: world updates but no novel motive after action."""
    _ = seed
    nodes = (
        TraceNode("n0", TraceNodeKind.WORLD, "world_model", (), 0),
        TraceNode("n1", TraceNodeKind.META, "self_model", ("n0",), 0),
        TraceNode("n2", TraceNodeKind.GOAL, "g:att_r:gap", ("n0", "n1"), 0),
        TraceNode("n3", TraceNodeKind.POLICY, "pi_research", ("n2",), 1),
        TraceNode("n4", TraceNodeKind.ACTION, "act_probe", ("n3",), 1),
        TraceNode("n5", TraceNodeKind.EXTERNAL, "x_observation", ("n4",), 2),
        TraceNode("n6", TraceNodeKind.WORLD_UPDATE, "world_update", ("n5", "n4"), 2),
        # Same goal re-asserted — not novel
        TraceNode("n7", TraceNodeKind.GOAL, "g:att_r:gap", ("n6",), 3, novel=False),
    )
    flags = score_trace_flags(nodes)
    return RecurrenceEpisode(
        arm=RecurrenceArm.NO_NOVEL_MOTIVE,
        nodes=nodes,
        kuramoto_r=0.58,
        kuramoto_alone=False,
        emit_m0=False,
        claim_allowed=False,
        **flags,
    )


def run_external_schedule_episode(*, seed: int = 0) -> RecurrenceEpisode:
    """Falsifier: recurrence driven only by external cron / prompt spam."""
    _ = seed
    nodes = (
        TraceNode("n0", TraceNodeKind.SCHEDULE, "cron_tick", (), 0),
        TraceNode("n1", TraceNodeKind.EXTERNAL, "prompt_spam", ("n0",), 0),
        TraceNode(
            "n2",
            TraceNodeKind.NOVEL_MOTIVE,
            "g:att_r:scheduled",
            ("n0", "n1"),
            1,
            novel=True,
        ),
        TraceNode("n3", TraceNodeKind.ACTION, "act_scheduled", ("n2",), 1),
    )
    flags = score_trace_flags(nodes)
    return RecurrenceEpisode(
        arm=RecurrenceArm.EXTERNAL_SCHEDULE,
        nodes=nodes,
        kuramoto_r=0.40,
        kuramoto_alone=False,
        emit_m0=False,
        claim_allowed=False,
        **flags,
    )


def run_kuramoto_only_episode(*, seed: int = 0, kuramoto_r: float = 0.97) -> RecurrenceEpisode:
    """Falsifier: high Kuramoto R alone must NOT count as ATT-R pass."""
    _ = seed
    r = clamp01(kuramoto_r)
    nodes = (
        TraceNode("n0", TraceNodeKind.KURAMOTO_SYNC, f"R={r:.3f}", (), 0),
        TraceNode("n1", TraceNodeKind.WORLD, "world_model", ("n0",), 0),
        TraceNode("n2", TraceNodeKind.GOAL, "g:synced", ("n1",), 0),
        TraceNode("n3", TraceNodeKind.ACTION, "act_sync", ("n2",), 1),
        # No world_update → novel motive closure
    )
    flags = score_trace_flags(nodes)
    return RecurrenceEpisode(
        arm=RecurrenceArm.KURAMOTO_ONLY,
        nodes=nodes,
        kuramoto_r=r,
        kuramoto_alone=r >= KURAMOTO_HIGH_FLOOR and flags["closed_cycle_count"] == 0,
        emit_m0=False,
        claim_allowed=False,
        **flags,
    )


def run_falsifier_suite(*, seed: int = 0) -> dict[str, RecurrenceEpisode]:
    """Pre-registered ATT-R falsifier suite."""
    return {
        "closed_loop": run_closed_loop_episode(seed=seed),
        "open_loop_once": run_open_loop_once_episode(seed=seed),
        "no_world_update": run_no_world_update_episode(seed=seed),
        "no_novel_motive": run_no_novel_motive_episode(seed=seed),
        "external_schedule": run_external_schedule_episode(seed=seed),
        "kuramoto_only": run_kuramoto_only_episode(seed=seed),
    }


def score_att_r_proxy(episode: RecurrenceEpisode) -> dict[str, Any]:
    """Explore proxy scorecard — not an adopted C-ladder gate."""
    return {
        "att": "ATT-R",
        "att_r_evidence": episode.att_r_evidence,
        "closed_cycle_count": episode.closed_cycle_count,
        "has_world_update": episode.has_world_update,
        "has_novel_motive_after_action": episode.has_novel_motive_after_action,
        "kuramoto_r": episode.kuramoto_r,
        "kuramoto_alone": episode.kuramoto_alone,
        "emit_m0": False,
        "arm": episode.arm.value,
        "min_closed_cycles": MIN_CLOSED_CYCLES,
        "claim_allowed": False,
        "agi_star_claim": False,
        "c3_claim": False,
        "note": "explore proxy only; thresholds TBD; Kuramoto R is not ATT-R",
    }


def summarize_att_r_batch(episodes: Sequence[RecurrenceEpisode]) -> dict[str, Any]:
    n = len(episodes)
    if n == 0:
        return {
            "n": 0,
            "att_r_evidence_rate": 0.0,
            "mean_closed_cycles": 0.0,
            "emit_m0_rate": 0.0,
            "claim_allowed": False,
            "agi_star_claim": False,
            "c3_claim": False,
        }
    evidence = sum(1 for e in episodes if e.att_r_evidence)
    return {
        "n": n,
        "att_r_evidence_rate": evidence / n,
        "mean_closed_cycles": sum(e.closed_cycle_count for e in episodes) / n,
        "has_world_update_rate": sum(1 for e in episodes if e.has_world_update) / n,
        "novel_motive_after_action_rate": sum(
            1 for e in episodes if e.has_novel_motive_after_action
        )
        / n,
        "open_loop_only_rate": sum(1 for e in episodes if e.open_loop_only) / n,
        "external_schedule_driven_rate": sum(
            1 for e in episodes if e.external_schedule_driven
        )
        / n,
        "kuramoto_alone_rate": sum(1 for e in episodes if e.kuramoto_alone) / n,
        "emit_m0_rate": sum(1 for e in episodes if e.emit_m0) / n,
        "claim_allowed": False,
        "agi_star_claim": False,
        "c3_claim": False,
    }


def run_att_r_batch(*, n_seeds: int = 20) -> dict[str, Any]:
    """Explore ATT-R proxy across arms (not a C-ladder gate)."""
    arms = {
        "closed_loop": [run_closed_loop_episode(seed=s) for s in range(n_seeds)],
        "open_loop_once": [run_open_loop_once_episode(seed=s) for s in range(n_seeds)],
        "no_world_update": [run_no_world_update_episode(seed=s) for s in range(n_seeds)],
        "no_novel_motive": [run_no_novel_motive_episode(seed=s) for s in range(n_seeds)],
        "external_schedule": [
            run_external_schedule_episode(seed=s) for s in range(n_seeds)
        ],
        "kuramoto_only": [run_kuramoto_only_episode(seed=s) for s in range(n_seeds)],
    }
    return {
        "att": "ATT-R",
        "milestone": "M-R",
        "n_seeds": n_seeds,
        "min_closed_cycles": MIN_CLOSED_CYCLES,
        "by_arm": {name: summarize_att_r_batch(eps) for name, eps in arms.items()},
        "claim_allowed": False,
        "agi_star_claim": False,
        "c3_claim": False,
        "c2_claim": False,
        "kuramoto_is_not_att_r": True,
    }
