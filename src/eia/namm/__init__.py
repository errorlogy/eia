"""NAMM adapter stub — internal_experiment intent logging when epistemic drive spikes."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from eia.schemas.motivation import DriveKind, Motivation


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


@dataclass
class NammAdapter:
    """Stub: fires when epistemic drive exceeds threshold — no namm.cli yet."""

    epistemic_threshold: float = 0.55
    log_dir: Path = field(default_factory=lambda: Path("traces/namm_intents"))
    intents: list[InternalExperimentIntent] = field(default_factory=list)

    def maybe_propose_internal_experiment(self, motivation: Motivation) -> InternalExperimentIntent | None:
        epistemic = next(
            (s for s in motivation.signals if s.drive == DriveKind.EPISTEMIC),
            None,
        )
        if not epistemic or epistemic.intensity < self.epistemic_threshold:
            return None

        intent = InternalExperimentIntent(
            intent_id=f"namm-intent-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            drive=DriveKind.EPISTEMIC.value,
            intensity=epistemic.intensity,
            target_belief_ids=epistemic.target_belief_ids,
            certificate_placeholder=f"cert-pending-{uuid.uuid4().hex[:12]}",
            status="logged",
        )
        self.intents.append(intent)
        self._persist(intent)
        return intent

    def _persist(self, intent: InternalExperimentIntent) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        path = self.log_dir / f"{intent.intent_id}.json"
        path.write_text(
            json.dumps(
                {
                    "kind": "internal_experiment",
                    "intent_id": intent.intent_id,
                    "timestamp": intent.timestamp,
                    "drive": intent.drive,
                    "intensity": intent.intensity,
                    "target_belief_ids": intent.target_belief_ids,
                    "certificate_placeholder": intent.certificate_placeholder,
                    "namm_experiment_ref": intent.namm_experiment_ref,
                    "note": (
                        "MVP-0 stub — future: namm.cli run-experiment with K_A/K_H gates"
                    ),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
