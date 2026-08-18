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
    EVENT_RULE = "event_rule"
    PREDICTIVE_P3 = "predictive_p3"
    FULL_EIA = "full_eia"


DEFAULT_EVENT_RULE_SALIENCE = 0.30
DEFAULT_PREDICTIVE_P3_NEED = 0.55


def load_event_rule_salience(path: Path | None = None) -> float:
    """Load event-rule salience threshold from configs/experiment.json."""
    config_path = path or Path(__file__).resolve().parents[3] / "configs" / "experiment.json"
    if not config_path.is_file():
        return DEFAULT_EVENT_RULE_SALIENCE
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return float(raw.get("event_rule_salience", DEFAULT_EVENT_RULE_SALIENCE))


def load_predictive_p3_need(path: Path | None = None) -> float:
    """Load predictive P3 need threshold from configs/experiment.json."""
    config_path = path or Path(__file__).resolve().parents[3] / "configs" / "experiment.json"
    if not config_path.is_file():
        return DEFAULT_PREDICTIVE_P3_NEED
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    return float(raw.get("predictive_p3_need", DEFAULT_PREDICTIVE_P3_NEED))


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


def make_event_rule_stub(
    loop: CognitiveLoop,
    sim: Simulator,
    *,
    salience_threshold: float | None = None,
) -> tuple:
    """Event-rule baseline: one cognition pass gated by max drive salience."""
    from eia.audit import TraceNodeKind
    from eia.beliefs import BeliefField
    from eia.scheduler import PipelineStage
    from eia.schemas.motivation import DriveKind

    threshold = (
        salience_threshold
        if salience_threshold is not None
        else load_event_rule_salience()
    )
    now = datetime.now(timezone.utc)
    comprehension = loop._last_comprehension or loop.sense_making.snapshot()

    novelty = {DriveKind.EPISTEMIC: 0.15, DriveKind.COHERENCE: 0.20}
    loop._motivation_count += 1
    motivation = loop.drives.compute(
        loop.field,
        novelty_events=novelty,
        motivation_id=f"mot-event-rule-{loop._motivation_count}",
    )
    max_salience = max((s.intensity for s in motivation.signals), default=0.0)

    loop._record_stage(
        PipelineStage.MOTIVE_FORMATION,
        f"event_rule salience={max_salience:.3f} threshold={threshold}",
        {
            **motivation.model_dump(mode="json"),
            "baseline": BaselineCondition.EVENT_RULE.value,
            "salience_threshold": threshold,
            "max_salience": max_salience,
        },
        trace_kind=TraceNodeKind.MOTIVE_FORMATION,
        parent_kind=TraceNodeKind.SENSE_MAKING,
    )

    if max_salience < threshold:
        abstain = InitiativeCandidate(id=new_id("cand-abstain"), kind=InitiativeKind.ABSTAIN)
        initiative = Initiative(
            id=new_id("init-event-rule"),
            timestamp=now,
            candidate=abstain,
            abstained=True,
            parent_motivation_id=motivation.id,
            evsi=0.0,
        )
        decision = ContactDecision(
            id=new_id("dec-event-rule"),
            timestamp=now,
            initiative_id=initiative.id,
            outcome=ContactOutcome.ABSTAIN,
            contact_score=-1.0,
            reason=f"event_rule baseline: salience {max_salience:.3f} < {threshold}",
        )
        loop._record_stage(
            PipelineStage.INTENTION_GENESIS,
            "event_rule stub — salience below threshold",
            {**initiative.model_dump(mode="json"), "baseline": BaselineCondition.EVENT_RULE.value},
            trace_kind=TraceNodeKind.INTENTION_GENESIS,
            parent_kind=TraceNodeKind.MOTIVE_FORMATION,
        )
    else:
        from eia.intention import IntentionGenesis

        rule_intention = IntentionGenesis(abstain_threshold=0.0, min_evsi=0.0)
        candidates = rule_intention.generate_candidates(motivation, loop.field)
        initiative = rule_intention.best_or_abstain(motivation, loop.field)
        loop._record_stage(
            PipelineStage.INTENTION_GENESIS,
            f"event_rule fired — candidates={len(candidates)}",
            {
                **initiative.model_dump(mode="json"),
                "baseline": BaselineCondition.EVENT_RULE.value,
                "competing_count": len(candidates),
            },
            trace_kind=TraceNodeKind.INTENTION_GENESIS,
            parent_kind=TraceNodeKind.MOTIVE_FORMATION,
        )
        loop._record_stage(
            PipelineStage.INITIATIVE_EMISSION,
            f"Emitted initiative kind={initiative.candidate.kind.value}",
            initiative.model_dump(mode="json"),
            trace_kind=TraceNodeKind.INITIATIVE_EMISSION,
            parent_kind=TraceNodeKind.INTENTION_GENESIS,
        )
        decision = loop.governor.evaluate(initiative)

    loop._record_stage(
        PipelineStage.CONTACT_GOVERNOR,
        f"Outcome={decision.outcome.value}",
        decision.model_dump(mode="json"),
        trace_kind=TraceNodeKind.CONTACT_GOVERNOR,
        parent_kind=TraceNodeKind.INTENTION_GENESIS,
    )
    loop._snapshot_field = BeliefField.model_validate(loop.field.model_dump())
    loop.governor.state.current_tick = sim.clock.tick
    return motivation, initiative, decision, None


