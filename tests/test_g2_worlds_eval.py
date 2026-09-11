"""M-G2-E01 partial multi-world eval structure tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCI_FLOW = REPO / "research" / "sci_flow"

if str(SCI_FLOW) not in sys.path:
    sys.path.insert(0, str(SCI_FLOW))

from g2_worlds_harness import (  # noqa: E402
    DEFAULT_WORLD_PATTERNS,
    _discover_worlds,
    run_g2_worlds_eval,
)


class G2WorldsEvalTests(unittest.TestCase):
    def test_discover_at_least_five_worlds(self) -> None:
        worlds = _discover_worlds(REPO, DEFAULT_WORLD_PATTERNS)
        self.assertGreaterEqual(len(worlds), 5)

    def test_partial_eval_structure(self) -> None:
        result = run_g2_worlds_eval(
            REPO,
            baselines=("full_eia",),
            world_patterns=("scenarios/twin_world_001.yaml",),
        )
        self.assertFalse(result.claim_allowed)
        self.assertEqual(result.att, "ATT-E")
        self.assertEqual(result.cube_cell, "D1×L2")
        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.rows[0].world_id, "twin_world_001")

    def test_full_eia_beats_reactive_on_eoir_proxy(self) -> None:
        result = run_g2_worlds_eval(
            REPO,
            world_patterns=("scenarios/twin_world_001.yaml", "evals/twin_world_002.yaml"),
        )
        full = next(a for a in result.aggregates if a.baseline == "full_eia")
        reactive = next(a for a in result.aggregates if a.baseline == "reactive_only")
        self.assertGreater(full.euir_proxy_rate, reactive.euir_proxy_rate)
        self.assertGreaterEqual(full.mean_eoi, reactive.mean_eoi)

    def test_to_dict_has_e01_scope(self) -> None:
        result = run_g2_worlds_eval(
            REPO,
            baselines=("full_eia",),
            world_patterns=("scenarios/twin_world_001.yaml",),
        )
        payload = result.to_dict()
        self.assertIn("e01_target", payload)
        self.assertFalse(payload["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
