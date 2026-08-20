"""Unit tests for AGI* phase-transition stubs (non-claiming)."""

from __future__ import annotations

import unittest

from eia.agi_transition import (
    default_order_parameter_specs,
    snapshot_from_partial_e,
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

    def test_conjunction_still_requires_both(self) -> None:
        self.assertFalse(
            agi_star_conjunction_allowed(e_endo_supported=True, c_non_emb_supported=False)
        )


if __name__ == "__main__":
    unittest.main()
