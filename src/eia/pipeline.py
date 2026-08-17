"""EIA cognitive loop orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from eia.audit import CausalTrace, TraceNodeKind, TwinRunner
from eia.beliefs import BeliefField
from eia.drives import DriveEngine
from eia.governor import ContactGovernor, GovernorState
from eia.intention import IntentionGenesis
from eia.namm import NammAdapter
from eia.schemas.belief import BeliefKind
from eia.schemas.observation import Observation
from eia.simulator import Simulator, load_scenario


class CognitiveLoop:
    """End-to-end pipeline: observations → beliefs → drives → initiative → governor."""

    def __init__(self, *, seed: int = 42) -> None:
        self.field = BeliefField()
        self.drives = DriveEngine()
        self.intention = IntentionGenesis(abstain_threshold=0.30, min_evsi=0.12)
        self.governor = ContactGovernor()
        self.namm = NammAdapter(epistemic_threshold=0.50)
        self.trace = CausalTrace()
        self.twin_runner = TwinRunner()
        self.seed = seed
        self._motivation_count = 0
        self._snapshot_field: BeliefField | None = None
        self._snapshot_drives = None

    def apply_observation(self, obs: Observation) -> None:
        self.trace.record_observation(obs)
        payload = obs.payload

        if obs.topic == "project_atlas_deadline":
            self.field.upsert_belief(
                "belief-deadline",
                kind=BeliefKind.CATEGORICAL,
                subject="Project Atlas",
                claim="deadline date",
                distribution=payload.get("distribution", {"Aug 30": 0.4, "Sep 15": 0.35, "unknown": 0.25}),
                uncertainty=0.85,
                source_observation_id=obs.id,
            )
        elif obs.topic == "conflicting_deadline_report":
            self.field.upsert_belief(
                "belief-deadline-alt",
                kind=BeliefKind.CATEGORICAL,
                subject="Project Atlas",
                claim="alternate deadline from email",
                distribution=payload.get("distribution", {"Aug 30": 0.1, "Sep 15": 0.8, "unknown": 0.1}),
                uncertainty=0.7,
                source_observation_id=obs.id,
            )
            self.field.register_contradiction("belief-deadline", "belief-deadline-alt", "Project Atlas deadline")
        elif obs.topic == "commitment_created":
            self.field.upsert_belief(
                "belief-commit-atlas",
                kind=BeliefKind.COMMITMENT,
                subject="Project Atlas",
                claim="track milestone progress until deadline confirmed",
                uncertainty=payload.get("urgency", 0.6),
                metadata={"status": "open", "urgency": payload.get("urgency", 0.7)},
                source_observation_id=obs.id,
            )
        elif obs.topic == "user_departed":
            self.field.upsert_belief(
                "belief-user-absent",
                kind=BeliefKind.CATEGORICAL,
                subject="user presence",
                claim="user left without clarifying deadline",
                distribution={"absent": 0.95, "present": 0.05},
                uncertainty=0.1,
                source_observation_id=obs.id,
            )

        if self.field.updates:
            last = self.field.updates[-1]
            self.trace.record_belief_update(last.model_dump(mode="json"))

    def tick_cognition(self, *, tick: int, hour: int, finalize: bool = True) -> tuple:
        """One cognitive cycle after observations."""
        self.governor.state.current_tick = tick
        self.governor.state.hour = hour

        novelty = {}
        if tick > 2:
            from eia.schemas.motivation import DriveKind

            novelty[DriveKind.EPISTEMIC] = 0.15
            novelty[DriveKind.COHERENCE] = 0.20

        self._motivation_count += 1
        motivation = self.drives.compute(
            self.field,
            novelty_events=novelty,
            motivation_id=f"mot-{self._motivation_count}",
        )

        namm_intent = self.namm.maybe_propose_internal_experiment(motivation)
        initiative = self.intention.best_or_abstain(motivation, self.field)

        if finalize:
            self.trace.record_motivation(motivation)
            self.trace.record_initiative(initiative)
            decision = self.governor.evaluate(initiative)
            self.trace.record_contact_decision(decision)
        else:
            decision = None

        self._snapshot_field = BeliefField.model_validate(self.field.model_dump())
        self._snapshot_drives = motivation

        return motivation, initiative, decision, namm_intent

    def run_twin(self, removed_event_ids: list[str], sim: Simulator) -> tuple:
        """Counterfactual: restore pre-user-removal state, re-run cognition."""
        if not self._snapshot_field:
            raise RuntimeError("No snapshot — run tick_cognition first")

        twin_field = BeliefField.model_validate(self._snapshot_field.model_dump())
        twin_drives = DriveEngine()
        # Preserve accumulated drive levels — endogeneity lives in internal state
        twin_drives.state.epistemic = self.drives.state.epistemic
        twin_drives.state.coherence = self.drives.state.coherence
        twin_drives.state.commitment = self.drives.state.commitment
        twin_drives.state.tick = self.drives.state.tick
        twin_intention = IntentionGenesis(abstain_threshold=0.30, min_evsi=0.12)
        twin_gov = ContactGovernor()
        twin_gov.state = GovernorState(
            current_tick=sim.clock.tick,
            hour=sim.clock.hour,
        )

        motivation = twin_drives.compute(twin_field, motivation_id="mot-twin")
        initiative = twin_intention.best_or_abstain(motivation, twin_field)
        decision = twin_gov.evaluate(initiative)

        return motivation, initiative, decision


def run_scenario(scenario_path: Path, *, traces_dir: Path | None = None) -> dict:
    """Full end-to-end scenario run."""
    scenario = load_scenario(scenario_path)
    sim = Simulator(scenario, seed=scenario.seed)
    loop = CognitiveLoop(seed=scenario.seed)
    traces_dir = traces_dir or Path("traces")

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

    max_tick = max((e.tick for e in scenario.events), default=10)
    sim.run_until(max_tick)

    for obs in sim.bus.events:
        loop.apply_observation(obs)

    sim.advance_quiet_period(ticks=4)

    # Accumulate drive dynamics, then finalize once (single governor decision)
    motivation = initiative = decision = namm_intent = None
    for i in range(3):
        motivation, initiative, decision, namm_intent = loop.tick_cognition(
            tick=sim.clock.tick + i,
            hour=sim.clock.hour,
            finalize=(i == 2),
        )

    removed = sim.bus.remove_last_user_events(1)
    removed_ids = [o.id for o in removed]

    orig_initiative = initiative
    _, twin_initiative, _ = loop.run_twin(removed_ids, sim)
    twin_result = loop.twin_runner.compare(orig_initiative, twin_initiative, removed_ids)

    loop.trace.add_node(
        TraceNodeKind.TWIN_RUN,
        {
            "removed_user_event_ids": removed_ids,
            "original_initiative_id": orig_initiative.id,
            "twin_initiative_id": twin_initiative.id,
        },
    )
    loop.trace.add_node(
        TraceNodeKind.EOI_SCORE,
        {
            "eoi": twin_result.eoi,
            "semantic_match": twin_result.semantic_match,
            "abstained_in_twin": twin_result.abstained_in_twin,
        },
    )

    trace_path = traces_dir / f"{loop.trace.trace_id}.jsonl"
    loop.trace.export_jsonl(trace_path)

    return {
        "scenario": scenario,
        "simulator": sim,
        "loop": loop,
        "motivation": motivation,
        "initiative": initiative,
        "decision": decision,
        "namm_intent": namm_intent,
        "twin_result": twin_result,
        "trace_path": trace_path,
    }
