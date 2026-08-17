"""Independent contact and action authorization boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .math_model import accumulated_prefix_risk, initiative_utility
from .models import (
    ActionDecision,
    ContactDecision,
    ContactMode,
    InitiativeProposal,
    ProposalKind,
)


@dataclass(frozen=True, slots=True)
class ContactContext:
    now: datetime
    consent: bool = True
    quiet_hours: bool = False
    interruptibility: float = 0.5
    recent_decline: bool = False
    channel_available: bool = True
    emergency: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.interruptibility <= 1.0:
            raise ValueError("interruptibility must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class ContactPolicy:
    minimum_score: float = 0.20
    maximum_contacts: int = 2
    window_seconds: float = 86_400.0
    cooldown_seconds: float = 3_600.0
    maximum_privacy_cost: float = 0.35
    maximum_combined_risk: float = 0.25


class ContactGovernor:
    """A proposer cannot bypass this class to emit an external contact."""

    def __init__(self, policy: ContactPolicy = ContactPolicy()) -> None:
        self.policy = policy

    def evaluate(
        self,
        proposal: InitiativeProposal,
        context: ContactContext,
        contact_history: tuple[datetime, ...] = (),
    ) -> ContactDecision:
        now = context.now
        if not proposal.is_contact:
            return ContactDecision(True, ContactMode.NONE, 0.0, ("not_a_contact",), now)

        hard_denials: list[str] = []
        if not context.consent:
            hard_denials.append("consent_absent")
        if not context.channel_available:
            hard_denials.append("channel_unavailable")
        if context.recent_decline:
            hard_denials.append("recent_user_decline")
        if proposal.features.privacy_cost > self.policy.maximum_privacy_cost:
            hard_denials.append("privacy_cost_too_high")

        combined_risk = accumulated_prefix_risk(
            (proposal.features.immediate_risk, proposal.features.trajectory_risk)
        )
        if combined_risk > self.policy.maximum_combined_risk:
            hard_denials.append("risk_too_high")
        if context.quiet_hours and not context.emergency:
            hard_denials.append("quiet_hours")

        window_start = now - timedelta(seconds=self.policy.window_seconds)
        recent = tuple(ts for ts in contact_history if ts >= window_start)
        if len(recent) >= self.policy.maximum_contacts:
            hard_denials.append("contact_budget_exhausted")
        if recent and (now - max(recent)).total_seconds() < self.policy.cooldown_seconds:
            hard_denials.append("cooldown_active")

        adjusted_interrupt = proposal.features.interruption_cost + context.interruptibility
        score = initiative_utility(proposal.features) - adjusted_interrupt
        if score < self.policy.minimum_score:
            hard_denials.append("insufficient_net_value")

        if hard_denials:
            next_check = now + timedelta(seconds=self.policy.cooldown_seconds)
            return ContactDecision(
                False,
                ContactMode.NONE,
                score,
                tuple(hard_denials),
                now,
                next_check,
            )

        mode = proposal.requested_mode
        if mode is ContactMode.URGENT and not context.emergency:
            mode = ContactMode.IN_APP
        return ContactDecision(True, mode, score, ("authorized",), now)


@dataclass(frozen=True, slots=True)
class ActionPolicy:
    maximum_immediate_risk: float = 0.15
    maximum_trajectory_risk: float = 0.20
    require_reversible: bool = True


class ActionGovernor:
    def __init__(self, policy: ActionPolicy = ActionPolicy()) -> None:
        self.policy = policy

    def evaluate(
        self,
        proposal: InitiativeProposal,
        *,
        granted_capabilities: frozenset[str],
        reversible: bool,
        explicit_approval: bool,
    ) -> ActionDecision:
        reasons: list[str] = []
        if proposal.kind is not ProposalKind.ACT:
            return ActionDecision(True, 0.0, ("not_an_action",))
        if proposal.capability is None or proposal.capability not in granted_capabilities:
            reasons.append("capability_not_granted")
        if proposal.features.immediate_risk > self.policy.maximum_immediate_risk:
            reasons.append("immediate_risk_too_high")
        if proposal.features.trajectory_risk > self.policy.maximum_trajectory_risk:
            reasons.append("trajectory_risk_too_high")
        if self.policy.require_reversible and not reversible and not explicit_approval:
            reasons.append("irreversible_action_requires_approval")
        return ActionDecision(not reasons, initiative_utility(proposal.features), tuple(reasons or ["authorized"]))

