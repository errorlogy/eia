"""Baseline condition stubs for EXPERIMENTS.md evaluation protocol."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from eia.ids import new_id
from eia.schemas.contact import ContactDecision, ContactOutcome
from eia.schemas.initiative import Initiative, InitiativeCandidate, InitiativeKind
from eia.schemas.motivation import Motivation, MotivationSignal, DriveKind

if TYPE_CHECKING:
    from eia.pipeline import CognitiveLoop
    from eia.simulator import Simulator


class BaselineCondition(str, Enum):
    """First-wave baseline conditions (EXPERIMENTS.md §3)."""

    REACTIVE_ONLY = "reactive_only"
    SCHEDULED_STUB = "scheduled_stub"
    FULL_EIA = "full_eia"


def load_baseline_from_config(path: Path | None = None) -> BaselineCondition:
    """Load baseline from configs/experiment.json if present."""
    config_path = path or Path(__file__).resolve().parents[3] / "configs" / "experiment.json"
    if not config_path.is_file():
        return BaselineCondition.FULL_EIA
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    value = raw.get("baseline", BaselineCondition.FULL_EIA.value)
    return BaselineCondition(value)


def make_reactive_stub(loop: CognitiveLoop, sim: Simulator) -> tuple:
    """Reactive baseline: ingest only, mandatory abstain, no proactive cognition."""
    from eia.scheduler import PipelineStage
    from eia.audit import TraceNodeKind

    now = datetime.now(timezone.utc)
    motivation = Motivation(
        id="mot-reactive-stub",
        timestamp=now,
        dominant_drive=DriveKind.EPISTEMIC,
        signals=[
            MotivationSignal(
                drive=DriveKind.EPISTEMIC,
                intensity=0.0,
                error_term=0.0,
                explanation="reactive_only baseline: drives not evaluated",
            )
        ],
    )
    abstain = InitiativeCandidate(id=new_id("cand-abstain"), kind=InitiativeKind.ABSTAIN)
    initiative = Initiative(
        id=new_id("init-reactive"),
        timestamp=now,
        candidate=abstain,
        abstained=True,
        parent_motivation_id=motivation.id,
        evsi=0.0,
    )
    decision = ContactDecision(
        id=new_id("dec-reactive"),
        timestamp=now,
        initiative_id=initiative.id,
        outcome=ContactOutcome.ABSTAIN,
        contact_score=-1.0,
        reason="reactive_only baseline: no proactive initiative",
    )

    loop._record_stage(
        PipelineStage.MOTIVE_FORMATION,
        "reactive_only stub — skipped drive evaluation",
        {"baseline": BaselineCondition.REACTIVE_ONLY.value},
        trace_kind=TraceNodeKind.MOTIVE_FORMATION,
        parent_kind=TraceNodeKind.SENSE_MAKING,
    )
    loop._record_stage(
        PipelineStage.INTENTION_GENESIS,
        "reactive_only stub — mandatory abstain",
        {**initiative.model_dump(mode="json"), "baseline": BaselineCondition.REACTIVE_ONLY.value},
        trace_kind=TraceNodeKind.INTENTION_GENESIS,
        parent_kind=TraceNodeKind.MOTIVE_FORMATION,
    )
    loop._record_stage(
        PipelineStage.CONTACT_GOVERNOR,
        f"Outcome={decision.outcome.value}",
        decision.model_dump(mode="json"),
        trace_kind=TraceNodeKind.CONTACT_GOVERNOR,
        parent_kind=TraceNodeKind.INTENTION_GENESIS,
    )
    from eia.beliefs import BeliefField

    loop._snapshot_field = BeliefField.model_validate(loop.field.model_dump())
    loop.governor.state.current_tick = sim.clock.tick
    return motivation, initiative, decision, None


def cognition_tick_count(baseline: BaselineCondition) -> int:
    """How many cognition ticks to run for a baseline condition."""
    if baseline == BaselineCondition.REACTIVE_ONLY:
        return 0
    if baseline == BaselineCondition.SCHEDULED_STUB:
        return 1
    return 3
