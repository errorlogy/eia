from __future__ import annotations

import unittest

from eia.goal_genesis import CATALOG_GOAL_IDS, compose_from_world_state
from eia.model_roles import (
    GoalGenesisState,
    ModelRoleAdapter,
    ModelRoleConfig,
    default_catalog_snapshot,
    maybe_model_role_adapter,
)


def _sample_state() -> GoalGenesisState:
    return GoalGenesisState(
        seed=11,
        catalog_snapshot=tuple(CATALOG_GOAL_IDS),
        epistemic_pressure=0.72,
        goal_separation=0.4,
        top_target_id="wm:causal_gap",
        top_target_label="causal gap",
        self_prior_mismatch=0.55,
        prospective_tension=0.48,
        peak_coherence=0.8,
        prompts_applied=0,
    )


class ModelRoleAdapterTests(unittest.TestCase):
    def test_tier0_matches_compose_from_world_state(self) -> None:
        state = _sample_state()
        cfg = ModelRoleConfig(enabled=True, tier=0, att_evidence_llm_allowed=False)
        adapter = ModelRoleAdapter(cfg)
        expected = compose_from_world_state(**state.to_compose_kwargs())
        got = adapter.genesis_record(state)
        self.assertEqual(got.goal_id, expected.goal_id)
        self.assertEqual(got.label, expected.label)
        self.assertEqual(got.catalog_target, expected.catalog_target)

    def test_tier0_forbids_llm_att_evidence(self) -> None:
        with self.assertRaises(ValueError):
            ModelRoleAdapter(
                ModelRoleConfig(enabled=True, tier=0, att_evidence_llm_allowed=True)
            )

    def test_disabled_config_returns_no_adapter(self) -> None:
        self.assertIsNone(maybe_model_role_adapter())

    def test_default_catalog_snapshot_covers_catalog(self) -> None:
        snap = default_catalog_snapshot()
        self.assertTrue(CATALOG_GOAL_IDS.issubset(set(snap)))


if __name__ == "__main__":
    unittest.main()
