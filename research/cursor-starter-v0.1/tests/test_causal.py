from __future__ import annotations

import unittest
from pathlib import Path

from eia.causal import EndogeneityEstimator, root_cause_purity
from eia.models import InitiativeProposal
from eia.simulator import SimulationRunner, load_scenario
from eia.topology import CognitiveTopology


ROOT = Path(__file__).resolve().parents[1]


class CausalTests(unittest.TestCase):
    def test_counterfactual_eoi_is_one_for_ambient_cause(self) -> None:
        scenario = load_scenario(ROOT / "examples" / "autonomous_question.json")
        simulation_runner = SimulationRunner()
        factual = simulation_runner.run(scenario)
        observed = next(tick.selected for tick in factual.results if tick.selected)

        def twin(remove_user_events: bool, seed: int) -> InitiativeProposal | None:
            del seed
            result = simulation_runner.run(scenario, remove_user_events=remove_user_events)
            return next((tick.selected for tick in result.results if tick.selected), None)

        estimate = EndogeneityEstimator().estimate(observed, twin, trials=16)
        self.assertEqual(estimate.eoi, 1.0)
        self.assertEqual(estimate.retained, 16)

    def test_root_cause_purity_uses_trace_types(self) -> None:
        scenario = load_scenario(ROOT / "examples" / "autonomous_question.json")
        result = SimulationRunner().run(scenario)
        selected_tick = next(tick for tick in result.results if tick.selected)
        ancestors = result.runtime.ledger.ancestors(selected_tick.trace_id)
        purity = root_cause_purity(ancestors)
        self.assertGreater(purity, 0.0)
        self.assertLessEqual(purity, 1.0)

    def test_topology_separates_ambient_signal_from_user_request(self) -> None:
        scenario = load_scenario(ROOT / "examples" / "autonomous_question.json")
        result = SimulationRunner().run(scenario)
        selected_tick = next(tick for tick in result.results if tick.selected)
        metrics = CognitiveTopology(result.runtime.ledger).measure(selected_tick.trace_id)
        self.assertEqual(metrics.source_mass.user_request, 0.0)
        self.assertEqual(metrics.source_mass.ambient, 1.0)
        self.assertEqual(metrics.source_mass.request_independence, 1.0)
        self.assertGreaterEqual(metrics.depth, 3)


if __name__ == "__main__":
    unittest.main()
