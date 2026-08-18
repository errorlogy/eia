"""Scenario ground-truth loading and scoring utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

KIND_MAP: dict[str, str] = {
    "ask": "ask_question",
    "notify": "notify",
    "observe": "observe",
    "research": "internal_research",
    "act": "act",
    "abstain": "abstain",
}


def load_ground_truth(scenario_path: Path) -> dict[str, Any] | None:
    """Load ground_truth block from a scenario YAML file."""
    data = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
    return data.get("ground_truth")


def expected_initiative_kind(label: dict[str, Any]) -> str:
    """Map ground-truth expected_kind to InitiativeKind value."""
    return KIND_MAP.get(label["expected_kind"], label["expected_kind"])


def score_initiative_against_label(run: dict, label: dict[str, Any]) -> dict:
    """Score one pipeline run against a single ground-truth initiative label."""
    initiative = run["initiative"]
    decision = run["decision"]
    twin = run["twin_result"]
    auth = run["authentic_verdict"]

    expected_kind = expected_initiative_kind(label)
    actual_kind = initiative.candidate.kind.value if initiative.candidate else None
    kind_match = actual_kind == expected_kind

    contact_made = decision.outcome.value in ("send_now", "defer")
    proactive = not initiative.abstained

    if label["expected_kind"] == "abstain":
        precision_hit = initiative.abstained or decision.outcome.value == "abstain"
        contact_useful = False
    else:
        eoi_ok = (
            twin.eoi >= 0.5 if label.get("counterfactual_should_persist", True) else True
        )
        endogenous_ok = auth.initiative_class == "endogenous" or label.get("source_family") == "ambient"
        precision_hit = (
            proactive
            and kind_match
            and eoi_ok
            and endogenous_ok
        )
        contact_useful = contact_made and precision_hit

    channel_ok = "in_app" in label.get("allowed_channels", ["in_app"])
    if contact_made and not channel_ok:
        contact_useful = False

    return {
        "expected_kind": label["expected_kind"],
        "expected_target": label.get("target"),
        "actual_kind": actual_kind,
        "kind_match": kind_match,
        "initiative_abstained": initiative.abstained,
        "contact_outcome": decision.outcome.value,
        "contact_made": contact_made,
        "eoi": round(twin.eoi, 4),
        "initiative_class": auth.initiative_class,
        "precision_hit": precision_hit,
        "contact_useful": contact_useful,
        "label_source": label.get("label_source"),
    }
