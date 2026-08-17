"""Ports for models, sensors, contacts and tools.

Concrete integrations belong outside the cognitive core. These protocols make
the separation executable and easy to mock in safety evaluations.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from .models import ContactDecision, InitiativeProposal, Observation


class SensorAdapter(Protocol):
    def poll(self) -> Iterable[Observation]: ...


class CandidateModel(Protocol):
    def expand(self, proposals: tuple[InitiativeProposal, ...]) -> tuple[InitiativeProposal, ...]: ...


class ContactAdapter(Protocol):
    def deliver(self, proposal: InitiativeProposal, decision: ContactDecision) -> str: ...


class ToolAdapter(Protocol):
    capability: str
    reversible: bool

    def dry_run(self, proposal: InitiativeProposal) -> dict[str, object]: ...

    def execute(self, proposal: InitiativeProposal) -> dict[str, object]: ...


class MemoryAdapter(Protocol):
    def remember(self, key: str, value: dict[str, object]) -> None: ...

    def recall(self, query: str, limit: int = 8) -> tuple[dict[str, object], ...]: ...

