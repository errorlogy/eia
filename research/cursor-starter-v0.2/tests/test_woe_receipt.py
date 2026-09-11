from __future__ import annotations

import unittest

from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator
from eia.endogenous import EndogenousSpectrumLevel
from eia.woe_receipt import (
    WoENodeType,
    apply_governor_isolation,
    woe_internal_purity,
    woe_root_cause_purity,
)


class WoEReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.simulator = EndogenousEmergenceSimulator()
        self.config = EmergenceConfig(duration_seconds=6.0)

    def test_intent_emission_includes_typed_causal_receipt(self) -> None:
        run = self.simulator.run(self.config, seed=7)
        assert run.intent is not None
        assert run.receipt is not None
        assert run.ledger is not None
        self.assertEqual(run.receipt.seed, 7)
        self.assertEqual(len(run.receipt.parent_ids), 3)
        self.assertTrue(run.receipt.why_now)
        self.assertEqual(
            run.receipt.spectrum_level,
            EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT,
        )
        for parent_id in run.receipt.parent_ids:
            node = run.ledger.get(parent_id)
            self.assertIn(
                node.node_type,
                {
                    WoENodeType.WINDOW_STATE,
                    WoENodeType.PHASE_SAMPLE,
                    WoENodeType.TARGET_TENSION,
                },
            )
        run.receipt.validate_against_ledger(run.ledger)
        self.assertGreater(woe_internal_purity(run.ledger, run.receipt.intent_id), 0.99)
        self.assertGreater(woe_root_cause_purity(run.ledger, run.receipt.intent_id), 0.99)

    def test_receipt_absent_when_no_intent(self) -> None:
        run = self.simulator.run(self.config, seed=7, world_model_enabled=False)
        self.assertIsNone(run.intent)
        self.assertIsNone(run.receipt)

    def test_cf7_governor_denial_preserves_receipt(self) -> None:
        run = self.simulator.run(self.config, seed=7)
        assert run.intent is not None
        assert run.receipt is not None
        assert run.ledger is not None
        original_parent_ids = run.receipt.parent_ids
        outcome = apply_governor_isolation(run.receipt, run.ledger, run.intent)
        self.assertFalse(outcome.decision.allowed)
        self.assertIn("quiet_hours", outcome.decision.reasons)
        self.assertFalse(outcome.receipt.governor_allowed)
        self.assertEqual(outcome.receipt.parent_ids, original_parent_ids)
        self.assertEqual(outcome.receipt.intent_id, run.receipt.intent_id)
        self.assertIsNotNone(run.intent)
        self.assertEqual(outcome.receipt.why_now, run.receipt.why_now)
        outcome.receipt.validate_against_ledger(outcome.ledger)
        governor_nodes = [
            node
            for node in outcome.ledger.nodes
            if node.node_type == WoENodeType.GOVERNOR_DECISION
        ]
        self.assertEqual(len(governor_nodes), 1)
        self.assertEqual(governor_nodes[0].parents, (run.receipt.intent_id,))


if __name__ == "__main__":
    unittest.main()
