"""Deterministic scenario runner and twin-world counterfactual harness."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .governors import ContactContext
from .models import Observation, PrivacyClass, TickResult
from .runtime import EIARuntime


@dataclass(frozen=True, slots=True)
class ScenarioEvent:
    at_seconds: float
    observation: Observation


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    starts_at: datetime
    events: tuple[ScenarioEvent, ...]
    final_tick_seconds: float


@dataclass(frozen=True, slots=True)
class SimulationResult:
    scenario: str
    results: tuple[TickResult, ...]
    runtime: EIARuntime


class SimulationRunner:
    def __init__(self, runtime_factory: type[EIARuntime] = EIARuntime) -> None:
        self.runtime_factory = runtime_factory

    def run(
        self,
        scenario: Scenario,
        *,
        remove_user_events: bool = False,
        interruption_load: float = 0.0,
    ) -> SimulationResult:
        runtime = self.runtime_factory()
        results: list[TickResult] = []
        for event in sorted(scenario.events, key=lambda item: item.at_seconds):
            if remove_user_events and event.observation.user_initiated:
                continue
            runtime.ingest(event.observation)
            now = scenario.starts_at + timedelta(seconds=event.at_seconds)
            results.append(runtime.tick(ContactContext(now=now, interruptibility=interruption_load)))
        final_now = scenario.starts_at + timedelta(seconds=scenario.final_tick_seconds)
        results.append(runtime.tick(ContactContext(now=final_now, interruptibility=interruption_load)))
        return SimulationResult(scenario.name, tuple(results), runtime)


def load_scenario(path: str | Path) -> Scenario:
    raw: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    starts_at = datetime.fromisoformat(raw["starts_at"])
    events: list[ScenarioEvent] = []
    for index, item in enumerate(raw["events"]):
        timestamp = starts_at + timedelta(seconds=float(item["at_seconds"]))
        observation = Observation(
            observation_id=str(item.get("observation_id", f"obs:{index:04d}")),
            source=str(item["source"]),
            kind=str(item["kind"]),
            payload=dict(item["payload"]),
            observed_at=timestamp,
            salience=float(item.get("salience", 0.5)),
            reliability=float(item.get("reliability", 0.8)),
            privacy_class=PrivacyClass(str(item.get("privacy_class", "personal"))),
            user_initiated=bool(item.get("user_initiated", False)),
        )
        events.append(ScenarioEvent(float(item["at_seconds"]), observation))
    return Scenario(
        str(raw["name"]),
        starts_at,
        tuple(events),
        float(raw["final_tick_seconds"]),
    )

