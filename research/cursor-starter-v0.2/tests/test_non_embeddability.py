"""Unit tests for ATT-N / M-N non-embeddability (non-claiming)."""

from __future__ import annotations

import unittest

from eia.non_embeddability import (
    EXPLORE_DELTA_P_FLOOR,
    EXPLORE_DH_LOSS_FLOOR,
    EXPLORE_ENCODING_BUDGET_B,
    EncodingBudget,
    NonEmbedArm,
    NonEmbeddabilityProbe,
    agi_star_conjunction_allowed,
    evaluate_stub,
    run_att_n_batch,
    run_causal_loss_under_b_episode,
    run_faithful_under_b_episode,
    run_falsifier_suite,
    run_length_only_hard_episode,
    run_no_causal_relevance_episode,
    run_opacity_only_episode,
    run_unbounded_phi_episode,
    score_att_n_proxy,
    summarize_att_n_batch,
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


class AttNBudgetAndProxyTests(unittest.TestCase):
    def test_explore_budget_b_is_concrete(self) -> None:
        b = EXPLORE_ENCODING_BUDGET_B
        self.assertIsInstance(b, EncodingBudget)
        self.assertEqual(b.max_tokens, 256)
        self.assertEqual(b.max_diagram_nodes, 32)
        self.assertEqual(b.max_feature_dim, 64)
        self.assertEqual(b.max_phi_ops, 100)
        self.assertEqual(b.max_attention_slots, 8)
        self.assertEqual(b.wall_clock_seconds, 30.0)

    def test_causal_loss_under_b_counts_as_att_n_evidence(self) -> None:
        ep = run_causal_loss_under_b_episode(seed=1)
        self.assertEqual(ep.arm, NonEmbedArm.CAUSAL_LOSS_UNDER_B)
        self.assertTrue(ep.phi_within_budget)
        self.assertGreater(ep.delta_p_action, EXPLORE_DELTA_P_FLOOR)
        self.assertGreaterEqual(ep.d_h_proxy, EXPLORE_DH_LOSS_FLOOR)
        self.assertFalse(ep.opacity_only)
        self.assertFalse(ep.emit_m0)
        self.assertTrue(ep.att_n_evidence)
        self.assertFalse(ep.claim_allowed)
        self.assertFalse(ep.as_dict()["agi_star_claim"])
        self.assertFalse(ep.as_dict()["n_h_claim"])
        self.assertGreater(ep.compression_asymmetry, 1.0)

    def test_opacity_only_fails(self) -> None:
        ep = run_opacity_only_episode()
        self.assertTrue(ep.opacity_only)
        self.assertLessEqual(ep.delta_p_action, EXPLORE_DELTA_P_FLOOR)
        self.assertFalse(ep.att_n_evidence)

    def test_no_causal_relevance_fails(self) -> None:
        ep = run_no_causal_relevance_episode()
        self.assertFalse(ep.causal_relevant)
        self.assertFalse(ep.att_n_evidence)

    def test_unbounded_phi_fails(self) -> None:
        ep = run_unbounded_phi_episode()
        self.assertFalse(ep.phi_within_budget)
        self.assertLess(ep.d_h_proxy, EXPLORE_DH_LOSS_FLOOR)
        self.assertFalse(ep.att_n_evidence)

    def test_length_only_hard_fails(self) -> None:
        ep = run_length_only_hard_episode()
        self.assertLess(ep.d_h_proxy, EXPLORE_DH_LOSS_FLOOR)
        self.assertFalse(ep.att_n_evidence)

    def test_faithful_under_b_fails(self) -> None:
        ep = run_faithful_under_b_episode()
        self.assertTrue(ep.phi_within_budget)
        self.assertTrue(ep.causal_relevant)
        self.assertLess(ep.d_h_proxy, EXPLORE_DH_LOSS_FLOOR)
        self.assertFalse(ep.att_n_evidence)

    def test_falsifier_suite_shapes(self) -> None:
        suite = run_falsifier_suite()
        self.assertTrue(suite["causal_loss_under_b"].att_n_evidence)
        self.assertFalse(suite["opacity_only"].att_n_evidence)
        self.assertFalse(suite["no_causal_relevance"].att_n_evidence)
        self.assertFalse(suite["unbounded_phi"].att_n_evidence)
        self.assertFalse(suite["length_only_hard"].att_n_evidence)
        self.assertFalse(suite["faithful_under_b"].att_n_evidence)
        for ep in suite.values():
            self.assertFalse(ep.emit_m0)
            self.assertFalse(ep.claim_allowed)

    def test_batch_rates(self) -> None:
        payload = run_att_n_batch(n_seeds=10)
        self.assertFalse(payload["agi_star_claim"])
        self.assertFalse(payload["n_h_claim"])
        self.assertTrue(payload["opacity_is_not_n_h"])
        self.assertEqual(payload["encoding_budget_B"]["max_tokens"], 256)
        by = payload["by_arm"]
        self.assertEqual(by["causal_loss_under_b"]["att_n_evidence_rate"], 1.0)
        self.assertEqual(by["opacity_only"]["att_n_evidence_rate"], 0.0)
        self.assertEqual(by["no_causal_relevance"]["att_n_evidence_rate"], 0.0)
        self.assertEqual(by["unbounded_phi"]["att_n_evidence_rate"], 0.0)
        self.assertEqual(by["length_only_hard"]["att_n_evidence_rate"], 0.0)
        self.assertEqual(by["faithful_under_b"]["att_n_evidence_rate"], 0.0)
        self.assertEqual(by["causal_loss_under_b"]["emit_m0_rate"], 0.0)

    def test_summarize_never_claims(self) -> None:
        eps = [run_causal_loss_under_b_episode(seed=i) for i in range(3)]
        summary = summarize_att_n_batch(eps)
        self.assertEqual(summary["att_n_evidence_rate"], 1.0)
        self.assertFalse(summary["agi_star_claim"])
        self.assertFalse(summary["n_h_claim"])
        self.assertEqual(summary["emit_m0_rate"], 0.0)

    def test_scorecard_never_claims(self) -> None:
        card = score_att_n_proxy(run_causal_loss_under_b_episode())
        self.assertTrue(card["att_n_evidence"])
        self.assertFalse(card["n_h_claim"])
        self.assertFalse(card["agi_star_claim"])


if __name__ == "__main__":
    unittest.main()
