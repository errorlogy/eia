"""Unit tests for ATT-R live/shadow closed-loop scoring (non-claiming)."""

from __future__ import annotations

import unittest

from eia.goal_recurrence import RecurrenceArm
from eia.live_att_r import (
    episode_from_shadow_log,
    events_to_nodes,
    run_live_att_r_batch_from_raw,
    score_shadow_suite,
)


def _closed_log() -> dict:
    return {
        "arm": "closed_loop",
        "events": [
            {"node_id": "n0", "kind": "W", "label": "world_model", "parent_ids": [], "tick": 0},
            {"node_id": "n1", "kind": "M", "label": "self_model", "parent_ids": ["n0"], "tick": 0},
            {"node_id": "n2", "kind": "G", "label": "mot-1", "parent_ids": ["n0", "n1"], "tick": 0},
            {"node_id": "n3", "kind": "Pi", "label": "pi", "parent_ids": ["n2"], "tick": 1},
            {"node_id": "n4", "kind": "A", "label": "act", "parent_ids": ["n3"], "tick": 1},
            {"node_id": "n5", "kind": "X", "label": "x", "parent_ids": ["n4"], "tick": 2},
            {
                "node_id": "n6",
                "kind": "W_prime",
                "label": "world_update",
                "parent_ids": ["n5", "n4"],
                "tick": 2,
            },
            {
                "node_id": "n7",
                "kind": "G_prime",
                "label": "mot-2",
                "parent_ids": ["n6", "n1"],
                "tick": 3,
                "novel": True,
            },
        ],
        "kuramoto_r": 0.42,
        "emit_m0": False,
    }


class LiveAttRUnitTests(unittest.TestCase):
    def test_events_to_nodes_maps_kinds(self) -> None:
        nodes = events_to_nodes(_closed_log()["events"])
        self.assertEqual(len(nodes), 8)
        self.assertTrue(any(n.kind.value == "W_prime" for n in nodes))

    def test_closed_log_is_att_r_evidence(self) -> None:
        ep = episode_from_shadow_log(_closed_log())
        self.assertEqual(ep.arm, RecurrenceArm.CLOSED_LOOP)
        self.assertTrue(ep.att_r_evidence)
        self.assertFalse(ep.emit_m0)
        self.assertFalse(ep.claim_allowed)

    def test_open_loop_fails(self) -> None:
        log = {
            "arm": "open_loop_once",
            "events": [
                {"node_id": "n0", "kind": "X", "label": "prompt", "parent_ids": [], "tick": 0},
                {"node_id": "n1", "kind": "G", "label": "g", "parent_ids": ["n0"], "tick": 0},
                {"node_id": "n2", "kind": "Pi", "label": "pi", "parent_ids": ["n1"], "tick": 0},
                {"node_id": "n3", "kind": "A", "label": "a", "parent_ids": ["n2"], "tick": 1},
            ],
            "kuramoto_r": 0.5,
        }
        ep = episode_from_shadow_log(log)
        self.assertFalse(ep.att_r_evidence)
        self.assertTrue(ep.open_loop_only)

    def test_kuramoto_alone_fails(self) -> None:
        log = {
            "arm": "kuramoto_only",
            "events": [
                {"node_id": "n0", "kind": "kuramoto_R", "label": "R=0.970", "parent_ids": [], "tick": 0},
                {"node_id": "n1", "kind": "W", "label": "w", "parent_ids": ["n0"], "tick": 0},
                {"node_id": "n2", "kind": "G", "label": "g", "parent_ids": ["n1"], "tick": 0},
                {"node_id": "n3", "kind": "A", "label": "a", "parent_ids": ["n2"], "tick": 1},
            ],
            "kuramoto_r": 0.97,
        }
        ep = episode_from_shadow_log(log)
        self.assertTrue(ep.kuramoto_alone)
        self.assertFalse(ep.att_r_evidence)

    def test_suite_and_batch_never_claim(self) -> None:
        suite = score_shadow_suite(
            {
                "closed_loop": _closed_log(),
                "kuramoto_only": {
                    "arm": "kuramoto_only",
                    "events": [
                        {
                            "node_id": "n0",
                            "kind": "kuramoto_R",
                            "label": "R=0.970",
                            "parent_ids": [],
                            "tick": 0,
                        },
                        {
                            "node_id": "n1",
                            "kind": "A",
                            "label": "a",
                            "parent_ids": [],
                            "tick": 1,
                        },
                    ],
                    "kuramoto_r": 0.97,
                },
            }
        )
        self.assertTrue(suite["closed_loop"].att_r_evidence)
        self.assertFalse(suite["kuramoto_only"].att_r_evidence)
        raw = {
            "closed_loop": [_closed_log() for _ in range(3)],
            "open_loop_once": [
                {
                    "arm": "open_loop_once",
                    "events": [
                        {
                            "node_id": "n0",
                            "kind": "X",
                            "label": "p",
                            "parent_ids": [],
                            "tick": 0,
                        },
                        {
                            "node_id": "n1",
                            "kind": "A",
                            "label": "a",
                            "parent_ids": ["n0"],
                            "tick": 1,
                        },
                    ],
                    "kuramoto_r": 0.4,
                }
                for _ in range(3)
            ],
        }
        batch = run_live_att_r_batch_from_raw(raw, n_seeds=3)
        self.assertFalse(batch["agi_star_claim"])
        self.assertEqual(batch["by_arm"]["closed_loop"]["att_r_evidence_rate"], 1.0)
        self.assertEqual(batch["by_arm"]["open_loop_once"]["att_r_evidence_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
