"""ATT-R live/shadow closed-loop scoring — maps main shadow events to recurrence.

Consumes event dicts from main `eia.runtime.shadow_multitick` (or fixtures) and
scores them with the same ATT-R falsifiers as M-R / `goal_recurrence`.

Does not claim AGI*, C3, or tau_AGI. emit_m0 must remain false.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .goal_recurrence import (
    KURAMOTO_HIGH_FLOOR,
    MIN_CLOSED_CYCLES,
    RecurrenceArm,
    RecurrenceEpisode,
    TraceNode,
    TraceNodeKind,
    score_att_r_proxy,
    score_trace_flags,
    summarize_att_r_batch,
)

# Map shadow_multitick kind strings → TraceNodeKind
_KIND_MAP: dict[str, TraceNodeKind] = {
    "W": TraceNodeKind.WORLD,
    "M": TraceNodeKind.META,
    "G": TraceNodeKind.GOAL,
    "Pi": TraceNodeKind.POLICY,
    "A": TraceNodeKind.ACTION,
    "X": TraceNodeKind.EXTERNAL,
    "W_prime": TraceNodeKind.WORLD_UPDATE,
    "G_prime": TraceNodeKind.NOVEL_MOTIVE,
    "schedule": TraceNodeKind.SCHEDULE,
    "kuramoto_R": TraceNodeKind.KURAMOTO_SYNC,
}


def events_to_nodes(events: Sequence[Mapping[str, Any]]) -> tuple[TraceNode, ...]:
    """Convert shadow AttREvent dicts to typed TraceNodes."""
    nodes: list[TraceNode] = []
    for ev in events:
        kind_raw = str(ev["kind"])
        kind = _KIND_MAP.get(kind_raw)
        if kind is None:
            # Allow enum values already matching TraceNodeKind.value
            try:
                kind = TraceNodeKind(kind_raw)
            except ValueError as exc:
                raise ValueError(f"unknown ATT-R event kind: {kind_raw}") from exc
        nodes.append(
            TraceNode(
                node_id=str(ev["node_id"]),
                kind=kind,
                label=str(ev.get("label", "")),
                parent_ids=tuple(ev.get("parent_ids") or ()),
                tick=int(ev.get("tick", 0)),
                novel=bool(ev.get("novel", False)),
            )
        )
    return tuple(nodes)


def episode_from_shadow_log(log: Mapping[str, Any]) -> RecurrenceEpisode:
    """Score one shadow multi-tick log under ATT-R (claim_allowed=False)."""
    arm = RecurrenceArm(str(log["arm"]))
    nodes = events_to_nodes(log.get("events") or [])
    flags = score_trace_flags(nodes)
    kuramoto_r = float(log.get("kuramoto_r") or 0.0)
    closed = flags["closed_cycle_count"]
    kuramoto_alone = (
        arm == RecurrenceArm.KURAMOTO_ONLY
        and kuramoto_r >= KURAMOTO_HIGH_FLOOR
        and closed == 0
    ) or bool(log.get("kuramoto_alone", False))
    return RecurrenceEpisode(
        arm=arm,
        nodes=nodes,
        kuramoto_r=kuramoto_r,
        kuramoto_alone=kuramoto_alone,
        emit_m0=False,
        claim_allowed=False,
        **flags,
    )


def score_shadow_suite(
    suite: Mapping[str, Mapping[str, Any]],
) -> dict[str, RecurrenceEpisode]:
    """Score a name→shadow-log mapping (e.g. run_shadow_falsifier_suite)."""
    return {name: episode_from_shadow_log(log) for name, log in suite.items()}


def run_live_att_r_batch_from_raw(
    by_arm_raw: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    n_seeds: int,
) -> dict[str, Any]:
    """Summarize scored shadow batch (explore proxy only)."""
    by_arm: dict[str, list[RecurrenceEpisode]] = {}
    for name, logs in by_arm_raw.items():
        by_arm[name] = [episode_from_shadow_log(log) for log in logs]
    return {
        "att": "ATT-R",
        "milestone": "M-R-LIVE",
        "n_seeds": n_seeds,
        "min_closed_cycles": MIN_CLOSED_CYCLES,
        "by_arm": {name: summarize_att_r_batch(eps) for name, eps in by_arm.items()},
        "claim_allowed": False,
        "agi_star_claim": False,
        "c3_claim": False,
        "c2_claim": False,
        "kuramoto_is_not_att_r": True,
        "emit_m0": False,
        "shadow": True,
        "live_telegram": False,
    }


def scorecard_from_shadow_log(log: Mapping[str, Any]) -> dict[str, Any]:
    """Explore proxy scorecard for one shadow episode."""
    return score_att_r_proxy(episode_from_shadow_log(log))
