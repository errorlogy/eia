"""Twin-world intervention policies for counterfactual EOI estimation."""

from __future__ import annotations

from enum import Enum

from eia.schemas.observation import Observation


class TwinInterventionPolicy(str, Enum):
    """How user-initiated events are removed in twin-world counterfactual runs.

    REMOVE_LAST_USER_EVENT — strip only the last N user triggers (default N=1).
    Used by main EIA TwinRunner for partial counterfactual robustness.

    REMOVE_ALL_USER_INITIATED — strip every user-initiated observation.
    Used by research starter EndogeneityEstimator for aggressive counterfactuals.
    """

    REMOVE_LAST_USER_EVENT = "remove_last_user_event"
    REMOVE_ALL_USER_INITIATED = "remove_all_user_initiated"


DEFAULT_TWIN_POLICY = TwinInterventionPolicy.REMOVE_LAST_USER_EVENT
DEFAULT_REMOVE_LAST_N = 1


def apply_twin_intervention(
    events: list[Observation],
    policy: TwinInterventionPolicy,
    *,
    remove_last_n: int = DEFAULT_REMOVE_LAST_N,
) -> tuple[list[Observation], list[Observation]]:
    """Return (remaining_events, removed_events) after applying twin policy."""
    if policy == TwinInterventionPolicy.REMOVE_ALL_USER_INITIATED:
        removed = [e for e in events if e.is_user_trigger]
        remaining = [e for e in events if not e.is_user_trigger]
        return remaining, removed

    user_idxs = [i for i, e in enumerate(events) if e.is_user_trigger]
    to_remove = set(user_idxs[-remove_last_n:]) if user_idxs else set()
    removed = [events[i] for i in sorted(to_remove)]
    remaining = [e for i, e in enumerate(events) if i not in to_remove]
    return remaining, removed
