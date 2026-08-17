"""Typed agent inner state X_t — replaces informal fuzzy-set blobs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from eia.schemas.belief import Belief, BeliefUpdate
from eia.schemas.motivation import DriveKind, MotivationSignal

if TYPE_CHECKING:
    from eia.beliefs import BeliefField
    from eia.drives import DriveEngine, DriveState
    from eia.governor import ContactGovernor, GovernorState


class MemorySnapshot(BaseModel):
    """Episodic slice of M_t — recent belief mutations with trace refs."""

    recent_update_ids: list[str] = Field(default_factory=list)
    contradiction_pairs: list[tuple[str, str]] = Field(default_factory=list)
    field_entropy: float = 0.0


class GoalSnapshot(BaseModel):
    """Active goals g_t — commitment beliefs and open intentions."""

    commitment_belief_ids: list[str] = Field(default_factory=list)
    open_intention_ids: list[str] = Field(default_factory=list)


class UserModelSnapshot(BaseModel):
    """Relationship / context slice u_t (MVP-0 minimal)."""

    last_user_observation_id: str | None = None
    user_trigger_count: int = 0
    interruptibility_estimate: float = 0.5


class ConsentPolicySnapshot(BaseModel):
    """Normative layer c_t — ontology + policy flags."""

    constitution_version: str = "0.1"
    quiet_hours_active: bool = False
    capabilities: list[str] = Field(default_factory=list)


class ResourceBudgetSnapshot(BaseModel):
    """Contact and compute budget r_t."""

    contacts_today: int = 0
    daily_budget: int = 2
    budget_remaining: int = 2
    cooldown_active: bool = False
    last_contact_tick: int = -999


class HealthSnapshot(BaseModel):
    """System integrity h_t."""

    memory_integrity: str = "unknown"
    clock_integrity: str = "ok"
    sensor_integrity: str = "unknown"


class AgentState(BaseModel):
    """X_t = {b, M, d, g, u, c, r, h} — serializable inner state at time t."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tick: int = 0
    trace_id: str | None = None

    beliefs: list[Belief] = Field(default_factory=list)
    memory: MemorySnapshot = Field(default_factory=MemorySnapshot)
    drives: list[MotivationSignal] = Field(default_factory=list)
    goals: GoalSnapshot = Field(default_factory=GoalSnapshot)
    user_model: UserModelSnapshot = Field(default_factory=UserModelSnapshot)
    consent_policy: ConsentPolicySnapshot = Field(default_factory=ConsentPolicySnapshot)
    resource_budget: ResourceBudgetSnapshot = Field(default_factory=ResourceBudgetSnapshot)
    health: HealthSnapshot = Field(default_factory=HealthSnapshot)

    aggregate_uncertainty: float = 0.0
    dominant_drive: DriveKind | None = None
    risk_estimate: float = 0.0

    @classmethod
    def from_cognitive_loop(
        cls,
        *,
        field: BeliefField,
        drive_state: DriveState,
        governor: ContactGovernor | None = None,
        trace_id: str | None = None,
        tick: int = 0,
        recent_updates: list[BeliefUpdate] | None = None,
    ) -> AgentState:
        """Build X_t snapshot from live pipeline components."""
        beliefs = list(field.beliefs.values())
        gradients = field.gradient_snapshot()

        drives = [
            MotivationSignal(
                drive=DriveKind.EPISTEMIC,
                intensity=drive_state.epistemic,
                error_term=gradients["epistemic"],
                explanation="BeliefField gradient (structural)",
            ),
            MotivationSignal(
                drive=DriveKind.COHERENCE,
                intensity=drive_state.coherence,
                error_term=gradients["coherence"],
                explanation="BeliefField gradient (structural)",
            ),
            MotivationSignal(
                drive=DriveKind.COMMITMENT,
                intensity=drive_state.commitment,
                error_term=gradients["commitment"],
                explanation="BeliefField gradient (structural)",
            ),
        ]

        commitment_ids = [
            b.id for b in beliefs if b.kind.value == "commitment"
        ]

        gov_state: GovernorState | None = governor.state if governor else None
        budget = ResourceBudgetSnapshot()
        consent = ConsentPolicySnapshot()
        if governor and gov_state:
            budget.contacts_today = gov_state.contacts_today
            budget.daily_budget = governor.config.daily_budget
            budget.budget_remaining = max(
                0, governor.config.daily_budget - gov_state.contacts_today
            )
            budget.last_contact_tick = gov_state.last_contact_tick
            budget.cooldown_active = (
                gov_state.current_tick - gov_state.last_contact_tick
            ) < governor.config.cooldown_ticks
            consent.quiet_hours_active = governor._in_quiet_hours()

        updates = recent_updates or field.updates
        contradictions = [
            (c[0], c[1]) for c in field.contradictions[:10]
        ]

        avg_uncertainty = (
            sum(b.uncertainty for b in beliefs) / len(beliefs) if beliefs else 0.0
        )

        dominant = max(drives, key=lambda s: s.intensity).drive if drives else None

        return cls(
            tick=tick,
            trace_id=trace_id,
            beliefs=beliefs,
            memory=MemorySnapshot(
                recent_update_ids=[u.id for u in updates[-10:]],
                contradiction_pairs=contradictions,
                field_entropy=gradients.get("epistemic", 0.0),
            ),
            drives=drives,
            goals=GoalSnapshot(commitment_belief_ids=commitment_ids),
            user_model=UserModelSnapshot(),
            consent_policy=consent,
            resource_budget=budget,
            aggregate_uncertainty=avg_uncertainty,
            dominant_drive=dominant,
        )

    def as_x_t_dict(self) -> dict[str, Any]:
        """Map to formal notation keys for trace export."""
        return {
            "b_t": [b.model_dump(mode="json") for b in self.beliefs],
            "M_t": self.memory.model_dump(mode="json"),
            "d_t": [d.model_dump(mode="json") for d in self.drives],
            "g_t": self.goals.model_dump(mode="json"),
            "u_t": self.user_model.model_dump(mode="json"),
            "c_t": self.consent_policy.model_dump(mode="json"),
            "r_t": self.resource_budget.model_dump(mode="json"),
            "h_t": self.health.model_dump(mode="json"),
        }
