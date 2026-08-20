from __future__ import annotations

import unittest

from eia.goal_genesis import catalog_negative_control, propose_non_catalog_goal


class GoalGenesisTests(unittest.TestCase):
    def test_non_catalog_requires_parents(self) -> None:
        with self.assertRaises(ValueError):
            propose_non_catalog_goal(
                seed_label="x",
                parent_ids=(),
                goal_separation=0.8,
            )

    def test_non_catalog_novelty_above_catalog_cap(self) -> None:
        rec = propose_non_catalog_goal(
            seed_label="causal_gap",
            parent_ids=("woe:wm:1", "woe:tension:2"),
            goal_separation=0.9,
        )
        self.assertFalse(rec.catalog_target)
        self.assertFalse(rec.claim_allowed)
        self.assertGreaterEqual(rec.novelty_proxy, 0.75)
        self.assertFalse(rec.as_dict()["agi_star_claim"])

    def test_catalog_control_capped(self) -> None:
        rec = catalog_negative_control(
            target_id="wm:causal_gap",
            parent_ids=("woe:wm:1",),
        )
        self.assertTrue(rec.catalog_target)
        self.assertLess(rec.novelty_proxy, 0.75)


if __name__ == "__main__":
    unittest.main()
