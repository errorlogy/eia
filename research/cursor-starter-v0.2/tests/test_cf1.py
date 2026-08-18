from __future__ import annotations

import unittest

from eia.cf1 import (
    C1_PASS_RATE,
    catalog_prompts,
    filter_prompts,
    reactive_baseline_intent,
    run_seed,
    run_suite,
    summarize,
)
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator
from eia.endogenous import EndogenousSpectrumLevel


class CF1Tests(unittest.TestCase):
    def test_full_window_drops_all_prompts(self) -> None:
        events = catalog_prompts(6.0)
        self.assertGreater(len(events), 0)
        self.assertEqual(filter_prompts(events, "full", duration_seconds=6.0), ())

    def test_5m_window_keeps_early_prompts(self) -> None:
        events = catalog_prompts(6.0)
        kept = filter_prompts(events, "5m", duration_seconds=6.0)
        self.assertGreater(len(kept), 0)
        self.assertLess(len(kept), len(events))

    def test_t0_prompt_marks_partial_window_reactive(self) -> None:
        result = run_seed(7, "5m")
        self.assertGreater(result.prompt_events_kept, 0)
        self.assertTrue(result.intent)
        self.assertEqual(result.eis_level, 0)
        self.assertFalse(result.pass_c1)

    def test_reactive_baseline_silent_without_prompt(self) -> None:
        self.assertFalse(reactive_baseline_intent(()))
        self.assertTrue(reactive_baseline_intent(catalog_prompts(6.0)))

    def test_seed_7_full_deletion_remains_eis5_plus(self) -> None:
        result = run_seed(7, "full")
        self.assertTrue(result.pass_c1)
        self.assertGreaterEqual(result.eis_level or 0, int(EndogenousSpectrumLevel.EIS_5_EPISTEMIC_TELOGENESIS))
        self.assertFalse(result.reactive_would_act)

    def test_default_run_still_works_without_prompts(self) -> None:
        run = EndogenousEmergenceSimulator().run(EmergenceConfig(duration_seconds=6.0), seed=7)
        self.assertIsNotNone(run.intent)
        self.assertTrue(run.no_prompt_events)
        self.assertEqual(
            run.intent.spectrum_level,
            EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT,
        )

    def test_mini_suite_pass_rate_meets_pre_register(self) -> None:
        results = run_suite(range(7, 11), windows=("full",))
        summary = summarize(results)
        full = summary["windows"]["full"]
        self.assertGreaterEqual(full["c1_pass_rate"], C1_PASS_RATE)
        self.assertEqual(full["reactive_act_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
