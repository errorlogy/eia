"""Evaluation metrics for proactive initiative experiments."""

from __future__ import annotations

from dataclasses import dataclass

from .models import TickResult


@dataclass(frozen=True, slots=True)
class EvaluationSummary:
    ticks: int
    proposals: int
    selected: int
    contacts: int
    abstentions: int
    mean_selected_utility: float
    contact_rate: float


def summarize(results: tuple[TickResult, ...]) -> EvaluationSummary:
    ticks = len(results)
    selected_items = tuple(item for item in results if item.selected is not None)
    contacts = sum(bool(item.selected and item.selected.is_contact) for item in results)
    proposals = sum(len(item.alternatives) for item in results)
    selected = len(selected_items)
    mean_utility = sum(item.utility for item in selected_items) / selected if selected else 0.0
    return EvaluationSummary(
        ticks=ticks,
        proposals=proposals,
        selected=selected,
        contacts=contacts,
        abstentions=ticks - selected,
        mean_selected_utility=mean_utility,
        contact_rate=contacts / ticks if ticks else 0.0,
    )

