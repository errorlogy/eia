"""Tests for AuthenticReasonDiscriminator and AgentState schema."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from eia.audit import (
    AuthenticReasonCode,
    AuthenticReasonDiscriminator,
    CausalTrace,
    EOIScorer,
    TraceNodeKind,
)
from eia.beliefs import BeliefField
from eia.drives import DriveEngine
from eia.governor import ContactGovernor, GovernorConfig
from eia.pipeline import run_scenario
from eia.schemas.agent_state import AgentState
from eia.schemas.belief import BeliefKind
from eia.schemas.contact import ContactDecision, ContactOutcome
from eia.schemas.initiative import Initiative, InitiativeCandidate, InitiativeKind
from eia.schemas.motivation import DriveKind, Motivation, MotivationSignal

SCENARIO = Path(__file__).resolve().parents[1] / "scenarios" / "twin_world_001.yaml"


def _full_trace() -> CausalTrace:
    trace = CausalTrace("trace-auth-test")
    trace.add_node(TraceNodeKind.OBSERVATION_INGEST, {"id": "o1"})
    trace.add_node(
        TraceNodeKind.MOTIVE_FORMATION,
        {"id": "m1"},
        parent_kind=TraceNodeKind.OBSERVATION_INGEST,
    )
    trace.add_node(
        TraceNodeKind.INTENTION_GENESIS,
        {"id": "i1"},
        parent_kind=TraceNodeKind.MOTIVE_FORMATION,
    )
    trace.add_node(
        TraceNodeKind.CONTACT_GOVERNOR,
        {"id": "g1"},
        parent_kind=TraceNodeKind.INTENTION_GENESIS,
    )
    return trace


def _structural_motivation() -> Motivation:
    return Motivation(
        id="m1",
        timestamp=datetime.now(timezone.utc),
        signals=[
            MotivationSignal(
                drive=DriveKind.EPISTEMIC,
                intensity=0.7,
                error_term=0.5,
                explanation="epistemic drive: error=0.500 from BeliefField gradient",
            ),
            MotivationSignal(drive=DriveKind.COHERENCE, intensity=0.3, error_term=0.2),
            MotivationSignal(drive=DriveKind.COMMITMENT, intensity=0.1, error_term=0.05),
        ],
        dominant_drive=DriveKind.EPISTEMIC,
    )


def _initiative() -> Initiative:
    return Initiative(
        id="i1",
        timestamp=datetime.now(timezone.utc),
        candidate=InitiativeCandidate(
            id="c1",
            kind=InitiativeKind.ASK_QUESTION,
            expected_info_gain=0.5,
            source_drives=[DriveKind.EPISTEMIC],
        ),
        abstained=False,
        parent_motivation_id="m1",
        evsi=0.4,
    )


def _approved_decision() -> ContactDecision:
    return ContactDecision(
        id="gov-1",
        timestamp=datetime.now(timezone.utc),
        initiative_id="i1",
        outcome=ContactOutcome.SEND_NOW,
        contact_score=0.5,
        budget_remaining=1,
        reason="Contact justified",
    )


def test_authentic_reason_passes_endogenous_scenario() -> None:
    disc = AuthenticReasonDiscriminator()
    verdict = disc.evaluate(
        trace=_full_trace(),
        motivation=_structural_motivation(),
        initiative=_initiative(),
        decision=_approved_decision(),
        eoi=0.75,
    )
    assert verdict.is_authentic is True
    assert verdict.initiative_class == "endogenous"
    assert AuthenticReasonCode.ENDOGENOUS in verdict.reason_codes


def test_authentic_reason_fails_low_eoi() -> None:
    disc = AuthenticReasonDiscriminator()
    verdict = disc.evaluate(
        trace=_full_trace(),
        motivation=_structural_motivation(),
        initiative=_initiative(),
        decision=_approved_decision(),
        eoi=0.2,
    )
    assert verdict.is_authentic is False
    assert AuthenticReasonCode.EOI_BELOW_THRESHOLD in verdict.reason_codes
    assert "eoi_threshold" in verdict.failed_checks


def test_authentic_reason_fails_narrative_drive() -> None:
    mot = _structural_motivation()
    mot.signals[0].explanation = "I feel curious about this topic"
    disc = AuthenticReasonDiscriminator()
    verdict = disc.evaluate(
        trace=_full_trace(),
        motivation=mot,
        initiative=_initiative(),
        decision=_approved_decision(),
        eoi=0.8,
    )
    assert verdict.is_authentic is False
    assert AuthenticReasonCode.DRIVE_NARRATIVE in verdict.reason_codes


def test_authentic_reason_fails_missing_causal_chain() -> None:
    trace = CausalTrace("incomplete")
    trace.add_node(TraceNodeKind.OBSERVATION_INGEST, {"id": "o1"})
    disc = AuthenticReasonDiscriminator()
    verdict = disc.evaluate(
        trace=trace,
        motivation=_structural_motivation(),
        initiative=_initiative(),
        decision=_approved_decision(),
        eoi=0.8,
    )
    assert verdict.is_authentic is False
    assert AuthenticReasonCode.CAUSAL_CHAIN_MISSING in verdict.reason_codes


def test_authentic_reason_fails_governor_reject() -> None:
    decision = ContactDecision(
        id="gov-deny",
        timestamp=datetime.now(timezone.utc),
        initiative_id="i1",
        outcome=ContactOutcome.DENY,
        contact_score=-0.5,
        budget_remaining=2,
        reason="Contact score below threshold",
    )
    disc = AuthenticReasonDiscriminator()
    verdict = disc.evaluate(
        trace=_full_trace(),
        motivation=_structural_motivation(),
        initiative=_initiative(),
        decision=decision,
        eoi=0.8,
    )
    assert verdict.is_authentic is False
    assert AuthenticReasonCode.GOVERNOR_REJECTED in verdict.reason_codes


def test_authentic_reason_abstained_initiative() -> None:
    init = _initiative()
    init.abstained = True
    disc = AuthenticReasonDiscriminator()
    verdict = disc.evaluate(
        trace=_full_trace(),
        motivation=_structural_motivation(),
        initiative=init,
        decision=_approved_decision(),
        eoi=0.9,
    )
    assert verdict.is_authentic is False
    assert AuthenticReasonCode.ABSTAINED in verdict.reason_codes


def test_eoi_scorer_is_endogenous() -> None:
    scorer = EOIScorer(threshold=0.5)
    assert scorer.is_endogenous(0.75) is True
    assert scorer.is_endogenous(0.3) is False


def test_agent_state_from_cognitive_loop() -> None:
    field = BeliefField()
    field.upsert_belief(
        "b1",
        kind=BeliefKind.CATEGORICAL,
        subject="Atlas",
        claim="deadline",
        distribution={"Aug 30": 0.4, "Sep 15": 0.4},
        uncertainty=0.7,
    )
    drives = DriveEngine()
    drives.compute(field)
    gov = ContactGovernor()
    state = AgentState.from_cognitive_loop(
        field=field,
        drive_state=drives.state,
        governor=gov,
        trace_id="trace-test",
        tick=3,
    )
    x = state.as_x_t_dict()
    assert "b_t" in x
    assert "d_t" in x
    assert len(x["b_t"]) == 1
    assert state.dominant_drive is not None


def test_end_to_end_authentic_reason_in_trace() -> None:
    result = run_scenario(SCENARIO, traces_dir=Path("traces/test"))
    kinds = {n.kind for n in result["loop"].trace.nodes}
    assert TraceNodeKind.AUTHENTIC_REASON in kinds
    assert result["authentic_verdict"].is_authentic is True
