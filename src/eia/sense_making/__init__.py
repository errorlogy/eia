"""SenseMaking — explicit comprehension step between observation and drives.

Separates raw ObservationEvent ingestion from BeliefField update and
structural comprehension (topology, entropy, contradiction energy).
NAMM-aligned: uses graph topology metrics, not embedding similarity.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from eia.beliefs import BeliefField
from eia.schemas.belief import BeliefKind, BeliefUpdate
from eia.schemas.observation import Observation


class ComprehensionResult(BaseModel):
    """Machine-readable sense-making output — causal input to DriveEngine."""

    id: str
    timestamp: datetime
    pipeline_stage: str = "sense_making"
    observation_ids: list[str] = Field(default_factory=list)
    belief_update_ids: list[str] = Field(default_factory=list)
    field_entropy: float = 0.0
    inconsistency_energy: float = 0.0
    commitment_debt: float = 0.0
    contradiction_count: int = 0
    comprehension_summary: str = ""
    epistemic_threshold_met: bool = False
    coherence_threshold_met: bool = False
    namm_topology_ref: str | None = None


class SenseMakingEngine:
    """Apply observations to BeliefField and emit comprehension artifact."""

    EPISTEMIC_THRESHOLD = 0.45
    COHERENCE_THRESHOLD = 0.20

    def __init__(self, field: BeliefField) -> None:
        self.field = field

    def ingest_observation(self, obs: Observation) -> ComprehensionResult | None:
        """Map observation topic → belief updates; return comprehension snapshot."""
        payload = obs.payload
        updates_before = len(self.field.updates)

        if obs.topic == "project_atlas_deadline":
            self.field.upsert_belief(
                "belief-deadline",
                kind=BeliefKind.CATEGORICAL,
                subject="Project Atlas",
                claim="deadline date",
                distribution=payload.get(
                    "distribution",
                    {"Aug 30": 0.4, "Sep 15": 0.35, "unknown": 0.25},
                ),
                uncertainty=0.85,
                source_observation_id=obs.id,
            )
        elif obs.topic == "conflicting_deadline_report":
            self.field.upsert_belief(
                "belief-deadline-alt",
                kind=BeliefKind.CATEGORICAL,
                subject="Project Atlas",
                claim="alternate deadline from email",
                distribution=payload.get(
                    "distribution",
                    {"Aug 30": 0.1, "Sep 15": 0.8, "unknown": 0.1},
                ),
                uncertainty=0.7,
                source_observation_id=obs.id,
            )
            self.field.register_contradiction(
                "belief-deadline", "belief-deadline-alt", "Project Atlas deadline"
            )
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
        elif obs.topic in ("quiet_period", "clock_tick"):
            return None
        else:
            return None

        new_updates = self.field.updates[updates_before:]
        gradients = self.field.gradient_snapshot()
        epistemic = gradients["epistemic"]
        coherence = gradients["coherence"]
        ep_met = epistemic >= self.EPistemic_THRESHOLD
        co_met = coherence >= self.COHERENCE_THRESHOLD

        namm_ref = None
        if co_met:
            namm_ref = "NAMM-2026-006"
        if ep_met and co_met:
            namm_ref = "NAMM-2026-004"

        summary_parts = [f"Processed {obs.topic}"]
        if self.field.contradictions:
            summary_parts.append(
                f"{len(self.field.contradictions)} contradiction(s) in belief topology"
            )
        summary_parts.append(f"field_entropy={epistemic:.3f}")

        return ComprehensionResult(
            id=f"comp-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc),
            observation_ids=[obs.id],
            belief_update_ids=[u.id for u in new_updates],
            field_entropy=epistemic,
            inconsistency_energy=coherence,
            commitment_debt=gradients["commitment"],
            contradiction_count=len(self.field.contradictions),
            comprehension_summary="; ".join(summary_parts),
            epistemic_threshold_met=ep_met,
            coherence_threshold_met=co_met,
            namm_topology_ref=namm_ref,
        )

    def snapshot(self) -> ComprehensionResult:
        """Field-level comprehension without new observation."""
        gradients = self.field.gradient_snapshot()
        ep = gradients["epistemic"]
        co = gradients["coherence"]
        return ComprehensionResult(
            id=f"comp-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc),
            belief_update_ids=[u.id for u in self.field.updates[-5:]],
            field_entropy=ep,
            inconsistency_energy=co,
            commitment_debt=gradients["commitment"],
            contradiction_count=len(self.field.contradictions),
            comprehension_summary=(
                f"BeliefField snapshot: entropy={ep:.3f}, "
                f"coherence_tension={co:.3f}, contradictions={len(self.field.contradictions)}"
            ),
            epistemic_threshold_met=ep >= self.EPistemic_THRESHOLD,
            coherence_threshold_met=co >= self.COHERENCE_THRESHOLD,
            namm_topology_ref="NAMM-2026-006" if co >= self.COHERENCE_THRESHOLD else None,
        )
