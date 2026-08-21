"""Unit tests for ATT-D / M-D2 cross-domain generality (non-claiming)."""

from __future__ import annotations

import unittest

from eia.cross_domain import (
    EXPLORE_MIN_DOMAINS,
    PRE_REGISTERED_DOMAINS,
    CrossDomainArm,
    CrossDomainEpisode,
    DomainESummary,
    DomainId,
    domain_target_ids,
    domains_substantially_disjoint,
    run_domain_cf4_seed,
    run_falsifier_suite,
    run_schedule_prompt_transfer_episode,
    run_single_domain_only_episode,
    score_att_d_proxy,
    score_p_explore_on_domain,
    score_r_explore_on_domain,
    summarize_att_d_batch,
    twin_ops_targets,
)
from eia.emergence import default_targets


class DomainOntologyTests(unittest.TestCase):
    def test_pre_registered_domains_are_disjoint(self) -> None:
        a, b = PRE_REGISTERED_DOMAINS
        self.assertTrue(domains_substantially_disjoint(a, b))
        self.assertEqual(len(PRE_REGISTERED_DOMAINS), EXPLORE_MIN_DOMAINS)
        self.assertTrue(domain_target_ids(a).isdisjoint(domain_target_ids(b)))

    def test_twin_ops_ontology_differs_from_woe_catalog(self) -> None:
        woe_ids = {t.target_id for t in default_targets()}
        twin_ids = {t.target_id for t in twin_ops_targets()}
        self.assertTrue(woe_ids.isdisjoint(twin_ids))
        self.assertTrue(all(i.startswith("ops:") for i in twin_ids))
        self.assertTrue(any(i.startswith("wm:") for i in woe_ids))


class AttDProxyTests(unittest.TestCase):
    def _hold_episode_both_pass(self) -> tuple[CrossDomainEpisode, dict[str, DomainESummary]]:
        summaries = {
            DomainId.WOE_CATALOG.value: DomainESummary(
                domain=DomainId.WOE_CATALOG,
                n_seeds=20,
                intent_rates={
                    "default": 0.9,
                    "zero_epistemic_gap": 0.05,
                    "wm_off": 0.0,
                },
                suppressing_named_factors=("zero_epistemic_gap",),
                e_endo_pattern=True,
                default_rate=0.9,
                wm_off_rate=0.0,
            ),
            DomainId.TWIN_OPS.value: DomainESummary(
                domain=DomainId.TWIN_OPS,
                n_seeds=20,
                intent_rates={
                    "default": 0.9,
                    "zero_epistemic_gap": 0.05,
                    "wm_off": 0.0,
                },
                suppressing_named_factors=("zero_epistemic_gap",),
                e_endo_pattern=True,
                default_rate=0.9,
                wm_off_rate=0.0,
            ),
        }
        ep = CrossDomainEpisode(
            arm=CrossDomainArm.CROSS_DOMAIN_HOLD,
            domains_tested=PRE_REGISTERED_DOMAINS,
            domain_e_pass={
                DomainId.WOE_CATALOG.value: True,
                DomainId.TWIN_OPS.value: True,
            },
            domains_passing=2,
            p_explore_by_domain={
                DomainId.WOE_CATALOG.value: True,
                DomainId.TWIN_OPS.value: True,
            },
            r_explore_by_domain={
                DomainId.WOE_CATALOG.value: True,
                DomainId.TWIN_OPS.value: True,
            },
            single_domain_only=False,
            schedule_prompt_transfer=False,
            emit_m0=False,
            claim_allowed=False,
        )
        return ep, summaries

    def test_cross_domain_hold_counts_as_att_d_evidence(self) -> None:
        ep, summaries = self._hold_episode_both_pass()
        self.assertEqual(ep.arm, CrossDomainArm.CROSS_DOMAIN_HOLD)
        self.assertFalse(ep.emit_m0)
        self.assertFalse(ep.claim_allowed)
        self.assertFalse(ep.as_dict()["agi_star_claim"])
        self.assertFalse(ep.as_dict()["c5_claim"])
        self.assertGreaterEqual(ep.domains_passing, EXPLORE_MIN_DOMAINS)
        self.assertTrue(ep.att_d_evidence)
        self.assertEqual(score_att_d_proxy(domain_summaries=summaries, episode=ep), 1.0)

    def test_single_domain_only_fails(self) -> None:
        ep = run_single_domain_only_episode()
        self.assertEqual(ep.arm, CrossDomainArm.SINGLE_DOMAIN_ONLY)
        self.assertTrue(ep.single_domain_only)
        self.assertEqual(ep.domains_passing, 1)
        self.assertFalse(ep.att_d_evidence)

    def test_schedule_prompt_transfer_fails(self) -> None:
        ep = run_schedule_prompt_transfer_episode()
        self.assertEqual(ep.arm, CrossDomainArm.SCHEDULE_PROMPT_TRANSFER)
        self.assertTrue(ep.schedule_prompt_transfer)
        self.assertFalse(ep.att_d_evidence)

    def test_falsifier_suite_all_fail_evidence(self) -> None:
        suite = run_falsifier_suite(seed=0)
        self.assertFalse(suite["single_domain_only"].att_d_evidence)
        self.assertFalse(suite["schedule_prompt_transfer"].att_d_evidence)

    def test_domain_cf4_seed_on_twin_ops(self) -> None:
        row = run_domain_cf4_seed(0, "default", DomainId.TWIN_OPS)
        self.assertEqual(row.domain, DomainId.TWIN_OPS)
        self.assertTrue(row.intent)

    def test_p_r_explore_proxies_on_both_domains(self) -> None:
        for domain in PRE_REGISTERED_DOMAINS:
            self.assertTrue(score_p_explore_on_domain(domain, seed=0))
            self.assertTrue(score_r_explore_on_domain(domain, seed=0))

    def test_batch_summary_never_claims_c5(self) -> None:
        # Lightweight synthetic batch shape (full n=20 CF-4 is the metrics runner).
        ep, summaries = self._hold_episode_both_pass()
        batch = {
            "n_seeds": 20,
            "domains": [d.value for d in PRE_REGISTERED_DOMAINS],
            "domains_disjoint": True,
            "domain_summaries": {k: v.as_dict() for k, v in summaries.items()},
            "hold_episode": ep.as_dict(),
            "by_arm": {
                "cross_domain_hold": {
                    "n": 1,
                    "att_d_evidence_rate": 1.0,
                    "d_proxy": 1.0,
                    "emit_m0_rate": 0.0,
                },
                "single_domain_only": {"att_d_evidence_rate": 0.0},
                "schedule_prompt_transfer": {"att_d_evidence_rate": 0.0},
            },
            "c5_claim": False,
            "agi_star_claim": False,
            "emit_m0": False,
        }
        summary = summarize_att_d_batch(batch)
        self.assertEqual(summary["att_d_evidence_rate_hold"], 1.0)
        self.assertEqual(summary["att_d_evidence_rate_single"], 0.0)
        self.assertEqual(summary["att_d_evidence_rate_schedule_prompt"], 0.0)
        self.assertFalse(summary["c5_claim"])
        self.assertFalse(summary["agi_star_claim"])


if __name__ == "__main__":
    unittest.main()
