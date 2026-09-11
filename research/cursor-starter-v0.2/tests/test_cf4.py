from __future__ import annotations

import unittest

from eia.cf4 import run_seed, run_suite, summarize
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator, InternalReset


class CF4Tests(unittest.TestCase):
    def test_default_reference_seed_emits(self) -> None:
        result = run_seed(7, "default")
        self.assertTrue(result.intent)

    def test_wm_off_blocks_reference_seed(self) -> None:
        result = run_seed(7, "wm_off")
        self.assertFalse(result.intent)

    def test_internal_reset_zero_epistemic_gap_lowers_pressure(self) -> None:
        sim = EndogenousEmergenceSimulator()
        cfg = EmergenceConfig(duration_seconds=6.0)
        default = sim.run(cfg, seed=7)
        ablated = sim.run(
            cfg,
            seed=7,
            internal_reset=InternalReset(zero_epistemic_gap=True),
        )
        self.assertIsNotNone(default.intent)
        # Ablation may or may not block seed-7; population rates decide C2.
        self.assertLessEqual(ablated.peak_potential, default.peak_potential)

    def test_mini_suite_default_high_wm_off_zero(self) -> None:
        results = run_suite(
            range(7, 11),
            conditions=("default", "wm_off", "zero_staleness"),
        )
        summary = summarize(results)
        self.assertGreaterEqual(summary["conditions"]["default"]["intent_rate"], 0.75)
        self.assertEqual(summary["conditions"]["wm_off"]["intent_rate"], 0.0)

    def test_summarize_does_not_claim_c2_without_named_factor(self) -> None:
        # Synthetic: only default + wm_off rows → only_wm_off_suppresses path.
        results = run_suite(range(1, 5), conditions=("default", "wm_off"))
        summary = summarize(results)
        self.assertFalse(summary["c2_claim"])
        self.assertFalse(summary["agi_star_claim"])
        if summary["conditions"]["default"]["intent_rate"] >= 0.85:
            self.assertTrue(summary["only_wm_off_suppresses"] or summary["suppressing_named_factors"])

    def test_summarize_never_claims_agi_star(self) -> None:
        results = run_suite(
            range(7, 9),
            conditions=("default", "zero_epistemic_gap", "wm_off"),
        )
        summary = summarize(results)
        self.assertFalse(summary["agi_star_claim"])
        self.assertEqual(summary["e_endo_partial"], summary["c2_claim"])


if __name__ == "__main__":
    unittest.main()
