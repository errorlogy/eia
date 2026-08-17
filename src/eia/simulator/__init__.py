"""Simulator kernel — WorldState, clock, event bus, scenario loader."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

from eia.ids import new_id
from eia.schemas.observation import Observation, ObservationSource


@dataclass
class InjectedClock:
    """Deterministic simulated time — no wall-clock dependency in replay."""

    start: datetime = field(default_factory=lambda: datetime(2026, 8, 17, 9, 0, tzinfo=timezone.utc))
    tick_minutes: int = 15
    tick: int = 0

    @property
    def now(self) -> datetime:
        return self.start + timedelta(minutes=self.tick_minutes * self.tick)

    @property
    def hour(self) -> int:
        return self.now.hour

    def advance(self, steps: int = 1) -> datetime:
        self.tick += steps
        return self.now


@dataclass
class WorldState:
    """Typed world variables for twin world scenarios."""

    variables: dict[str, Any] = field(default_factory=dict)
    hidden: dict[str, Any] = field(default_factory=dict)
    user_present: bool = True
    last_user_event_tick: int = -1

    def set(self, key: str, value: Any, *, hidden: bool = False) -> None:
        if hidden:
            self.hidden[key] = value
        else:
            self.variables[key] = value


class EventBus:
    """In-process event bus with subscriber hooks."""

    def __init__(self) -> None:
        self._handlers: list[Callable[[Observation], None]] = []
        self.events: list[Observation] = []

    def subscribe(self, handler: Callable[[Observation], None]) -> None:
        self._handlers.append(handler)

    def emit(self, observation: Observation) -> None:
        self.events.append(observation)
        for h in self._handlers:
            h(observation)

    def user_events(self) -> list[Observation]:
        return [e for e in self.events if e.is_user_trigger]

    def remove_last_user_events(self, n: int = 1) -> list[Observation]:
        """Counterfactual intervention: strip last n user triggers."""
        user_idxs = [i for i, e in enumerate(self.events) if e.is_user_trigger]
        to_remove = set(user_idxs[-n:]) if user_idxs else set()
        removed = [self.events[i] for i in sorted(to_remove)]
        self.events = [e for i, e in enumerate(self.events) if i not in to_remove]
        return removed


@dataclass
class ScenarioEvent:
    tick: int
    source: str
    topic: str
    payload: dict[str, Any] = field(default_factory=dict)
    is_user_trigger: bool = False
    trust: float = 1.0


@dataclass
class Scenario:
    id: str
    title: str
    seed: int
    events: list[ScenarioEvent]
    initial_beliefs: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def load_scenario(path: Path) -> Scenario:
    """Load YAML scenario manifest."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    events = [
        ScenarioEvent(
            tick=e["tick"],
            source=e["source"],
            topic=e["topic"],
            payload=e.get("payload", {}),
            is_user_trigger=e.get("is_user_trigger", False),
            trust=e.get("trust", 1.0),
        )
        for e in data.get("events", [])
    ]
    return Scenario(
        id=data["id"],
        title=data["title"],
        seed=data.get("seed", 42),
        events=events,
        initial_beliefs=data.get("initial_beliefs", []),
        metadata=data.get("metadata", {}),
    )


class Simulator:
    """Run scenario against cognitive pipeline hooks."""

    def __init__(self, scenario: Scenario, *, seed: int | None = None) -> None:
        self.scenario = scenario
        self.clock = InjectedClock()
        self.world = WorldState()
        self.bus = EventBus()
        self.seed = seed if seed is not None else scenario.seed
        self._event_index = 0

    def _make_observation(self, ev: ScenarioEvent) -> Observation:
        return Observation(
            id=new_id("obs"),
            timestamp=self.clock.now,
            source=ObservationSource(ev.source),
            topic=ev.topic,
            payload=ev.payload,
            trust=ev.trust,
            is_user_trigger=ev.is_user_trigger,
            trace_id=self.scenario.id,
        )

    def run_until(self, max_tick: int) -> list[Observation]:
        """Advance clock and emit scenario events up to max_tick."""
        emitted: list[Observation] = []
        while self._event_index < len(self.scenario.events):
            ev = self.scenario.events[self._event_index]
            if ev.tick > max_tick:
                break
            while self.clock.tick < ev.tick:
                self.clock.advance()
            obs = self._make_observation(ev)
            if ev.is_user_trigger:
                self.world.last_user_event_tick = self.clock.tick
                self.world.user_present = ev.payload.get("user_present", True)
            self.bus.emit(obs)
            emitted.append(obs)
            self._event_index += 1
        return emitted

    def advance_quiet_period(self, ticks: int = 4) -> None:
        """Simulate user absence — drives should accumulate."""
        for _ in range(ticks):
            self.clock.advance()
            self.world.user_present = False
            self.bus.emit(
                Observation(
                    id=f"obs-quiet-{self.clock.tick}",
                    timestamp=self.clock.now,
                    source=ObservationSource.CLOCK_TICK,
                    topic="quiet_period",
                    payload={"user_present": False},
                    is_user_trigger=False,
                )
            )
