"""CF-7 governor isolation harness tests (D3×L2)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCI_FLOW = REPO / "research" / "sci_flow"
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from cf7_governor_isolation_harness import (  # noqa: E402
    run_cf7_arm,
    run_cf7_paired,
    run_cf7_paired_batch,
)


class Cf7GovernorIsolationTests(unittest.TestCase):
    def test_governor_off_emits_intent_under_x_zero(self) -> None:
        arm = run_cf7_arm(REPO, seed=7, governor_on=False)
        self.assertTrue(arm.intent_emitted)
        self.assertTrue(arm.x_trigger_zero)
        self.assertFalse(arm.governor_applied)
        self.assertTrue(arm.external_contact_allowed)
        self.assertTrue(arm.ok)

    def test_governor_on_denies_but_preserves_receipt(self) -> None:
        arm = run_cf7_arm(REPO, seed=7, governor_on=True)
        self.assertTrue(arm.intent_emitted)
        self.assertTrue(arm.governor_applied)
        self.assertTrue(arm.governor_denied)
        self.assertFalse(arm.external_contact_allowed)
        self.assertTrue(arm.parent_ids_preserved)
        self.assertIn("quiet_hours", arm.governor_reasons)
        self.assertTrue(arm.ok)

    def test_paired_isolation_seed_7(self) -> None:
        paired = run_cf7_paired(REPO, seed=7)
        self.assertIsNotNone(paired)
        assert paired is not None
        self.assertTrue(paired.isolation_ok)
        self.assertTrue(paired.governor_off.ok)
        self.assertTrue(paired.governor_on.ok)

    def test_batch_claim_ceiling(self) -> None:
        batch = run_cf7_paired_batch(REPO, seeds=(7, 8, 9))
        self.assertEqual(batch.intervention_id, "do_z_governor_isolation")
        self.assertTrue(batch.x_trigger_zero)
        self.assertGreaterEqual(batch.n_paired, 1)
        self.assertFalse(batch.claim_allowed)
        self.assertFalse(batch.n_h_claim)
        self.assertFalse(batch.agi_star_claim)
        self.assertEqual(batch.claim_ceiling, "C2")
        self.assertTrue(batch.passed)


if __name__ == "__main__":
    unittest.main()
