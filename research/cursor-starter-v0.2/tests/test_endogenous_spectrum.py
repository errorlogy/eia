from __future__ import annotations

import unittest

from eia.endogenous import EndogeneityVector, EndogenousSpectrumLevel


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


if __name__ == "__main__":
    unittest.main()
