"""Twin counterfactual honesty and EOI product controls (C2 harness)."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from eia.audit.eoi_product import user_invariant_under_twin
from eia.experiment.baseline import make_reactive_stub
from eia.pipeline import CognitiveLoop, run_scenario
from eia.schemas.belief import BeliefKind
from eia.simulator import Simulator, load_scenario

SCENARIO = Path(__file__).resolve().parents[1] / "scenarios" / "twin_world_001.yaml"


def test_twin_replay_excludes_removed_observation_traces() -> None:
    result = run_scenario(SCENARIO, traces_dir=Path("traces/test_twin_honesty"))
    loop = result["loop"]
    removed_ids = result["twin_result"].removed_user_event_ids
    assert removed_ids

    twin_field = loop.replay_field_excluding_observations(removed_ids)
    for obs_id in removed_ids:
        assert not any(u.parent_observation_id == obs_id for u in twin_field.updates)

    full_ids = {u.parent_observation_id for u in loop.field.updates if u.parent_observation_id}
    twin_ids = {u.parent_observation_id for u in twin_field.updates if u.parent_observation_id}
    assert twin_ids <= full_ids - set(removed_ids)


def test_honest_twin_differs_from_post_removal_snapshot_copy() -> None:
    """Legacy bug: copying post-cognition snapshot kept removed-event belief updates."""
    result = run_scenario(SCENARIO, traces_dir=Path("traces/test_twin_honesty"))
    loop = result["loop"]
    removed_ids = result["twin_result"].removed_user_event_ids

    dishonest_field = loop._snapshot_field
    assert dishonest_field is not None
    honest_field = loop.replay_field_excluding_observations(removed_ids)

    dishonest_trace = {
        u.parent_observation_id for u in dishonest_field.updates if u.parent_observation_id
    }
    honest_trace = {
        u.parent_observation_id for u in honest_field.updates if u.parent_observation_id
    }
    assert set(removed_ids) & honest_trace == set()
    assert set(removed_ids) & dishonest_trace


def test_initial_beliefs_ablation_changes_initiative() -> None:
    """YAML priors change cognition when world observations are fixed."""

    def _target(beliefs: list) -> str | None:
        from eia.ids import seeded_context

        scenario = load_scenario(SCENARIO)
        scenario.events = [e for e in scenario.events if not e.is_user_trigger]
        with seeded_context(scenario.seed):
            sim = Simulator(scenario, seed=scenario.seed)
            loop = CognitiveLoop(seed=scenario.seed)
            for spec in beliefs:
                loop.field.upsert_belief(
                    spec["id"],
                    kind=BeliefKind(spec.get("kind", "categorical")),
                    subject=spec["subject"],
                    claim=spec["claim"],
                    distribution=spec.get("distribution"),
                    uncertainty=spec.get("uncertainty", 0.5),
                    metadata=spec.get("metadata", {}),
                )
            for contra in scenario.metadata.get("contradictions", []):
                loop.field.register_contradiction(contra[0], contra[1], contra[2])
            loop.mark_observation_phase_begin()
            sim.run_until(max((e.tick for e in scenario.events), default=10))
            for obs in sim.bus.events:
                loop.apply_observation(obs)
            sim.advance_quiet_period(ticks=4)
            for i in range(3):
                _, initiative, _, _ = loop.tick_cognition(
                    tick=sim.clock.tick + i,
                    hour=14,
                    finalize=(i == 2),
                )
            return initiative.candidate.target_belief_id

    base = load_scenario(SCENARIO)
    open_commit = deepcopy(base.initial_beliefs)
    closed_commit = deepcopy(base.initial_beliefs)
    for spec in closed_commit:
        if spec["id"] == "belief-commit-atlas":
            spec["metadata"] = {"status": "closed", "urgency": 0.05}

    assert _target(open_commit) == "belief-commit-atlas"
    assert _target(closed_commit) == "belief-deadline"


def test_world_observation_perturbation_changes_field() -> None:
    scenario = load_scenario(SCENARIO)

    def _alt_sep(alt_sep: float) -> float:
        from eia.ids import seeded_context

        with seeded_context(scenario.seed):
            sim = Simulator(scenario, seed=scenario.seed)
            loop = CognitiveLoop(seed=scenario.seed)
            for spec in scenario.initial_beliefs:
                loop.field.upsert_belief(
                    spec["id"],
                    kind=BeliefKind(spec.get("kind", "categorical")),
                    subject=spec["subject"],
                    claim=spec["claim"],
                    distribution=spec.get("distribution"),
                    uncertainty=spec.get("uncertainty", 0.5),
                    metadata=spec.get("metadata", {}),
                )
            for contra in scenario.metadata.get("contradictions", []):
                loop.field.register_contradiction(contra[0], contra[1], contra[2])
            loop.mark_observation_phase_begin()
            sim.run_until(max((e.tick for e in scenario.events), default=10))
            for obs in sim.bus.events:
                if obs.topic == "conflicting_deadline_report":
                    payload = dict(obs.payload)
                    payload["distribution"] = {
                        "Aug 30": 0.05,
                        "Sep 15": alt_sep,
                        "unknown": 0.10,
                    }
                    obs = obs.model_copy(update={"payload": payload})
                loop.apply_observation(obs)
            belief = loop.field.beliefs.get("belief-deadline-alt")
            assert belief is not None
            return belief.distribution.get("Sep 15", 0.0)

    assert _alt_sep(0.85) != _alt_sep(0.05)


def test_twin_world_endogenous_user_invariant_product() -> None:
    result = run_scenario(SCENARIO, traces_dir=Path("traces/test_twin_honesty"))
    orig = result["initiative"]
    _, twin_init, _ = result["loop"].run_twin(
        result["twin_result"].removed_user_event_ids,
        result["simulator"],
        cognition_ticks=3,
    )
    assert user_invariant_under_twin(orig, twin_init)
    assert result["twin_result"].eoi >= 0.5


@pytest.mark.skip(reason="Negative control skeleton: user-only steering scenario TBD in sci_flow")
def test_user_caused_initiative_expects_low_eoi() -> None:
    pytest.skip("await dedicated user-steered scenario fixture")


def test_reactive_stub_answers_user_message_in_scenario() -> None:
    scenario = load_scenario(SCENARIO)
    from eia.ids import seeded_context

    with seeded_context(scenario.seed):
        sim = Simulator(scenario, seed=scenario.seed)
        loop = CognitiveLoop(seed=scenario.seed)
        for spec in scenario.initial_beliefs:
            loop.field.upsert_belief(
                spec["id"],
                kind=BeliefKind(spec.get("kind", "categorical")),
                subject=spec["subject"],
                claim=spec["claim"],
                distribution=spec.get("distribution"),
                uncertainty=spec.get("uncertainty", 0.5),
                metadata=spec.get("metadata", {}),
            )
        loop.mark_observation_phase_begin()
        sim.run_until(max((e.tick for e in scenario.events), default=10))
        for obs in sim.bus.events:
            loop.apply_observation(obs)
        _mot, init, dec, _ = make_reactive_stub(loop, sim)
        assert not init.abstained
        assert init.candidate.question_text
        assert dec.outcome.value != "abstain"