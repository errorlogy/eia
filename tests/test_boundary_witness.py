"""D3×L3 boundary witness harness tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCI_FLOW = REPO / "research" / "sci_flow"
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from boundary_witness_harness import (  # noqa: E402
    REQUIRED_BOUNDARY_FALSIFIERS,
    run_boundary_witness,
    run_falsifier_registry_smoke,
    run_governor_gate_smoke,
    run_namm_soft_witness,
)


class BoundaryWitnessTests(unittest.TestCase):
    def test_falsifier_registry_links(self) -> None:
        row = run_falsifier_registry_smoke(REPO)
        self.assertGreaterEqual(row.intervention_count_d3, 2)
        self.assertEqual(set(row.linked), set(REQUIRED_BOUNDARY_FALSIFIERS))
        self.assertEqual(row.missing, ())
        self.assertTrue(row.ok)

    def test_governor_gate_smoke(self) -> None:
        row = run_governor_gate_smoke(REPO)
        self.assertTrue(row.deny_low_value)
        self.assertTrue(row.cf7_intervention_present)
        self.assertTrue(row.ok)

    def test_namm_soft_witness_corpus(self) -> None:
        row = run_namm_soft_witness(REPO)
        if row.intent_files > 0:
            self.assertGreater(row.valid_json, 0)
            self.assertEqual(row.tier, "B")

    def test_boundary_witness_passes(self) -> None:
        result = run_boundary_witness(REPO, att_n_seeds=2)
        self.assertTrue(result.passed)
        self.assertFalse(result.claim_allowed)
        self.assertFalse(result.n_h_claim)
        self.assertFalse(result.agi_star_claim)
        self.assertEqual(result.claim_ceiling, "C2")
        self.assertIn(result.witness_tier, ("B_soft_NH", "B_partial"))


if __name__ == "__main__":
    unittest.main()
