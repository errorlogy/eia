from __future__ import annotations

import unittest

from eia.cf5 import run_seed, run_suite, summarize
from eia.coherence import CoherenceConfig, permute_graph, sparse_typed_graph
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator


class CF5Tests(unittest.TestCase):
    def test_scramble_blocks_reference_seed(self) -> None:
        result = run_seed(7, "scramble")
        self.assertFalse(result.intent)

    def test_k0_does_not_block_reference_seed(self) -> None:
        """Coupling ablation is not a hard seed-7 blocker; C2 uses population rates."""
        result = run_seed(7, "k0")
        self.assertTrue(result.intent)

    def test_coupled_reference_seed_emits(self) -> None:
        result = run_seed(7, "coupled")
        self.assertTrue(result.intent)

    def test_sparse_graph_still_emits_reference_seed(self) -> None:
        result = run_seed(7, "sparse")
        self.assertTrue(result.intent)

    def test_permute_graph_is_not_identity(self) -> None:
        graph = sparse_typed_graph()
        permuted = permute_graph(graph, seed=19)
        self.assertNotEqual(graph, permuted)
        self.assertEqual(len(permuted), 6)

    def test_bad_graph_shape_rejected(self) -> None:
        with self.assertRaises(ValueError):
            CoherenceConfig(coupling_graph=((1.0, 0.0),))

    def test_mini_suite_scramble_below_coupled(self) -> None:
        results = run_suite(range(7, 11), conditions=("coupled", "scramble", "k0"))
        summary = summarize(results)
        coupled = summary["conditions"]["coupled"]["intent_rate"]
        scramble = summary["conditions"]["scramble"]["intent_rate"]
        self.assertGreaterEqual(coupled, 0.75)
        self.assertLess(scramble, coupled)

    def test_simulator_accepts_coherence_config(self) -> None:
        run = EndogenousEmergenceSimulator().run(
            EmergenceConfig(),
            seed=7,
            coherence_config=CoherenceConfig(delay_steps=0),
        )
        self.assertIsNotNone(run.intent)


if __name__ == "__main__":
    unittest.main()
