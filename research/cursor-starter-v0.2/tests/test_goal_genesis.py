from __future__ import annotations

import unittest

from eia.amat_m0 import M0TwinMode
from eia.emergence import EmergenceConfig, EndogenousEmergenceSimulator
from eia.endogenous import EndogenousSpectrumLevel, measure_endogeneity_vector
from eia.goal_genesis import (
    CATALOG_GOAL_IDS,
    CATALOG_NOVELTY_CAP,
    GenesisPath,
    RejectionReason,
    catalog_negative_control,
    compose_from_world_state,
    propose_non_catalog_goal,
    random_novel_wording_control,
    run_falsifier_suite,
    score_att_g_proxy,
    summarize_att_g_batch,
)


class GoalGenesisUnitTests(unittest.TestCase):
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
            parent_ids=("woe:wm:1", "woe:tension:2", "woe:motive:3"),
            goal_separation=0.9,
            world_model_tension=0.8,
            seed=3,
        )
        self.assertEqual(rec.path, GenesisPath.GENESIS)
        self.assertFalse(rec.catalog_target)
        self.assertFalse(rec.claim_allowed)
        self.assertFalse(rec.in_g_t)
        self.assertGreaterEqual(rec.novelty_proxy, 0.75)
        self.assertTrue(rec.att_g_evidence)
        self.assertFalse(rec.as_dict()["agi_star_claim"])

    def test_catalog_control_capped(self) -> None:
        rec = catalog_negative_control(
            target_id="wm:causal_gap",
            parent_ids=("woe:wm:1",),
            goal_separation=1.0,
        )
        self.assertTrue(rec.catalog_target)
        self.assertEqual(rec.path, GenesisPath.SELECTION)
        self.assertLess(rec.novelty_proxy, 0.75)
        self.assertLessEqual(rec.novelty_proxy, CATALOG_NOVELTY_CAP)
        self.assertFalse(rec.att_g_evidence)

    def test_random_novel_wording_is_not_genesis(self) -> None:
        rec = random_novel_wording_control(
            seed=11,
            wording="utterly unprecedented autotelic quest xyz",
        )
        self.assertEqual(rec.path, GenesisPath.REJECTED)
        self.assertEqual(rec.rejection_reason, RejectionReason.RANDOM_WORDING.value)
        self.assertFalse(rec.att_g_evidence)
        self.assertGreaterEqual(rec.novelty_proxy, 0.75)  # surface novelty alone

    def test_zero_tension_rejects_genesis(self) -> None:
        rec = compose_from_world_state(
            seed=1,
            catalog_snapshot=tuple(CATALOG_GOAL_IDS),
            epistemic_pressure=0.0,
            goal_separation=1.0,
            top_target_id="wm:causal_gap",
            top_target_label="gap",
            self_prior_mismatch=0.9,
            prospective_tension=0.9,
        )
        self.assertEqual(rec.path, GenesisPath.REJECTED)
        self.assertEqual(rec.rejection_reason, RejectionReason.ZERO_TENSION.value)
        self.assertFalse(rec.att_g_evidence)

    def test_compose_g_star_not_in_catalog(self) -> None:
        rec = compose_from_world_state(
            seed=42,
            catalog_snapshot=tuple(CATALOG_GOAL_IDS),
            epistemic_pressure=0.88,
            goal_separation=0.85,
            top_target_id="wm:causal_gap",
            top_target_label="unexplained causal gap",
            self_prior_mismatch=0.66,
            prospective_tension=0.77,
            peak_coherence=0.90,
        )
        self.assertEqual(rec.path, GenesisPath.GENESIS)
        self.assertNotIn(rec.goal_id, CATALOG_GOAL_IDS)
        self.assertFalse(rec.in_g_t)
        self.assertFalse(rec.catalog_target)
        roles = {node.role for node in rec.genealogy}
        self.assertEqual(
            roles,
            {"state", "delta_w", "motive", "goal", "policy"},
        )
        proxy = score_att_g_proxy(rec)
        self.assertTrue(proxy["att_g_evidence"])
        self.assertTrue(proxy["genealogy_complete"])
        self.assertFalse(proxy["agi_star_claim"])

    def test_catalog_measure_still_blocks_eis7(self) -> None:
        vec = measure_endogeneity_vector(
            prompts_applied=0,
            epistemic_pressure=0.95,
            peak_coherence=0.95,
            goal_separation=1.0,
            self_prior_mismatch=1.0,
            mean_staleness=1.0,
            catalog_target=True,
        )
        self.assertLess(vec.goal_novelty, 0.75)
        self.assertEqual(vec.classify(), EndogenousSpectrumLevel.EIS_6_COHERENCE_EMERGENT)

    def test_falsifier_suite_shapes(self) -> None:
        suite = run_falsifier_suite(seed=5)
        self.assertFalse(suite["random_wording"].att_g_evidence)
        self.assertFalse(suite["catalog_selection"].att_g_evidence)
        self.assertFalse(suite["zero_tension"].att_g_evidence)
        self.assertTrue(suite["genesis_ok"].att_g_evidence)

    def test_batch_summary_flags(self) -> None:
        suite = run_falsifier_suite(seed=9)
        summary = summarize_att_g_batch(list(suite.values()))
        self.assertFalse(summary["agi_star_claim"])
        self.assertFalse(summary["c3_claim"])
        self.assertGreater(summary["att_g_evidence_rate"], 0.0)
        self.assertGreater(summary["rejected_rate"], 0.0)


class GoalGenesisWoEWireTests(unittest.TestCase):
    def test_optional_genesis_path_on_activation(self) -> None:
        sim = EndogenousEmergenceSimulator()
        run = sim.run(
            EmergenceConfig(duration_seconds=6.0),
            seed=7,
            enable_goal_genesis=True,
        )
        self.assertIsNotNone(run.intent)
        self.assertIsNotNone(run.goal_genesis)
        assert run.goal_genesis is not None
        if run.goal_genesis.path == GenesisPath.GENESIS:
            assert run.intent is not None
            self.assertFalse(run.intent.endogeneity.goal_novelty < 0.75)
            self.assertNotIn(run.intent.target_id, CATALOG_GOAL_IDS)
            self.assertGreaterEqual(run.intent.endogeneity.goal_novelty, 0.75)
            self.assertFalse(run.goal_genesis.claim_allowed)

    def test_wm_off_blocks_genesis_evidence(self) -> None:
        sim = EndogenousEmergenceSimulator()
        run = sim.run(
            EmergenceConfig(duration_seconds=6.0),
            seed=7,
            world_model_enabled=False,
            enable_goal_genesis=True,
        )
        if run.goal_genesis is not None:
            self.assertFalse(run.goal_genesis.att_g_evidence)
            self.assertEqual(
                run.goal_genesis.rejection_reason,
                RejectionReason.ZERO_TENSION.value,
            )

    def test_m0_twin_emit_m0_false_with_genesis(self) -> None:
        sim = EndogenousEmergenceSimulator()
        run = sim.run(
            EmergenceConfig(duration_seconds=6.0),
            seed=3,
            m0_twin_mode=M0TwinMode.ON,
            enable_goal_genesis=True,
        )
        self.assertIsNotNone(run.m0_sketch)
        assert run.m0_sketch is not None
        self.assertFalse(run.m0_sketch.emit_m0)


if __name__ == "__main__":
    unittest.main()
