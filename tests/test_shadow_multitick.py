"""Tests for shadow multi-tick ATT-R support (main runtime; no TG)."""

from __future__ import annotations

from eia.runtime.shadow_multitick import (
    ShadowArm,
    run_shadow_carryover_tick,
    run_shadow_episode,
    run_shadow_falsifier_suite,
)


def test_closed_loop_has_world_update_and_novel_motive() -> None:
    ep = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=3)
    kinds = {e.kind for e in ep.events}
    assert "W_prime" in kinds
    assert any(e.kind == "G_prime" and e.novel for e in ep.events)
    assert ep.shadow is True
    assert ep.live_telegram is False
    assert ep.emit_m0 is False
    assert ep.ticks_run >= 2


def test_open_loop_has_no_world_update() -> None:
    ep = run_shadow_episode(ShadowArm.OPEN_LOOP_ONCE, seed=1)
    assert not any(e.kind == "W_prime" for e in ep.events)
    assert ep.ticks_run == 1


def test_falsifier_suite_covers_all_arms() -> None:
    suite = run_shadow_falsifier_suite(seed=0)
    assert set(suite) == {a.value for a in ShadowArm}
    for ep in suite.values():
        assert ep.emit_m0 is False
        assert ep.live_telegram is False


def test_no_governor_threshold_fields_in_result() -> None:
    """Science harness must not advertise lowered contact thresholds."""
    ep = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=0)
    blob = ep.as_dict()
    assert "min_contact_score" not in blob
    assert blob["claim_allowed"] is False
    assert blob["agi_star_claim"] is False


def test_closed_loop_exports_session_carryover() -> None:
    ep = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=4)
    assert ep.carryover is not None
    assert ep.carryover.beliefs_json
    assert ep.carryover.last_motive_id in ep.motive_ids
    assert ep.carryover.drive_tick >= 1


def test_carryover_tick_produces_g_prime_without_reseed() -> None:
    ep1 = run_shadow_episode(ShadowArm.CLOSED_LOOP, seed=7)
    assert ep1.carryover is not None

    ep2 = run_shadow_carryover_tick(ep1.carryover, seed=7)
    assert ep2.used_carryover is True
    assert ep2.emit_m0 is False
    assert ep2.claim_allowed is False
    assert any(e.kind == "G_prime" and e.novel for e in ep2.events)
    assert not any(e.label == "user_prompt" for e in ep2.events)
    assert ep2.carryover is not None
    assert ep2.carryover.session_tick > ep1.carryover.session_tick
