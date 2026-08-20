from __future__ import annotations

import unittest

from eia.amat_m0 import (
    M0TwinMode,
    compute_m0_sketch,
    differs_from_m0,
    select_median_m0,
    select_m0_twin,
    summarize_mode_batch,
)
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator, default_targets
from eia.endogenous import IntentKind


class AmatM0UnitTests(unittest.TestCase):
    def test_emit_m0_always_false(self) -> None:
        sketch = compute_m0_sketch(
            epistemic_pressure=0.9,
            peak_coherence=0.5,
            self_prior_mismatch=0.8,
            targets=default_targets(),
            mode=M0TwinMode.ON,
        )
        self.assertFalse(sketch.emit_m0)
        self.assertFalse(sketch.as_audit_dict()["emit_m0"])

    def test_high_mismatch_hints_nd(self) -> None:
        sketch = compute_m0_sketch(
            epistemic_pressure=0.9,
            peak_coherence=0.5,
            self_prior_mismatch=0.9,
            targets=default_targets(),
            mode=M0TwinMode.AUDIT_ONLY,
        )
        self.assertEqual(sketch.phase_hint, "K_AI_nd_hint")
        self.assertGreaterEqual(sketch.distance_to_typical, 1.0)

    def test_median_m0_prefers_ask(self) -> None:
        m0 = select_median_m0(default_targets())
        self.assertEqual(m0.kind, IntentKind.ASK)
        self.assertEqual(m0.target_id, "collaboration:latent_question")

    def test_twin_differs_from_m0(self) -> None:
        targets = default_targets()
        m0 = select_median_m0(targets)
        twin = select_m0_twin(targets, m0=m0)
        self.assertNotEqual(twin.target_id, m0.target_id)
        self.assertEqual(twin.kind, IntentKind.INTERNAL_RESEARCH)

    def test_off_mode_collapses_to_m0(self) -> None:
        sketch = compute_m0_sketch(
            epistemic_pressure=0.9,
            peak_coherence=0.5,
            self_prior_mismatch=0.9,
            targets=default_targets(),
            mode=M0TwinMode.OFF,
        )
        self.assertTrue(sketch.collapsed_to_m0)
        self.assertIsNotNone(sketch.selected)
        assert sketch.selected is not None
        self.assertEqual(sketch.selected.target_id, sketch.m0.target_id)
        self.assertFalse(differs_from_m0(sketch))

    def test_on_mode_selects_twin_when_gate_clears(self) -> None:
        sketch = compute_m0_sketch(
            epistemic_pressure=0.95,
            peak_coherence=0.55,
            self_prior_mismatch=0.95,
            targets=default_targets(),
            mode=M0TwinMode.ON,
        )
        self.assertTrue(sketch.gate_cleared)
        self.assertTrue(differs_from_m0(sketch))
        assert sketch.selected is not None
        self.assertEqual(sketch.selected.target_id, sketch.twin.target_id)
        self.assertFalse(sketch.emit_m0)

    def test_on_mode_abstains_when_gate_misses(self) -> None:
        sketch = compute_m0_sketch(
            epistemic_pressure=0.05,
            peak_coherence=0.99,
            self_prior_mismatch=0.05,
            targets=default_targets(),
            mode=M0TwinMode.ON,
        )
        self.assertFalse(sketch.gate_cleared)
        self.assertIsNone(sketch.selected)
        self.assertFalse(sketch.emit_m0)

    def test_reassert_antigravity_after_collapse(self) -> None:
        prev = compute_m0_sketch(
            epistemic_pressure=0.4,
            peak_coherence=0.8,
            self_prior_mismatch=0.3,
            targets=default_targets(),
            mode=M0TwinMode.OFF,
            tick=1,
        )
        self.assertTrue(prev.collapsed_to_m0)
        nxt = compute_m0_sketch(
            epistemic_pressure=0.55,
            peak_coherence=0.6,
            self_prior_mismatch=0.55,
            targets=default_targets(),
            mode=M0TwinMode.ON,
            tick=2,
            previous=prev,
        )
        self.assertGreaterEqual(nxt.distance_to_typical, 0.55)

    def test_summarize_batch_falsifier_shape(self) -> None:
        off = [
            compute_m0_sketch(
                epistemic_pressure=0.8,
                peak_coherence=0.5,
                self_prior_mismatch=0.7,
                targets=default_targets(),
                mode=M0TwinMode.OFF,
            )
            for _ in range(5)
        ]
        summary = summarize_mode_batch(off)
        self.assertEqual(summary["n"], 5)
        self.assertEqual(summary["emit_m0_rate"], 0.0)
        self.assertEqual(summary["collapse_to_m0_rate"], 1.0)
        self.assertEqual(summary["differs_from_m0_rate"], 0.0)


