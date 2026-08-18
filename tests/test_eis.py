"""M-B: EIS type port + classification vs AuthenticReason."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from eia.audit import (
    AuthenticReasonCode,
    AuthenticReasonDiscriminator,
    CausalTrace,
    EndogeneityVector,
    EndogenousSpectrumLevel,
    TraceNodeKind,
    authentic_vs_eis_agreement,
    infer_endogeneity_vector,
)
from eia.audit.eis import EIS_8_FORBIDDEN_AS_CAPABILITY
from eia.pipeline import run_scenario
from eia.schemas.contact import ContactDecision, ContactOutcome
from eia.schemas.initiative import Initiative, InitiativeCandidate, InitiativeKind
from eia.schemas.motivation import DriveKind, Motivation, MotivationSignal

SCENARIO = Path(__file__).resolve().parents[1] / "scenarios" / "twin_world_001.yaml"


def test_eis_8_is_forbidden_capability() -> None:
    assert EIS_8_FORBIDDEN_AS_CAPABILITY is True


def test_endogeneity_vector_bounds() -> None:
    with pytest.raises(ValueError):
        EndogeneityVector(
            prompt_independence=1.2,
            scheduler_independence=1.0,
            event_rule_independence=1.0,
            persistent_state_dependence=1.0,
            world_model_grounding=1.0,
            coherence_dependence=0.5,
            goal_novelty=0.4,
            self_model_continuity=1.0,
            constitutional_boundedness=1.0,
        )


def test_classify_parity_v0_2_cascade() -> None:
    """Pre-registered parity: same cascade as research/cursor-starter-v0.2 endogenous.py."""
    reactive = EndogeneityVector(
        prompt_independence=0.2,
        scheduler_independence=1.0,
        event_rule_independence=1.0,
        persistent_state_dependence=0.8,
        world_model_grounding=0.8,
        coherence_dependence=0.6,
        goal_novelty=0.4,
        self_model_continuity=1.0,
        constitutional_boundedness=1.0,
    )
    assert reactive.classify() == EndogenousSpectrumLevel.EIS_0_REACTIVE

    ambient = EndogeneityVector(
        prompt_independence=0.9,
        scheduler_independence=0.9,
        event_rule_independence=0.3,
        persistent_state_dependence=0.8,
        world_model_grounding=0.8,
        coherence_dependence=0.6,
        goal_novelty=0.4,
        self_model_continuity=1.0,
        constitutional_boundedness=1.0,
    )
    assert ambient.classify() == EndogenousSpectrumLevel.EIS_3_AMBIENT_ADAPTATION

    coherence = EndogeneityVector(
        prompt_independence=1.0,
        scheduler_independence=1.0,
        event_rule_independence=1.0,
        persistent_state_dependence=0.8,
        world_model_grounding=0.8,
        coherence_dependence=0.7,
        goal_novelty=0.40,
        self_model_continuity=1.0,
        constitutional_boundedness=0.95,
    )
    assert coherence.classify() == EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT
    assert 0.0 < coherence.endogenous_origin_score <= 1.0

    autotelic = EndogeneityVector(
        prompt_independence=1.0,
        scheduler_independence=1.0,
        event_rule_independence=1.0,
        persistent_state_dependence=0.8,
        world_model_grounding=0.8,
        coherence_dependence=0.7,
        goal_novelty=0.80,
        self_model_continuity=1.0,
        constitutional_boundedness=0.95,
    )
    assert autotelic.classify() == EndogenousSpectrumLevel.EIS_7_AUTOTELIC_GOAL_CONSTRUCTION


def test_authentic_vs_eis_agreement_helper() -> None:
    assert authentic_vs_eis_agreement(
        is_authentic=True,
        initiative_class="endogenous",
        level=EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT,
    )
    assert authentic_vs_eis_agreement(
        is_authentic=False,
        initiative_class="exogenous",
        level=EndogenousSpectrumLevel.EIS_0_REACTIVE,
    )
    assert not authentic_vs_eis_agreement(
        is_authentic=True,
        initiative_class="endogenous",
        level=EndogenousSpectrumLevel.EIS_0_REACTIVE,
    )


def test_infer_low_eoi_is_reactive() -> None:
    vec = infer_endogeneity_vector(eoi=0.1, structural_drive=True)
    assert vec.classify() == EndogenousSpectrumLevel.EIS_0_REACTIVE


def test_verdict_attaches_eis_on_approved_structural() -> None:
    trace = CausalTrace("trace-eis")
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
    motivation = Motivation(
        id="m1",
        timestamp=datetime.now(timezone.utc),
        signals=[
            MotivationSignal(
                drive=DriveKind.EPISTEMIC,
                intensity=0.7,
                error_term=0.5,
                explanation="epistemic drive: error=0.500 from BeliefField gradient",
            ),
            MotivationSignal(drive=DriveKind.COHERENCE, intensity=0.6, error_term=0.2),
            MotivationSignal(drive=DriveKind.COMMITMENT, intensity=0.4, error_term=0.2),
        ],
        dominant_drive=DriveKind.EPISTEMIC,
    )
    initiative = Initiative(
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
    )
    decision = ContactDecision(
        id="d1",
        timestamp=datetime.now(timezone.utc),
        initiative_id="i1",
        outcome=ContactOutcome.SEND_NOW,
        contact_score=0.5,
        reason="ok",
    )
    verdict = AuthenticReasonDiscriminator().evaluate(
        trace=trace,
        motivation=motivation,
        initiative=initiative,
        decision=decision,
        eoi=1.0,
    )
    assert verdict.eis_level is not None
    assert verdict.eos_score is not None
    assert verdict.endogeneity is not None
    assert verdict.eis_level >= 4
    assert authentic_vs_eis_agreement(
        is_authentic=verdict.is_authentic,
        initiative_class=verdict.initiative_class,
        level=EndogenousSpectrumLevel(verdict.eis_level),
    )


def test_abstain_has_no_eis() -> None:
    trace = CausalTrace("trace-abs")
    trace.add_node(TraceNodeKind.OBSERVATION_INGEST, {"id": "o1"})
    initiative = Initiative(
        id="i1",
        timestamp=datetime.now(timezone.utc),
        candidate=InitiativeCandidate(
            id="c1",
            kind=InitiativeKind.ASK_QUESTION,
            expected_info_gain=0.1,
            source_drives=[DriveKind.EPISTEMIC],
        ),
        abstained=True,
        parent_motivation_id="m1",
    )
    motivation = Motivation(
        id="m1",
        timestamp=datetime.now(timezone.utc),
        signals=[
            MotivationSignal(drive=DriveKind.EPISTEMIC, intensity=0.1, error_term=0.5),
        ],
        dominant_drive=DriveKind.EPISTEMIC,
    )
    decision = ContactDecision(
        id="d1",
        timestamp=datetime.now(timezone.utc),
        initiative_id="i1",
        outcome=ContactOutcome.DENY,
        contact_score=0.0,
        reason="abstained",
    )
    verdict = AuthenticReasonDiscriminator().evaluate(
        trace=trace,
        motivation=motivation,
        initiative=initiative,
        decision=decision,
        eoi=0.9,
    )
    assert AuthenticReasonCode.ABSTAINED in verdict.reason_codes
    assert verdict.eis_level is None
    assert verdict.eos_score is None


def test_twin_world_authentic_reason_includes_eis() -> None:
    result = run_scenario(SCENARIO, traces_dir=Path("traces/test"))
    verdict = result["authentic_verdict"]
    assert verdict.is_authentic is True
    assert verdict.eis_level is not None
    assert verdict.eos_score is not None
    level = EndogenousSpectrumLevel(verdict.eis_level)
    assert authentic_vs_eis_agreement(
        is_authentic=verdict.is_authentic,
        initiative_class=verdict.initiative_class,
        level=level,
    )
    payload = next(
        n.payload
        for n in result["loop"].trace.nodes
        if n.kind.value == "authentic_reason"
    )
    assert "eis_level" in payload
    assert payload["eis_level"] == verdict.eis_level
