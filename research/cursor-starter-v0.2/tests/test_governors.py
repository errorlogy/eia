from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from eia.governors import ActionGovernor, ContactContext, ContactGovernor
from eia.models import (
    ContactMode,
    DriveKind,
    InitiativeFeatures,
    InitiativeProposal,
    ProposalKind,
)


NOW = datetime(2026, 8, 17, 8, 0, tzinfo=timezone.utc)


def proposal(
    *,
    kind: ProposalKind = ProposalKind.ASK,
    privacy: float = 0.05,
    immediate_risk: float = 0.01,
    trajectory_risk: float = 0.01,
    capability: str | None = None,
) -> InitiativeProposal:
    return InitiativeProposal(
        proposal_id="proposal:test",
        kind=kind,
        motive=DriveKind.EPISTEMIC,
        target="fact",
        content="Is the fact true?",
        features=InitiativeFeatures(
            information_gain=0.8,
            value_alignment=0.8,
            human_benefit=0.7,
            privacy_cost=privacy,
            immediate_risk=immediate_risk,
            trajectory_risk=trajectory_risk,
            interruption_cost=0.05,
        ),
        causal_parents=(),
        created_at=NOW,
        expires_at=NOW + timedelta(hours=1),
        requested_mode=ContactMode.IN_APP,
        capability=capability,
    )


class GovernorTests(unittest.TestCase):
    def test_contact_is_authorized_when_value_dominates(self) -> None:
        decision = ContactGovernor().evaluate(
            proposal(),
            ContactContext(NOW, interruptibility=0.0),
        )
        self.assertTrue(decision.allowed)

    def test_quiet_hours_are_hard_constraint(self) -> None:
        decision = ContactGovernor().evaluate(
            proposal(),
            ContactContext(NOW, quiet_hours=True, interruptibility=0.0),
        )
        self.assertFalse(decision.allowed)
        self.assertIn("quiet_hours", decision.reasons)

    def test_budget_prevents_contact_spam(self) -> None:
        history = (NOW - timedelta(hours=2), NOW - timedelta(hours=1))
        decision = ContactGovernor().evaluate(
            proposal(),
            ContactContext(NOW, interruptibility=0.0),
            history,
        )
        self.assertFalse(decision.allowed)
        self.assertIn("contact_budget_exhausted", decision.reasons)

    def test_action_needs_capability(self) -> None:
        action = proposal(kind=ProposalKind.ACT, capability="calendar.write")
        decision = ActionGovernor().evaluate(
            action,
            granted_capabilities=frozenset(),
            reversible=True,
            explicit_approval=False,
        )
        self.assertFalse(decision.allowed)
        self.assertIn("capability_not_granted", decision.reasons)


if __name__ == "__main__":
    unittest.main()

