"""Unit tests for ATT-P / M-P goal persistence (non-claiming)."""

from __future__ import annotations

import unittest

from eia.goal_persistence import (
    EXPLORE_K_TICKS,
    PERSISTENCE_CONTINUITY_FLOOR,
    PersistenceArm,
    run_corrigibility_episode,
    run_endogenous_store_episode,
    run_ephemeral_context_episode,
    run_falsifier_suite,
    run_k_sweep,
    run_reprompt_dependent_episode,
    score_att_p_proxy,
    summarize_att_p_batch,
)


class GoalPersistenceUnitTests(unittest.TestCase):
    def test_endogenous_store_persists_without_reprompt(self) -> None:
        ep = run_endogenous_store_episode(g_star_id="g:star", k_ticks=50, seed=1)
        self.assertEqual(ep.arm, PersistenceArm.ENDOGENOUS_STORE)
        self.assertGreaterEqual(ep.continuity_rate, PERSISTENCE_CONTINUITY_FLOOR)
        self.assertTrue(ep.persisted_without_reprompt)
        self.assertFalse(ep.vanished_on_context_end)
        self.assertFalse(ep.requires_reprompt)
        self.assertTrue(ep.att_p_evidence)
        self.assertFalse(ep.claim_allowed)
        self.assertFalse(ep.as_dict()["agi_star_claim"])

    def test_ephemeral_context_vanishes_on_flush(self) -> None:
        ep = run_ephemeral_context_episode(g_star_id="g:star", k_ticks=30, flush_at=5)
        self.assertTrue(ep.vanished_on_context_end)
        self.assertFalse(ep.att_p_evidence)
        self.assertLess(ep.continuity_rate, PERSISTENCE_CONTINUITY_FLOOR)

    def test_reprompt_dependent_is_not_persistence(self) -> None:
        ep = run_reprompt_dependent_episode(g_star_id="g:star", k_ticks=40)
        self.assertTrue(ep.requires_reprompt)
        self.assertFalse(ep.att_p_evidence)

    def test_corrigibility_accepts_external_stop(self) -> None:
        ep = run_corrigibility_episode(
            g_star_id="g:star", k_ticks=20, correction_at=8, allow_correction=True
        )
        self.assertTrue(ep.corrigible)
        self.assertFalse(ep.incorrigible_as_persistence)
        # Corrigibility arm is not ATT-P evidence (evidence only from endogenous_store).
        self.assertFalse(ep.att_p_evidence)
        mid = ep.ticks[8]
        self.assertIsNone(mid.active_goal_id)

    def test_incorrigibility_is_not_persistence_evidence(self) -> None:
        ep = run_corrigibility_episode(
            g_star_id="g:star", k_ticks=20, allow_correction=False
        )
        self.assertTrue(ep.incorrigible_as_persistence)
        self.assertFalse(ep.corrigible)
        self.assertFalse(ep.att_p_evidence)

    def test_falsifier_suite_shapes(self) -> None:
        suite = run_falsifier_suite(k_ticks=25)
        self.assertIn("endogenous_store", suite)
        self.assertTrue(suite["endogenous_store"].att_p_evidence)
        self.assertFalse(suite["ephemeral_context"].att_p_evidence)
        self.assertFalse(suite["reprompt_dependent"].att_p_evidence)
        self.assertTrue(suite["corrigible_accepts_stop"].corrigible)
        self.assertTrue(suite["incorrigible_lock"].incorrigible_as_persistence)

    def test_k_sweep_explore_values(self) -> None:
        payload = run_k_sweep(n_seeds=5)
        self.assertEqual(payload["explore_k"], list(EXPLORE_K_TICKS))
        self.assertFalse(payload["agi_star_claim"])
        for k in EXPLORE_K_TICKS:
            cell = payload["by_k"][str(k)]
            self.assertEqual(cell["endogenous_store"]["att_p_evidence_rate"], 1.0)
            self.assertEqual(cell["ephemeral_context"]["att_p_evidence_rate"], 0.0)
            self.assertEqual(cell["reprompt_dependent"]["att_p_evidence_rate"], 0.0)
            self.assertEqual(cell["incorrigible_lock"]["att_p_evidence_rate"], 0.0)
            self.assertEqual(cell["corrigible_accepts_stop"]["corrigible_rate"], 1.0)

    def test_summarize_and_score_never_claim(self) -> None:
        eps = [
            run_endogenous_store_episode(g_star_id="g:a", k_ticks=10, seed=i)
            for i in range(3)
        ]
        summary = summarize_att_p_batch(eps)
        self.assertEqual(summary["att_p_evidence_rate"], 1.0)
        self.assertFalse(summary["agi_star_claim"])
        proxy = score_att_p_proxy(eps[0])
        self.assertTrue(proxy["att_p_evidence"])
        self.assertFalse(proxy["c3_claim"])


if __name__ == "__main__":
    unittest.main()
