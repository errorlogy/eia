"""D01 multi-seed EOI-k batch + E_C continuous probe tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAIN_SRC = REPO / "src"
SCI_FLOW = REPO / "research" / "sci_flow"

for path in (MAIN_SRC, SCI_FLOW):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from e_c_continuous_harness import run_e_c_continuous_probe  # noqa: E402
from eoi_k_harness import DEFAULT_BATCH_SEEDS, run_eoi_k_batch  # noqa: E402


class EoiKBatchTests(unittest.TestCase):
    def test_batch_structure(self) -> None:
        batch = run_eoi_k_batch(
            REPO,
            seeds=(0,),
            k_values=(1, 5),
            scenario_ids=("twin_world_001",),
            include_carryover=False,
        )
        self.assertEqual(batch.claim_allowed, False)
        self.assertEqual(len(batch.runs), 1)
        self.assertEqual(len(batch.runs[0].result.rows), 2)

    def test_multi_seed_steered_gradient(self) -> None:
        batch = run_eoi_k_batch(
            REPO,
            seeds=DEFAULT_BATCH_SEEDS,
            k_values=(1, 5),
            scenario_ids=("eoi_k_steered",),
            include_carryover=False,
        )
        for run in batch.runs:
            by_k = {r.k: r for r in run.result.rows}
            self.assertGreater(by_k[1].eoi, by_k[5].eoi)


class ECContinuousTests(unittest.TestCase):
    def test_e_c_probe_structure(self) -> None:
        result = run_e_c_continuous_probe(seeds=(0,))
        self.assertFalse(result.claim_allowed)
        self.assertEqual(result.pool_metric_id, "E_C")
        self.assertGreater(len(result.intervention_ids), 0)
        self.assertEqual(len(result.rows), len(result.intervention_ids))

    def test_e_c_bounded(self) -> None:
        result = run_e_c_continuous_probe(seeds=(0, 7))
        for row in result.rows:
            self.assertGreaterEqual(row.e_c, 0.0)
            self.assertLessEqual(row.e_c, 1.0)


if __name__ == "__main__":
    unittest.main()
