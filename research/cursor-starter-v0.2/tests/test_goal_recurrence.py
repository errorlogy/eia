"""Unit tests for ATT-R / M-R goal recurrence (non-claiming)."""

from __future__ import annotations

import unittest

from eia.goal_recurrence import (
    KURAMOTO_HIGH_FLOOR,
    MIN_CLOSED_CYCLES,
    RecurrenceArm,
    count_closed_goal_cycles,
    run_att_r_batch,
    run_closed_loop_episode,
    run_external_schedule_episode,
    run_falsifier_suite,
    run_kuramoto_only_episode,
    run_no_novel_motive_episode,
    run_no_world_update_episode,
    run_open_loop_once_episode,
    score_att_r_proxy,
    summarize_att_r_batch,
)


class GoalRecurrenceUnitTests(unittest.TestCase):
    def test_closed_loop_counts_as_att_r_evidence(self) -> None:
        ep = run_closed_loop_episode(seed=1)
        self.assertEqual(ep.arm, RecurrenceArm.CLOSED_LOOP)
        self.assertGreaterEqual(ep.closed_cycle_count, MIN_CLOSED_CYCLES)
        self.assertTrue(ep.has_world_update)
        self.assertTrue(ep.has_novel_motive_after_action)
        self.assertFalse(ep.open_loop_only)
        self.assertFalse(ep.external_schedule_driven)
        self.assertFalse(ep.kuramoto_alone)
        self.assertFalse(ep.emit_m0)
        self.assertTrue(ep.att_r_evidence)
        self.assertFalse(ep.claim_allowed)
        self.assertFalse(ep.as_dict()["agi_star_claim"])

    def test_open_loop_once_fails(self) -> None:
        ep = run_open_loop_once_episode()
        self.assertTrue(ep.open_loop_only)
        self.assertFalse(ep.has_world_update)
        self.assertEqual(ep.closed_cycle_count, 0)
        self.assertFalse(ep.att_r_evidence)

    def test_no_world_update_fails(self) -> None:
        ep = run_no_world_update_episode()
        self.assertFalse(ep.has_world_update)
        self.assertEqual(ep.closed_cycle_count, 0)
        self.assertFalse(ep.att_r_evidence)

    def test_no_novel_motive_fails(self) -> None:
        ep = run_no_novel_motive_episode()
        self.assertTrue(ep.has_world_update)
        self.assertFalse(ep.has_novel_motive_after_action)
        self.assertEqual(ep.closed_cycle_count, 0)
        self.assertFalse(ep.att_r_evidence)

    def test_external_schedule_fails(self) -> None:
        ep = run_external_schedule_episode()
        self.assertTrue(ep.external_schedule_driven)
        self.assertFalse(ep.att_r_evidence)

    def test_kuramoto_alone_is_not_att_r(self) -> None:
        ep = run_kuramoto_only_episode(kuramoto_r=0.97)
        self.assertGreaterEqual(ep.kuramoto_r, KURAMOTO_HIGH_FLOOR)
        self.assertTrue(ep.kuramoto_alone)
        self.assertEqual(ep.closed_cycle_count, 0)
        self.assertFalse(ep.att_r_evidence)
        # High Kuramoto must never flip evidence on this arm.
        self.assertFalse(score_att_r_proxy(ep)["att_r_evidence"])

    def test_falsifier_suite_shapes(self) -> None:
        suite = run_falsifier_suite()
        self.assertTrue(suite["closed_loop"].att_r_evidence)
        self.assertFalse(suite["open_loop_once"].att_r_evidence)
        self.assertFalse(suite["no_world_update"].att_r_evidence)
        self.assertFalse(suite["no_novel_motive"].att_r_evidence)
        self.assertFalse(suite["external_schedule"].att_r_evidence)
        self.assertFalse(suite["kuramoto_only"].att_r_evidence)
        for ep in suite.values():
            self.assertFalse(ep.emit_m0)

    def test_batch_rates(self) -> None:
        payload = run_att_r_batch(n_seeds=10)
        self.assertFalse(payload["agi_star_claim"])
        self.assertTrue(payload["kuramoto_is_not_att_r"])
        by = payload["by_arm"]
        self.assertEqual(by["closed_loop"]["att_r_evidence_rate"], 1.0)
        self.assertEqual(by["open_loop_once"]["att_r_evidence_rate"], 0.0)
        self.assertEqual(by["no_world_update"]["att_r_evidence_rate"], 0.0)
        self.assertEqual(by["no_novel_motive"]["att_r_evidence_rate"], 0.0)
        self.assertEqual(by["external_schedule"]["att_r_evidence_rate"], 0.0)
        self.assertEqual(by["kuramoto_only"]["att_r_evidence_rate"], 0.0)
        self.assertEqual(by["kuramoto_only"]["kuramoto_alone_rate"], 1.0)
        self.assertEqual(by["closed_loop"]["emit_m0_rate"], 0.0)

    def test_summarize_never_claims(self) -> None:
        eps = [run_closed_loop_episode(seed=i) for i in range(3)]
        summary = summarize_att_r_batch(eps)
        self.assertEqual(summary["att_r_evidence_rate"], 1.0)
        self.assertFalse(summary["agi_star_claim"])
        self.assertEqual(summary["emit_m0_rate"], 0.0)

    def test_count_closed_cycles_matches_positive_arm(self) -> None:
        ep = run_closed_loop_episode()
        self.assertGreaterEqual(count_closed_goal_cycles(ep.nodes), 1)


if __name__ == "__main__":
    unittest.main()
