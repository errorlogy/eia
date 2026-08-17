"""ContactGovernor — independent rule engine, structurally separate from proposer."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from eia.schemas.contact import ContactDecision, ContactOutcome
from eia.schemas.initiative import Initiative, InitiativeKind


@dataclass
class GovernorConfig:
    """Contact budget and anti-spam parameters."""

    daily_budget: int = 2
    min_contact_score: float = 0.18
    min_evsi: float = 0.15
    fatigue_base: float = 0.10
    cooldown_ticks: int = 3
    quiet_hours: tuple[int, int] = (22, 7)
    defer_low_value: bool = True


@dataclass
class GovernorState:
    """Mutable governor state across episodes."""

    contacts_today: int = 0
    last_contact_tick: int = -999
    dismiss_count: int = 0
    current_tick: int = 0
    hour: int = 12


class ContactGovernor:
    """Rule-based contact gate — does NOT re-evaluate motive interestingness."""

    def __init__(self, config: GovernorConfig | None = None) -> None:
        self.config = config or GovernorConfig()
        self.state = GovernorState()

    def _in_quiet_hours(self) -> bool:
        start, end = self.config.quiet_hours
        h = self.state.hour
        if start > end:
            return h >= start or h < end
        return start <= h < end

    def _fatigue_penalty(self) -> float:
        base = self.config.fatigue_base * self.state.contacts_today
        dismiss = 0.15 * self.state.dismiss_count
        return min(0.8, base + dismiss)

    def _contact_score(self, initiative: Initiative) -> float:
        c = initiative.candidate
        if initiative.abstained or c.kind == InitiativeKind.ABSTAIN:
            return -1.0
        if c.kind == InitiativeKind.OBSERVE:
            return 0.0

        useful = c.expected_info_gain + c.coherence_relief + c.commitment_progress
        ic = c.interrupt_cost
        fp = self._fatigue_penalty()
        return useful - ic - fp - c.risk

    def evaluate(self, initiative: Initiative) -> ContactDecision:
        """Independent contact decision — may REJECT proposer's choice."""
        score = self._contact_score(initiative)
        fatigue = self._fatigue_penalty()
        cooldown = (
            self.state.current_tick - self.state.last_contact_tick
        ) < self.config.cooldown_ticks

        features = {
            "contact_score": score,
            "evsi": initiative.evsi,
            "fatigue_penalty": fatigue,
            "contacts_today": float(self.state.contacts_today),
            "in_quiet_hours": float(self._in_quiet_hours()),
        }

        budget_remaining = max(0, self.config.daily_budget - self.state.contacts_today)

        if initiative.abstained:
            return ContactDecision(
                id=f"gov-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(timezone.utc),
                initiative_id=initiative.id,
                outcome=ContactOutcome.ABSTAIN,
                contact_score=score,
                fatigue_penalty=fatigue,
                budget_remaining=budget_remaining,
                reason="Initiative genesis abstained — governor concurs",
                features=features,
            )

        if self.state.contacts_today >= self.config.daily_budget:
            return ContactDecision(
                id=f"gov-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(timezone.utc),
                initiative_id=initiative.id,
                outcome=ContactOutcome.DENY,
                contact_score=score,
                fatigue_penalty=fatigue,
                budget_remaining=0,
                reason="Daily contact budget exhausted",
                features=features,
            )

        if cooldown:
            return ContactDecision(
                id=f"gov-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(timezone.utc),
                initiative_id=initiative.id,
                outcome=ContactOutcome.DEFER,
                contact_score=score,
                fatigue_penalty=fatigue,
                budget_remaining=budget_remaining,
                cooldown_active=True,
                reason="Cooldown active — defer contact",
                features=features,
            )

        if self._in_quiet_hours() and score < 0.7:
            return ContactDecision(
                id=f"gov-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(timezone.utc),
                initiative_id=initiative.id,
                outcome=ContactOutcome.DEFER,
                contact_score=score,
                fatigue_penalty=fatigue,
                budget_remaining=budget_remaining,
                reason="Quiet hours — defer non-critical contact",
                features=features,
            )

        if score < self.config.min_contact_score or initiative.evsi < self.config.min_evsi:
            if initiative.candidate.kind == InitiativeKind.INTERNAL_RESEARCH:
                outcome = ContactOutcome.INTERNAL_RESEARCH
                reason = "Low contact score — route to internal research"
            else:
                outcome = ContactOutcome.DENY
                reason = (
                    f"Contact score {score:.3f} below threshold "
                    f"{self.config.min_contact_score} — REJECTED"
                )
            return ContactDecision(
                id=f"gov-{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(timezone.utc),
                initiative_id=initiative.id,
                outcome=outcome,
                contact_score=score,
                fatigue_penalty=fatigue,
                budget_remaining=budget_remaining,
                reason=reason,
                features=features,
            )

        self.state.contacts_today += 1
        self.state.last_contact_tick = self.state.current_tick

        return ContactDecision(
            id=f"gov-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc),
            initiative_id=initiative.id,
            outcome=ContactOutcome.SEND_NOW,
            contact_score=score,
            fatigue_penalty=fatigue,
            budget_remaining=budget_remaining - 1,
            reason="Contact justified — EVSI exceeds interruption cost",
            features=features,
        )
