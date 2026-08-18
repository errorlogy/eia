"""NAMM adapter — internal_experiment hooks keyed by pipeline stage and drive."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from eia.ids import new_id

from eia.scheduler import PipelineStage
from eia.schemas.motivation import DriveKind, Motivation
from eia.sense_making import ComprehensionResult

DEFAULT_NAMM_ROOT = Path(os.environ.get("NAMM_ROOT", "C:/Users/Public/NAMM"))


@dataclass(frozen=True, slots=True)
class SandboxCertificate:
    """Certificate reference returned by NAMM sandbox delegation."""

    experiment_id: str
    status: str  # verified | stub | error | not_installed
    hypothesis_confirmed: bool | None = None
    certificate_path: str | None = None
    result_path: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "status": self.status,
            "hypothesis_confirmed": self.hypothesis_confirmed,
            "certificate_path": self.certificate_path,
            "result_path": self.result_path,
            "metrics": self.metrics,
            "error": self.error,
        }


CERTIFICATE_SCHEMA = {
    "type": "object",
    "required": ["experiment_id", "protocol", "status"],
    "properties": {
        "experiment_id": {"type": "string"},
        "protocol": {"type": "string"},
        "status": {"type": "string", "enum": ["VERIFIED", "PENDING", "REJECTED"]},
        "d_med_lift": {"type": "string"},
        "pipeline_compliance": {"type": "string"},
        "z_star_mean": {"type": "number"},
    },
}


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
    namm_root: Path = field(default_factory=lambda: DEFAULT_NAMM_ROOT)
    intents: list[InternalExperimentIntent] = field(default_factory=list)
    hooks: list[NammHook] = field(default_factory=list)
    sandbox_runs: list[SandboxCertificate] = field(default_factory=list)
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
                    hook_id=new_id("namm-hook"),
                    pipeline_stage=PipelineStage.SENSE_MAKING.value,
                    namm_experiment_ref=exp["id"],
                    domain=exp.get("domain", ""),
                    artifact=exp.get("artifact", ""),
                    trigger=trigger,
                    intensity=max(
                        comprehension.field_entropy,
                        comprehension.inconsistency_energy,
                    ),
                    certificate_placeholder=new_id("cert-pending"),
                )
                fired.append(hook)
                self.hooks.append(hook)
                self._persist_hook(hook)

        if comprehension.namm_topology_ref and not fired:
            hook = NammHook(
                hook_id=new_id("namm-hook"),
                pipeline_stage=PipelineStage.SENSE_MAKING.value,
                namm_experiment_ref=comprehension.namm_topology_ref,
                domain="meta_evaluation" if "004" in comprehension.namm_topology_ref else "tda_frame",
                artifact="topology comprehension threshold",
                trigger="comprehension_namm_ref",
                intensity=comprehension.field_entropy,
                certificate_placeholder=new_id("cert-pending"),
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
            intent_id=new_id("namm-intent"),
            timestamp=datetime.now(timezone.utc).isoformat(),
            drive=DriveKind.EPISTEMIC.value,
            intensity=epistemic.intensity,
            target_belief_ids=epistemic.target_belief_ids,
            certificate_placeholder=new_id("cert-pending"),
            status="logged",
            namm_experiment_ref=exp_ref,
            pipeline_stage=PipelineStage.MOTIVE_FORMATION.value,
            artifact=artifact,
        )
        self.intents.append(intent)
        self._persist(intent)

        if coherence and coherence.intensity >= self.coherence_threshold:
            hook = NammHook(
                hook_id=new_id("namm-hook"),
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

    def get_or_run_sandbox(self, experiment_id: str) -> SandboxCertificate:
        """Return cached sandbox certificate or delegate to NAMM CLI."""
        for cert in self.sandbox_runs:
            if cert.experiment_id == experiment_id:
                return cert
        return self.run_sandbox(experiment_id)

    def verified_sandbox_certificates(self) -> list[SandboxCertificate]:
        """Certificates with live NAMM verification."""
        return [c for c in self.sandbox_runs if c.status == "verified"]

    def run_sandbox(self, experiment_id: str) -> SandboxCertificate:
        """Delegate to NAMM CLI run-experiment when install is available."""
        artifacts_dir = self.namm_root / "experiments" / experiment_id / "artifacts"
        cert_path = artifacts_dir / "certificate.json"
        result_path = artifacts_dir / "result.json"

        if not self.namm_root.exists():
            cert = SandboxCertificate(
                experiment_id=experiment_id,
                status="not_installed",
                error=f"NAMM root not found: {self.namm_root}",
            )
            self.sandbox_runs.append(cert)
            self._persist_certificate(cert)
            return cert

        try:
            proc = subprocess.run(
                [sys.executable, "-m", "namm", "run-experiment", "--id", experiment_id],
                cwd=str(self.namm_root),
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            if proc.returncode != 0:
                cert = SandboxCertificate(
                    experiment_id=experiment_id,
                    status="error",
                    error=(proc.stderr or proc.stdout or "namm run-experiment failed").strip(),
                )
                self.sandbox_runs.append(cert)
                self._persist_certificate(cert)
                return cert
        except (OSError, subprocess.TimeoutExpired) as exc:
            cert = SandboxCertificate(
                experiment_id=experiment_id,
                status="error",
                error=str(exc),
            )
            self.sandbox_runs.append(cert)
            self._persist_certificate(cert)
            return cert

        metrics: dict[str, Any] = {}
        hypothesis_confirmed = None
        if result_path.exists():
            result_data = json.loads(result_path.read_text(encoding="utf-8"))
            hypothesis_confirmed = result_data.get("hypothesis_confirmed")
            metrics = result_data.get("metrics_summary", {})

        status = "verified" if cert_path.exists() else "stub"
        cert = SandboxCertificate(
            experiment_id=experiment_id,
            status=status,
            hypothesis_confirmed=hypothesis_confirmed,
            certificate_path=str(cert_path) if cert_path.exists() else None,
            result_path=str(result_path) if result_path.exists() else None,
            metrics=metrics,
        )
        self.sandbox_runs.append(cert)
        self._persist_certificate(cert)
        return cert

    def on_intention_genesis(self, candidate_count: int, max_evsi: float) -> NammHook | None:
        """Optional hook when competing candidates exceed threshold."""
        for exp in self._stage_experiments("intention_genesis"):
            if exp.get("trigger") == "competing_candidates_ge_3" and candidate_count >= 3:
                hook = NammHook(
                    hook_id=new_id("namm-hook"),
                    pipeline_stage=PipelineStage.INTENTION_GENESIS.value,
                    namm_experiment_ref=exp["id"],
                    domain=exp.get("domain", ""),
                    artifact=exp.get("artifact", ""),
                    trigger=exp["trigger"],
                    intensity=max_evsi,
                    certificate_placeholder=new_id("cert-pending"),
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

    def _persist_certificate(self, cert: SandboxCertificate) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        path = self.log_dir / f"sandbox-{cert.experiment_id}.json"
        payload = {
            "kind": "namm_sandbox_certificate",
            "certificate_schema": CERTIFICATE_SCHEMA,
            **cert.to_dict(),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
