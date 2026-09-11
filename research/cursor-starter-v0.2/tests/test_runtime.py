from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from eia.models import DriveKind, ProposalKind
from eia.simulator import SimulationRunner, load_scenario


ROOT = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def test_ambient_event_generates_question_without_request(self) -> None:
        scenario = load_scenario(ROOT / "examples" / "autonomous_question.json")
        result = SimulationRunner().run(scenario)
        selected = [tick.selected for tick in result.results if tick.selected]
        self.assertTrue(selected)
        self.assertEqual(selected[0].kind, ProposalKind.ASK)
        self.assertEqual(selected[0].motive, DriveKind.EPISTEMIC)
        self.assertEqual(selected[0].target, "project_review_time_confirmed")

    def test_user_event_removal_preserves_endogenous_question(self) -> None:
        scenario = load_scenario(ROOT / "examples" / "autonomous_question.json")
        result = SimulationRunner().run(scenario, remove_user_events=True)
        selected = [tick.selected for tick in result.results if tick.selected]
        self.assertTrue(selected)
        self.assertEqual(selected[0].target, "project_review_time_confirmed")

    def test_commitment_can_wake_agent(self) -> None:
        from eia.governors import ContactContext
        from eia.runtime import EIARuntime

        now = datetime(2026, 8, 17, 8, 0, tzinfo=timezone.utc)
        runtime = EIARuntime()
        runtime.register_commitment(
            commitment_id="c1",
            target="paper_deadline",
            label="подготовить черновик статьи",
            due_at=now,
            importance=1.0,
            registered_at=now,
        )
        tick = runtime.tick(ContactContext(now, interruptibility=0.0))
        self.assertIsNotNone(tick.selected)
        assert tick.selected is not None
        self.assertEqual(tick.selected.motive, DriveKind.COMMITMENT)


if __name__ == "__main__":
    unittest.main()

