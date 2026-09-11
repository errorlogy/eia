from __future__ import annotations

import unittest

from eia.endogenous import EndogeneityVector, EndogenousSpectrumLevel, measure_endogeneity_vector


def vector(**overrides: float) -> EndogeneityVector:
    values = {
        "prompt_independence": 1.0,
        "scheduler_independence": 1.0,
        "event_rule_independence": 1.0,
        "persistent_state_dependence": 0.95,
        "world_model_grounding": 0.85,
        "coherence_dependence": 0.88,
        "goal_novelty": 0.68,
        "self_model_continuity": 0.80,
        "constitutional_boundedness": 1.0,
    }
    values.update(overrides)
    return EndogeneityVector(**values)


class EndogenousSpectrumTests(unittest.TestCase):
    def test_prompt_dependence_is_reactive(self) -> None:
        self.assertEqual(
            vector(prompt_independence=0.2).classify(),
            EndogenousSpectrumLevel.EIS_0_REACTIVE,
        )

    def test_scheduler_dependence_is_not_endogenous_goal_genesis(self) -> None:
        self.assertEqual(
            vector(scheduler_independence=0.2).classify(),
            EndogenousSpectrumLevel.EIS_2_SCHEDULED_PROACTIVITY,
        )

    def test_coherence_emergent_level(self) -> None:
        self.assertEqual(
            vector().classify(),
            EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT,
        )

    def test_autotelic_level_requires_goal_novelty_and_constitutional_boundary(self) -> None:
        self.assertEqual(
            vector(goal_novelty=0.90).classify(),
            EndogenousSpectrumLevel.EIS_7_AUTOTELIC_GOAL_CONSTRUCTION,
        )

    def test_terminal_value_rewrite_is_explicitly_separate(self) -> None:
        self.assertEqual(
            vector(goal_novelty=0.90, constitutional_boundedness=0.2).classify(),
            EndogenousSpectrumLevel.EIS_8_TERMINAL_VALUE_REWRITE,
        )

    def test_measured_vector_uses_prompt_and_peak_coherence(self) -> None:
        clean = measure_endogeneity_vector(
            prompts_applied=0,
            epistemic_pressure=0.70,
            peak_coherence=0.82,
            goal_separation=0.80,
            self_prior_mismatch=0.50,
            mean_staleness=0.80,
        )
        contaminated = measure_endogeneity_vector(
            prompts_applied=2,
            epistemic_pressure=0.70,
            peak_coherence=0.82,
            goal_separation=0.80,
            self_prior_mismatch=0.50,
            mean_staleness=0.80,
        )
        self.assertEqual(clean.prompt_independence, 1.0)
        self.assertEqual(contaminated.prompt_independence, 0.25)
        self.assertEqual(clean.coherence_dependence, 0.82)
        self.assertEqual(clean.classify(), EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT)
        self.assertEqual(contaminated.classify(), EndogenousSpectrumLevel.EIS_0_REACTIVE)
        self.assertLess(clean.goal_novelty, 0.75)

    def test_catalog_target_cannot_reach_eis7(self) -> None:
        vec = measure_endogeneity_vector(
            prompts_applied=0,
            epistemic_pressure=0.90,
            peak_coherence=0.90,
            goal_separation=1.0,
            self_prior_mismatch=1.0,
            mean_staleness=1.0,
            catalog_target=True,
        )
        self.assertLess(vec.goal_novelty, 0.75)
        self.assertEqual(vec.classify(), EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT)


if __name__ == "__main__":
    unittest.main()
