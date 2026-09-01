"""D01 EOI-k sweep tests (main pipeline + research intervention cube)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAIN_SRC = REPO / "src"
SCI_FLOW = REPO / "research" / "sci_flow"
if str(MAIN_SRC) not in sys.path:
    sys.path.insert(0, str(MAIN_SRC))
if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from eoi_k_harness import DEFAULT_K_VALUES, run_eoi_k_sweep  # noqa: E402


class EoiKSweepTests(unittest.TestCase):
    def test_twin_world_k_sweep_structure(self) -> None:
        result = run_eoi_k_sweep(
            REPO,
            k_values=DEFAULT_K_VALUES,
            scenario_ids=("twin_world_001",),
            seed=101,
        )
        self.assertEqual(result.claim_allowed, False)
        self.assertEqual(result.pool_metric_id, "E_ENDO")
        self.assertEqual(len(result.rows), len(DEFAULT_K_VALUES))
        for row in result.rows:
            self.assertEqual(row.scenario_id, "twin_world_001")
            self.assertFalse(row.claim_allowed)

    def test_twin_world_k1_endogenous_eoi(self) -> None:
        result = run_eoi_k_sweep(
            REPO,
            k_values=(1,),
            scenario_ids=("twin_world_001",),
            seed=101,
        )
        row = result.rows[0]
        self.assertGreaterEqual(row.eoi, 0.5)
        self.assertFalse(row.twin_abstained)


if __name__ == "__main__":
    unittest.main()
