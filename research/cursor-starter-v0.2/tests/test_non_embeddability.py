from __future__ import annotations

import unittest

from eia.non_embeddability import (
    NonEmbeddabilityProbe,
    agi_star_conjunction_allowed,
    evaluate_stub,
)


class NonEmbeddabilityStubTests(unittest.TestCase):
    def test_projection_stub_never_allows_claim(self) -> None:
        probe = NonEmbeddabilityProbe(
            proxy="projection_loss",
            encoding_budget_tokens=256,
        )
        verdict = evaluate_stub(probe, projection_loss=0.9)
        self.assertTrue(verdict.substantial_loss_suspected)
        self.assertFalse(verdict.claim_allowed)

    def test_missing_inputs_abstain(self) -> None:
        probe = NonEmbeddabilityProbe(
            proxy="human_carrier_sufficiency",
            encoding_budget_tokens=128,
        )
        verdict = evaluate_stub(probe)
        self.assertIsNone(verdict.score)
        self.assertFalse(verdict.claim_allowed)

    def test_agi_star_requires_both_conjuncts(self) -> None:
        self.assertFalse(
            agi_star_conjunction_allowed(
                e_endo_supported=True,
                c_non_emb_supported=False,
            )
        )
        self.assertFalse(
            agi_star_conjunction_allowed(
                e_endo_supported=False,
                c_non_emb_supported=True,
            )
        )
        self.assertTrue(
            agi_star_conjunction_allowed(
                e_endo_supported=True,
                c_non_emb_supported=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