def _predicted_user_need(loop: CognitiveLoop) -> tuple[float, float, float]:
    """P3 proxy: urgency from commitments + uncertainty from open beliefs."""
    from eia.schemas.belief import BeliefKind

    max_urgency = 0.0
    max_uncertainty = 0.0
    for belief in loop.field.beliefs.values():
        if belief.kind == BeliefKind.COMMITMENT:
            urgency = float(belief.metadata.get("urgency", belief.uncertainty))
            max_urgency = max(max_urgency, urgency)
        elif belief.kind == BeliefKind.CATEGORICAL:
            max_uncertainty = max(max_uncertainty, belief.uncertainty)
    predicted = 0.60 * max_urgency + 0.40 * max_uncertainty
    return predicted, max_urgency, max_uncertainty


def make_predictive_p3_stub(
    loop: CognitiveLoop,
    sim: Simulator,
    *,
    need_threshold: float | None = None,
) -> tuple:
    """Predictive P3 baseline: rule-based user-need prediction, no drive dynamics."""
    from eia.audit import TraceNodeKind
    from eia.beliefs import BeliefField
    from eia.scheduler import PipelineStage
    from eia.schemas.motivation import DriveKind

    threshold = (
        need_threshold if need_threshold is not None else load_predictive_p3_need()
    )
    now = datetime.now(timezone.utc)
    predicted_need, max_urgency, max_uncertainty = _predicted_user_need(loop)

    loop._motivation_count += 1
    motivation = Motivation(
        id=f"mot-predictive-p3-{loop._motivation_count}",
        timestamp=now,
        dominant_drive=DriveKind.COMMITMENT,
        signals=[
            MotivationSignal(
                drive=DriveKind.COMMITMENT,
                intensity=max_urgency,
                error_term=0.0,
                explanation="predictive_p3: commitment urgency proxy",
            ),
            MotivationSignal(
                drive=DriveKind.EPISTEMIC,
                intensity=max_uncertainty,
                error_term=0.0,
                explanation="predictive_p3: belief uncertainty proxy",
            ),
        ],
    )
    loop._record_stage(
        PipelineStage.MOTIVE_FORMATION,
        f"predictive_p3 need={predicted_need:.3f} threshold={threshold}",
        {
            **motivation.model_dump(mode="json"),
            "baseline": BaselineCondition.PREDICTIVE_P3.value,
            "predicted_need": predicted_need,
            "need_threshold": threshold,
            "max_urgency": max_urgency,
            "max_uncertainty": max_uncertainty,
        },
        trace_kind=TraceNodeKind.MOTIVE_FORMATION,
        parent_kind=TraceNodeKind.SENSE_MAKING,
    )

    if predicted_need < threshold:
        abstain = InitiativeCandidate(id=new_id("cand-abstain"), kind=InitiativeKind.ABSTAIN)
        initiative = Initiative(
            id=new_id("init-predictive-p3"),
            timestamp=now,
            candidate=abstain,
            abstained=True,
            parent_motivation_id=motivation.id,
            evsi=0.0,
        )
        decision = ContactDecision(
            id=new_id("dec-predictive-p3"),
            timestamp=now,
            initiative_id=initiative.id,
            outcome=ContactOutcome.ABSTAIN,
            contact_score=-1.0,
            reason=f"predictive_p3 baseline: need {predicted_need:.3f} < {threshold}",
        )
        loop._record_stage(
            PipelineStage.INTENTION_GENESIS,
            "predictive_p3 stub — predicted need below threshold",
            {**initiative.model_dump(mode="json"), "baseline": BaselineCondition.PREDICTIVE_P3.value},
            trace_kind=TraceNodeKind.INTENTION_GENESIS,
            parent_kind=TraceNodeKind.MOTIVE_FORMATION,
        )
    else:
        candidate = InitiativeCandidate(
            id=new_id("cand-p3"),
            kind=InitiativeKind.ASK_QUESTION,
            question_text=(
                "Based on your open commitments, should I follow up on the deadline?"
            ),
            expected_info_gain=0.35,
            interrupt_cost=0.25,
            risk=0.10,
            commitment_progress=max_urgency * 0.4,
        )
        initiative = Initiative(
            id=new_id("init-predictive-p3"),
            timestamp=now,
            candidate=candidate,
            abstained=False,
            parent_motivation_id=motivation.id,
            evsi=predicted_need * 0.5,
        )
        loop._record_stage(
            PipelineStage.INTENTION_GENESIS,
            "predictive_p3 fired — predicted user need",
            {**initiative.model_dump(mode="json"), "baseline": BaselineCondition.PREDICTIVE_P3.value},
            trace_kind=TraceNodeKind.INTENTION_GENESIS,
            parent_kind=TraceNodeKind.MOTIVE_FORMATION,
        )
        loop._record_stage(
            PipelineStage.INITIATIVE_EMISSION,
            f"Emitted initiative kind={initiative.candidate.kind.value}",
            initiative.model_dump(mode="json"),
            trace_kind=TraceNodeKind.INITIATIVE_EMISSION,
            parent_kind=TraceNodeKind.INTENTION_GENESIS,
        )
        decision = loop.governor.evaluate(initiative)

    loop._record_stage(
        PipelineStage.CONTACT_GOVERNOR,
        f"Outcome={decision.outcome.value}",
        decision.model_dump(mode="json"),
        trace_kind=TraceNodeKind.CONTACT_GOVERNOR,
        parent_kind=TraceNodeKind.INTENTION_GENESIS,
    )
    loop._snapshot_field = BeliefField.model_validate(loop.field.model_dump())
    loop.governor.state.current_tick = sim.clock.tick
    return motivation, initiative, decision, None


def cognition_tick_count(baseline: BaselineCondition) -> int:
    """How many cognition ticks to run for a baseline condition."""
    if baseline == BaselineCondition.REACTIVE_ONLY:
        return 0
    if baseline == BaselineCondition.SCHEDULED_STUB:
        return 1
    if baseline == BaselineCondition.EVENT_RULE:
        return 0
    if baseline == BaselineCondition.PREDICTIVE_P3:
        return 0
    return 3
