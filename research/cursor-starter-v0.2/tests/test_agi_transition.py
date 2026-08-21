"""Unit tests for AGI* phase-transition stubs (non-claiming)."""

from __future__ import annotations

import unittest

from eia.agi_transition import (
    default_order_parameter_specs,
    snapshot_from_partial_e,
    snapshot_with_d_explore,
    snapshot_with_n_h_explore,
    snapshot_with_p_explore,
    snapshot_with_r_explore,
    tau_agi_claim_allowed,
)
from eia.non_embeddability import agi_star_conjunction_allowed


class TestAgiTransitionStubs(unittest.TestCase):
    def test_specs_have_tbd_thresholds(self) -> None:
        specs = default_order_parameter_specs()
        self.assertEqual(len(specs), 5)
        self.assertTrue(all(s.threshold is None for s in specs))
        ids = {s.param_id for s in specs}
        self.assertEqual(ids, {"E", "N_H", "P", "R", "D"})

    def test_tau_requires_preregistration(self) -> None:
        self.assertFalse(
            tau_agi_claim_allowed(
                e_above=True,
                n_h_above=True,
                p_above=True,
                r_above=True,
                d_above=True,
                sustained=True,
                thresholds_preregistered=False,
            )
        )

    def test_snapshot_never_claims_agi_star(self) -> None:
        snap = snapshot_from_partial_e(e_endo_partial=True)
        self.assertTrue(snap.e_endo_partial)
        self.assertFalse(snap.agi_star_claim)
        self.assertIsNone(snap.n_h_score)

    def test_p_explore_snapshot_never_claims(self) -> None:
        snap = snapshot_with_p_explore(e_endo_partial=True, p_explore_proxy=1.0)
        self.assertEqual(snap.p_score, 1.0)
        self.assertFalse(snap.agi_star_claim)

    def test_r_explore_snapshot_never_claims(self) -> None:
        snap = snapshot_with_r_explore(
            e_endo_partial=True, p_explore_proxy=1.0, r_explore_proxy=1.0
        )
        self.assertEqual(snap.r_score, 1.0)
        self.assertFalse(snap.agi_star_claim)
        self.assertIn("not Kuramoto", snap.rationale)

    def test_n_h_explore_snapshot_never_claims(self) -> None:
        snap = snapshot_with_n_h_explore(
            e_endo_partial=True,
            p_explore_proxy=1.0,
            r_explore_proxy=1.0,
            n_h_explore_proxy=1.0,
        )
        self.assertEqual(snap.n_h_score, 1.0)
        self.assertFalse(snap.agi_star_claim)
        self.assertIn("not strong N_H", snap.rationale)
        self.assertIn("opacity", snap.rationale)

    def test_d_explore_snapshot_never_claims(self) -> None:
        snap = snapshot_with_d_explore(
            e_endo_partial=True,
            p_explore_proxy=1.0,
            r_explore_proxy=1.0,
            n_h_explore_proxy=1.0,
            d_explore_proxy=1.0,
        )
        self.assertEqual(snap.d_score, 1.0)
        self.assertFalse(snap.agi_star_claim)
        self.assertIn("not C5", snap.rationale)
        self.assertIn("cross-domain", snap.rationale)

    def test_conjunction_still_requires_both(self) -> None:
        self.assertFalse(
            agi_star_conjunction_allowed(e_endo_supported=True, c_non_emb_supported=False)
        )


if __name__ == "__main__":
    unittest.main()
