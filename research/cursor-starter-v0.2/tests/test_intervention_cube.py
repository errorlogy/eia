"""Tests for sci-flow intervention cube registry."""

from __future__ import annotations

import unittest

from eia.intervention_cube import (
    eoi_k_interventions,
    get_intervention,
    list_all,
    list_by_axis,
)


class InterventionCubeTests(unittest.TestCase):
    def test_get_cf4_reset(self) -> None:
        item = get_intervention("do_z_zero_epistemic_gap")
        self.assertEqual(item.axis, "D1")
        self.assertEqual(item.kind, "do_z")
        self.assertEqual(item.cf4_condition, "zero_epistemic_gap")
        self.assertIn("F-EXT", item.falsifiers)

    def test_list_by_axis_d1(self) -> None:
        d1 = list_by_axis("D1")
        self.assertGreaterEqual(len(d1), 5)
        self.assertTrue(all(i.axis == "D1" for i in d1))

    def test_eoi_k_interventions(self) -> None:
        items = eoi_k_interventions()
        self.assertEqual(len(items), 3)
        ks = {i.twin_remove_last_n for i in items}
        self.assertEqual(ks, {1, 5, 20})

    def test_unknown_raises(self) -> None:
        with self.assertRaises(KeyError):
            get_intervention("do_z_nonexistent")

    def test_registry_non_empty(self) -> None:
        self.assertGreater(len(list_all()), 10)


if __name__ == "__main__":
    unittest.main()
