"""Tests for EIA MVP-0."""

from __future__ import annotations

from pathlib import Path

import pytest

from eia.audit import CausalTrace, EOIScorer, TwinRunner
from eia.beliefs import BeliefField, shannon_entropy
from eia.drives import DriveEngine
from eia.governor import ContactGovernor, GovernorConfig
from eia.intention import IntentionGenesis
from eia.pipeline import run_scenario
from eia.schemas.belief import BeliefKind
from eia.schemas.contact import ContactOutcome
from eia.schemas.initiative import Initiative, InitiativeCandidate, InitiativeKind
from eia.schemas.motivation import DriveKind, Motivation, MotivationSignal
from datetime import datetime, timezone


SCENARIO = Path(__file__).resolve().parents[1] / "scenarios" / "twin_world_001.yaml"


def test_shannon_entropy_uniform() -> None:
    h = shannon_entropy({"a": 0.5, "b": 0.5})
    assert h == pytest.approx(1.0, abs=0.01)


def test_belief_field_gradients() -> None:
    field = BeliefField()
    field.upsert_belief(
        "b1",
        kind=BeliefKind.CATEGORICAL,
        subject="Atlas",
        claim="deadline",
        distribution={"Aug 30": 0.4, "Sep 15": 0.4, "unknown": 0.2},
        uncertainty=0.8,
    )
    field.register_contradiction("b1", "b2", "deadline")
    g = field.gradient_snapshot()
    assert g["epistemic"] > 0.5
    assert g["coherence"] > 0


def test_drive_engine_no_llm_deterministic() -> None:
    field = BeliefField()
    field.upsert_belief(
        "b1",
        kind=BeliefKind.CATEGORICAL,
        subject="X",
        claim="uncertain",
        distribution={"a": 0.33, "b": 0.33, "c": 0.34},
    )
    e1 = DriveEngine()
    e2 = DriveEngine()
    m1 = e1.compute(field, motivation_id="m1")
    m2 = e2.compute(field, motivation_id="m2")
    assert m1.signals[0].intensity == m2.signals[0].intensity


def test_intention_genesis_mandatory_abstain() -> None:
    genesis = IntentionGenesis(abstain_threshold=0.99, min_evsi=0.99)
    field = BeliefField()
    mot = Motivation(
        id="m-low",
        timestamp=datetime.now(timezone.utc),
        signals=[
            MotivationSignal(drive=DriveKind.EPISTEMIC, intensity=0.1, error_term=0.1),
            MotivationSignal(drive=DriveKind.COHERENCE, intensity=0.1, error_term=0.1),
            MotivationSignal(drive=DriveKind.COMMITMENT, intensity=0.1, error_term=0.1),
        ],
    )
    init = genesis.best_or_abstain(mot, field)
    assert init.abstained is True


def test_contact_governor_rejects_low_value() -> None:
    gov = ContactGovernor(GovernorConfig(min_contact_score=0.99, min_evsi=0.99))
    init = Initiative(
        id="i1",
        timestamp=datetime.now(timezone.utc),
        candidate=InitiativeCandidate(
            id="c1",
            kind=InitiativeKind.ASK_QUESTION,
            expected_info_gain=0.05,
            interrupt_cost=0.5,
        ),
        abstained=False,
        parent_motivation_id="m1",
        evsi=0.05,
    )
    decision = gov.evaluate(init)
    assert decision.outcome == ContactOutcome.DENY


def test_eoi_scorer() -> None:
    scorer = EOIScorer()
    orig = Initiative(
        id="i1",
        timestamp=datetime.now(timezone.utc),
        candidate=InitiativeCandidate(
            id="c1",
            kind=InitiativeKind.ASK_QUESTION,
            target_belief_id="b1",
            expected_info_gain=0.5,
            source_drives=[DriveKind.EPISTEMIC],
        ),
        abstained=False,
        parent_motivation_id="m1",
    )
    twin = Initiative(
        id="i2",
        timestamp=datetime.now(timezone.utc),
        candidate=InitiativeCandidate(
            id="c2",
            kind=InitiativeKind.ASK_QUESTION,
            target_belief_id="b1",
            expected_info_gain=0.5,
            source_drives=[DriveKind.EPISTEMIC],
        ),
        abstained=False,
        parent_motivation_id="m1",
    )
    eoi = scorer.score(orig, twin, removed_count=1)
    assert eoi >= 0.75


def test_end_to_end_demo_scenario() -> None:
    result = run_scenario(SCENARIO, traces_dir=Path("traces/test"))
    assert result["initiative"].abstained is False
    assert result["initiative"].candidate.question_text is not None
    assert result["decision"].outcome == ContactOutcome.SEND_NOW
    assert result["twin_result"].eoi > 0.5
    assert result["trace_path"].exists()


def test_causal_trace_roundtrip(tmp_path: Path) -> None:
    from eia.audit import TraceNodeKind

    trace = CausalTrace("test-trace-2")
    trace.add_node(TraceNodeKind.OBSERVATION, {"id": "o1", "topic": "test"})
    path = tmp_path / "t.jsonl"
    trace.export_jsonl(path)
    loaded = CausalTrace.load_jsonl(path)
    assert loaded.trace_id == "test-trace-2"
    assert len(loaded.nodes) == 1
