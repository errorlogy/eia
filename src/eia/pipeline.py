"""EIA five-stage cognitive pipeline orchestrator.

Pipeline:
  ObservationIngest → SenseMaking → MotiveFormation → IntentionGenesis
  → InitiativeEmission → ContactGovernor
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eia.audit import (
    AuthenticReasonDiscriminator,
    CausalTrace,
    TraceMetadata,
    TraceNodeKind,
    TwinInterventionPolicy,
    TwinRunner,
)
from eia.audit.twin_policy import DEFAULT_TWIN_POLICY
from eia.experiment.baseline import (
    BaselineCondition,
    cognition_tick_count,
    make_event_rule_stub,
    make_predictive_p3_stub,
    make_reactive_stub,
)
from eia.version import get_code_version
from eia.beliefs import BeliefField
from eia.drives import DriveEngine
from eia.governor import ContactGovernor, GovernorState
from eia.ids import new_trace_id, seeded_context
from eia.intention import IntentionGenesis
from eia.namm import NammAdapter, NammHook
from eia.scheduler import LoopScheduler, PipelineStage
from eia.schemas.agent_state import AgentState
from eia.schemas.belief import BeliefKind
from eia.schemas.observation import Observation
from eia.sense_making import ComprehensionResult, SenseMakingEngine
from eia.simulator import Simulator, load_scenario


@dataclass
class PipelineStageResult:
    """One labeled stage output for trace and demo."""

    stage: PipelineStage
    summary: str
    payload: dict[str, Any] = field(default_factory=dict)


class CognitiveLoop:
    """End-to-end five-stage pipeline with NAMM artifact hooks."""

    def __init__(self, *, seed: int = 42) -> None:
        self.field = BeliefField()
        self.sense_making = SenseMakingEngine(self.field)
        self.drives = DriveEngine()
        self.intention = IntentionGenesis(abstain_threshold=0.30, min_evsi=0.12)
        self.governor = ContactGovernor()
        self.namm = NammAdapter(epistemic_threshold=0.50)
        self.scheduler = LoopScheduler.from_config()
        self.trace = CausalTrace(seed=seed)
        self.twin_runner = TwinRunner()
        self.authentic_reason = AuthenticReasonDiscriminator()
        self.seed = seed
        self._motivation_count = 0
        self._snapshot_field: BeliefField | None = None
        self._last_comprehension: ComprehensionResult | None = None
        self.stage_log: list[PipelineStageResult] = []

    def _record_stage(
        self,
        stage: PipelineStage,
        summary: str,
        payload: dict[str, Any],
        *,
        trace_kind: TraceNodeKind,
        parent_kind: TraceNodeKind | None = None,
    ) -> None:
        schedule = self.scheduler.stage_schedule(stage)
        full_payload = {
            "pipeline_stage": stage.value,
            "stage_summary": summary,
            "loop_schedule": schedule,
            **payload,
        }
        self.stage_log.append(
            PipelineStageResult(stage=stage, summary=summary, payload=full_payload)
        )
        self.trace.add_node(
            trace_kind,
            full_payload,
            parent_kind=parent_kind,
        )

    def apply_observation(self, obs: Observation) -> ComprehensionResult | None:
        """Stage 1–2: ObservationIngest → SenseMaking."""
        self._record_stage(
            PipelineStage.OBSERVATION_INGEST,
            f"Ingested observation topic={obs.topic}",
            obs.model_dump(mode="json"),
            trace_kind=TraceNodeKind.OBSERVATION_INGEST,
        )

        comprehension = self.sense_making.ingest_observation(obs)
        if comprehension is None:
            return None

        for upd_id in comprehension.belief_update_ids:
            upd = next((u for u in self.field.updates if u.id == upd_id), None)
            if upd:
                self.trace.add_node(
                    TraceNodeKind.BELIEF_UPDATE,
                    upd.model_dump(mode="json"),
                    parent_kind=TraceNodeKind.OBSERVATION_INGEST,
                )

        namm_hooks = self.namm.on_sense_making(comprehension)
        self._record_stage(
            PipelineStage.SENSE_MAKING,
            comprehension.comprehension_summary,
            {
                **comprehension.model_dump(mode="json"),
                "namm_hooks": [h.namm_experiment_ref for h in namm_hooks],
            },
            trace_kind=TraceNodeKind.SENSE_MAKING,
            parent_kind=TraceNodeKind.OBSERVATION_INGEST,
        )
        self._last_comprehension = comprehension
        return comprehension

    def tick_cognition(self, *, tick: int, hour: int, finalize: bool = True) -> tuple:
        """Stages 3–6: MotiveFormation → IntentionGenesis → InitiativeEmission → Governor."""
        self.governor.state.current_tick = tick
        self.governor.state.hour = hour

        comprehension = self._last_comprehension or self.sense_making.snapshot()

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

        self._record_stage(
            PipelineStage.MOTIVE_FORMATION,
            f"Dominant drive={motivation.dominant_drive.value}",
            motivation.model_dump(mode="json"),
            trace_kind=TraceNodeKind.MOTIVE_FORMATION,
            parent_kind=TraceNodeKind.SENSE_MAKING,
        )

        namm_intent = self.namm.maybe_propose_internal_experiment(
            motivation, comprehension=comprehension
        )
        if namm_intent:
            self.trace.add_node(
                TraceNodeKind.NAMM_HOOK,
                {
                    "kind": "internal_experiment",
                    "intent_id": namm_intent.intent_id,
                    "namm_experiment_ref": namm_intent.namm_experiment_ref,
                    "artifact": namm_intent.artifact,
                    "pipeline_stage": PipelineStage.MOTIVE_FORMATION.value,
                    "intensity": namm_intent.intensity,
                },
                parent_kind=TraceNodeKind.MOTIVE_FORMATION,
            )

        candidates = self.intention.generate_candidates(motivation, self.field)
        namm_ig_hook = self.namm.on_intention_genesis(
            len(candidates),
            max((c.expected_info_gain for c in candidates), default=0.0),
        )
        initiative = self.intention.best_or_abstain(motivation, self.field)

        self._record_stage(
            PipelineStage.INTENTION_GENESIS,
            f"Candidates={len(candidates)} abstained={initiative.abstained}",
            {
                **initiative.model_dump(mode="json"),
                "competing_count": len(candidates),
                "namm_hook": namm_ig_hook.namm_experiment_ref if namm_ig_hook else None,
            },
            trace_kind=TraceNodeKind.INTENTION_GENESIS,
            parent_kind=TraceNodeKind.MOTIVE_FORMATION,
        )

        if finalize:
            self._record_stage(
                PipelineStage.INITIATIVE_EMISSION,
                f"Emitted initiative kind={initiative.candidate.kind.value}",
                initiative.model_dump(mode="json"),
                trace_kind=TraceNodeKind.INITIATIVE_EMISSION,
                parent_kind=TraceNodeKind.INTENTION_GENESIS,
            )

            decision = self.governor.evaluate(initiative)
            self._record_stage(
                PipelineStage.CONTACT_GOVERNOR,
                f"Outcome={decision.outcome.value} score={decision.contact_score:.3f}",
                decision.model_dump(mode="json"),
                trace_kind=TraceNodeKind.CONTACT_GOVERNOR,
                parent_kind=TraceNodeKind.INITIATIVE_EMISSION,
            )
        else:
            decision = None

        self._snapshot_field = BeliefField.model_validate(self.field.model_dump())

        return motivation, initiative, decision, namm_intent

    def run_twin(self, removed_event_ids: list[str], sim: Simulator) -> tuple:
        """Counterfactual: restore pre-user-removal state, re-run cognition."""
        if not self._snapshot_field:
            raise RuntimeError("No snapshot — run tick_cognition first")

        twin_field = BeliefField.model_validate(self._snapshot_field.model_dump())
        twin_drives = DriveEngine()
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


def run_scenario(
    scenario_path: Path,
    *,
    traces_dir: Path | None = None,
    seed: int | None = None,
    twin_policy: TwinInterventionPolicy = DEFAULT_TWIN_POLICY,
    twin_remove_last_n: int = 1,
    baseline: BaselineCondition = BaselineCondition.FULL_EIA,
) -> dict:
    """Full end-to-end scenario run with labeled pipeline stages."""
    scenario = load_scenario(scenario_path)
    run_seed = seed if seed is not None else scenario.seed
    traces_dir = traces_dir or Path("traces")

    with seeded_context(run_seed):
        sim = Simulator(scenario, seed=run_seed)
        loop = CognitiveLoop(seed=run_seed)
        loop.twin_runner = TwinRunner(
            policy=twin_policy,
            remove_last_n=twin_remove_last_n,
        )

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

        motivation = initiative = decision = namm_intent = None
        tick_count = cognition_tick_count(baseline)
        if baseline == BaselineCondition.REACTIVE_ONLY:
            motivation, initiative, decision, namm_intent = make_reactive_stub(loop, sim)
        elif baseline == BaselineCondition.EVENT_RULE:
            motivation, initiative, decision, namm_intent = make_event_rule_stub(loop, sim)
        elif baseline == BaselineCondition.PREDICTIVE_P3:
            motivation, initiative, decision, namm_intent = make_predictive_p3_stub(loop, sim)
        else:
            for i in range(tick_count):
                motivation, initiative, decision, namm_intent = loop.tick_cognition(
                    tick=sim.clock.tick + i,
                    hour=sim.clock.hour,
                    finalize=(i == tick_count - 1),
                )

        removed = sim.bus.apply_twin_policy(twin_policy, remove_last_n=twin_remove_last_n)
        removed_ids = [o.id for o in removed]

        orig_initiative = initiative
        _, twin_initiative, _ = loop.run_twin(removed_ids, sim)
        twin_result = loop.twin_runner.compare(orig_initiative, twin_initiative, removed_ids)

        loop.trace.add_node(
            TraceNodeKind.TWIN_RUN,
            {
                "twin_intervention_policy": twin_policy.value,
                "twin_remove_last_n": twin_remove_last_n,
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

        agent_state = AgentState.from_cognitive_loop(
            field=loop.field,
            drive_state=loop.drives.state,
            governor=loop.governor,
            trace_id=loop.trace.trace_id,
            tick=sim.clock.tick,
        )

        if namm_intent is not None:
            loop.namm.get_or_run_sandbox(namm_intent.namm_experiment_ref)

        auth_verdict = loop.authentic_reason.evaluate(
            trace=loop.trace,
            motivation=motivation,
            initiative=initiative,
            decision=decision,
            eoi=twin_result.eoi,
            governor_state=loop.governor.state,
            sandbox_certificates=loop.namm.verified_sandbox_certificates(),
        )
        loop.trace.add_node(
            TraceNodeKind.AUTHENTIC_REASON,
            auth_verdict.model_dump(mode="json"),
            parent_kind=TraceNodeKind.CONTACT_GOVERNOR,
        )

        loop.trace.metadata = TraceMetadata(
            seed=run_seed,
            scenario_path=str(scenario_path.resolve()),
            code_version=get_code_version(),
            initial_state={
                "initial_beliefs": scenario.initial_beliefs,
                "contradictions": scenario.metadata.get("contradictions", []),
                "scenario_id": scenario.id,
                "baseline": baseline.value,
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
        "authentic_verdict": auth_verdict,
        "agent_state": agent_state,
        "trace_path": trace_path,
        "stage_log": loop.stage_log,
    }
