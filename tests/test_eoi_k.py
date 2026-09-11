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

from eoi_k_harness import (  # noqa: E402
    DEFAULT_K_VALUES,
    run_carryover_witness,
    run_eoi_k_sweep,
)


class EoiKSweepTests(unittest.TestCase):
    def test_twin_world_k_sweep_structure(self) -> None:
        result = run_eoi_k_sweep(
            REPO,
            k_values=DEFAULT_K_VALUES,
            scenario_ids=("twin_world_001",),
            seed=101,
            include_carryover=False,
        )
        self.assertEqual(result.claim_allowed, False)
        self.assertEqual(result.pool_metric_id, "E_ENDO")
        self.assertEqual(result.att, "ATT-E")
        self.assertTrue(result.counterfactual_replay)
        self.assertEqual(len(result.rows), len(DEFAULT_K_VALUES))
        for row in result.rows:
            self.assertEqual(row.scenario_id, "twin_world_001")
            self.assertFalse(row.claim_allowed)
            self.assertEqual(row.trace_mode, "twin_counterfactual")

    def test_twin_world_k1_endogenous_eoi(self) -> None:
        result = run_eoi_k_sweep(
            REPO,
            k_values=(1,),
            scenario_ids=("twin_world_001",),
            seed=101,
            include_carryover=False,
        )
        row = result.rows[0]
        self.assertGreaterEqual(row.eoi, 0.5)
        self.assertFalse(row.twin_abstained)

    def test_eoi_k_steered_gradient(self) -> None:
        result = run_eoi_k_sweep(
            REPO,
            k_values=(1, 5, 20),
            scenario_ids=("eoi_k_steered",),
            steered_seed=303,
            include_carryover=False,
        )
        by_k = {r.k: r for r in result.rows}
        self.assertGreater(by_k[1].eoi, by_k[5].eoi)
        self.assertEqual(by_k[1].twin_target, "belief-commit-atlas")
        self.assertEqual(by_k[5].twin_target, "belief-deadline")

    def test_carryover_witness_smoke(self) -> None:
        row = run_carryover_witness(seed=0, session_ticks=4)
        self.assertGreaterEqual(row.session_ticks, 4)
        self.assertGreater(row.drive_norm_final, 0.0)
        self.assertFalse(row.claim_allowed)
        self.assertEqual(row.trace_mode, "shadow_carryover")


if __name__ == "__main__":
    unittest.main()