class AmatM0EmergenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.simulator = EndogenousEmergenceSimulator()
        self.config = EmergenceConfig(duration_seconds=6.0)

    def test_legacy_path_unchanged_without_m0_mode(self) -> None:
        run = self.simulator.run(self.config, seed=7)
        self.assertIsNotNone(run.intent)
        self.assertIsNone(run.m0_sketch)
        assert run.intent is not None
        self.assertEqual(run.intent.target_id, "wm:causal_gap")

    def test_off_mode_forces_median_m0_intent(self) -> None:
        run = self.simulator.run(
            self.config,
            seed=7,
            m0_twin_mode=M0TwinMode.OFF,
        )
        self.assertIsNotNone(run.intent)
        self.assertIsNotNone(run.m0_sketch)
        assert run.intent is not None
        assert run.m0_sketch is not None
        self.assertEqual(run.intent.target_id, "collaboration:latent_question")
        self.assertEqual(run.intent.kind, IntentKind.ASK)
        self.assertTrue(run.m0_sketch.collapsed_to_m0)
        self.assertFalse(run.m0_sketch.emit_m0)

    def test_on_mode_emits_off_m0_or_abstains(self) -> None:
        run = self.simulator.run(
            self.config,
            seed=7,
            m0_twin_mode=M0TwinMode.ON,
        )
        self.assertIsNotNone(run.m0_sketch)
        assert run.m0_sketch is not None
        self.assertFalse(run.m0_sketch.emit_m0)
        if run.intent is not None:
            self.assertNotEqual(run.intent.target_id, run.m0_sketch.m0.target_id)
            self.assertIn("m0_twin_anti_median", run.intent.causal_factors)

    def test_audit_only_keeps_default_target(self) -> None:
        run = self.simulator.run(
            self.config,
            seed=7,
            m0_twin_mode=M0TwinMode.AUDIT_ONLY,
        )
        self.assertIsNotNone(run.intent)
        self.assertIsNotNone(run.m0_sketch)
        assert run.intent is not None
        self.assertEqual(run.intent.target_id, "wm:causal_gap")

    def test_falsifier_batch_off_collapses_on_differs(self) -> None:
        """Pre-registered shape: OFF → collapse; ON → differs when intent forms."""
        off_sketches = []
        on_differs = 0
        on_intents = 0
        for seed in range(20):
            off = self.simulator.run(
                self.config, seed=seed, m0_twin_mode=M0TwinMode.OFF
            )
            self.assertIsNotNone(off.m0_sketch)
            assert off.m0_sketch is not None
            off_sketches.append(off.m0_sketch)
            on = self.simulator.run(
                self.config, seed=seed, m0_twin_mode=M0TwinMode.ON
            )
            if on.intent is not None:
                on_intents += 1
                assert on.m0_sketch is not None
                if on.intent.target_id != on.m0_sketch.m0.target_id:
                    on_differs += 1
        off_summary = summarize_mode_batch(off_sketches)
        self.assertEqual(off_summary["emit_m0_rate"], 0.0)
        self.assertGreaterEqual(off_summary["collapse_to_m0_rate"], 0.9)
        self.assertEqual(off_summary["differs_from_m0_rate"], 0.0)
        if on_intents > 0:
            self.assertEqual(on_differs, on_intents)


if __name__ == "__main__":
    unittest.main()
