from __future__ import annotations

import unittest

from eia.coherence import CoherenceConfig, OscillatoryCoherenceField
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator
from eia.endogenous import EndogenousSpectrumLevel


class EmergenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.simulator = EndogenousEmergenceSimulator()
        self.config = EmergenceConfig(duration_seconds=6.0)

    def test_woe_forms_internal_intent_without_prompt_schedule_or_rule_event(self) -> None:
        run = self.simulator.run(self.config, seed=7)
        self.assertIsNotNone(run.intent)
        self.assertTrue(run.no_prompt_events)
        self.assertTrue(run.no_scheduler_events)
        self.assertTrue(run.no_rule_trigger_events)
        assert run.intent is not None
        self.assertEqual(
            run.intent.spectrum_level,
            EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT,
        )
        self.assertEqual(run.intent.boundary, "proposal_only")

    def test_zero_world_model_tension_is_negative_control(self) -> None:
        run = self.simulator.run(self.config, seed=7, world_model_enabled=False)
        self.assertIsNone(run.intent)
        self.assertEqual(run.samples[-1].integrated_hazard, 0.0)

    def test_phase_scrambling_blocks_reference_emergence(self) -> None:
        run = self.simulator.run(self.config, seed=7, scramble_phases=True)
        self.assertIsNone(run.intent)

    def test_42_hz_is_not_a_privileged_causal_constant(self) -> None:
        results = [
            self.simulator.run(
                EmergenceConfig(nominal_frequency_hz=frequency, duration_seconds=6.0),
                seed=7,
            )
            for frequency in (20.0, 30.0, 42.0, 70.0)
        ]
        self.assertTrue(all(result.intent is not None for result in results))
        targets = {result.intent.target_id for result in results if result.intent is not None}
        times = {result.intent.emerged_at_seconds for result in results if result.intent is not None}
        self.assertEqual(targets, {"wm:causal_gap"})
        self.assertEqual(len(times), 1)

    def test_coherence_config_rejects_nonpositive_frequency(self) -> None:
        with self.assertRaises(ValueError):
            CoherenceConfig(nominal_frequency_hz=0.0)

    def test_coherence_field_rejects_bad_activation_shape(self) -> None:
        field = OscillatoryCoherenceField(seed=3)
        with self.assertRaises(ValueError):
            field.step(0.001, integration_pressure=0.5, module_activations=(0.5,))


if __name__ == "__main__":
    unittest.main()
