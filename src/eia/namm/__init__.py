"""NAMM adapter — internal_experiment hooks keyed by pipeline stage and drive."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from eia.scheduler import PipelineStage
from eia.schemas.motivation import DriveKind, Motivation
from eia.sense_making import ComprehensionResult


@dataclass
class NammHook:
    """Single NAMM experiment hook fired during pipeline."""

    hook_id: str
    pipeline_stage: str
    namm_experiment_ref: str
    domain: str
    artifact: str
    trigger: str
    intensity: float
    certificate_placeholder: str
    status: str = "logged"


@dataclass
class InternalExperimentIntent:
    """Placeholder for NAMM Protocol v2 sandbox delegation."""

    intent_id: str
    timestamp: str
    drive: str
    intensity: float
    target_belief_ids: list[str]
    certificate_placeholder: str
    status: str = "logged"
    namm_experiment_ref: str = "NAMM-2026-003"
    pipeline_stage: str = "motive_formation"
    artifact: str = ""


@dataclass
class NammAdapter:
    """Stage-aware NAMM hooks — no namm.cli invocation in MVP-0."""

    epistemic_threshold: float = 0.50
    coherence_threshold: float = 0.20
    log_dir: Path = field(default_factory=lambda: Path("traces/namm_intents"))
    config_path: Path | None = None
    intents: list[InternalExperimentIntent] = field(default_factory=list)
    hooks: list[NammHook] = field(default_factory=list)
    _stage_config: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        path = self.config_path or (
            Path(__file__).resolve().parents[3] / "config" / "namm_crosswalk.yaml"
        )
        if path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            self._stage_config = data.get("stages", {})

    def _stage_experiments(self, stage: str) -> list[dict[str, Any]]:
        return self._stage_config.get(stage, {}).get("namm_experiments", [])

    def on_sense_making(self, comprehension: ComprehensionResult) -> list[NammHook]:
        """Fire topology hooks when comprehension thresholds met."""
        fired: list[NammHook] = []
        for exp in self._stage_experiments("sense_making"):
            trigger = exp.get("trigger", "")
            fired_hook = False
            if trigger == "coherence_energy_above":
                if comprehension.inconsistency_energy >= exp.get("threshold", 0.25):
                    fired_hook = True
            elif trigger == "epistemic_and_coherence_above":
                if (
                    comprehension.field_entropy >= exp.get("epistemic_threshold", 0.45)
                    and comprehension.inconsistency_energy
                    >= exp.get("coherence_threshold", 0.20)
                ):
                    fired_hook = True

            if fired_hook:
                hook = NammHook(
                    hook_id=f"namm-hook-{uuid.uuid4().hex[:8]}",
                    pipeline_stage=PipelineStage.SENSE_MAKING.value,
                    namm_experiment_ref=exp["id"],
                    domain=exp.get("domain", ""),
                    artifact=exp.get("artifact", ""),
                    trigger=trigger,
                    intensity=max(
                        comprehension.field_entropy,
                        comprehension.inconsistency_energy,
                    ),
                    certificate_placeholder=f"cert-pending-{uuid.uuid4().hex[:12]}",
                )
                fired.append(hook)
                self.hooks.append(hook)
                self._persist_hook(hook)

        if comprehension.namm_topology_ref and not fired:
            hook = NammHook(
                hook_id=f"namm-hook-{uuid.uuid4().hex[:8]}",
                pipeline_stage=PipelineStage.SENSE_MAKING.value,
                namm_experiment_ref=comprehension.namm_topology_ref,
                domain="meta_evaluation" if "004" in comprehension.namm_topology_ref else "tda_frame",
                artifact="topology comprehension threshold",
                trigger="comprehension_namm_ref",
                intensity=comprehension.field_entropy,
                certificate_placeholder=f"cert-pending-{uuid.uuid4().hex[:12]}",
            )
            fired.append(hook)
            self.hooks.append(hook)
            self._persist_hook(hook)

        return fired

    def maybe_propose_internal_experiment(
        self,
        motivation: Motivation,
        *,
        comprehension: ComprehensionResult | None = None,
    ) -> InternalExperimentIntent | None:
        """Fire when epistemic drive exceeds threshold — maps to NAMM-2026-003/013."""
        epistemic = next(
            (s for s in motivation.signals if s.drive == DriveKind.EPISTEMIC),
            None,
        )
        coherence = next(
            (s for s in motivation.signals if s.drive == DriveKind.COHERENCE),
            None,
        )
        if not epistemic or epistemic.intensity < self.epistemic_threshold:
            return None

        exp_ref = "NAMM-2026-003"
        artifact = "program AST synthesis — internal epistemic sandbox"
        if comprehension and comprehension.coherence_threshold_met:
            exp_ref = "NAMM-2026-013"
            artifact = "cognitive antigravity — escape median embedding gravity (H-CA-001)"

        for exp in self._stage_experiments("motive_formation"):
            if exp["id"] == exp_ref:
                artifact = exp.get("artifact", artifact)
                break

        intent = InternalExperimentIntent(
            intent_id=f"namm-intent-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            drive=DriveKind.EPISTEMIC.value,
            intensity=epistemic.intensity,
            target_belief_ids=epistemic.target_belief_ids,
            certificate_placeholder=f"cert-pending-{uuid.uuid4().hex[:12]}",
            status="logged",
            namm_experiment_ref=exp_ref,
            pipeline_stage=PipelineStage.MOTIVE_FORMATION.value,
            artifact=artifact,
        )
        self.intents.append(intent)
        self._persist(intent)

        if coherence and coherence.intensity >= self.coherence_threshold:
            hook = NammHook(
                hook_id=f"namm-hook-{uuid.uuid4().hex[:8]}",
                pipeline_stage=PipelineStage.MOTIVE_FORMATION.value,
                namm_experiment_ref="NAMM-2026-004",
                domain="meta_evaluation",
                artifact="drive arbitration under AI thinking topology",
                trigger="coherence_drive_above",
                intensity=coherence.intensity,
                certificate_placeholder=intent.certificate_placeholder,
            )
            self.hooks.append(hook)
            self._persist_hook(hook)

        return intent

    def on_intention_genesis(self, candidate_count: int, max_evsi: float) -> NammHook | None:
        """Optional hook when competing candidates exceed threshold."""
        for exp in self._stage_experiments("intention_genesis"):
            if exp.get("trigger") == "competing_candidates_ge_3" and candidate_count >= 3:
                hook = NammHook(
                    hook_id=f"namm-hook-{uuid.uuid4().hex[:8]}",
                    pipeline_stage=PipelineStage.INTENTION_GENESIS.value,
                    namm_experiment_ref=exp["id"],
                    domain=exp.get("domain", ""),
                    artifact=exp.get("artifact", ""),
                    trigger=exp["trigger"],
                    intensity=max_evsi,
                    certificate_placeholder=f"cert-pending-{uuid.uuid4().hex[:12]}",
                )
                self.hooks.append(hook)
                self._persist_hook(hook)
                return hook
        return None

    def _persist(self, intent: InternalExperimentIntent) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        path = self.log_dir / f"{intent.intent_id}.json"
        path.write_text(
            json.dumps(
                {
                    "kind": "internal_experiment",
                    "intent_id": intent.intent_id,
                    "timestamp": intent.timestamp,
                    "pipeline_stage": intent.pipeline_stage,
                    "drive": intent.drive,
                    "intensity": intent.intensity,
                    "target_belief_ids": intent.target_belief_ids,
                    "certificate_placeholder": intent.certificate_placeholder,
                    "namm_experiment_ref": intent.namm_experiment_ref,
                    "artifact": intent.artifact,
                    "note": (
                        "MVP-0 stub — future: namm.cli run-experiment with K_A/K_H gates"
                    ),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def _persist_hook(self, hook: NammHook) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        path = self.log_dir / f"{hook.hook_id}.json"
        path.write_text(
            json.dumps(
                {
                    "kind": "namm_hook",
                    "hook_id": hook.hook_id,
                    "pipeline_stage": hook.pipeline_stage,
                    "namm_experiment_ref": hook.namm_experiment_ref,
                    "domain": hook.domain,
                    "artifact": hook.artifact,
                    "trigger": hook.trigger,
                    "intensity": hook.intensity,
                    "certificate_placeholder": hook.certificate_placeholder,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
