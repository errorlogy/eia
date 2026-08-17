"""Tests for twin intervention policy."""

from __future__ import annotations

from datetime import datetime, timezone

from eia.audit import TwinInterventionPolicy, TwinRunner, apply_twin_intervention
from eia.schemas.observation import Observation, ObservationSource
from eia.simulator import EventBus


def _obs(topic: str, *, user: bool) -> Observation:
    return Observation(
        id=f"obs-{topic}",
        timestamp=datetime.now(timezone.utc),
        source=ObservationSource.USER_MESSAGE if user else ObservationSource.WORLD_EVENT,
        topic=topic,
        is_user_trigger=user,
    )


def test_remove_last_user_event_policy() -> None:
    events = [_obs("a", user=True), _obs("b", user=False), _obs("c", user=True)]
    remaining, removed = apply_twin_intervention(
        events,
        TwinInterventionPolicy.REMOVE_LAST_USER_EVENT,
        remove_last_n=1,
    )
    assert [e.topic for e in removed] == ["c"]
    assert [e.topic for e in remaining] == ["a", "b"]


def test_remove_all_user_initiated_policy() -> None:
    events = [_obs("a", user=True), _obs("b", user=False), _obs("c", user=True)]
    remaining, removed = apply_twin_intervention(
        events,
        TwinInterventionPolicy.REMOVE_ALL_USER_INITIATED,
    )
    assert {e.topic for e in removed} == {"a", "c"}
    assert [e.topic for e in remaining] == ["b"]


def test_event_bus_apply_twin_policy() -> None:
    bus = EventBus()
    for ev in [_obs("u1", user=True), _obs("w", user=False), _obs("u2", user=True)]:
        bus.emit(ev)
    removed = bus.apply_twin_policy(TwinInterventionPolicy.REMOVE_LAST_USER_EVENT)
    assert len(removed) == 1
    assert removed[0].topic == "u2"
    assert len(bus.events) == 2


def test_twin_runner_stores_policy() -> None:
    runner = TwinRunner(
        policy=TwinInterventionPolicy.REMOVE_ALL_USER_INITIATED,
        remove_last_n=2,
    )
    assert runner.policy == TwinInterventionPolicy.REMOVE_ALL_USER_INITIATED
    assert runner.remove_last_n == 2
